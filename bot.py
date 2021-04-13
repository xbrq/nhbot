# -*- coding: utf-8 -*-
import discord, asyncio, logging, os, math, subprocess, json, dotenv, requests
from discord.ext import commands
from discord.ext.commands import Bot
from hentai import Hentai, Format, Utils, Sort, Option, Tag

dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")

description = 'Simple bot based around nhentai API'

help_message = \
"""```
NHentaiBot help

Commands:
    >help               : Produces this message
    >tag <tag> <number> : Returns the top <number> doujinshi with tag <tag> this week
        Ex. >tag loli 5
    ><ID>               : Returns information about the doujin with ID <ID>
        Ex. >177013
    >random             : Returns information about a random doujin
```"""

bot = discord.Client()

@bot.event
async def on_ready():
        print('Logged in as: ')
        print(bot.user.name)
        print(bot.user.id)
        print('------------')
        activity = discord.Activity(name = 'for \'>\'', type = discord.ActivityType.watching)
        await bot.change_presence(activity=activity)

@bot.event
async def on_message(message):
        if message.author.bot: return
        if message.content[0] != '>': return # prefix is '>'
        # help message
        if message.content[1:] == 'help':
            await message.reply(help_message)
            return
        # get a doujin from id number
        # cast to int if possible; otherwise, it's not an ID number
        try:
            ID = int(message.content[1:])
            try:
                doujin = Hentai(ID)
                desc = '**Tags**: ' + str([tag.name for tag in doujin.tag])[1:-1].replace("'", '')
                artist_name = ''
                try:
                    artist_name = '\n**Artist**: {doujin.artist[0].name}'
                except:
                    return False
                desc += f'\n**Uploaded**: {doujin.upload_date}'
                e = discord.Embed(title=doujin.title(Format.Pretty), description=desc, url=f'https://nhentai.net/g/{doujin.id}', color=0xf54d4d)
                # e.set_thumbnail(url=message.author.avatar_url_as(size=256))
                e.set_footer(text='Questions, comments or concerns? DM thief#0001.')
                e.set_image(url=doujin.cover)
                await message.reply(embed=e)
                return
            except (TypeError, requests.exceptions.HTTPError):
                await message.reply('Invalid ID.')
                return
        except ValueError: # not an ID query
            if message.content[1:] == 'random': # get a random doujin
                doujin = Utils.get_random_hentai()
                desc = '**Tags**: ' + str([tag.name for tag in doujin.tag])[1:-1].replace("'", '')
                desc += f'\n**Uploaded**: {doujin.upload_date}\n**ID**: {doujin.id}\n**Artist**: {doujin.artist[0].name}'
                e = discord.Embed(title=doujin.title(Format.Pretty), description=desc, url=f'https://nhentai.net/g/{doujin.id}', color=0xf54d4d)
                # e.set_thumbnail(url=message.author.avatar_url_as(size=256))
                e.set_footer(text='Questions, comments or concerns? DM thief#0001.')
                e.set_image(url=doujin.cover)
                await message.reply(embed=e)
                return
            if message.content[1:5] == 'tag ': # get a list of doujinshi with a certain tag
                content = message.content.split()
                tag, num = content[1], content[2]
                title = f'Top {num} {tag} doujinshi this week:\n' if num != 1 else f'Top {tag} doujinshi this week:\n'
                top = []
                try:
                    num = int(num)
                except ValueError:
                    await message.reply('Incorrect syntax. Use `>tag <tag> <number>` ' + \
                                               'to get the top `<number>` doujinshi this week.')
                    return
                for doujin in Utils.search_by_query('tag:' + tag, sort=Sort.PopularWeek)[:num]:
                    top.append((doujin.title(Format.Pretty), [tag.name for tag in doujin.tag], doujin.id))
                if top == []: await message.reply('No results found for this tag.')
                else:
                    error = ''
                    if len(top) < num:
                        title = title.replace(str(num), str(len(top)))
                        error += f'\nMaximum number of weekly doujinshi queried. (There were fewer than {num}.)'
                    e = discord.Embed(title=title, description=f'Requested by {message.author.mention}' + error, color=0xf54d4d)
                    for doujin in top:
                        e.add_field(name=f'{doujin[0]} ({doujin[2]})', value=str(doujin[1])[1:-1].replace("'", '') + \
                                    f'\nLink: [nhentai.net/g/{doujin[2]}](https://nhentai.net/g/{doujin[2]})', inline=False)
                    e.set_footer(text='Questions, comments or concerns? DM thief#0001.')
                    await message.reply(embed=e)
                return
        # command: get info about a tag
        await message.reply('Invalid query.')



bot.run(TOKEN)
