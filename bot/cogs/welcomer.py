from discord.ext import commands

test_channel_id = 929217867642187826

class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(test_channel_id)
        if channel is not None:
            await channel.send('Welcome {0.mention}.'.format(member))
    
    @commands.command()
    async def welcome(self, ctx, member):
        channel = self.bot.get_channel(test_channel_id)
        if channel is not None:
            await channel.send('Welcome {0}.'.format(member))
