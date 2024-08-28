import discord.message as dc_msg
import discord
from discord.ext import commands,tasks
from discord import Client
import discord.channel as dc_channel
import datetime
from pkg.state_relate.state_model import manga_state,chicken_state,channel_state
import json
import random
from random import randint
import os
import shutil
import asyncio
from pkg.manga_pkg import *
import threading
import shutil

import ssl
ssl._create_default_https_context = ssl._create_stdlib_context
from pathvalidate import sanitize_filepath
from pytube import YouTube
import pytube
#from pkg.yt_relate.yt_demoer import *
class channel_property():
    def __init__(self,channel:dc_channel):
        self._channel = channel
        self._channel_id = str(channel.id)
        self._dataroot = './data/{}'.format( self._channel_id)

        

       
        self._manga_state_class = manga_state(self._dataroot+'/manga_state.json')
        self._chicken_state_class = chicken_state(self._dataroot+'/chicken_state.json')
        self._channel_state_class = channel_state(self._dataroot+'/channel_state.json')

        chi_itv = float(self._channel_state_class._state_dict["chicken_interval"])
        self.thread_chicken.change_interval(
                            minutes=chi_itv)
        
    async def set_channel_label(self):
        self._channel_state_class.setting('label',self._channel.name)
        await self._channel_state_class.save_json()
    def change_loop_itv(self,func,minutes):
        func.change_interval( minutes=minutes )

    async def save_manga(self):
        await self._manga_state_class.save_json()
    async def save_chicken(self):
        await self._chicken_state_class.save_json()
    async def send_manga_updated(self, update_list:list):
        def deal_with_text(list_:list):
            text_list = []
            text_list.append( datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S 更新程式") )

            text = ''
            for i in list_:
                try:
                    text = text + '[{}]({})'.format(i._title,i._web) +'\n從{}\n到{}\n'.format(i._words[0],i._words[1])
                except:
                    text = text + '[{}]'.format(i._title) +'\n從{}\n到{}\n'.format(i._words[0],i._words[1])
                    continue
                if( len(text  )>1500 ):
                    text_list.append( text )
                    text = ''
            text_list.append(text)
            return text_list
        text_list = deal_with_text(update_list)
        for text in text_list:
            await self._channel.send(text)
        for updates in update_list:
            print( updates._web + '::'+updates._words[1])
            await self._manga_state_class.update_manga_info(self._channel_id , updates)
        await self.save_manga()
    async def update_manga(self):
        await self._manga_state_class.update_json()
    async def update_chicken(self):
        await self._chicken_state_class.update_json()
    async def get_manga_dict(self):
        return self._manga_state_class._state_dict
    async def cmd_change_chicken_itv(self,message,prefix='!#ccitv'):
        try:
            minute = float( message.content.removeprefix(prefix) )
        except:
            await self._channel.send('修改雞湯間距失敗')
            print( message.content.removeprefix(prefix) )
            return 
        self.thread_chicken.change_interval(minutes=minute)
        self._channel_state_class.setting('chicken_interval',minute)
        await self._channel_state_class.save_json()
        await self._channel.send('修改雞湯間距成功')
    async def cmd_report_chicken_soup_state(self,message,prefix = '!#cs'):
        content = {}
        chicken_dict = self._chicken_state_class._state_dict
        text = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S 告知有誰的雞湯\n")
        text = text + '本聊天室有:\n'
        for people in chicken_dict.keys():
            text = text + people +' 有 ' + str(len(chicken_dict[people])) +' 碗 雞湯 \n'
        text = text + '本資料庫有:\n'
        with open('pkg/chicken_soup.json', 'r', encoding='utf-8') as jsonfile:
            soup_dict =  json.load(jsonfile)
        
        for people in soup_dict:
            text = text + people +' 有 ' + str(len(soup_dict[people])) +' 碗 雞湯 \n'
        await message.channel.send(text)
    async def cmd_report_manga_state(self,message,prefix='!#ms'):
        content = {}
        manga_dict = await self.get_manga_dict()
        for web in manga_dict.keys():
            content[web] = manga_dict[web]  
        text = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S 羅列漫畫\n")
        for web in content.keys():
            if(web =='demo_web'):
                continue
            i = content[web]
            text = text + '[{}]({})\n'.format(i['title'],web) 
        await message.channel.send(text)
    async def cmd_del_chicken_item(self,message,prefix = '!#cd'):
        people_name = message.content.removeprefix(prefix).replace(' ','').split('\n')
        suc = await self._chicken_state_class.del_item(channel=message.channel , people_list=people_name)
        await message.channel.send('成功刪除:' + ','.join(suc['suc']))
        await message.channel.send('以下失敗:' + ','.join(suc['non']))
        await self.save_chicken()
    async def cmd_add_chicken_item(self,message,prefix = '!#ca'):
        people_list = message.content.removeprefix(prefix).removeprefix(prefix).replace(' ','').split('\n')
        suc = await self._chicken_state_class.add_item(channel=message.channel , people_list=people_list)
        await message.channel.send('成功上傳:' + ','.join(suc['suc']))
        await message.channel.send('以下失敗:' + ','.join(suc['non']))
        await self._chicken_state_class.add_item(self._channel,people_list=people_list)
        await self.save_chicken()
    async def cmd_add_manga_item(self,message,prefix = '!#ma'):
        manga_web = message.content.removeprefix(prefix).replace(' ','').split('\n')
        await self._manga_state_class.add_item(web_list= manga_web)
        await message.channel.send('成功上傳漫畫網站')
        await self.save_manga()
    async def cmd_add_manga_item(self,message,prefix = '!#ma'):
        manga_web = message.content.removeprefix(prefix).replace(' ','').split('\n')
        await self._manga_state_class.add_item(web_list= manga_web)
        await message.channel.send('成功上傳漫畫網站')
        await self.save_manga()
    async def cmd_send_youtube(self, message , prefix = '!#yt'):
        await message.channel.send('暫時無法使用')
        return
        yt_web = message.content.removeprefix(prefix).replace(' ','').split('\n')[0]
        print(yt_web)
        yt = YouTube(yt_web)
        filename = sanitize_filepath(f'{yt.title}.mp4')

        await message.channel.send('測試下載回傳中...')
        os.makedirs('{}/data/video'.format(self._dataroot), exist_ok=True)
        os.makedirs('{}/data/img'.format(self._dataroot), exist_ok=True)
        print('download...')
        vdo_output_path = f'{self._dataroot}/data/video/{filename}'
        try:
            yt.streams.filter( res = '480p',only_video=True).first().download( filename= vdo_output_path )
        except Exception as e:
            await message.channel.send('有問題喔~ 以下錯誤:')
            await message.channel.send(e)
            return
        print('fine')
        suc = youtube_demoer(vdo_output_path , '{}/data/img'.format(self._dataroot) )
        if(suc!=None):
            files_to_send: list[discord.File] = []
            for i,path in enumerate( suc ):
                if( i % 9 == 0 and i != 0 ):
                    await message.channel.send(files=files_to_send)
                    files_to_send: list[discord.File] = []
                with open(path,'rb') as f:
                    files_to_send.append(discord.File(f) )
            await message.channel.send(files=files_to_send)
        else:
            await message.channel.send('失敗')


        pass
    async def cmd_report_help(self,message,command_dict:dict):
        text = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S help說明\n")
        for prefix in command_dict.keys():
            text = text + command_dict[prefix]['comment'] +'\n'
        await self._channel.send(text)
    @tasks.loop(minutes=12*60)
    async def thread_chicken(self):
        await self._chicken_state_class.update_json()
            
        state_dict = self._chicken_state_class._state_dict
        if( len(state_dict) == 0):
            pass
        else:
            text = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S 發送雞湯\n")
            people_name = random.choice( list( state_dict.keys() ) )
            people_speech = random.choice(  state_dict[people_name] )
            await self._channel.send( text + people_name + ' : ' + people_speech)

class central_dogma():
    def __init__(self,client:Client):
        #load all settings for users
        self._client = client
        self._json_path = './pkg/channel_view.json'

    async def update_channel_state(self):
        self._channel_func = {}
        self._channel_ids = []
        for dir_ in os.listdir('./data'):
            if(dir_=='demo'):
                continue
            elif(os.path.isdir('./data/'+ dir_) ):
                if( self._client.get_channel( int(dir_) )==None ):
                    shutil.rmtree('./data/'+ dir_)
                    continue
                self._channel_ids.append( dir_ )
        for channel_id in self._channel_ids:
            self._channel_func[channel_id] = channel_property(
                                self._client.get_channel( int(channel_id) ))  

    async def exist_channel(self,channel:dc_channel ):
        #要重新建立新的資料夾，建立新的channel_property
        channel_id = str(channel.id)
        if(  channel_id not in self._channel_ids):
            shutil.copytree('./data/demo' ,'./data/{}'.format(str(channel.id)) )
            self._channel_ids.append(str(channel.id) )
            self._channel_func[channel_id] = channel_property(
                                self._client.get_channel( int(channel_id) ))  
            await self._channel_func[channel_id].set_channel_label()
            self._channel_func[channel_id].thread_chicken.start()
            await channel.send('新建立資料夾')
        else:
            return  
    async def cmd_respond(channel_id:str, message):
        pass
    async def get_message(self, message:dc_msg):
        channel_id = str( message.channel.id )
        
        command_dict = {
        '!#ma':{'comment':'''>>!#mahttps\\n+https... : 新增漫畫網站，複數個網址使用換行符分開(Discord 鍵入 shift + enter )''',
                'func':self._channel_func[channel_id].cmd_add_manga_item },
        
        '!#ms':{'comment':'''>>!#ms: 羅列現有的漫畫名稱''',
                'func':self._channel_func[channel_id].cmd_report_manga_state },
        '!#ca':{'comment':'''>>!#ca人名: 添加想要的雞湯來源，該來源必須是已存在本資料庫的人物( 查看 !#cs ) ''',
                'func':self._channel_func[channel_id].cmd_add_chicken_item },
        '!#cd':{'comment':'''>>!#cd人名: 刪除已加入的雞湯來源，該來源必須是已存在本聊天室的人名( 查看 !#cs)''',
                'func':self._channel_func[channel_id].cmd_del_chicken_item},
        '!#cs':{'comment':'''>>!cs: 羅列已存在本聊天室，以及有被收入到本資料庫的雞湯來源''',
                'func':self._channel_func[channel_id].cmd_report_chicken_soup_state},
        '!#ccitv':{'comment':'''>>!#ccitv數字 : 修改放送雞湯的時間週期，數字代表接下來的週期(單位:分鐘)''',
                'func':self._channel_func[channel_id].cmd_change_chicken_itv },
        '!#yt':{'comment':'''>>!#ythttps... : 傳送影片縮圖''',
                'func':self._channel_func[channel_id].cmd_send_youtube },
        }
        if(message.content.startswith('!#help')):   
            await self._channel_func[channel_id].cmd_report_help(message,command_dict=command_dict)
        else:
            for command in command_dict.keys():
                if(message.content.startswith(command)): #完成測試
                    await command_dict[command]['func'](message)
                    break
        
    async def collect_all_manga_state(self):
        # 從所有 channel_property 提取需要運行的漫畫資訊。
        self._manga_class_dict = {}
        for channel_id in self._channel_ids:
            self._manga_class_dict[channel_id] =  await self._channel_func[channel_id].get_manga_dict()



    @tasks.loop(minutes=60)
    async def thread_manga(self):
        print('thread id:', threading.get_ident())
        await self.collect_all_manga_state()
        for channel_id in self._manga_class_dict:
            if(channel_id!='demo' ):
                update_list =  []
                channel_dict = self._manga_class_dict[channel_id]
                for web in channel_dict.keys():
                    try:
                        print(web)
                        await asyncio.sleep(randint(3,8))
                        manga_class= check_manga_updating_state(web,channel_dict[web]['dep'])
                        if( manga_class._state =='updated'):
                            print('updated')
                            update_list.append( manga_class )
                        else:
                            print('no update')
                            continue
                    except:
                        continue
                print(len(update_list))
                if(len(update_list)):
                    await self._channel_func[channel_id].send_manga_updated(update_list)

    async def start_tasks(self):
        tasks_ = []
        self.thread_manga.start()
        for channel_id in self._channel_ids:
            self._channel_func[channel_id].thread_chicken.start() 
            
        
