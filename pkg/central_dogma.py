import discord.message as dc_msg
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
from pkg.thread_content.manga_pkg import *
import threading
class channel_property():
    def __init__(self,channel:dc_channel):
        self._channel = channel
        self._channel_id = str(channel.id)
        self._dataroot = './data/{}'.format( self._channel_id)

        

       
        self._manga_state_class = manga_state(self._dataroot+'/manga_state.json')
        self._chicken_state_class = chicken_state(self._dataroot+'/chicken_state.json')
        self._channel_state_class = channel_state(self._dataroot+'/channel_state.json')

        
        
    async def set_channel_label(self):
        await self._channel_state_class.setting('label',self._channel.name)
        await self._channel_state_class.save_json()
    def change_loop_itv(self,func,minutes):
        func.change_interval( minutes=minutes )

    

    async def save_manga(self):
        await self._manga_state_class.save_json()
    async def save_chicken(self):
        await self._chicken_state_class.save_json()

    async def send_manga_updated(self, update_list:list[manga_updated]):
        def deal_with_text(list_:list[manga_updated]) -> str:
                text = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S 更新程式\n")
                for i in list_:
                    text = text + '[{}]({})'.format(i._title,i._web) +'\n從{}\n到{}\n'.format(i._words[0],i._words[1])
                return text
        text = deal_with_text(update_list)
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
        await self._channel_state_class.setting('chicken_interval',minute)
        await self._channel_state_class.save_json()
        await self._channel.send('修改雞湯間距成功')
    async def cmd_report_chicken_soup_state(self,message:dc_msg,prefix = '!#cs'):
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
    async def cmd_report_manga_state(self,message:dc_msg,prefix='!#ms'):
        def shorten_title(text:str):
            fail_text = '[]()'
            for j in fail_text:
                text = text.replace(j,'')
            if( len(text  )>7 ):
                return text[0:7]+'...'
            else:
                return text
        content = {}
        manga_dict = await self.get_manga_dict()
        for web in manga_dict.keys():
            content[web] = manga_dict[web]  
        text = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S 羅列漫畫\n")
        for web in content.keys():
            if(web =='demo_web'):
                continue
            i = content[web]
            text = text + '[{}]({})\n'.format( shorten_title(i['title']) ,web) 
        await message.channel.send(text)
    async def cmd_del_chicken_item(self,message:dc_msg,prefix = '!#cd'):
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
    async def cmd_report_help(self,message:dc_msg,command_dict:dict):
        text = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S help說明\n")
        for prefix in command_dict.keys():
            text = text + command_dict[prefix]['comment'] +'\n'
        await self._channel.send(text)
    async def cmd_mute_channel(self,message:dc_msg,prefix='!#mute'):
        await self._channel_state_class.setting('mute',value = 1)
        await self._channel.send('本頻道已安靜')
    async def cmd_unmute_channel(self,message:dc_msg,prefix='!#unmute'):
        await self._channel_state_class.setting('mute',value = 0)
        await self._channel.send('本頻道恢復吵鬧')
    
    
    def dec_check_mute(func):
        async def wrap(self):
            if( self._channel_state_class.value_query('mute') ):
                print( 'mute')
                return await asyncio.sleep(0.01)
            else:
                return await func(self)
        return wrap
    async def thread_soup_counter(self):
        
        minutes= self._channel_state_class.value_query('chicken_interval')
        await asyncio.sleep( minutes * 60)

    @tasks.loop(seconds=0.01)
    @dec_check_mute
    async def thread_chicken(self):
        print('thread id:', threading.get_ident())
        await self._chicken_state_class.update_json()
        
        state_dict = self._chicken_state_class._state_dict
        if( len(state_dict) == 0):
            pass
        else:
            text = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S 發送雞湯\n")
            people_name = random.choice( list( state_dict.keys() ) )
            people_speech = random.choice(  state_dict[people_name] )
            await self._channel.send( text + people_name + ' : ' + people_speech)
        await self.thread_soup_counter()
    
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
        '!#mute':{'comment':'''>>!#mute : 接下來的時光將會無視漫畫及雞湯提醒(忽略提醒並非不會更新)''',
                'func':self._channel_func[channel_id].cmd_mute_channel },
        '!#unmute':{'comment':'''>>!#unmute: 恢復提醒功能''',
                'func':self._channel_func[channel_id].cmd_unmute_channel },
        
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



    @tasks.loop(seconds=60)
    async def thread_manga(self):

        await self.collect_all_manga_state()
        for channel_id in self._manga_class_dict:
            if(channel_id!='demo' ):
                update_list =  []
                channel_dict = self._manga_class_dict[channel_id]
                for web in channel_dict.keys():
                    try:
                        await asyncio.sleep(randint(3,8))
                        manga_class= check_manga_updating_state(web,channel_dict[web]['dep'])
                        if( manga_class._state =='updated'):
                            update_list.append( manga_class )
                        else:
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
            
        
