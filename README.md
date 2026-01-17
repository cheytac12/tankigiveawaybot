<img width="1014" height="402" alt="image" src="https://github.com/user-attachments/assets/8180647d-4222-4f9c-9d09-544363b4cba3" /># RubyNotifi — Discord Giveaway Alert Bot

RubyNotifi is a Discord bot that tracks the live Ruby Fund on the Tanki Online Summer Major 2025 giveaway page and notifies users when purchasing the 1390-ruby offer (adding 1000 rubies to the pool) would result in a new winner being added.

The bot is designed to help users maximize their probability of being selected by timing their purchase as close as possible to a winner threshold.



## Overview

- The giveaway selects **1 winner for every 8000 rubies** added to the fund.
- The 1390-ruby offer contributes **1000 rubies** to the pool.
- The bot continuously checks the live fund value and determines whether purchasing the offer at that moment would cross a new winner threshold.



## Features

- Live scraping of the Ruby Fund from a JavaScript-rendered webpage
- Automatic Discord notifications when it is optimal to buy
- Command to display the current ruby pool and winner count
- Configurable check interval



## Technical Approach

Because the giveaway page renders data dynamically via JavaScript, the bot uses **Selenium with a headless Chrome browser** to retrieve the current ruby pool value. Discord integration is handled using `discord.py`.

The buy condition is evaluated as:
(current_pool + 1000) // 8000 > current_pool // 8000


If the condition is true, a notification is sent to the configured Discord channel.



## Requirements

- Python 3.9 or newer
- Google Chrome browser
- ChromeDriver (must match the installed Chrome version)

### Python dependencies


## Setup

1. Create a Discord application and bot via the Discord Developer Portal.
2. Enable **Message Content Intent** for the bot.
3. Invite the bot to your server using the OAuth2 URL generator.
4. Copy the bot token and channel ID.
5. Update the following variables in the script:

```python
TOKEN = "YOUR_DISCORD_BOT_TOKEN"
CHANNEL_ID = YOUR_CHANNEL_ID
```

6. Run the bot:

```python
python ruby_bot_discord.py



