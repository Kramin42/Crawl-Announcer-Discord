from discord import TextChannel, Member
from discord.ext import commands
import asyncio
import socketio
import dataset
import json
import sqlite3
import datetime

CRAWLAPI_SERVER = 'http://127.0.0.1:5001'

with open('TOKEN', 'r') as f:
    TOKEN = f.read().strip()

db = dataset.connect('sqlite:///store.db')
channels = db['channels']
channel_nicks = db['channel_nicks']

bot = commands.Bot(command_prefix='$')

sio = socketio.AsyncClient()

loop = asyncio.get_event_loop()


#
# formatter
#

def format_milestone(data):
    return data['name'] + \
        ' (L' + data['xl'] + ' ' + data['char'] + ') '+ \
        data['milestone'] + \
        ' (' + (data['oplace'] if ('oplace' in data and 'left' in data['milestone']) else data['place']) + \
        ') ['+data['src']+' '+data['v']+']'

def format_gameover(data):
    loc_string = ''
    if data['ktyp'] != 'winning' and data['ktyp'] != 'leaving':
        if ':' in data['place']:
            loc_string = ' on ' + data['place']
        else:
            loc_string = ' in ' + data['place']

    duration = str(datetime.timedelta(seconds=int(data['dur'])))
    
    return data['name'] + ' the ' + data['title'] + \
        ' (L' + data['xl'] + ' ' + data['char'] + ')' + \
        (' worshipper of ' + data['god'] if 'god' in data else '') + ', ' + \
        (data['vmsg'] if 'vmsg' in data else data['tmsg']) + \
        loc_string + ', with ' + \
        data['sc'] + ' points after ' + data['turn'] + ' turns and ' + duration + '.'

def format_event(event):
    data = event['data']
    data['src'] = event['src_abbr'].upper();
    if event['type'] == 'milestone':
        return format_milestone(data)
    else:
        return format_gameover(data)


#
# Discord handlers
#

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

@bot.command()
@commands.has_permissions(administrator=True)
async def addchannel(ctx, *, target: TextChannel):
    try:
        channels.insert(dict(id=target.id, name=target.name))
        await ctx.send(f'Added channel {target}')
    except: # TODO: find out the right error type to except
        await ctx.send(f'Channel {target} already exists')
    for x in channels:
        print(x)

@bot.command()
async def addnick(ctx, nick: str):
    if channels.find_one(id=ctx.channel.id) is not None:
        channel_nicks.insert_ignore(dict(channel_id=ctx.channel.id, nick=nick.lower()), ['channel_id', 'nick'])
        await ctx.send(f'Added nick: {nick.lower()}')
    else:
        await ctx.send(f'Announcing is not enabled in this channel, an admin must run `$addchannel #{ctx.channel}`')
    for x in channel_nicks:
        print(x)


#
# Socketio handlers
#

@sio.on('connect')
async def sio_on_connect():
    print('connected to socketio server')


@sio.on('crawlevent')
async def sio_on_crawlevent(data):
    for event in json.loads(data):
        for ch_nick in channel_nicks.find(nick=event['data']['name'].lower()):
            await bot.get_channel(ch_nick['channel_id']).send(format_event(event))


async def start_sio():
    await sio.connect(CRAWLAPI_SERVER)
    await sio.wait()


#
# main
#

if __name__=='__main__':
    # start asyncio loop
    try:
        loop.run_until_complete(asyncio.gather(
            bot.start(TOKEN),
            start_sio()
        ))
    except KeyboardInterrupt:
        print('Bye')
    finally:
        loop.close()
