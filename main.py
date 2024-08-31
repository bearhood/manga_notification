#導入Discord.py
import discord
import os
from discord.ext import commands

from configparser import ConfigParser
from discord import app_commands
from typing import Optional
config = ConfigParser()
config.read("./config.ini")


# intents是要求機器人的權限
intents = discord.Intents.all()
# command_prefix是前綴符號，可以自由選擇($, #, &...)
bot = commands.Bot(command_prefix = "$", intents = intents)

@bot.event
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")
    

@bot.command()
async def load(ctx, extension):
    await bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Loaded {extension} done.")

# 卸載指令檔案
@bot.command()
async def unload(ctx, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"UnLoaded {extension} done.")

# 重新載入程式檔案
@bot.command()
async def reload(ctx, extension):
    await bot.reload_extension(f"cogs.{extension}")
    await ctx.send(f"ReLoaded {extension} done.")

# 一開始bot開機需載入全部程式檔案
@bot.command()
async def load_all(ctx):
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            await ctx.send(f"Loaded {filename[:-3]} done.")
#Sync slash command: I'll use in the future
@bot.command() 
async def sync(ctx):
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s).")
#Sync slash command: list if there are cogs in the folder
@bot.command() 
async def list_pkg(ctx):
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await ctx.send(f"{filename[:-3]}")



'''@app_commands.command(name = "hello", description = "Hello, world!")
async def hello(interaction: discord.Interaction):
    # 回覆使用者的訊息
    await interaction.response.send_message("Hello, world!")'''
bot.run(config["Discord"]['token'])