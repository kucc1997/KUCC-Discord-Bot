from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle

import discord, os, json

json_path =  os.path.join(os.getcwd(),"bot", "cogs", "json", "roles.json")
with open(json_path, mode="r") as jfile:
    res = json.load(jfile)
    MESSAGE_IDS = res["message_ids"]

class EventHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_channel_id = 933010435559555183
        self.event_mod_channel_id = 939152289791344670
        self.moderator_role_id = 927212191571136523
        self.archive_category = "Archives"

    @commands.has_any_role('Manager', 'Moderator')
    @commands.command(brief="Create event roles and category >create_event Intro to Python Workshop")
    async def create_event(self, ctx, *event):
        guild = ctx.message.guild
        if event is None:
            await ctx.send("Event missing... $crev <Event-Name>")
            return
        else:
            event = " ".join(event)
            colour = discord.Colour.random()
            event_role = await guild.create_role(name=event, colour=colour, mentionable=True)
            admin_role = discord.utils.get(guild.roles, name="Manager")
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
                admin_role: discord.PermissionOverwrite(read_messages=True),
                event_role:discord.PermissionOverwrite(read_messages=True)
            }

            event_category = await guild.create_category(event, overwrites=overwrites)
            gen_tc = await guild.create_text_channel("General", category=event_category)
            await guild.create_text_channel("Resources", category=event_category)
            await guild.create_voice_channel("VC", category=event_category)

            await ctx.send(f"Created the {event_role.mention} event role and event category in {gen_tc.mention}")

            with open(json_path, "w") as jfile:
                res["event"]["roles"] = [{"name": event, "emoji": "☑️"}]
                json.dump(res, jfile, indent=4)
            
            mod_channel = self.bot.get_channel(self.event_mod_channel_id)
            embed = discord.Embed(title=event, description=f"**Created by:** {ctx.author.mention}\n\nEvent category: **{event}**\n\nEvent Role: {event_role.mention}\n\nEvent channel: {gen_tc.mention}\n\nStatus: **Open**\n", color=colour)
            await mod_channel.send(embed=embed, components=[
                Button(style=ButtonStyle.red, label="Close", custom_id=f"close_event_{'_'.join(event.split())}")
            ])
    
    async def close_event(self, payload, event):
        guild = payload.guild
        category = discord.utils.get(guild.categories, name=event)
        arc_category = discord.utils.get(guild.categories, name=self.archive_category)
        general_tc = discord.utils.get(category.channels, name="general")
        event_role = discord.utils.get(guild.roles, name=event)

        ## Deleting event role
        await event_role.delete()

        ## Archiving channel
        await general_tc.edit(category=arc_category, name=category.name)
        for c in category.channels:
            await c.delete()
        await category.delete()

        ## Editing status
        message = payload.message
        embed = message.embeds[0]
        description = embed.description[:-8] + "**Closed**\n"
        embed.description = description
        await message.edit(embed=embed, components = [Button(style=ButtonStyle.grey, label="Close", custom_id=f"close_event_{'_'.join(event.split())}", disabled=True)])
        

    @commands.has_any_role('Manager', 'Moderator')
    @commands.command(name="event_msg", brief="Announce event and its description on the event channel\n **>eventmsg @event \"event description, mentions and links\"**")
    async def event_message(self, ctx, role, message):
        guild = ctx.message.guild
        eve_announcement_channel = discord.utils.get(guild.channels, id=933010435559555183)
        role = discord.utils.get(guild.roles, id=int(role[3:-1]))
        msg = await eve_announcement_channel.send(message, components=[[
            Button(style=ButtonStyle.green, label="Interested", custom_id=f"role_{role.name}"),
            Button(style=ButtonStyle.red, label="Not Interested", custom_id="not_interested"),
        ]])

    @commands.command(name="evar", brief="Archive event with id (not necessary) >evar <category_id>")
    async def event_archive(self, ctx, id):
        guild = ctx.message.guild
        category = discord.utils.get(guild.categories, id=int(id))
        arc_category = discord.utils.get(guild.categories, id=933010712396202015)
        general_tc = discord.utils.get(category.channels, name="general")

        await general_tc.edit(category=arc_category, name=category.name)
        for c in category.channels:
            await c.delete()
        await category.delete()
        await ctx.send(f"Deleted {id} category")


    @commands.Cog.listener('on_button_click')
    async def event_button_clicked(self, payload):
        message = payload.message
        event = message.embeds[0].title
        try:
            if payload.custom_id == f"close_event_{'_'.join(event.split())}":
                moderator_role = discord.utils.get(payload.guild.roles, id=self.moderator_role_id)
                if moderator_role in payload.user.roles:
                    await payload.respond(content=f"Purged {event} category and role")
                    await self.close_event(payload, event)
                else:
                    response = await payload.respond(content=f"**Event: {event}** can only be closed by **Moderators**.")
        except AttributeError:
            pass
    
    @commands.Cog.listener('on_button_click')
    async def events_interest(self, payload):
        if payload.custom_id == "not_interested":
            await payload.respond(content="Aww, okay. Stay on hold for upcoming events.")
        elif payload.custom_id.startswith("role_"):
            event = payload.custom_id[5:]
            role = discord.utils.get(payload.guild.roles, name=event)
            category = discord.utils.get(payload.guild.categories, name=event)
            channel = discord.utils.get(category.channels, name="general")
            await payload.user.add_roles(role)
            await payload.respond(content=f"{role.mention} role has been assigned.")
            # await channel.send(f"Everything starts with an interest. {payload.user.mention} Stay tuned for further notice.")
            
    


def setup(bot):
    bot.add_cog(EventHandler(bot))
