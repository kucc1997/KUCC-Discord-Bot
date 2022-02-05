from discord.ext import commands
from discord import Embed, utils, PermissionOverwrite
from discord_components import DiscordComponents, Button, ButtonStyle
import asyncio
import random
import re

class TicketHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notification_channel_id = 939156961520398357
        self.moderator_role_id = 927212191571136523
        self.kucc_member_role = 931537416421015602
        self.ticket_category_name = "Tickets"
        self.claimed_category_name = "Active Support"
        self.verification_category_name = "KUCC Verification"

    async def create_support_ticket(self, payload, guild, category, overwrites):
        #Create a new ticket with unique name
        if payload.custom_id == "lan_query":
            channel_name = 'language-' + str(random.randint(300,9000))
        elif payload.custom_id == "ind_query":
            channel_name = 'industry-' + str(random.randint(300,9000))
        elif payload.custom_id == "gen_query":
            channel_name = 'general-' + str(random.randint(300,9000))
        elif payload.custom_id == "rep_query":
            channel_name = 'report-' + str(random.randint(300,9000))
        channel_exists = utils.get(guild.channels, name=channel_name)
        if not channel_exists:
            channel = await guild.create_text_channel(channel_name, category = category, overwrites=overwrites)

        response = await payload.respond(content=f"<#{channel.id}> Ticket created")
        info = '''Someone from the team will be with you sortly. Please add the details about your question or request in this channel. This will help us understand it better and solve it faster.\n\nTo close🔐 the ticket press the button below.'''
        embedTic = Embed(description=info, color=0x384077)
        embedTic.set_footer(text="KUCC - Kathmandu University Computer Club", icon_url="http://kucc.ku.edu.np/wp-content/uploads/2020/11/kucc-2048x1666.png")
        await channel.send(
            content = f"{payload.user.mention}",
            embed=embedTic,
            components=[[
                Button(style=ButtonStyle.red, label="🔐Close Ticket", custom_id="close_ticket")
                ]]
            )

        notification_channel  = guild.get_channel(self.notification_channel_id)
        notification = f'{payload.user.mention} has opened ticket <#{channel.id}>'
        embedNotification = Embed(title="Support", description=notification, color=0xEA1537)
        embedNotification.set_footer(text=f"🎫{channel} is unclaimed", icon_url="")
        await notification_channel.send(
            embed=embedNotification,
            components=[[
                Button(style=ButtonStyle.red, label="Claim", custom_id="claim_ticket")
                ]]
            )

    async def create_verification_ticket(self, payload, guild, category, overwrites):
        channel_name = 'verify-' + str(random.randint(300,9000))
        channel_exists = utils.get(guild.channels, name=channel_name)
        if not channel_exists:
            channel = await guild.create_text_channel(channel_name, category = category, overwrites=overwrites)

        response = await payload.respond(content=f"<#{channel.id}> Ticket created")
        info = '''Someone from the team will be with you sortly. Please send a photo of your **KUCC ID card** for verification.\n\nTo close🔐 the ticket press the button below. The green button is for use by **authorized individuals** only.'''
        embedTic = Embed(description=info, color=0x384077)
        embedTic.set_footer(text="KUCC - Kathmandu University Computer Club", icon_url="http://kucc.ku.edu.np/wp-content/uploads/2020/11/kucc-2048x1666.png")
        await channel.send(
            content = f"{payload.user.mention}",
            embed=embedTic,
            components=[[
                Button(style=ButtonStyle.red, label="🔐Close Ticket", custom_id="close_ticket"),
                Button(style=ButtonStyle.green, label="Give the Role", custom_id="grant_kucc_member_role")
                ]]
            )

        notification_channel  = guild.get_channel(self.notification_channel_id)
        notification = f'{payload.user.mention} has opened ticket <#{channel.id}>'
        embedNotification = Embed(title="Verification", description=notification, color=0x384077)
        embedNotification.set_footer(text=f"🎫{channel} for role verification", icon_url="")
        await notification_channel.send(embed=embedNotification)

    async def claim_ticket_click(self, payload, guild, category):
        channel  = guild.get_channel(self.notification_channel_id)
        message = payload.message
        embedNotification = message.embeds[0]

        ticket_id = re.findall(r'<#(.*?)>',embedNotification.description)[0]
        ticket_to_move  = guild.get_channel(int(ticket_id))

        await ticket_to_move.edit(category=category)

        embedNotification.color = 0x05A580
        embedNotification.set_footer(text=f"{payload.user} claimed 🎫{ticket_to_move}", icon_url="")
        await message.edit(embed=embedNotification,
               components=[])

    @commands.has_any_role('Manager', 'Moderator')
    @commands.command(name="delete", brief='Deletes all channels inside "Tickets" category.')
    async def delete(self, ctx):
        category = utils.get(ctx.guild.categories, name = self.ticket_category_name)
        for channel in category.channels:
            await channel.delete()

    @commands.has_any_role('Manager', 'Moderator')
    @commands.command(name="set_notifier", brief='Sets up current channel to receive ticket notification.')
    async def set_notifier(self, ctx):
        self.notification_channel_id = ctx.channel.id
        embed = Embed(description = f"{ctx.channel.mention} set as **ticket notification channel**")
        await ctx.channel.send(embed=embed)

    @commands.has_any_role('Manager', 'Moderator')
    @commands.command(name="check_categories", brief='Checks if required categories exists, if not creates.')
    async def check_categories(self, ctx):
        embed = Embed(description = "Checking if required categories exist...")
        await ctx.channel.send(embed=embed, delete_after = 3)
        categories = [self.ticket_category_name, self.claimed_category_name, self.verification_category_name]
        for category in categories:
            category_exists = utils.get(ctx.guild.categories, name = category)
            if not category_exists:
                await ctx.guild.create_category(category)

    # Giver KUCC member role to user on button press
    @commands.Cog.listener('on_button_click')
    async def claim_ticket(self, payload):
        if payload.custom_id == "grant_kucc_member_role":
            moderator_role = utils.get(payload.guild.roles, id=self.moderator_role_id)
            if moderator_role in payload.user.roles:
                async for message in payload.channel.history(oldest_first = True, limit = 1):
                    member_role = utils.get(message.guild.roles, id= self.kucc_member_role)
                    await message.mentions[0].add_roles(member_role)
                    response = await payload.respond(content=f"Role **{member_role}** granted to **{message.mentions[0]}**")
            else:
                response = await payload.respond(content=f"**Give the Role** button is for use by **authorized individuals** only")


    @commands.Cog.listener('on_button_click')
    async def button_clicked(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        moderator_role = utils.get(guild.roles, id=self.moderator_role_id)
        ticket_overwrites = {
        moderator_role: PermissionOverwrite(read_messages=True),
        payload.user: PermissionOverwrite(read_messages=True),
        payload.message.author: PermissionOverwrite(read_messages=True),
        guild.default_role: PermissionOverwrite(read_messages=False),
        }

        if "query" in payload.custom_id.split('_'):
            category = utils.get(guild.categories, name = self.ticket_category_name)
            await self.create_support_ticket(payload, guild, category, ticket_overwrites)
        elif payload.custom_id == "member_verification":
            category = utils.get(guild.categories, name = self.verification_category_name)
            await self.create_verification_ticket(payload, guild, category, ticket_overwrites)
        elif payload.custom_id == "close_ticket":
            await payload.channel.delete()
        elif payload.custom_id == "claim_ticket":
            category = utils.get(guild.categories, name = self.claimed_category_name)
            await self.claim_ticket_click(payload, guild, category)

    @commands.has_any_role('Manager', 'Moderator')
    @commands.command(name="setup_support", brief='Sets up support ticket-counter in current channel.')
    async def setup_support(self, ctx):
        guild = ctx.guild
        title = "KUCC Support"
        description = '''Is there a problem that you're facing? Reach out to our moderators for support, questions, or requests.

                        Click the button that corresponds to your specific request type to open a ticket🎟 and reach out to us.

                        **Language Queries**- (Python, JS, Dart, etc)
                        **Industry Trends** - Cloud, ML, AI, Blockchain etc
                        **General Guidance** - For any kind of guidance from the community
                        **Report Incident** - For any violation of code of conduct
                        '''
        embedVar = Embed(title=title, description=description, color=0x384077)
        embedVar.set_footer(text="KUCC - Kathmandu University Computer Club", icon_url="http://kucc.ku.edu.np/wp-content/uploads/2020/11/kucc-2048x1666.png")
        await ctx.send(
            embed=embedVar,
            components=[[
                Button(style=ButtonStyle.grey, label="Language Queries", custom_id="lan_query"),
                Button(style=ButtonStyle.grey, label="Industry Trends", custom_id="ind_query"),
                Button(style=ButtonStyle.grey, label="General Guidance", custom_id="gen_query"),
                Button(style=ButtonStyle.grey, label="Report Incident", custom_id="rep_query")
                ]]
            )

    @commands.has_any_role('Manager', 'Moderator')
    @commands.command(name="setup_verify", brief='Sets up verification ticket-counter in current channel.')
    async def setup_verify(self, ctx):
        guild = ctx.guild
        channel = self.bot.get_channel(939151573098037298)
        title = "KUCC member role verification"
        description = '''There are various perks of having the **KUCC Member** role in this server. To access that role you need to first verify your identity as a KUCC member.

                        Click the **verify** button to open a ticket and start your verification process or the **apply** button to apply for membership.
                        '''
        embedVar = Embed(title=title, description=description, color=0x384077)
        embedVar.set_footer(text="KUCC - Kathmandu University Computer Club", icon_url="http://kucc.ku.edu.np/wp-content/uploads/2020/11/kucc-2048x1666.png")
        await channel.send(
            embed=embedVar,
            components=[[
                Button(style=ButtonStyle.grey, label="🎟 Verify", custom_id="member_verification"),
                Button(style=ButtonStyle.URL, label="Apply Now", custom_id="redirect_kucc", url="http://kucc.ku.edu.np/register/")
                ]]
            )

def setup(bot):
    bot.add_cog(TicketHandler(bot))
