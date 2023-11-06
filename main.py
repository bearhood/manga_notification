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
intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)

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
        tmp = message.content.split(" ",2)
        channel_id = str( message.channel.id )
        if(message.content.startswith('!#ma')):
            manga_web = message.content[4:].replace(' ','').split('\n')
            add_manga_state_target(message , manga_web)
            await message.channel.send('成功上傳漫畫網站')
        elif(message.content.startswith('!#ms')):
            content = {}
            for web in manga_state[channel_id]['manga'].keys():
                content[web] = manga_state[channel_id]['manga'][web]  
            text = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S 羅列漫畫\n")
            for web in content.keys():
                if(web =='demo_web'):
                    continue
                i = content[web]
                text = text + '[{}]({})\n'.format(i['title'],web) 
            await message.channel.send(text)
def add_manga_state_target(message = dc_msg,web_list=[]):
    channel = message.channel
    channel_id = str( channel.id )
    if( channel.id not in manga_state.keys() ):
        create_manga_state(channel)
    for web in web_list:
        manga_state[channel_id]['manga'][web] = {}
        solu = check_manga_state(web,'_')
        manga_state[channel_id]['manga'][web]['title']=solu._title
        manga_state[channel_id]['manga'][web]['dep'] = solu._words[1]
    save_manga_state()
    pass
def create_manga_state(channel = dc_channel):
    channel_id = str( channel.id )
    manga_state[channel_id] = copy.deepcopy( manga_state['demo'] )
    del manga_state[channel_id]['manga']['demo_web']
    manga_state[channel_id]["label_name"] = channel.name
path_log_book = './data/log_book/manga_output.md'
def output_to_log_book(typee='mna',text='none'):
    #typee = 'mna'/'usr'
    timing = datetime.datetime.now()  
    timing_format = timing.strftime("%Y_%m_%d@%H_%M_%S@{}@".format(typee))
    with open( path_log_book,'a+',encoding='utf-8') as output:
        output.write( timing_format)
        output.write( text + '\n' )
    pass
def save_manga_state():
    global manga_state
    print('saving manga_state')
    with open('./pkg/manga_state.json','w',) as manga_state_file:
        json.dump(manga_state, manga_state_file)



def _deal_with_text(update_list = [manga_updated]):
    text = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S 更新程式\n")
    for i in update_list:
        text = text + '[{}]({})'.format(i._title,i._web) +'\n從{}\n到{}\n'.format(i._words[0],i._words[1])
    return text
    pass
@tasks.loop(minutes=60)
async def threading_manga_state():
    global manga_state
    with  open('./pkg/manga_state.json','r',encoding="utf-8") as manga_state_file:
        manga_state = json.load( manga_state_file )
    output_to_log_book('ini','suc@start_update')

    for user_id in manga_state.keys():
        if(user_id=='demo' ):
            continue
        output_to_log_book('ini','beg@{}'.format(user_id))
        update_list =  []
        
        for web in manga_state[user_id]['manga'].keys():
            
            try:
                await asyncio.sleep(randint(3,8))
                current_value = manga_state[user_id]['manga'][web]['dep']
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
            await client.get_channel( int(user_id) ).send(text)
            output_to_log_book('usr','suc@'+user_id)
            for updates in update_list:
                print( updates._web + '::'+updates._words[1])
                manga_state[user_id]['manga'][updates._web]['dep'] = updates._words[1]
                manga_state[user_id]['manga'][updates._web]['title'] = updates._title
            save_manga_state()
        else:
            continue


@tasks.loop(minutes=60)
async def threading_soup_sending():
    async with  open('./pkg/chichen_state,json','r',encoding="utf-8") as chicken_state_file:
        chicken_state = json.load( chicken_state_file )

    async for id in manga_state.keys()



@client.event
async def on_ready():
    print('on ready')
    threading_manga_state.start()
client.run("")