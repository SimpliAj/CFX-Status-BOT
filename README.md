# CFX-Status-BOT


This bot was originally developed for use with my own FiveM server and has since been adapted to support multiple Discord servers. Written in Python, this bot monitors the CFX.re status page (https://status.cfx.re/) for any changes in server status.

## Key features include:

- Automatic updates to an existing status embed when there are changes.
- The ability to send a new embed in the same or a different channel to notify users about which components are down or back online.

This bot is a useful tool for staying informed about the status of CFX.re services across your or multiple Discord communities.

## Config Editing:

To set up the bot, follow these steps:

1. Open the config.json file.
2. Enter your Discord Bot Token.
3. Adjust the refresh interval if needed (default is 60 seconds).

**Optional:** If you're familiar with the configuration, you can also change the status page that the bot monitors, provided it uses the https://statuspage.io/ platform but you have to edit the  thumbnail_url in main.py by yourself.

In a future update, I plan to add configuration options to customize the thumbnail URLs for the status embed and error messages.
