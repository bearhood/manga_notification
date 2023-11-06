#導入Discord.py
import discord
from discord.ext import commands,tasks
import discord.message as dc_msg
import discord.channel as dc_channel
import asyncio
import random
import datetime
import json
import copy
from random import randint
from pkg.manga_pkg import *
from pkg.state_relate.state_model import * 

intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents , command_prefix='$')


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
    if message.content.startswith('!#'):
        global manga_state_class
        global chicken_state_class
        tmp = message.content.split(" ",2)
        channel_id = str( message.channel.id )
        if(message.content.startswith('!#ma')):
            manga_web = message.content[4:].replace(' ','').split('\n')
            await manga_state_class.add_item(channel=message.channel , web_list=manga_web)
            await message.channel.send('成功上傳漫畫網站')
        elif(message.content.startswith('!#ms')):
            content = {}
            manga_dict = await manga_state_class.get_manga_dict(channel_id)
            for web in manga_dict['manga'].keys():
                content[web] = manga_dict['manga'][web]  
            text = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S 羅列漫畫\n")
            for web in content.keys():
                if(web =='demo_web'):
                    continue
                i = content[web]
                text = text + '[{}]({})\n'.format(i['title'],web) 
            await message.channel.send(text)
        elif(message.content.startswith('!#ca')):
            people_name = message.content[4:].replace(' ','').split('\n')
            suc = await chicken_state_class.add_item(channel=message.channel , people_list=people_name)
            await message.channel.send('成功上傳:' + ','.join(suc['suc']))
            await message.channel.send('以下失敗:' + ','.join(suc['non']))
path_log_book = './data/log_book/manga_output.md'
def output_to_log_book(typee='mna',text='none'):
    #typee = 'mna'/'usr'
    timing = datetime.datetime.now()  
    timing_format = timing.strftime("%Y_%m_%d@%H_%M_%S@{}@".format(typee))
    with open( path_log_book,'a+',encoding='utf-8') as output:
        output.write( timing_format)
        output.write( text + '\n' )
    pass



def _deal_with_text(update_list = [manga_updated]):
    text = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S 更新程式\n")
    for i in update_list:
        text = text + '[{}]({})'.format(i._title,i._web) +'\n從{}\n到{}\n'.format(i._words[0],i._words[1])
    return text
    pass
@tasks.loop(minutes=60)
async def threading_manga_state():
    global manga_state_class
    await manga_state_class.update_json()

    output_to_log_book('ini','suc@start_update')
    manga_channel_id_dict = await manga_state_class.get_channels_dict()
    for channel_id in manga_channel_id_dict:
        if(channel_id=='demo' ):
            continue
        
        output_to_log_book('ini','beg@{}'.format(channel_id))
        update_list =  []
        channel_dict = await manga_state_class.get_manga_dict(channel_id)

        for web in channel_dict['manga'].keys():
            try:
                await asyncio.sleep(randint(3,8))
                current_value = channel_dict['manga'][web]['dep']
                manga_class= check_manga_state(web,current_value)
            except:
                print('error occur in opening')
                output_to_log_book('mnm','err'+'@{}'.format(web))
                continue
            output_to_log_book('mnm',manga_class._state+'@{}'.format(web))
            if( manga_class._state =='updated'):
                update_list.append( manga_class )
            else:
                pass
        print(len(update_list))
        if(len(update_list) != 0):
            #如果有更新
            text = _deal_with_text(update_list)
            await client.get_channel( int(channel_id) ).send(text)
            output_to_log_book('usr','suc@'+channel_id)
            for updates in update_list:
                print( updates._web + '::'+updates._words[1])
                await manga_state_class.update_manga_info(channel_id , updates)
            
        else:
            continue
    await manga_state_class.save_json()



@tasks.loop(minutes=60)
async def threading_soup_sending():
    global chicken_state_class
    await chicken_state_class.update_json()




@client.event
async def on_ready():
    print('on ready')
    global chicken_state_class
    global manga_state_class

    chicken_state_class = chicken_state(path = 'pkg/chicken_state.json') 
    manga_state_class = manga_state(path = 'pkg/manga_state.json') 
    
    threading_manga_state.start()
client.run("MTE3MDIyMjExODQ1NDE4NjAzNA.G6meI7.4lyEH_pphT_tKGRBYdopxfqwqOhE8i2Ka7OdVo")