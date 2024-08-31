import discord
from discord.ext import commands, tasks
import functools

import os
import json
import re
import urllib
import json
import functools
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from  datetime import datetime

web_update = 'https://tw.manhuagui.com/update/'
url_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'}


def check_if_user_exist():
    def wrapper(func):
        @functools.wraps(func)
        async def wrapper(classs, ctx):
            print('in wrapper')
            '''This block use to check if the corresponding user exist in specific json file'''
            if(str( ctx.channel.id ) not in classs.manga_class.manga_dict.keys() ):
                classs.manga_class.manga_dict[str( ctx.channel.id )] = {}
                await classs.manga_class.save_json()
                print( f'add {str( ctx.channel.id )} into the channel')
            return await func(classs, ctx)
        return wrapper
    return wrapper
# 定義名為 Main 的 Cog
class manga(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manga_class = manga_state()
        self.scraper = manga_scraper()
    # 前綴指令
    @commands.command(brief='add web only in manhuagui', description='add web into json')
    @check_if_user_exist()
    async def manga_add_manga(self, ctx: commands.Context):
        await ctx.send('received manga')
        text = ctx.message.content
        text = re.sub(r'\s+',' ',text)[1:-1].split(' ')[1:]
        for i in range(len(text)):
            if(text[i][-1]!='/'):
                text[i]+='/'
        output = await self.manga_class.add_manga(ctx.channel.id,text)

        if( output==0 ):
            await ctx.send('error')
        if(output['bad'] !=[] ):
            await ctx.send('Not good:' +'\n  '.join(output['bad']))
        if(output['good'] !=[] ):
            await ctx.send('goods:' +'\n  '.join(output['good']))


    @commands.command(brief='del web', description='delete web from json')
    @check_if_user_exist()
    async def manga_del_manga(self, ctx: commands.Context):
        await ctx.send('not finishing')
    
    @commands.command(brief='trigger manga updating', description='trigger manga updating per hour')
    async def manga_doupdate(self, ctx: commands.Context):
        self.manga_updates_per_hour.start()
        await ctx.send('start manga updating')
    


    @commands.command(brief='stop manga updating', description='stop updating per hour')
    async def manga_undoupdate(self, ctx: commands.Context):
        self.manga_updates_per_hour.cancel()
        await ctx.send('end manga updating')

    @commands.command(brief='print mangas', description='print current tracing mangas')
    async def manga_listall(self, ctx: commands.Context):
        def deal_with_text(list_:dict):
            text_list = []
            text_list.append( datetime.now().strftime("%Y/%m/%d %H:%M:%S 更新程式") )
            text = ''
            for i in list_.keys():
                text = text + '[{}]({}) \n'.format(list_[i]['title'],i) 
                if( len(text  )>1500 ):
                    text_list.append( text )
                    text = ''
            text_list.append(text)
            return text_list
        id = ctx.channel.id
        if(self.manga_class.manga_dict[str(id)]!={} ):
            chan = self.bot.get_channel(int(id))

            text_list = deal_with_text(self.manga_class.manga_dict[str(id)])
            
            for text in text_list:
                await chan.send(text)






    #@commands.command(brief='update_manga', description='updaa web from json')
    @tasks.loop(minutes=60) #only it asked to be start
    async def manga_updates_per_hour(self):
        print(str(datetime.now().strftime('%Y-%m-%d')))
        print('update manga')
        updating_dict = self.scraper.update_manga_web()
        #print(updating_dict)
        updated_dict = await self.manga_class.check_manga_update( update_dict=updating_dict)

        def deal_with_text(list_:dict):
            text_list = []
            text_list.append( datetime.now().strftime("%Y/%m/%d %H:%M:%S 更新程式") )

            text = ''
            for i in list_.keys():
                try:
                    text = text + '[{}]({})'.format(list_[i]['title'],i) +'更新到{}\n'.format(list_[i]['dep'])
                except:
                    text = text + '[{}]'.format(list_[i]['title']) +'更新到{}\n'.format(list_[i]['dep'])
                    continue
                if( len(text  )>1500 ):
                    text_list.append( text )
                    text = ''
            text_list.append(text)
            return text_list
        for id in updated_dict.keys():  
            if(updated_dict[id] !={} ):
                chan = self.bot.get_channel(int(id))
                text_list = deal_with_text(updated_dict[id])
                for text in text_list:
                    await chan.send(text)
# Cog 載入 Bot 中


class manga_state():
    def __init__(self):
        self._json_path = './data/manga/manga_data.json'
        self.manga_dict = self.read_json()

    async def check_manga_update(self, update_dict={}):

        return_dict = {}
        '''
            return_dict = { id: {title: ... , dep: ...}  }
        '''
        update_web = update_dict.keys()

        for id in self.manga_dict.keys():

            return_dict[id]={}
            web_list = list( self.manga_dict[id].keys() )
            loc_list = [urlparse(web).path for web in web_list]
            
            updates = list(set(loc_list) & set(update_web))

            for update in updates:
                web_idx = loc_list.index(update)

                web = web_list[web_idx]
                up_dep = update_dict[update]['dep'].replace('更新','').replace('至','')
                up_title = update_dict[update]['title']
                if( self.manga_dict[id][web]['dep'] != up_dep):
                    self.manga_dict[id][web]['dep'] = up_dep
                    self.manga_dict[id][web]['title'] = up_title
                    self.manga_dict[id][web]['last'] = str(datetime.now().strftime('%Y-%m-%d'))
                    return_dict[id][web] = self.manga_dict[id][web]
        await self.save_json()
        return return_dict
    async def add_manga(self,id ,  webs = ''):
        print(webs)
        out = {'good':[],'bad':[]}
        if( webs==''):
            return 0
        
        for web in webs:
            if(urlparse(web).netloc != 'tw.manhuagui.com'):
                out['bad'].append(web)
                continue
            else:
                self.manga_dict[str(id)][web] = {
                    "title": ".",
                    "dep": ".",
                    "last": str(datetime.now().strftime('%Y-%m-%d'))
                }
                out['good'].append(web)

        await self.save_json()
        return out
    async def save_json(self):
        with open(self._json_path , 'w', encoding='utf-8')as jsonfile:
            json.dump(self.manga_dict,jsonfile)

    def read_json(self): #Reload data from saving
        with open(self._json_path , 'r', encoding='utf-8')as jsonfile:
            temp = json.load(jsonfile)
            print('loadmanga succeed')
        return temp

class manga_scraper():
    def __init__( self):
        pass
    def update_manga_web(self):
        req = urllib.request.Request( web_update,
                                headers = url_headers )
        html_page = urllib.request.urlopen( req ,timeout = 5)
        _soup = BeautifulSoup(html_page,'html.parser')

        #idiot updating
        updating_tot = _soup.findAll( attrs={'class':'latest-cont'})[0]
        last_day = updating_tot.findNext(name='h5').text.split(' ')[0]
        updating_ctx = updating_tot.findNext(attrs={'class':"latest-list"})
        updating_ctx_list = updating_ctx.findAll(name='li')
        today_date = str(datetime.now().strftime('%Y-%m-%d'))

        out_dict = {}
        if(last_day==today_date):
            for mginfo in updating_ctx_list:
                mghref=  mginfo.findNext(name='a')['href']
                mgname=  mginfo.findNext(name='a')['title']
                mgdep = mginfo.findNext(name='span' , attrs={'class':"tt"}).text
                out_dict[mghref] = {'dep':mgdep,  'title':mgname}
        else:
            pass
        return out_dict

async def setup(bot: commands.Bot):
    await bot.add_cog(manga(bot))