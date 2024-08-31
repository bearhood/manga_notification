import discord
from discord.ext import commands
from typing import Optional
from discord import app_commands
# 定義名為 Main 的 Cog
class test1(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 前綴指令
    @commands.command()
    async def update(self, ctx: commands.Context):
        await ctx.send("Hello, world!")

    # 關鍵字觸發
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if message.content == "Hello":
            await message.channel.send("Hello, world!")
            
    @app_commands.command(name='clean', description='clean messages')
    @app_commands.describe(num='number of message')
    @commands.has_permissions(manage_channels=True)
    async def clean(self, interaction: discord.Interaction, num: int):
        try:
            await interaction.channel.purge(limit=num)
            await interaction.response.defer()
            await interaction.followup.send(f'deleted {num} messages')
        except Exception as e:
            print(e)
# Cog 載入 Bot 中
async def setup(bot: commands.Bot):
    await bot.add_cog(test1(bot))
    print( 'succ')