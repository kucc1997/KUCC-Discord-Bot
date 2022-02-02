from discord.ext import commands
import discord, os, json

json_path =  os.path.join(os.getcwd(),"bot", "cogs", "json", "roles.json")
with open(json_path, mode="r") as jfile:
    res = json.load(jfile)
    MESSAGE_IDS = res["message_ids"]
    EVENT_ROLES = res["event"]["roles"]

class EventHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_role("Manager")
    @commands.command(name="crev")
    async def create_event(self, ctx, *event):
        guild = ctx.message.guild
        if event is None:
            await ctx.send("Event missing... $crev <Event-Name>")
            return
        else:
            event = " ".join([e.title() for e in event])
            event_role = await guild.create_role(name=event, colour=discord.Colour.random(), mentionable=True)
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

    @commands.has_role("Manager")
    @commands.command(name="evmsg")
    async def event_message(self, ctx, *message):
        guild = ctx.message.guild
        eve_announcement_channel = discord.utils.get(guild.channels, id=929031116566958100)
        msg = await eve_announcement_channel.send(" ".join(message))
        await msg.add_reaction("☑️")

        global MESSAGE_IDS
        MESSAGE_IDS.append({"id": msg.id, "type": "event"})

        with open(json_path, "w") as jfile:
            res["message_ids"] = MESSAGE_IDS
            json.dump(res, jfile, indent = 4)

    @commands.command(name="evar")
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

        with open(json_path, "w") as jfile:
            res["message_ids"] = []
            json.dump(res, jfile, indent=4)




def setup(bot):
    bot.add_cog(EventHandler(bot))
