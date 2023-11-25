from abc import ABC , abstractclassmethod
from typing import NoReturn

class email_content(ABC):
    def __init__(self):
        self._html_content = ''
        pass

    @abstractclassmethod
    def add_html_content(self):
        pass


    def get_html_content(self):
        return self._html_content

class updating_content(email_content):
    def __init__(self):
        email_content.__init__(self)
        self._count = 0
    def add_html_content(self,text:str) -> NoReturn:
        if( self._html_content ==''):
            self._count = 0
            self._html_content = '以下事情交代:<br>'
        self._html_content = self._html_content + f'{self._count+1}:{text}' + '<br>'
        self._count = self._count +1
        print('suc')
    def get_html_content(self):
        self._count = 0
        text = self._html_content
        self._html_content = ''
        return text