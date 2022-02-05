from discord.ext import commands
import discord
from PIL import Image, ImageFont, ImageDraw, ImageChops
from io import BytesIO


welcome_channel_id = 932974032519823360

def circle(avatar, size=(400, 400)):
    avatar = avatar.resize(size, Image.ANTIALIAS).convert("RGBA")
    mask = Image.new('L', avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0,0) + avatar.size, fill=255)
    mask = ImageChops.darker(mask, avatar.split()[-1])
    avatar.putalpha(mask)
    return avatar

class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(welcome_channel_id)
        if channel is not None:
            embed = discord.Embed(
                title=f"Welcome to the server  :partying_face:",
                colour=1234567, description=f"{member.mention},\n\nPlease review <#932974078535565352> to gain access to the rest of the server.\n"
            ).add_field(
                name=f"Members Count:",
                value=f"{member.guild.member_count}",
                inline=False
            ).add_field(
                name=f"Website:",
                value=f"http://kucc.ku.edu.np"
            ).add_field(
                name=f"Facebook:",
                value=f"https://www.facebook.com/kucc1997"
            )

            # fetches backround
            background = Image.open("assets/background.jpg").convert("RGBA")

            # fetch user image
            userAvatar = member.avatar_url_as(size=256)
            userPic = Image.open(BytesIO(await userAvatar.read())).convert("RGBA")

            #crop circular user profile image and add border
            avatar = circle(userPic, (400,400))

            # paste userPic in background
            background.paste(avatar, (130, 150), avatar)

            #for long user names
            name = f"{member.name[:20]}.." if len(member.name) > 20 else member.name

            # write text
            write = ImageDraw.Draw(background)
            msg = f"Welcome to KUCC's\nOfficial Discord Server,\n"
            fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 80)
            write.multiline_text((650, 220), msg, font=fnt, fill=(
                0, 0, 0), stroke_width=3, stroke_fill="black")
            write.text((650, 390), name, font=fnt, fill=(
                0, 0, 0), stroke_width=3, stroke_fill="purple")
            background.convert("RGB").save("assets/welcomeImage.jpg")
            file = discord.File("assets/welcomeImage.jpg", filename="welcomeImg.jpg")

            #embeds
            embed.set_image(url="attachment://welcomeImg.jpg")
            embed.set_author(
                name="KUCC", icon_url="https://i.imgur.com/nnpCujW.png")
            await channel.send(embed=embed, file=file)

def setup(bot):
    bot.add_cog(Welcomer(bot))
