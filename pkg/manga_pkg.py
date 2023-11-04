from abc import ABC , abstractmethod,abstractproperty
from urllib.error import URLError as urlerror 
from urllib.parse import urlparse

import urllib.request
from bs4 import BeautifulSoup

url_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'}
class manga_state(ABC):
    def __init__(self,web,title,previous_state = "Null",
                          current_state = 'None'):

        pass
    def state_(self):
        return self._state
    def dict_(self):
        return self._dict
    def words_(self):
        return self._words
    def title(self):
        return self._title
class manga_failed(manga_state):
    def __init__(self,web,title,
                          previous_state = "Null",
                          current_state = 'None'):
        self._state = 'failed'
        self._web = web
        self._words = [previous_state , current_state]
        self._title = 'Null'
    pass
class manga_updated(manga_state):
    def __init__(self,web,title,
                          previous_state = "Null",
                          current_state = 'None'):
        self._state = 'updated'
        self._web = web
        self._words = [previous_state , current_state]
        self._title = title
    pass
class manga_nonupdated(manga_state):
    def __init__(self,web,title,
                          previous_state = "Null",
                          current_state = 'Null'):
        self._state = 'nonupdated'
        self._web = web
        self._words = [previous_state , current_state]
        self._title = title
    pass
class manga_unable(manga_state):
    def __init__(self,web,title,
                          previous_state = "Null",
                          current_state = 'Null'):
        self._state = 'nonupdated'
        self._web = web
        self._words = [previous_state , current_state]
        self._title = 'Null'
    pass

class web_scracher():
    def __init__(self , web,preval = 'Null'):
        self._web = web
        self._preval = preval
        self._title = 'Null'
        self._current_value = 'Null'
        pass
    def connect_process(self):
        req = urllib.request.Request( self._web,
                                      headers = url_headers )
        html_page = urllib.request.urlopen( req ,timeout = 5)
        self._soup = BeautifulSoup(html_page,'html.parser')
    def check_if_updated(self):
        if( self._current_value != self._preval):
            return 1
        else:
            return 0
    
    def get_web(self):
        return self._web 
    def get_title(self):
        return self._title
    def get_preval(self):
        return self._preval
    def get_current_value(self):
        return self._current_value
    @abstractmethod
    def search_update(self):
        self._
        pass
    @abstractmethod
    def search_title(self):
        pass

class web_scracher_tw_manhuagui_com(web_scracher):
    def __init__(self , web, preval ):
        self._web = web
        self._preval = preval
        pass
    def search_update(self):
        for link in self._soup.findAll( attrs={"target": '_blank','class':'blue'} ):
            value = link.text
        self._current_value = value 
    def search_title(self):
        for link in self._soup.findAll( name= 'title'):
            title = link.text
        self._title = title
class web_scracher_m_manhuagui_com(web_scracher):
    def __init__(self , web, preval ):
        self._web = web
        self._preval = preval
        pass
    def search_update(self):
        for link in self._soup.findAll( attrs={'class':'cont-list'}):
            for liki in link.find(name = 'dd'):
                value = liki.text
        self._current_value = value 
    def search_title(self):
        for link in self._soup.findAll( name= 'title'):
            title = link.text
        self._title = title
class web_scracher_www_manhuaren_com(web_scracher):
    def __init__(self , web, preval ):
        self._web = web
        self._preval = preval
        pass
    def search_update(self):
        for link in self._soup.findAll( name= 'title'):
            value = link.text
        self._current_value = value 
    def search_title(self):
        for link in self._soup.findAll( name= 'title'):
            title = link.text
        self._title = title
def check_manga_state( web,preval ):

    net_dict = {'tw.manhuagui.com':web_scracher_tw_manhuagui_com,
                'm.manhuagui.com':web_scracher_m_manhuagui_com,
                'www.manhuaren.com':web_scracher_www_manhuaren_com}
    if(urlparse(web).netloc in net_dict):
        try:
            solu = net_dict[urlparse(web).netloc](web,preval)
            solu.connect_process()
        except (urlerror,TimeoutError):
            print(web +' is not accessable')
            output_class = manga_unable(web,'Null',preval,'Null')
            return output_class
        solu.search_update()
        solu.search_title()
        if( solu.check_if_updated() ):
            output_class = manga_updated(web,solu.get_title(),solu.get_preval(),solu.get_current_value())
            return output_class
        else:
            output_class = manga_nonupdated(web,solu.get_title(),solu.get_preval(),solu.get_current_value())
            return output_class
    else:
        return manga_failed(web,'Null',preval,preval)