from discord.ext import commands
import discord
from discord_components import Button
import asyncio
import json


from discord.ext.commands.core import check
class EventHandler(commands.Cog):
    
    title = ''
    description = ''
    start_time = ''
    end_time = ''
    roles_list = ''
    eventCreationProcess=False
    
    def __init__(self, bot):
        self.bot = bot
        
    def reset_states(self):
        self.title = ''
        self.description = ''
        self.start_time = ''
        self.end_time = ''
        self.roles_list = ''
        self.eventCreationProcess=False
    
    @commands.command()
    async def event(self, ctx):
        if(self.eventCreationProcess==False):
            self.reset_states()
            self.eventCreationProcess = True
            channel = self.bot.get_channel(931194015112626177)
            
            #get the events from json file
            with open("bot/cogs/eventEmbeds.json") as json_file:
                embedsData = json.load(json_file)
            embeds ={}
            for (heading,value) in embedsData.items():
                if value[0].get("timeout") is not None:
                    timeoutText = f'\n\n *Timeout: {value[0]["timeout"]}*'
                else:
                    timeoutText = ''
                embeds[f"{heading}"] = discord.Embed(
                    title=value[0]["title"],
                    colour=value[0]["colour"],
                    description=value[0]["description"] + timeoutText,
                    footer=value[0]["footer"]
                ) 
                
            await ctx.channel.send(embed=embeds['titleEmbed'])
            
            try:
                self.title=await self.bot.wait_for(
                    "message", 
                    timeout=60,
                    check = lambda message: message.author==ctx.message.author
                )
                if self.title.content!='':
                    await ctx.channel.send(embed=embeds['discriptionEmbed'])
                    try:
                        self.description=await self.bot.wait_for(
                            "message", 
                            timeout=300,
                            check = lambda message: message.author==ctx.message.author
                        )
                        if self.description.content!='':
                            await ctx.channel.send(embed=embeds['startTimeEmbed'])
                            try:
                                self.start_time=await self.bot.wait_for(
                                    "message", 
                                    timeout=120,
                                    check = lambda message: message.author==ctx.message.author
                                )
                                if self.start_time.content!='':
                                    await ctx.channel.send(embed=embeds['endTimeEmbed'])
                                    try:
                                        self.end_time=await self.bot.wait_for(
                                            "message", 
                                            timeout=120,
                                            check = lambda message: message.author==ctx.message.author
                                        )
                                        if self.end_time.content!='':
                                            await ctx.channel.send(embed=embeds['rolesMentionEmbed'])
                                            try:
                                                self.roles_list=await self.bot.wait_for(
                                                    "message", 
                                                    timeout=120,
                                                    check = lambda message: message.author==ctx.message.author
                                                )
                                                if self.roles_list.content!='':
                                                    await ctx.channel.send(embed=embeds['finalEmbed'])
                                                    generalEmbed = discord.Embed(
                                                        title=f"{self.title.content}",
                                                        colour=1234567, description=f'{self.description.content}',
                                                        footer=f'created by {ctx.channel.name}'
                                                    ).add_field(
                                                        name=f"Start Time:",
                                                        value=f"{self.start_time.content}",
                                                        inline=False
                                                    ).add_field(
                                                        name=f"End Time:",
                                                        value=f"{self.end_time.content}",
                                                        inline=False
                                                    ).add_field(
                                                        name=f"Meeting Link:",
                                                        value=f"https://www.facebook.com/kucc1997",
                                                        inline=False
                                                    ).add_field(
                                                        name=f':white_check_mark: Accepted',
                                                        value=2
                                                    ).add_field(
                                                        name=f':x: Declined',
                                                        value=3
                                                    ).add_field(
                                                        name=f':question: Not Sure',
                                                        value=5
                                                    )
                                                    await channel.send(
                                                        embed=generalEmbed,
                                                        components=[
                                                            [Button(style="3", emoji = "✔️", custom_id = "tickButton"),
                                                            Button(style="4", emoji = "✖️", custom_id = "crossButton"),
                                                            Button(style="1", emoji = "❔", custom_id = "whatButton")
                                                            ]
                                                        ]
                                                    )
                                                    self.eventCreationProcess = False
                                                    
                                            except asyncio.TimeoutError:
                                                await ctx.channel.send("Cancelled due to timeout.")
                                                self.eventCreationProcess = False
                                    except asyncio.TimeoutError:
                                        await ctx.channel.send("Cancelled due to timeout.")
                                        self.eventCreationProcess = False
                            except asyncio.TimeoutError:
                                await ctx.channel.send("Cancelled due to timeout.")
                                self.eventCreationProcess = False
                    except asyncio.TimeoutError:
                        await ctx.channel.send("Cancelled due to timeout.")
                        self.eventCreationProcess = False
            except asyncio.TimeoutError:
                await ctx.channel.send("Cancelled due to timeout.")
                self.eventCreationProcess = False
        else:
            await ctx.channel.send("An event creation already in progress. Try again later.")
        
        
        
def setup(bot):
    bot.add_cog(EventHandler(bot))