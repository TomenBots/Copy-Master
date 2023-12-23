from pyrogram import Client,filters,enums
import requests,os,wget 

from mbot import AUTH_CHATS, LOG_GROUP,Mbot
from os import mkdir
#from utils import temp
from random import randint
#from database.users_chats_db import db
from yt_dlp import YoutubeDL
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import os
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mbot.utils.mainhelper import fetch_spotify_track
client_credentials_manager = SpotifyClientCredentials()
client = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

from pyrogram import filters
from mbot import AUTH_CHATS, LOG_GROUP,Mbot
from deezer import Client
from os import mkdir
from random import randint
from mbot.utils.mainhelper import fetch_tracks,download_dez,parse_deezer_url,thumb_down


client = Client()


@Client.on_message(filters.command('saavn') & filters.text)
async def saaven(client, message):
    try:
       args = message.text.split(None, 1)[1]
    except:
        return await message.reply("/saavn requires an argument.")
    if args.startswith(" "):
        await message.reply("/saavn requires an argument.")
        return ""
    pak = await message.reply('Downloading...')
    try:
        r = requests.get(f"https://saavn.me/search/songs?query={args}&page=1&limit=1").json()
    except Exception as e:
        await pak.edit(str(e))
        return
    sname = r['data']['results'][0]['name']
    slink = r['data']['results'][0]['downloadUrl'][4]['link']
    ssingers = r['data']['results'][0]['primaryArtists']
  #  album_id = r.json()[0]["albumid"]
    img = r['data']['results'][0]['image'][2]['link']
    thumbnail = wget.download(img)
    file = wget.download(slink)
    ffile = file.replace("mp4", "mp3")
    os.rename(file, ffile)
    await pak.edit('Uploading...')
    await message.reply_audio(audio=ffile, title=sname, performer=ssingers,caption=f"[{sname}]({r['data']['results'][0]['url']}) - from saavn ",thumb=thumbnail)
    os.remove(ffile)
    os.remove(thumbnail)
    await pak.delete()




client_credentials_manager = SpotifyClientCredentials()
client = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
async def get_data(query):
    ydl_opts = {
        'format': "bestaudio/best",
        'default_search': 'ytsearch',
        'noplaylist': True,
        "nocheckcertificate": True,
        "outtmpl": f"(title)s.mp3",
        "quiet": True,
        "addmetadata": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,

        "nocheckcertificate": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
            video = ydl.extract_info(query, download=False)
            return video 

async def down_data(item,query):
    ydl_opts = {
        'format': "bestaudio/best",
        'default_search': 'ytsearch',
        'noplaylist': True,
        "nocheckcertificate": True,
        "outtmpl": f"{item['title']} {item['uploader']}.mp3",
        "quiet": True,
        "addmetadata": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,

        "nocheckcertificate": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
            video = ydl.extract_info(query, download=True)
            return ydl.prepare_filename(video)


async def soudcloud(bot, message):
    try:
      # if message.from_user.id in temp.BANNED_USERS:
       #   return
       m = await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")
       await message.reply_chat_action(enums.ChatAction.TYPING)
       link = message.matches[0].group(0)
     #  get_s = await db.get_set(message.from_user.id)
    #   if get_s['http'] == "False":
     #     return
       item=await get_data(link)
       path=await down_data(item,link)
       await message.reply_audio(path)
       await m.delete()
       os.remove(path)
    except Exception as e:
        pass
        await message.reply(e)
    #    await Mbot.send_message(BUG,f"SoundCloud  {e}")
        await m.delete()
        os.remove(path)


async def deezer(_, message):
    link = message.matches[0].group(0)
    try:
        items = await parse_deezer_url(link)
        item_type = items[0]
        item_id = items[1]
        m = await message.reply_text("Gathering information... Please Wait.")
        songs = await fetch_tracks(client,item_type,item_id)
        if item_type in ["playlist", "album", "track"]:
            randomdir = f"/tmp/{str(randint(1,100000000))}"
            mkdir(randomdir)
            for song in songs:
                PForCopy = await message.reply_photo(song.get('cover'),caption=f"🎧 Title : `{song['name']}`\n🎤 Artist : `{song['artist']}`\n💽 Album : `{song['album']}`\n💽 Song Number : `{song['playlist_num']}`")
                path = await download_dez(song,randomdir)
                thumbnail = await thumb_down(song.get('thumb'),song.get('name'))
                AForCopy = await message.reply_audio(path,performer=song.get('artist'),title=f"{song.get('name')} - {song.get('artist')}",caption=f"[{song['name']}](https://www.deezer.com/track/{song['deezer_id']}) | {song['album']} - {song['artist']}",thumb=thumbnail,duration=song['duration'])
                if LOG_GROUP:
                    await PForCopy.copy(LOG_GROUP)
                    await AForCopy.copy(LOG_GROUP)
            await m.delete()
        elif item_type == "artist":
            await m.edit_text("This Is An Artist Account Link. Send me Track, Playlist or Album Link :)")
        else:
            await m.edit_text("Link Type Not Available for Download.")
    except Exception as e:
        await m.edit_text(f'Error: {e}', quote=True)
