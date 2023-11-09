from abc import ABC,  abstractmethod
import asyncio
import aiofiles
import json
import copy
import discord.channel as dc_channel
from pkg.manga_pkg import *
import datetime
'''
定義一個聊天室為一個channel
'''
class fundamental_state(ABC):
    def __init__(self,path):
        with open(path , 'r', encoding='utf-8') as jsonfile:
            self._state_dict = json.load(jsonfile)
        self._json_path = path

    async def add_channel(self,channel:dc_channel,label_name = 'Null' ):
        self._state_dict[str(channel.id)] = copy.deepcopy( self._state_dict['demo'] )
        self._state_dict[str(channel.id)]['label_name'] = label_name
    
    @abstractmethod
    def update_log_path(self):
        self._path_log_book = ''

    @abstractmethod
    async def add_item(self):
        pass
    async def get_channels_dict(self):
        ans = {}
        ids = self._state_dict.keys()
        for id in ids:
            ans[id] = self._state_dict[id]['label_name']
        return ans # {'1223xxx':'say'}
    async def save_json(self):
        with open(self._json_path , 'w', encoding='utf-8')as jsonfile:
            self._state_dict = json.dump(self._state_dict,jsonfile)
        await self.update_json()
    async def update_json(self):
        with open(self._json_path , 'r', encoding='utf-8') as jsonfile:
            self._state_dict = json.load(jsonfile)
    async def output_logbook(self, typee:str ,text = 'none'):
        timing = datetime.datetime.now()  
        timing_format = timing.strftime("%Y_%m_%d@%H_%M_%S@{}@".format(typee))
        with open( self._path_log_book,'a+',encoding='utf-8') as output:
            output.write( timing_format)
            output.write( text + '\n' )
        pass
    async def get_channelinfo_dict(self,channel_id:str):
        return self._state_dict[channel_id]
class manga_state(fundamental_state):
    def __init__(self, path):
        fundamental_state.__init__(self,path)

        self.update_log_path()
    async def add_item(self,channel:dc_channel, web_list:list):
        channel_id = str( channel.id )
        channel_infos=await self.get_channels_dict()
        if( channel_id  not in channel_infos.keys() ):
            await self.add_channel( channel_id ,channel.name)
        for web in web_list:
            self._state_dict[channel_id]['manga'][web] = {}
            solu = check_manga_state(web,'_')
            self._state_dict[channel_id]['manga'][web]['title']=solu._title
            self._state_dict[channel_id]['manga'][web]['dep'] = solu._words[1]

    async def update_manga_info(self,channel_id:str, updated_manga:manga_updated):
        self._state_dict[channel_id]['manga'][updated_manga._web]['dep'] = updated_manga._words[1]
        self._state_dict[channel_id]['manga'][updated_manga._web]['title']= updated_manga._title
    def update_log_path(self):
        self._path_log_book = './data/log_book/manga_output.md'
class chicken_state(fundamental_state):
    def __init__(self, path):
        fundamental_state.__init__(self,path)

        self.soup_path = './pkg/chicken_soup.json'
        self.update_soup_json()
        self.update_log_path()
    async def add_item(self,channel:dc_channel, people_list:list):
        channel_id = str( channel.id )
        channel_infos = await self.get_channels_dict()
        if( channel_id  not in channel_infos.keys() ):
            await self.add_channel( channel,channel.name)
        suc = {'suc':[],'non':[] }
        for people in people_list:
            if(people not in self._soup_dict.keys() ):
                suc['non'].append(people)
            else:
                self._state_dict[channel_id]['soup'][people] = self._soup_dict[people]
                suc['suc'].append(people)
        await self.save_json()
        return suc
    def update_soup_json(self):
        with open( self.soup_path , 'r', encoding='utf-8') as jsonfile:
            self._soup_dict = json.load(jsonfile)
    def update_log_path(self):
        self._path_log_book = './data/log_book/chicken_output.md'