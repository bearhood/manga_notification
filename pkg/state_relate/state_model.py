from abc import ABC,  abstractmethod
import asyncio
import json
class fundamental_state():
    async def __init__(self,path):
        async with open(path , 'r', encoding='utf-8'):
            self._state_dict = json.load(path)
        self.get_channels_dict
    @abstractmethod
    def add_user(self,id,label_name = 'Null' ):
        pass
    @abstractmethod
    def add_item(self):
        pass
    def get_channels_dict(self):
        return self._channel_dict