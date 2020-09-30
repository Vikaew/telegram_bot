from config import token

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from telegram import MessageEntity

import tempfile as tf
import os
import urllib.request
import eyed3

endpoint_link = "https://jio-saavan-api.herokuapp.com/result/?query="

import urllib.request, json


def fetchjson(url):
    resp = urllib.request.urlopen(url)
    return json.loads(resp.read().decode())


def start(update, context):
    text = "Hello {yourname}".format(yourname=update.effective_user.full_name)
    update.message.reply_text(text)


def download(update, context):
    x = update.message.parse_entities(types=MessageEntity.URL)
    msg = update.message.reply_text("Working on it... :-)")
    for i in x:
        try:
            rjson = fetchjson(endpoint_link + i)
            title = rjson["song"]
            link = rjson["media_url"]
            img_link = rjson["image"]
            album = rjson["album"]
            singers = rjson["singers"]
            image_file = tf.NamedTemporaryFile(suffix=".jpg", delete=False)
            temp_file = tf.NamedTemporaryFile(suffix=".mp3",delete=False)
            file_path = temp_file.name
            img_path = image_file.name
            temp_file.close()
            image_file.close()
            urllib.request.urlretrieve(link, file_path)
            urllib.request.urlretrieve(img_link,img_path)

            song = eyed3.load(file_path)
            song.tag.artist = singers
            song.tag.album = album
            song.tag.title = title
            song.tag.images.set(3, open(img_path, "rb").read(), "image/jpg")
            song.tag.save(version=eyed3.id3.ID3_V2_3)


            music = update.message.reply_document(open(file_path,"rb"),filename = title, caption="Here is {}".format(title))
            msg.delete()
            os.remove(file_path)
            return music
        except:
            continue
    msg.edit_text("I can't fetch from that url.Try again with another url.")


updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.entity(MessageEntity.URL), download))


updater.idle()
