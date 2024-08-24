from typing import TYPE_CHECKING

import discord
from discord.ext.commands import Cog
from discord import Interaction, app_commands

if TYPE_CHECKING:
    from main import MyBot


class Commands(Cog):
    bot: 'MyBot'

    def __init__(self, bot: 'MyBot'):
        self.bot = bot

    @app_commands.command()
    async def about(self, interaction: Interaction):
        """Shows general information about this bot."""

        total_members = sum([guild.member_count for guild in self.bot.guilds])

        embed = discord.Embed(
            description="Our Discord bot diligently monitors the https://status.cfx.re/ website for you, providing real-time notifications about any changes and the current status. Stay informed with accurate updates, ensuring you're always in the loop. Never miss critical updates again – this dependable bot is your solution for keeping track of stability and availability from cfx.",
            color=discord.Color.blue()
        )
        embed.set_author(
            name=self.bot.user.name,
            icon_url="https://i.imgur.com/VXvsDIA.png"
        )

        embed.add_field(name='Support', value='[Click here](https://github.com/SimpliAj/CFX-Status-BOT)',  inline=False)
        embed.add_field(
            name='Add Bot',
            value="[Click here](https://discord.com/oauth2/authorize?client_id=1276866058237775983&permissions=2048&integration_type=0&scope=bot)"
        )
        

        embed.add_field(name='Server Count', value=len(self.bot.guilds))
        embed.add_field(name='User Count', value=total_members)
        embed.set_footer(text='CFX Status bot | by @SimpiAj', icon_url="https://i.imgur.com/VXvsDIA.png")

        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.checks.has_permissions(
        administrator=True
    )  # Only members with the 'Administrator' permission can use this command
    @app_commands.default_permissions(administrator=True)  # Make it so only admins see the command by default
    async def features(self, interaction: Interaction):
        """Shows bot features."""

        embed = discord.Embed(
            title="Features",
            description=
            "Introducing the Ultimate Cfx.re Status Monitor Bot: Stay Informed, Effortlessly!\n\nSay goodbye to the tedious task of constantly checking Cfx.re's status. Our Discord bot is here to make your life easier and keep you up to date with real-time information! :alarm_clock:",
            color=discord.Color.blue()
        )

        embed.add_field(
            name='Instant Updates, Zero Hasslet',
            value="With our bot on board, you can wave goodbye to manual status checks. It tirelessly monitors https://status.cfx.re/ and delivers lightning-fast updates every 60 seconds. Stay ahead of the curve without lifting a finger!",
            inline=False
        )
        embed.add_field(
            name='Timely Alerts, No Surprises',
            value="Missed a service disruption in the past? Not anymore! Our bot not only presents status changes elegantly in embeds but also pings @everyone for significant updates. Whether it's a minor hiccup or an all-clear, you're in the loop.",
            inline=False
        )
        embed.add_field(
            name='Effortless Integration',
            value="Adding our bot to your Discord server is quick and simple. Within moments, you'll have a powerful status monitoring system right at your fingertips. No complex setups, just instant benefits.",
            inline=False
        )
        embed.add_field(
            name='Level Up Your Discord Experience',
            value="Upgrade your Discord server with our Cfx.re Status Monitor Bot. With instant updates, personalized alerts, and easy integration, you can bid farewell to constant refreshing and hello to seamless information.\n\n Don't miss out on crucial updates – add our bot now and enjoy hassle-free status tracking! :video_game::globe_with_meridians::bar_chart: Check the current ⁠cfx-status and soon you will be able to add the <@1276866058237775983> to your own discord server",
            inline=False
        )
        embed.set_thumbnail(url="https://i.imgur.com/VXvsDIA.png")
        embed.set_footer(
            text='Status Bot | by @SimpliAj',
            icon_url="https://i.imgur.com/VXvsDIA.png"
        )

        await interaction.response.send_message(embed=embed)

    @features.error
    async def features_error(self, interaction: Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "Sorry, you don't have the required permissions to use this command."
            )

        raise error

    @app_commands.command()
    async def help(self, interaction: Interaction):
        """Displays the bot commands."""

        embed = discord.Embed(
            title="Help | CFX Status Bot",
            description="Please make sure that he Bot has permissions to send messages in your discord server, otherwise the bot might not work as intended.",
            color=discord.Color.blue()
        )

   
     
        embed.add_field(
            name='Commands',
            value="/help - Displays this embed\n/features - Shows bot features*\n/about - Shows general information about this bot\n/setup - Sets up the bot*\n\nCommands with a * are limited to people who have admin rights in the discord."
        )
        embed.add_field(
            name='Emoji Status Indication:',
            value=":green_circle: Operational \n:red_circle: Major Outrage \n:orange_circle: Partial Outrage \n:yellow_circle: Degraded Performance \n:wrench: Under Maintenance"
        )
    


        embed.set_thumbnail(url="https://i.imgur.com/VXvsDIA.png")
        embed.set_footer(
            text='CFX Status bot | by @SimpliAj',
            icon_url="https://i.imgur.com/VXvsDIA.png"
        )

        await interaction.response.send_message(embed=embed)

        

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(
        channel='The channel for embed and alerts',
        send_embed='Whether embed updates should be enabled',
        send_alerts='Whether message alerts should be enabled',
        role='The role to mention in alerts, leave empty for @everyone'
    )
    async def setup(
        self,
        interaction: Interaction,
        channel: discord.TextChannel,
        send_embed: bool,
        send_alerts: bool,
        role: discord.Role = None
    ):
        """Sets up the bot."""

        await interaction.response.defer()

        message = None

        if send_embed:
            try:
                message = await channel.send(embed=self.bot.recent_embed)
            except discord.Forbidden:
                return await interaction.response.send_message(f'I cannot send a message in {channel.mention}!')

        await self.bot.db.execute('DELETE FROM setups WHERE channel_id = ?', (channel.id,))
        await self.bot.db.execute(
            'INSERT INTO setups VALUES (?, ?, ?, ?, ?)',
            (channel.id, send_embed, send_alerts, message.id if message else None, role.id if role else None)
        )
        await self.bot.db.commit()

        embed = discord.Embed(title='Setup', color=discord.Color.blue())
        embed.add_field(name='Channel', value=channel.mention)
        embed.add_field(name='Embed', value=str(send_embed))
        embed.add_field(name='Alerts', value=str(send_alerts))

        content = 'your content here'  # Replace this with your actual content

        if content == '@@everyone':
            mention = '@everyone'
        else:
            if role is None:
                mention = ''
            elif role == role.guild.default_role:
                mention = '@everyone'
            else:
                mention = role.mention

        embed.add_field(name='@Mention', value=mention if role else 'No pingrole set' )

        
        

        await interaction.followup.send(embed=embed)

    @setup.error
    async def setup_error(self, interaction: Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "Sorry, you don't have the required permissions to use this command."
            )

        raise error


async def setup(bot: 'MyBot'):
    await bot.add_cog(Commands(bot))