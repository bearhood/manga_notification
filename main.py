#導入Discord.py
import discord
from configparser import ConfigParser
from pkg.manga_pkg import *
from pkg.state_relate.state_model import *
from pkg.central_dogma import central_dogma

intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents , command_prefix='$')
config = ConfigParser()
config.read("./pkg/config.ini")


#調用event函式庫
@client.event
#當機器人完成啟動時
async def on_ready():
    print('目前登入身份：',client.user)

@client.event
#當有訊息時
async def on_message(message):
    #排除自己的訊息，避免陷入無限循環
    ## channel id 是根據所在的文字頻道判斷
    print( message.channel.id )
    if message.author == client.user:
        return
    #如果以「說」開頭
    print(message.content)
    global central_dog
    await central_dog.exist_channel(message.channel)
    if message.content.startswith('!#'):
        await central_dog.get_message(message)


@client.event
async def on_ready():
    print('on ready')
    global central_dog

    central_dog = central_dogma(client=client)
    await central_dog.update_channel_state()
    await central_dog.start_tasks()

client.run(config["Discord"]['token'])