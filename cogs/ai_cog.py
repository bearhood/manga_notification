from discord.ext import commands, tasks
import functools
import google.generativeai as genai
from google.generativeai.generative_models import  ChatSession
from google.generativeai.types.generation_types import StopCandidateException

import discord
import json
import os

'asd094198'
#api_key = 'AIzaSyCmEnVREncBvkq3HnFTVAFg-we8Miyn_8s'
'hebero'
api_key = 'AIzaSyCnjYb_MfCDAsX1oE_48OlcR6b1V_OndfQ'
genai.configure(api_key = api_key)
safe = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]


class ai(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        #self.models:dict[str,genai.GenerativeModel] = {}
        self.chats:dict[str,ChatSession] = {}
        self.hist_root_path = './data/ai/cm_hist'
        self.module_root_path = './data/ai/special_module'
        self.model = genai.GenerativeModel('gemini-pro',
                                           safety_settings=safe)


        self.ai_eff_label = 1 #開啟之後，說話的人前面會加一個自己的名稱
    '''
     genai.GenerativeModel('gemini-pro')
     self.chat = self.model.start_chat(history=[])
    '''
    @commands.command(brief='load_modules from preset', description='load_modules from preset')
    async def load_ai_module(self, ctx: commands.Context,args):
        args=  args.replace(' ', '')
        suc = await self.add_new_ai( str( ctx.channel.id ),module=args )
        if( suc ==1 ):
            await ctx.send('add this channel into talking')
        else:
            await ctx.send('fail to add')
    @commands.command(brief='show_module', description='show existing module')
    async def show_ai_module(self, ctx: commands.Context):
        for filename in os.listdir( self.module_root_path  ):
            if filename.endswith(".json"):
                await ctx.send(f"{filename[:-5]}")
    #@commands.command(brief='save_module', description='save current talk into module')
    async def save_ai_module(self, ctx: commands.Context, args):
        args = args.replace(' ','')
        await self.save_ai_history(str( ctx.channel.id ) , module=args)

    @commands.command(brief='add ai and load memory', description='add ai and load memory')
    async def start_ai_service(self, ctx: commands.Context):
        suc = await self.add_new_ai( str( ctx.channel.id) )
        if( suc ==1):
            await ctx.send('add this channel into talking')
        else:
            await ctx.send('fail to add')
    @commands.command(brief='remove ai and save for talkings', description='remove ai and save for talkings')
    async def end_ai_service(self, ctx: commands.Context):
        suc = await self.del_ai(str( ctx.channel.id ) )
        if( suc ==1 ):
            await ctx.send('remove this channel into talking')
        else:
            await ctx.send('fail to remove')

    @commands.command(brief='open person identifing', description='talking person is labeled')
    async def open_ai_identifier(self, ctx: commands.Context):
        self.ai_eff_label =  1
        await ctx.send('Now ai recognize you, please load from module "rem" or preload and saved one')
    @commands.command(brief='close person identifing', description='close labeled')
    async def close_ai_identifier(self, ctx: commands.Context):
        self.ai_eff_label =  0
        await ctx.send('Now ai don"t no you' )

    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if ( (message.author == self.bot.user) or
            (str(message.channel.id ) not in list( self.chats.keys()) ) ):
            return
        id = str( message.channel.id )
        if message.content[0]=='!': #
            
            if(self.ai_eff_label==1):
                ai_get_content = message.author.display_name+':' +message.content[1:]
            else:
                ai_get_content = message.content[1:]
            print(ai_get_content)
            try:
                response = await self.chats[id].send_message_async(ai_get_content)
                await message.channel.send( '有C: ' + response.text )
            except (StopCandidateException  ):
                await message.channel.send( 'Error: 請不要逼有C說帶有腥羶色的話' )
            
    async def add_new_ai(self , id , module=''):
        if( str(id) not in list( self.chats.keys() ) ):
            if ( module == '' ):
                hist = await self.get_ai_history( str(id) ) 
            else:
                hist = await self.get_ai_history( str(id) ,module =module  ) 
            if( hist == None ):
                return 0 
            
            self.chats[str(id)] = self.model.start_chat(history= hist)
            return 1
        else:
            return 0
    async def del_ai(self , id):
        if( str(id) not in list( self.chats.keys() ) ):
            return 0
        else:
            await self.save_ai_history(str(id))
            del self.chats[str(id)]
            return 1
    async def get_ai_history(self, id , module = '') -> list:
        ids = os.listdir( self.hist_root_path )
        idss = [i.split('.')[0] for i in ids]
        if(module != '' ):
            predict_path = os.path.join(self.module_root_path, module) +'.json'
            suc = os.path.exists( predict_path )
            if(suc):
                with open( predict_path, 'r', encoding='utf-8') as jsonfile:
                    try:
                        temp = json.load(jsonfile)
                    except:
                        temp = []
                    return temp
            else:
                return None
        elif(module =='' ): #如果沒有特別指定模組
            if( str(id) not in idss ):
                with open(os.path.join(self.hist_root_path, str(id)) +'.json',
                        'w', encoding='utf-8') as jsonfile:
                    json.dump([],jsonfile)
                    return []
            else:
                with open(os.path.join(self.hist_root_path, str(id)) +'.json',
                        'r', encoding='utf-8') as jsonfile:
                    try:
                        temp = json.load(jsonfile)
                    except:
                        temp = []
                    return temp
            
    async def save_ai_history(self, id , module = '') -> list:
        if(module==''):
            with open(os.path.join(self.hist_root_path, str(id)) +'.json',
                        'w', encoding='utf-8') as jsonfile:
                temp = await self.re_history( self.chats[id].history )
                print(temp)
                json.dump(temp,jsonfile)
        else:
            with open(os.path.join(self.module_root_path,module) +'.json',
                        'w', encoding='utf-8') as jsonfile:
                temp = await self.re_history( self.chats[id].history )
                print(temp)
                json.dump(temp,jsonfile)
    async def re_history(self, history): # Transform the "Google history" into "json history"
        solu = [{'parts':[] ,'role':''} for i in history ]
        for idx_hist, part in enumerate(history):
            solu[idx_hist]['parts']= [part.parts[0].text]
            solu[idx_hist]['role'] = part.role 
        return solu

async def setup(bot: commands.Bot):
    await bot.add_cog(ai(bot))
