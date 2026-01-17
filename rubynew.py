import asyncio
import discord
from discord.ext import commands, tasks
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIG ---
TOKEN = ""
CHANNEL_ID = 1380491672487464983
CHECK_INTERVAL = 5  

URL = "https://pages.tankionline.com/summer-major-2025/dxypnfljthxi?lang=en"
LOGIN_URL = "https://tankionline.com/play/"  
RUBIES_PER_WIN = 8000
MY_OFFER_ADD = 1000


options = Options()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)


intents = discord.Intents.default()
intents.message_content = True  # IMPORTANT for commands
bot = commands.Bot(command_prefix="!", intents=intents)

last_pool_sent = None

# --- Blocking Selenium call wrapped in async ---
def blocking_fetch_ruby_pool():
    driver.get(URL)
    wait = WebDriverWait(driver, 10)

    label = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[@class='label' and text()='Rubies in the fund']")
        )
    )
    number_div = driver.find_element(
        By.XPATH,
        "//div[@class='label' and text()='Rubies in the fund']/following-sibling::div[@class='number']"
    )
    coins = number_div.get_attribute("data-coins")
    if coins:
        return int(coins)
    else:
        raise ValueError("Could not find ruby pool amount in data-coins attribute.")

async def fetch_ruby_pool():
    return await asyncio.to_thread(blocking_fetch_ruby_pool)

# --- Selenium login function ---
def blocking_login(username, password):
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 10)

    # Wait for username input
    username_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
    username_input.clear()
    username_input.send_keys(username)

    # Password input
    password_input = driver.find_element(By.ID, "password")
    password_input.clear()
    password_input.send_keys(password)

   
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()

    # Wait for login success or failure, example: check URL or presence of element
    try:
        wait.until(EC.url_changes(LOGIN_URL))
        # Or wait for a user profile element, example:
        wait.until(EC.presence_of_element_located((By.ID, "profile-icon")))
        return True
    except:
        return False

async def login(username, password):
    return await asyncio.to_thread(blocking_login, username, password)

# --- Task to check ruby pool ---
@tasks.loop(seconds=CHECK_INTERVAL)
async def check_ruby_pool():
    global last_pool_sent
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f" ERROR: Could not find channel with ID {CHANNEL_ID}")
        return

    try:
        pool = await fetch_ruby_pool()
        winners_before = pool // RUBIES_PER_WIN
        new_pool = pool + MY_OFFER_ADD
        winners_after = new_pool // RUBIES_PER_WIN

        # Send alert only if a new winner slot opens
        if winners_after > winners_before:
            await channel.send(
                f"**BUY NOW!**\n Ruby Pool: `{pool}`\n➕ After 1000 rubies: `{new_pool}`\n This will trigger a NEW WINNER SLOT!"
            )

        # Send current pool update ONLY if it changed
        if last_pool_sent != pool:
            await channel.send(f" Current Ruby Pool: `{pool}` | Winners: `{winners_before}`")
            last_pool_sent = pool

    except Exception as e:
        print(f"Error checking ruby pool: {e}")
        if channel:
            await channel.send(" Error: Ruby pool not found on the page.")

# --- Command: !pool ---
@bot.command(name="pool")
async def pool(ctx):
    try:
        pool = await fetch_ruby_pool()
        winners = pool // RUBIES_PER_WIN
        await ctx.send(f" Current Ruby Pool: `{pool}` | Winners: `{winners}`")
    except Exception as e:
        print(f"Error in !pool command: {e}")
        await ctx.send("Error: Ruby pool not found on the page.")

# --- Command: !buyamt ---
@bot.command(name="buyamt")
async def buyamt(ctx):
    try:
        pool = await fetch_ruby_pool()
        current_level = pool // RUBIES_PER_WIN
        next_threshold = (current_level + 1) * RUBIES_PER_WIN
        buy_amount = next_threshold - MY_OFFER_ADD

        await ctx.send(
            f" To trigger the next winner slot, buy when the pool is at or above `{buy_amount}` rubies.\n"
            f"Current pool: `{pool}` | Next winner slot: `{next_threshold}`"
        )
    except Exception as e:
        print(f"Error in !buyamt command: {e}")
        await ctx.send(" Error: Could not calculate buy amount.")

# --- !tell command ---
@bot.command(name="tell")
async def tell(ctx):
    await ctx.send(f"{ctx.author.mention} Please send your credentials in the format `USER : PASSWORD` in this channel. I will delete your message immediately for privacy.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=60)  # wait max 60 sec
        # Delete user message for privacy
        await msg.delete()

        # Parse USER : PASSWORD
        if ':' not in msg.content:
            await ctx.send(f"{ctx.author.mention} Invalid format! Use `USER : PASSWORD`")
            return

        user, password = [x.strip() for x in msg.content.split(':', 1)]
        await ctx.send(f"{ctx.author.mention} Logging in...")

        success = await login(user, password)
        if success:
            await ctx.send(f"{ctx.author.mention} Login successful! ")
           
        else:
            await ctx.send(f"{ctx.author.mention} Login failed. Check your credentials and try again.")
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention} Timeout: you took too long to send your credentials.")


@bot.event
async def on_ready():
    print(f" Logged in as {bot.user}")
    if not check_ruby_pool.is_running():
        check_ruby_pool.start()
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("Bot is online and monitoring Ruby Pool!")
    else:
        print(f" ERROR: Could not find channel with ID {CHANNEL_ID} on startup")


bot.run(TOKEN)

