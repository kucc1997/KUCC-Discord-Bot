import discord
from discord.ext import commands
from discord_components import Button, ButtonStyle, InteractionEventType

import json, os, asyncio
from typing import Tuple

json_path =  os.path.join(os.getcwd(), "bot", "cogs", "json", "roles.json")
with open(json_path, mode="r") as jfile:
    res = json.load(jfile)
    COMMUNITY_ROLES = res["community"]["roles"]
    ROLES_CHANNEL_1 = res["default_role_channel1"]
    ROLES_CHANNEL_2 = res["default_role_channel2"]
    MESSAGE_IDS = res["message_ids"]
    VERIFY_CHANNELS= res["verify-channels"]
    VERIFY_CHANNELS_COUNT = len(VERIFY_CHANNELS)

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
    
    async def _verify_id(self, context, member):
        global VERIFY_CHANNELS_COUNT
        channel_name = "verify-membership-" + str(VERIFY_CHANNELS_COUNT+1)
        guild = context.guild
        category = discord.utils.get(guild.categories, id=932855860898693131)
        admin_role = discord.utils.get(guild.roles, name="Manager")
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if not existing_channel:
            print(f'Creating a new channel: {channel_name}')
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
                admin_role: discord.PermissionOverwrite(read_messages=True),
                member:discord.PermissionOverwrite(read_messages=True)
            }
            channel = await guild.create_text_channel(channel_name,overwrites=overwrites,category=category)
            with open(json_path, mode="w") as jfile:
                VERIFY_CHANNELS_COUNT += 1
                res["verify-channels"].append(channel.id)
                json.dump(res, jfile, indent=4)
        else:
            VERIFY_CHANNELS_COUNT += 1
            await self.verify_id(context, member)

        await channel.send(f"{member.mention} Verify your membership by sending picture or digital image of your KUCC Membership card. Once the {admin_role.mention} confirm your validity, you will be given the KUCC Member role.") 
        
    
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
                    if (message["type"] == "member" and action=="add_roles"):
                        if payload.emoji.name == "✅":
                            msg = await self.channel2.fetch_message(message["id"])
                            ctx = await self.bot.get_context(msg)
                            await self._verify_id(ctx, member)
                            return

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

    @commands.has_role("Manager")
    @commands.command(name="ccr")
    async def create_roles(self, ctx):
        guild = ctx.guild
        for role in COMMUNITY_ROLES:
            await guild.create_role(name=role["name"], colour=discord.Colour(int(role["color"].replace("#", "0x"), 16)), mentionable = True)
            print(f"Creating {role['name']} role... in {guild.name} server")

    @commands.has_role("Manager")
    @commands.command(name="dcr")
    async def delete_roles(self, ctx):
        guild = ctx.guild
        for role in COMMUNITY_ROLES:
            role_object = discord.utils.get(guild.roles, name=role["name"])
            await role_object.delete()

    @commands.has_role("Manager")
    @commands.command(name="sutc")
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
        
    @commands.has_role("Manager")
    @commands.command()
    async def verify(self, ctx, member: discord.Member):
        guild = ctx.guild
        channel = ctx.channel
        await member.add_roles(discord.utils.get(guild.roles, name="KUCC Member"))
        await ctx.send(f"{member.mention} You are verified. :white_check_mark:\n\n **Closing this channel in...**")
        timer = 5
        while timer > 0:
            await ctx.send(f"**-- {timer} --**")
            await asyncio.sleep(1)
            timer -= 1
        VERIFY_CHANNELS.remove(channel.id)
        with open(json_path, mode="w") as jfile:
                res["verify-channels"] = VERIFY_CHANNELS
                json.dump(res, jfile, indent=4)
        global VERIFY_CHANNELS_COUNT
        VERIFY_CHANNELS_COUNT -= 1
        await channel.delete()

    
    @commands.has_role("Manager")
    @commands.command(name="surr")
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
        c_msg = "\n**If you are from Department of Computer Science and Engineering, do select your faculty**\n"
        c_msg = self._get_role_message(c_msg, res["class"]["roles"])
        message = await self.channel2.send(c_msg)
        MESSAGE_IDS.append({"id": message.id, "type": "class"})
        for role in res["class"]["roles"]:
            await message.add_reaction(role["emoji"])
        
        ## KUCC Member
        message = await self.channel2.send(file=discord.File("assets/kuccMember.png"), components = [
            [Button(label="Yes, Verify", style=ButtonStyle.green, custom_id="verify"),
            Button(label="No, Apply", style=ButtonStyle.URL, url="http://kucc.ku.edu.np/register/")]]);
        
        # response = await self.bot.wait_for("button_click", check=lambda i: i.custom_id == "verify")
        # if response:
        #     member = discord.utils.find(lambda m: m.id == response.user.id, ctx.guild.members)
        #     await self._verify_id(ctx, member)
        #     await response.respond(
        # content=f'Check your verification channel {member.mention}'
        # )
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        MESSAGE_IDS.append({"id": message.id, "type": "member"})

        # Community roles
        await self.channel1.send(file=discord.File("assets/communityRoles.png"));
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
