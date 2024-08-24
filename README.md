# CFX-Status-BOT


This bot was originally developed for use with my own FiveM server and has since been adapted to support multiple Discord servers. Written in Python, this bot monitors the CFX.re status page (https://status.cfx.re/) for any changes in server status. It stores all settings in a local database file.

You can add my 24/7 CFX Status bot by clicking [here](https://discord.com/oauth2/authorize?client_id=1276866058237775983&permissions=2048&integration_type=0&scope=bot)


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

## Bot Commands:

- /help - Displays this embed
- /features - Shows bot features*
- /about - Shows general information about this bot
- /setup - Sets up the bot*

Commands with a * are limited to people who have admin rights in the discord.


When you run the /setup command the Bots want a few things which you setup:
- channel (set the channel where the bot should post)
- send_embed (true/false) This will send the Overview Embed
- send_alerts (true/false) This will set if alerts on change will be sent
- role (set Pingrole) this will add to the alerts the pingrole.
When you do not want a Pingrole just don't set the role


1. /setup channel: #channel send_embed: true send_alerts: true role: @PINGROLE 
(this would send Permanent Status embed + Notify on Changes into same Discord Channel with Roleping)
2. /setup channel: #channel2 send_embed: false send_alerts: true role: @PINGROLE 
(this would not send the Status Embed, it would Notify on Changes into the Channel Discord Channel with a Roleping)


# Future Plans

In a future update, I plan to add configuration options to customize the thumbnail URLs for the status embed and error messages.
