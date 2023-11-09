#導入Discord.py
import discord
from discord.ext import commands,tasks
import discord.message as dc_msg
import asyncio
import random
import datetime

from configparser import ConfigParser
from random import randint
from pkg.manga_pkg import *
from pkg.state_relate.state_model import *
from pkg.state_relate.state_model import chicken_state 
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


def _deal_with_text(update_list = [manga_updated]):
    text = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S 更新程式\n")
    for i in update_list:
        text = text + '[{}]({})'.format(i._title,i._web) +'\n從{}\n到{}\n'.format(i._words[0],i._words[1])
    return text
    pass
#@tasks.loop(minutes=60)
async def threading_manga_state():
    global manga_state_class
    await manga_state_class.update_json()
    await manga_state_class.output_logbook('ini','suc@start_update')
    manga_channel_id_dict = await manga_state_class.get_channels_dict()
    for channel_id in manga_channel_id_dict:
        if(channel_id!='demo' ):
            await manga_state_class.output_logbook('ini','beg@{}'.format(channel_id))
            update_list =  []
            channel_dict = await manga_state_class.get_channelinfo_dict(channel_id)

            for web in channel_dict['manga'].keys():
                try:
                    await asyncio.sleep(randint(3,8))
                    manga_class= check_manga_state(web,
                                                channel_dict['manga'][web]['dep'])
                except:
                    print('error occur in opening')
                    await manga_state_class.output_logbook('mnm','err'+'@{}'.format(web))
                    continue
                await manga_state_class.output_logbook('mnm',manga_class._state+'@{}'.format(web))
                if( manga_class._state =='updated'):
                    update_list.append( manga_class )

            print(len(update_list))
            if(len(update_list)):
                #如果有更新
                text = _deal_with_text(update_list)
                await client.get_channel( int(channel_id) ).send(text)
                await manga_state_class.output_logbook('usr','suc@'+channel_id)
                for updates in update_list:
                    print( updates._web + '::'+updates._words[1])
                    await manga_state_class.update_manga_info(channel_id , updates)

    await manga_state_class.save_json()





@client.event
async def on_ready():
    print('on ready')
    global central_dog

    central_dog = central_dogma(client=client)
    await central_dog.update_channel_state()
    await central_dog.start_tasks()
    #threading_manga_state.start()
    #threading_soup_sending.start()
client.run(config["Discord"]['token'])