from abc import ABC,  abstractmethod
import asyncio
import json
import copy
import discord.channel as dc_channel
from pkg.manga_pkg import *
'''
定義一個聊天室為一個channel
'''
class fundamental_state(ABC):
    async def __init__(self,path):
        async with open(path , 'r', encoding='utf-8') as jsonfile:
            self._state_dict = json.load(jsonfile)
        self._json_path = path

    async def add_channel(self,channel:dc_channel,label_name = 'Null' ):
        self._state_dict[str(channel.id)] = copy.deepcopy( self._state_dict['demo'] )
        self._state_dict['label_name'] = label_name

    @abstractmethod
    async def add_item(self):
        pass
    async def get_channels_dct(self):
        ans = {}
        ids = self._state_dict.keys()
        async for id in ids:
            ans[id] = self._state_dict[id]['label_name']
        return ans # {'1223xxx':'say'}
    async def save_json(self):
        async with open(self._json_path , 'w', encoding='utf-8')as jsonfile:
            self._state_dict = json.dump(self._state_dict,jsonfile)


class manga_state(fundamental_state):
    async def __init__(self, path):
        await fundamental_state.__init__(self,path)

    async def add_item(self,channel:dc_channel, web_list:list):
        channel_id = str( channel.id )
        if( channel_id  not in self.get_channels_dict().keys() ):
            await self.add_channel( channel_id ,channel.name)
        for web in web_list:
            self._state_dict[channel_id]['manga'][web] = {}
            solu = check_manga_state(web,'_')
            self._state_dict[channel_id]['manga'][web]['title']=solu._title
            self._state_dict[channel_id]['manga'][web]['dep'] = solu._words[1]