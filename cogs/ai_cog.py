from discord.ext import commands, tasks
import functools


class ai(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        

    async def start_service(self, ctx: commands.Context):
        await ctx.send('start manga updating')
    # 前綴指令

async def setup(bot: commands.Bot):
    await bot.add_cog(ai(bot))