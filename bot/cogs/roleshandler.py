from discord.ext import commands

import discord, json, os

json_path =  os.path.join(os.getcwd(), "bot", "cogs", "json", "roles.json")
with open(json_path, mode="r") as jfile:
    res = json.load(jfile)
    COMMUNITY_ROLES = res["community"]["roles"]
    ROLES_CHANNEL = res["default_role_channel"]
    MESSAGE_IDS = res["message_ids"]

class RolesHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = None
    
    async def react_role(self, action, payload):
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
                if not role:
                    print(f"{role_name} Role not found")
                    return
                
                member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
                if member is not None:
                    await getattr(member, action)(role)
                else:
                    print("Member not found")


    @commands.command(name="ccr")
    async def create_roles(self, ctx):
        guild = ctx.guild
        for role in COMMUNITY_ROLES:
            await guild.create_role(name=role["name"], colour=discord.Colour(int(role["color"].replace("#", "0x"), 16)), mentionable = True)
            print(f"Creating {role['name']} role... in {guild.name} server")

    
    @commands.command(name="dcr")
    async def delete_roles(self, ctx):
        guild = ctx.guild
        for role in COMMUNITY_ROLES:
            role_object = discord.utils.get(guild.roles, name=role["name"])
            await role_object.delete()

    
    @commands.command(name="sutc")
    async def set_up_text_channel(self, ctx, channel: discord.TextChannel = None):
        if not channel:
            self.channel = self.bot.get_channel(ROLES_CHANNEL) 
        else:
            self.channel = channel
        await ctx.send(f"Set up roles channel: {self.channel.mention} :white_check_mark:")

    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.react_role("add_roles", payload)

    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.react_role("remove_roles", payload)
        
    
    @commands.has_role("Manager")
    @commands.command(name="surr")
    async def set_up_reaction_roles(self, ctx):
        if not self.channel:
            await self.set_up_text_channel(ctx)
        
        global MESSAGE_IDS

        ## Status roles
        s_msg = "**Select your status**\n"
        STATUS_ROLES = res["status"]["roles"]
        for role in STATUS_ROLES:
            s_msg += f"{role['name']}: {role['emoji']}\n"
        message = await self.channel.send(s_msg)
        MESSAGE_IDS.append({"id": message.id, "type": "status"})

        for role in STATUS_ROLES:
            await message.add_reaction(role["emoji"])

        ## CE/CS Student roles
        c_msg = "\n**Select your faculty**\n"
        CLASS_ROLES = res["class"]["roles"]
        for role in CLASS_ROLES:
            c_msg += f"{role['name']}: {role['emoji']}\n"
        message = await self.channel.send(c_msg)
        MESSAGE_IDS.append({"id": message.id, "type": "class"})

        for role in CLASS_ROLES:
            await message.add_reaction(role["emoji"])

        ## Community roles
        cr_msg = "\n**Select your preferred community (multiple allowed)**\n"
        for role in COMMUNITY_ROLES:
            cr_msg += f"{role['name']}: {role['emoji']}\n"
        message = await self.channel.send(cr_msg)
        MESSAGE_IDS.append({"id": message.id, "type": "community"})

        for role in COMMUNITY_ROLES:
            await message.add_reaction(role["emoji"])
        
        with open(json_path, "w") as jfile:
            res["message_ids"] = MESSAGE_IDS
            json.dump(res, jfile)
        
def setup(bot):
    bot.add_cog(RolesHandler(bot))
