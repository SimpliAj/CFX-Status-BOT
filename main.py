import asyncio
import datetime
import json
from datetime import datetime
from typing import List, Tuple, Optional

import aiohttp
import aiosqlite
import discord
from discord.ext import commands

aiosqlite.register_converter('BOOLEAN', lambda v: v != '0')

with open('config.json') as f:
    config = json.load(f)

TOKEN = config['discord_bot_token']
REFRESH_INTERVAL = config['refresh_interval']


class MyBot(commands.Bot):
    db: aiosqlite.Connection
    session: aiohttp.ClientSession
    recent_embed: discord.Embed = discord.Embed(title='temp')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        """Sets up the database, attaches an aiohttp session and syncs the app commands."""

        self.session = aiohttp.ClientSession()

        self.db = await aiosqlite.connect('database.db')
        await self.db.execute(
            '''CREATE TABLE IF NOT EXISTS setups (
                channel_id INT NOT NULL PRIMARY KEY,
                send_embed BOOLEAN NOT NULL,
                send_alerts BOOLEAN NOT NULL,
                message_id INT,
                role_id INT
            )'''
        )
        await self.db.commit()

        await self.load_extension('cogs.commands')

        try:
            synced = await self.tree.sync()
            print(f'Synced {len(synced)} Command(s)')
        except Exception as e:
            print('e: {}'.format(e))

        asyncio.create_task(update_embed())

    async def close(self):
        """Closes the database connection, aiohttp session and the bot."""

        if hasattr(self, 'db'):
            await self.db.close()

        if hasattr(self, 'session'):
            await self.session.close()

        await super().close()

    async def get_alerts_data(self) -> List[Tuple[discord.TextChannel, Optional[discord.Role]]]:
        """Gets all channels which have alerts enabled and the roles to mention."""

        data = []

        sql = 'SELECT channel_id, role_id FROM setups WHERE send_alerts'
        async with self.db.execute(sql) as cursor:
            async for channel_id, role_id in cursor:
                channel = self.get_channel(channel_id)
                if channel is None:
                    continue

                role = channel.guild.get_role(role_id) if role_id else None

                data.append((channel, role))

        return data

    async def get_embed_data(self) -> List[Tuple[discord.TextChannel, Optional[discord.Message]]]:
        """Gets all channels which have embed enabled and the messages to edit."""

        data = []

        sql = 'SELECT channel_id, message_id FROM setups WHERE send_embed'
        async with self.db.execute(sql) as cursor:
            async for channel_id, message_id in cursor:
                channel = self.get_channel(channel_id)
                if channel is None:
                    continue

                message = None

                if message_id is not None:
                    try:
                        message = await channel.fetch_message(message_id)
                    except discord.HTTPException:
                        pass

                data.append((channel, message))

        return data


bot = MyBot(intents=discord.Intents.default(), command_prefix='!', help_command=None)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="CFX Status")
    )


async def fetch_status():
    status_url = config['status_url']
    components_url = config['components_url']

    async with bot.session.get(status_url) as status_response:
        status_data = await status_response.json()

    async with bot.session.get(components_url) as components_response:
        components_data = (await components_response.json())['components']

    return status_data, components_data


async def update_embed():
    downtime_start = None

    await bot.wait_until_ready()

    while not bot.is_closed():
        try:
            status_data, components_data = await fetch_status()

            status_indicator = status_data.get('status', {}).get('indicator')
            affected_components = []

            if status_indicator == 'none':
                status_text = 'All Systems Operational'
                status_emoji = ':green_circle:'
                embed_color = 6205745  # green color
                thumbnail_url = 'https://i.imgur.com/RKVLOX4.png'  # Bild für "All Systems Operational"

                if downtime_start is not None:
                    downtime_duration = int((datetime.now() - downtime_start).total_seconds() // 60)
                    downtime_start = None

                    # Senden des Embeds, wenn die Systeme wieder online sind
                    for channel, role in await bot.get_alerts_data():
                        mention = role.mention if role else ''
                        operational_embed = discord.Embed(
                            title="CFX Status Update",
                            description="Some components are back online!",
                            color=discord.Color.green()
                        )
                        operational_embed.add_field(name="Operational Components", value=affected_components_text, inline=False)
                        operational_embed.set_footer(text=f"Downtime took {downtime_duration} minute(s)", icon_url="https://i.imgur.com/VXvsDIA.png")
                        operational_embed.set_thumbnail(url='https://i.imgur.com/RKVLOX4.png')  # Thumbnail für "Systeme wieder online"

                        try:
                            await channel.send(f'{mention}', embed=operational_embed)
                        except discord.Forbidden:
                            print(f'No permissions to send a message in channel {channel}')
                        except discord.HTTPException as e:
                            print(f'Couldn\'t send a message in channel {channel} - {e}')

            else:
                status_text = 'Issues'
                status_emoji = ':orange_circle:'
                embed_color = 16711680  # red color
                thumbnail_url = 'https://i.imgur.com/pIkorRE.jpeg'  # Bild für "Issues"

                if downtime_start is None:
                    downtime_start = datetime.now()

                    # Sammeln der betroffenen Komponenten
                    status_emojis = {
                        'major_outage': ':red_circle:',
                        'degraded_performance': ':yellow_circle:',
                        'partial_outage': ':orange_circle:',
                        'under_maintenance': ':wrench:',
                    }

                    for component in components_data:
                        if component.get('status').lower() != 'operational':
                            affected_components.append(
                                f"{status_emojis.get(component.get('status').lower(), ':red_circle:')} {component.get('name')}"
                            )

                    affected_components_text = "\n".join(affected_components)

                    # Senden des Embeds, wenn Probleme auftreten (ohne Thumbnail)
                    for channel, role in await bot.get_alerts_data():
                        mention = role.mention if role else ''
                        issues_embed = discord.Embed(
                            title="CFX Status Update",
                            description="CFX has some issues and some components might not work!",
                            color=discord.Color.red()
                        )
                        issues_embed.add_field(name="Affected Components", value=affected_components_text, inline=False)
                        issues_embed.set_footer(text=f"Downtime started {downtime_start.strftime('%H:%M:%S %m-%d-%Y')}", icon_url="https://i.imgur.com/VXvsDIA.png")
                        # Kein Thumbnail für dieses Embed

                        try:
                            await channel.send(f'{mention}', embed=issues_embed)
                        except discord.Forbidden:
                            print(f'No permissions to send a message in channel {channel}')
                        except discord.HTTPException as e:
                            print(f'Couldn\'t send a message in channel {channel} - {e}')

            # Embed für den aktuellen Status aktualisieren
            embed = discord.Embed(title="CFX Status", color=embed_color)
            embed.add_field(name="Status", value=f"{status_emoji} {status_text}")

            component_lines = []
            for component in components_data:
                component_emoji = ':green_circle:' if component.get('status').lower() == 'operational' else ':red_circle:'
                formatted_status = component.get('status').replace('_', ' ').title()
                component_line = f"{component_emoji} **{component.get('name')}**: {formatted_status}"
                component_lines.append(component_line)

            embed.add_field(name="Components Status", value='\n'.join(component_lines), inline=False)
            embed.set_footer(text=f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | by @SimpiAj", icon_url="https://i.imgur.com/VXvsDIA.png")
            embed.set_thumbnail(url=thumbnail_url)  # Thumbnail für den allgemeinen Status

            bot.recent_embed = embed

            for channel, message in await bot.get_embed_data():
                if message:
                    try:
                        await message.edit(embed=embed)
                    except discord.HTTPException as e:
                        print(f'Couldn\'t edit a message in channel {channel} - {e}')
                else:
                    try:
                        new_message = await channel.send(embed=embed)
                        await bot.db.execute(
                            'UPDATE setups SET message_id = ? WHERE channel_id = ?',
                            (new_message.id, channel.id)
                        )
                        await bot.db.commit()
                    except discord.Forbidden:
                        print(f'No permissions to send a message in channel {channel}')
                    except discord.HTTPException as e:
                        print(f'Couldn\'t send a message in channel {channel} - {e}')

        except Exception as e:
            print(f"An error occurred: {str(e)}")

        await asyncio.sleep(REFRESH_INTERVAL)


bot.run(TOKEN)
