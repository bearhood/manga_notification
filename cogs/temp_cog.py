from discord.ext import commands, tasks
import functools
import google.generativeai as genai
from google.generativeai.generative_models import  ChatSession
from google.generativeai.types.generation_types import StopCandidateException
import discord
import json
import os

from PIL import Image
import io
api_key = 'AIzaSyCmEnVREncBvkq3HnFTVAFg-we8Miyn_8s'
genai.configure(api_key = api_key)



class temp(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


        self.ai_eff_label = 1 #開啟之後，說話的人前面會加一個自己的名稱
    '''
     genai.GenerativeModel('gemini-pro')
     self.chat = self.model.start_chat(history=[])
    '''
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if ( message.author == self.bot.user):
            return
        id = str( message.channel.id )
        print(id)
        if message.attachments:
            for attachment in message.attachments:
                if attachment.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp')):
                    image_data = await attachment.read()
                    image = Image.open(io.BytesIO(image_data))
                    # 在這裡處理 image 對象，例如保存或進行其他操作
                    image.show()  # 這將顯示圖片
async def setup(bot: commands.Bot):
    await bot.add_cog(temp(bot))
