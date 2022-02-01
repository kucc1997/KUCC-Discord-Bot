from discord.ext import commands
from discord import Embed, utils
from discord_components import DiscordComponents, Button, ButtonStyle
import asyncio
import random

class TicketHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="delete")
    async def delete(self, ctx):
        category = utils.get(ctx.guild.categories, name = "tickets")
        # category.children.forEach(channel => channel.delete())
        for channel in category.channels:
            await channel.delete()
        return

    @commands.Cog.listener('on_button_click')
    async def button_clicked(self, payload):
        print("clicked")

    @commands.command(name="naice")
    async def naice(self, ctx):

        guild = ctx.guild

        # Creating an embed, buttons for the message.
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
                Button(style=ButtonStyle.grey, label="Language Queries", custom_id="language_query"),
                Button(style=ButtonStyle.grey, label="Industry Trends", custom_id="industry_trends"),
                Button(style=ButtonStyle.grey, label="General Guidance", custom_id="general_guidance"),
                Button(style=ButtonStyle.grey, label="Report Incident", custom_id="report_incident")
                ]]
            )

        category = utils.get(guild.categories, name = "tickets")
        #Checking for any of the defined button clicks
        # while True:
        tasks = [
            asyncio.create_task(self.bot.wait_for("button_click", check = lambda i: i.custom_id == "language_query"), name="lan_query"),
            asyncio.create_task(self.bot.wait_for("button_click", check = lambda i: i.custom_id == "industry_trends"), name = "ind_query"),
            asyncio.create_task(self.bot.wait_for("button_click", check = lambda i: i.custom_id == "general_guidance"), name = "gen_query"),
            asyncio.create_task(self.bot.wait_for("button_click", check = lambda i: i.custom_id == "report_incident"), name = "rep_query")
        ]

        done, pending = await asyncio.wait(tasks , return_when=asyncio.FIRST_COMPLETED)
        finished : asyncio.Task = list(done)[0]

        for task in pending:
            try:
                task.cancel()
            except asyncio.CancelledError:
                pass

        interaction, ticket_type = finished.result() , finished.get_name()

        channel_exists = True
        if ticket_type == "lan_query":
            channel_name = 'language-' + str(random.randint(300,9000))
        elif ticket_type == "ind_query":
            channel_name = 'industry-' + str(random.randint(300,9000))
        elif ticket_type == "gen_query":
            channel_name = 'general-' + str(random.randint(300,9000))
        elif ticket_type == "rep_query":
            channel_name = 'report-' + str(random.randint(300,9000))

        channel_exists = utils.get(guild.channels, name=channel_name)

        if not channel_exists:
            channel = await guild.create_text_channel(channel_name, category = category)

        await interaction.respond(content=f"<#{channel.id}> Ticket created")

        info = '''Someone from the team will be with you sortly. Please add the details about your question or request in this channel. This will help us understand it better and solve it faster.

                To close🔐 the ticket press the button below.

        '''
        embedTic = Embed(description=info, color=0x384077)
        embedVar.set_footer(text="KUCC - Kathmandu University Computer Club", icon_url="http://kucc.ku.edu.np/wp-content/uploads/2020/11/kucc-2048x1666.png")

        await channel.send(
            embed=embedTic,
            components=[[
                Button(style=ButtonStyle.red, label="🔐Close Ticket", custom_id="close_ticket")
                ]]
            )

        close_ticket = await self.bot.wait_for("button_click", check = lambda i: i.custom_id == "close_ticket")

        await close_ticket.channel.delete()

        await interaction.delete_original_message()

        # commands.Bot.add_listener(function, 'on_message')
        #
        # interaction = await self.bot.wait_for("button_click", check = lambda i: i.custom_id == "language_query")
        # #     # pass
        # #     print("Language quesry")
        #
        # # done, pending = await asyncio.wait([
        # #             self.bot.wait_for("button_click", check = lambda i: i.custom_id == "language_query"),
        # #             self.bot.wait_for("button_click", check = lambda i: i.custom_id == "industry_trends")
        # #             ], return_when=asyncio.FIRST_COMPLETED)
        # # # await done.respond(content="Ticket created ")
        # # print(interaction)



def setup(bot):
    bot.add_cog(TicketHandler(bot))
