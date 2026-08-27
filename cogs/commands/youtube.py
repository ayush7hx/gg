import discord
from discord.ext import commands

class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='yt', aliases=['youtube'])
    async def search_youtube(self, ctx, *, search_query):
        await ctx.send('YouTube link search is disabled.')
