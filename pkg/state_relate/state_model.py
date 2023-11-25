from abc import ABC,  abstractmethod
import asyncio
import aiofiles
import json
import copy
import discord.channel as dc_channel
from pkg.thread_content.manga_pkg import *
import datetime
'''
定義一個聊天室為一個channel
'''
class fundamental_state(ABC):
    def __init__(self,path):
        with open(path , 'r', encoding='utf-8') as jsonfile:
            self._state_dict = json.load(jsonfile)
        self._json_path = path



    @abstractmethod
    async def add_item(self):
        pass

    async def save_json(self):
        with open(self._json_path , 'w', encoding='utf-8')as jsonfile:
            self._state_dict = json.dump(self._state_dict,jsonfile)
        await self.update_json()
    async def update_json(self):
        with open(self._json_path , 'r', encoding='utf-8') as jsonfile:
            self._state_dict = json.load(jsonfile)
    async def get_info_dict(self,channel_id:str):
        return self._state_dict
class manga_state(fundamental_state):
    def __init__(self, path):
        fundamental_state.__init__(self,path)

    async def add_item(self, web_list:list):
        for web in web_list:
            self._state_dict[web] = {}
            solu = check_manga_updating_state(web,'_')
            self._state_dict[web]['title']=solu._title
            self._state_dict[web]['dep'] = solu._words[1]
            await self.save_json()
    async def update_manga_info(self,channel_id:str, updated_manga:manga_updated):
        self._state_dict[updated_manga._web]['dep'] = updated_manga._words[1]
        self._state_dict[updated_manga._web]['title']= updated_manga._title

class channel_state(fundamental_state):
    def __init__(self, path):
        fundamental_state.__init__(self,path)
    async def add_item(self, web_list:list):
        pass
    async def setting(self,name:str , value:str):
        if( name in self._state_dict.keys() ):
            self._state_dict[name] = value
            await self.save_json()

        else:
            raise NameError
    def value_query(self,key):
        return self._state_dict[key]

class chicken_state(fundamental_state):
    def __init__(self, path):
        fundamental_state.__init__(self,path)

        self.chicken_path = path
    async def add_item(self,channel:dc_channel, people_list:list):
        suc = {'suc':[],'non':[] }
        with open('pkg/chicken_soup.json', 'r', encoding='utf-8') as jsonfile:
            _soup_dict =  json.load(jsonfile)
        
        for people in people_list:
            if(people not in _soup_dict.keys() ):
                suc['non'].append(people)
            else:
                self._state_dict[people] = _soup_dict[people]
                suc['suc'].append(people)
        await self.save_json()
        return suc
    async def del_item(self,channel:dc_channel, people_list:list):
        channel_id = str( channel.id )
        suc = {'suc':[],'non':[] }
        with open('./pkg/chicken_soup.json', 'r', encoding='utf-8') as jsonfile:
            _soup_dict =  json.load(jsonfile)
        for people in people_list:
            if(people in _soup_dict.keys() ):
                suc['suc'].append(people)
                del self._state_dict[people]
            else:
                suc['non'].append(people)
        await self.save_json()
        return suc

