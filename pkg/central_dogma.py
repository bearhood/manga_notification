import discord.message as dc_msg
from discord.ext import commands,tasks
from discord import Client
import discord.channel as dc_channel
import datetime
from pkg.state_relate.state_model import manga_state,chicken_state,channel_state
import json
import random
import os
import shutil
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
    async def cmd_add_manga_item(self,message,prefix = '!#ma'):
        manga_web = message.content.removeprefix(prefix).replace(' ','').split('\n')
        await self._manga_state_class.add_item(web_list= manga_web)
        await message.channel.send('成功上傳漫畫網站')
        await self.save_manga()
    async def cmd_add_chicken_item(self,message,prefix = '!#ca'):
        people_list = message.content.removeprefix(prefix).removeprefix(prefix).replace(' ','').split('\n')
        suc = await self._chicken_state_class.add_item(channel=message.channel , people_list=people_list)
        await message.channel.send('成功上傳:' + ','.join(suc['suc']))
        await message.channel.send('以下失敗:' + ','.join(suc['non']))
        await self._chicken_state_class.add_item(self._channel,people_list=people_list)
        await self.save_chicken()
    async def cmd_del_chicken_item(self,message,prefix = '!#cd'):
        people_name = message.content.removeprefix(prefix).replace(' ','').split('\n')
        suc = await self._chicken_state_class.del_item(channel=message.channel , people_list=people_name)
        await message.channel.send('成功刪除:' + ','.join(suc['suc']))
        await message.channel.send('以下失敗:' + ','.join(suc['non']))
        await self.save_chicken()
    async def save_manga(self):
        await self._manga_state_class.save_json()
    async def save_chicken(self):
        await self._chicken_state_class.save_json()

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
            await self._channel.send('修改間距失敗')
            print( message.content.removeprefix(prefix) )
            return 
        self.thread_chicken.change_interval(minutes=minute)
        self._channel_state_class.setting('chicken_interval',minute)
        self._channel_state_class.save_json()
        await self._channel.send('修改間距成功')
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
    '''
    有一天我一定要搞定被鎖的問題!!!!
    @tasks.loop(minutes=60)
    async def update_manga(self):
        pass
    '''
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

    async def get_message(self, message:dc_msg):
        channel_id = str( message.channel.id )
        
        if(message.content.startswith('!#ma')):
            await self._channel_func[channel_id].add_manga_item(message)
        elif(message.content.startswith('!#ms')):
            await self._channel_func[channel_id].cmd_report_manga_state(message)
        elif(message.content.startswith('!#ca')):
            await self._channel_func[channel_id].cmd_add_chicken_item(message)
        elif(message.content.startswith('!#cd')):
            await self._channel_func[channel_id].cmd_del_chicken_item(message)
        elif(message.content.startswith('!#cs')):
            await self._channel_func[channel_id].cmd_report_chicken_soup_state(message)
        elif(message.content.startswith('!#ccitv')):
            await self._channel_func[channel_id].cmd_change_chicken_itv(message)
    
    
    async def start_tasks(self):
        for channel_id in self._channel_ids:
            #await self._channel_func[channel_id].thread_manga.start()
            await self._channel_func[channel_id].thread_chicken.start()