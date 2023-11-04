from pkg.api_keys import *
from abc import ABC,abstractmethod
import shutil
from __main__ import *


class user_pkg(ABC):
    def __init__(self,event):
        self._group_id = ''
        self._user_id = ''
        self._groupname = ''
        self._username = ''
        self._event = event
        self._id = ''
        self._type = ''
        self._labelname = ''
        self._storagepath = './data/' + self._id
        self._mdpath = self._storagepath + '/hist.md'
        
    def check_if_folder_exist(self):
        if( os.path.isdir('./data/'+self._id) ):
            return 1
        else:
            return 0
    def delete_id_path(self):
        if( self.check_if_folder_exist() ):    
            shutil.rmtree('./data/' + self._id )
    
class user_pkg_user(user_pkg):
    def __init__(self,event):
        self._user_id = event.source.user_id
        self._username = line_bot_api.get_profile( self._user_id ).display_name
        self._id = self._user_id
        self._type = 'user'
        self._groupname = ''
        self._labelname = self._username
        self._event = event
        self._storagepath = './data/' + self._id
        self._mdpath = self._storagepath + '/hist.md'
        pass
class user_pkg_group(user_pkg):
    def __init__(self,event):
        self._group_id = event.source.sender_id
        self._user_id = event.source.user_id
        self._groupname = line_bot_api.get_group_summary(self._group_id).group_name
        try:
            self._username = line_bot_api.get_profile( self._user_id ).display_name
        except:
            self._username = '其他人'
        self._id = self._group_id
        self._type = 'group'
        self._labelname = self._groupname
        self._event = event
        self._storagepath = './data/' + self._id
        self._mdpath = self._storagepath + '/hist.md'
