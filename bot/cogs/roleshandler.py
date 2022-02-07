import discord
from discord.ext import commands
from discord_components import Button, ButtonStyle, InteractionEventType 
from .tickethandler import TicketHandler

import json, os, asyncio
from typing import Tuple

json_path =  os.path.join(os.getcwd(),"bot", "cogs", "json", "roles.json")
with open(json_path, mode="r") as jfile:
    res = json.load(jfile)
    COMMUNITY_ROLES = res["community"]["roles"]
    ROLES_CHANNEL_1 = res["default_role_channel1"]
    ROLES_CHANNEL_2 = res["default_role_channel2"]
    MESSAGE_IDS = res["message_ids"]

class RolesHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel1 = None
        self.channel2 = None

    def _get_role_message(self, msg, roles):
        msg += "**——————————————————————————————\n"
        for role in roles:
            msg += f"{role['name']} - {role['emoji']}\n"
        msg += "——————————————————————————————**\n"
        return msg

    async def react_role(self, action, payload):
        with open(json_path, mode="r") as jfile:
            res = json.load(jfile)

        if payload.user_id == self.bot.user.id:
            return

        for message in MESSAGE_IDS:
            if payload.message_id == message["id"]:
                guild_id = payload.guild_id
                guild = discord.utils.find(lambda g: g.id == guild_id, self.bot.guilds)

                for r in res[message["type"]]["roles"]:
                    names = r.get("emoji"), r.get("emojiname"), r.get("name")
                    if payload.emoji.name in names:
                        role_name = r["name"]
                        break
                else:
                    role_name = None

                role = discord.utils.get(guild.roles, name=role_name)
                member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
                if not role:
                    print(f"{role_name} Role not found for {payload.emoji}")
                    try:
                        message1 = await self.channel1.fetch_message(message["id"])
                        await message1.remove_reaction(payload.emoji, member)
                    except:
                        pass

                    try:
                        message2 = await self.channel2.fetch_message(message["id"])
                        await message2.remove_reaction(payload.emoji, member)
                    except:
                        pass
                    return

                if member is not None:
                    await getattr(member, action)(role)
                else:
                    print("Member not found")

    @commands.has_any_role('Manager')
    @commands.command(name="ccr", brief="Create community roles")
    async def create_roles(self, ctx):
        guild = ctx.guild
        for role in COMMUNITY_ROLES:
            await guild.create_role(name=role["name"], colour=discord.Colour(int(role["color"].replace("#", "0x"), 16)), mentionable = True)
            print(f"Creating {role['name']} role... in {guild.name} server")

    @commands.has_any_role('Manager')
    @commands.command(name="dcr", brief="Delete all community roles")
    async def delete_roles(self, ctx):
        guild = ctx.guild
        for role in COMMUNITY_ROLES:
            role_object = discord.utils.get(guild.roles, name=role["name"])
            try:
                await role_object.delete()
            except AttributeError:
                pass

    @commands.has_any_role('Manager', 'Moderator')
    @commands.command(name="sutc", brief="Set up text channels for roles")
    async def set_up_text_channel(self, ctx=None, *channel: discord.TextChannel):
        if not channel:
            self.channel1 = self.bot.get_channel(ROLES_CHANNEL_1)
            self.channel2 = self.bot.get_channel(ROLES_CHANNEL_2)
        else:
            try:
                self.channel1, self.channel2 = channel
            except:
                self.channel2 = self.bot.get_channel(ROLES_CHANNEL_2)

        if ctx:
            await ctx.send(f"Set up roles channel: {self.channel1.mention} :white_check_mark:\nSet up kucc roles channel: {self.channel2.mention} :white_check_mark:")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.set_up_text_channel()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.react_role("add_roles", payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.react_role("remove_roles", payload)
    
    @commands.Cog.listener("on_button_click")
    async def role_button_clicked(self, payload):
        ce_role = discord.utils.get(payload.guild.roles, name="CE")
        cs_role = discord.utils.get(payload.guild.roles, name="CS")
        ai_role = discord.utils.get(payload.guild.roles, name="BTech AI")
        member = payload.user
        if payload.custom_id == "CE":
            await member.add_roles(ce_role)
            await member.remove_roles(cs_role)
            await member.remove_roles(ai_role)
            await payload.respond(content="Assigned Computer Engineering role")
        elif payload.custom_id == "CS":
            await member.add_roles(cs_role)
            await member.remove_roles(ce_role)
            await member.remove_roles(ai_role)
            await payload.respond(content="Assigned Computer Science role")
        elif payload.custom_id == "AI":
            await member.add_roles(ai_role)
            await member.remove_roles(cs_role)
            await member.remove_roles(ce_role)
            await payload.respond(content="Assigned BTech AI role")

    @commands.has_any_role('Manager', 'Moderator')
    @commands.command(name="surr", brief="Sets up roles in role channels")
    async def set_up_reaction_roles(self, ctx):
        if not self.channel1:
            await self.set_up_text_channel(ctx)

        global MESSAGE_IDS

        # Introductory message
        await self.channel1.send("**React to the roles relative to you to gain access to different parts of the server 😇**")

        ## Status roles
        await self.channel1.send(file=discord.File("assets/statusRoles.png"));
        s_msg = "**Select according to your current status**\n"
        s_msg = self._get_role_message(s_msg, res["status"]["roles"])
        message = await self.channel1.send(s_msg)
        MESSAGE_IDS.append({"id": message.id, "type": "status"})

        for role in res["status"]["roles"]:
            await message.add_reaction(role["emoji"])

        ## CE/CS Student roles
        embed = discord.Embed(title="KUCC Faculty", description="Select your faculty from Department of Computer Science and Engineering\n**Computer Engineering** or **Computer Science**\n")
        await self.channel2.send(embed=embed, components=[[
            Button(style=ButtonStyle.green, label="CE", custom_id="CE"),
            Button(style=ButtonStyle.green, label="CS", custom_id="CS"),
            Button(style=ButtonStyle.green, label="BTech AI", custom_id="AI")]
        ])

        ## KUCC Member
        message = await self.channel2.send(file=discord.File("assets/kuccMember.png"))
        
        # Community roles
        await self.channel1.send(file=discord.File("assets/communityRoles.png"))
        cr_msg = "\n**Select your preferred community (multiple allowed)**\n"
        cr_msg = self._get_role_message(cr_msg, COMMUNITY_ROLES)
        message = await self.channel1.send(cr_msg)
        MESSAGE_IDS.append({"id": message.id, "type": "community"})

        for role in COMMUNITY_ROLES:
            await message.add_reaction(role["emoji"])

        with open(json_path, "w") as jfile:
            res["message_ids"] = MESSAGE_IDS
            json.dump(res, jfile, indent = 4)

def setup(bot):
    bot.add_cog(RolesHandler(bot))
