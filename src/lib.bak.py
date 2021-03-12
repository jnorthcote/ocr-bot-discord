import io
import requests
import time
import filetype
import json

from google.cloud import vision
from google.protobuf.json_format import MessageToDict
from elasticsearch_dsl import Search, Document, Index, Text, Long, Q
from discord import Embed
from hashlib import md5
from es_db import Elastic_Database, Attachment, TrekScreenShotDoc
from sql import Sqlite3_db
from discord.ext import menus
from screen_shot import ScreenShot, SectionType
from google.protobuf.json_format import MessageToJson
from PIL import Image

class MySource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data['fields_data'], per_page=5)
        self.search_phrase = data['search_phrase']

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page

        search_phrase = self.search_phrase
        embed = Embed.from_dict({
            'title': f'Search results for \"{search_phrase}\"',
            'type': 'rich',
            'fields': entries,
            'color': 0x89c6f6
        })

        return embed


# Load config keys
with open('config.json', 'r') as f:
    config = json.load(f)

with open('discord_secrets.json', 'r') as f:
    discord_secrets = json.load(f)

db_connect = config['db-connect']
# TODO - Automatic index management
index_name = config['index-name']

vision_client = vision.ImageAnnotatorClient()
sql_db = Sqlite3_db()


connected = False
while not connected and db_connect:
    try:
        global db
        db = Elastic_Database(index_name)
        connected = True
        print('[ELASTICSEARCH]: Successfully connected')
    except Exception as e:
        print(e)
        print("[ELASTICSEARCH]: Elasticsearch not available yet, trying again in 10s...")
        time.sleep(10)


async def handle_attachments(message):
    url = message.attachments[0].url
    attachment = message.attachments[0]

    # Get the raw bytes of the attachment
    filebytes = await attachment.read()
    kind = filetype.guess(filebytes)

    print(f'[URL]: {url}')
    print(f'[FILETYPE]: {kind.mime}')

    # Return if it's not an image
    if not 'image' in kind.mime:
        return

    # Return if the image is larger than 10MB, this is a limit of Google's OCR API
    if attachment.size > 10000000:
        print(f'[INFO]: Image too large, size: {attachment.size}')
        return

    # if not str(message.channel.id) in sql_db.get_blacklisted_channels(message.guild.id):
    if str(message.channel.id) in sql_db.get_blacklisted_channels(message.guild.id):
        await save_image_text(url, message)
    else:
        print(
            f"[BLACKLIST]: channel_id {message.channel.id} in blacklisted channels")


def search(phrase, guild_id):
    if db_connect:
        if not phrase:
            print(f'[SEARCH]: Empty search - returning')
            return

        print(f'[SEARCH]: Searching for {phrase}')

        search = Search()
        q = Q('bool', must=[Q('match', text=phrase),
                            Q('match', guild_id=guild_id)])
        s = search.query(q)

        result = [{
            'filename': h.filename,
            'author': h.author_username,
            'url': h.url,
            'message_url': h.message_url,
            'id': h.meta.id
        } for h in s.scan()]

        return result
    else:
        return ""

def bs(phrase, guild_id, btag):
    if db_connect:
        if not phrase:
            print(f'[SEARCH]: Empty search - returning')
            return

        print(f'[SEARCH]: Searching for {phrase} in ')

        search = Search()
        q = Q('bool', must=[Q('match', text=phrase),
                            Q('match', guild_id=guild_id),
                            Q('match', btag=btag)])
        s = search.query(q)

        result = [{
            'filename': h.filename,
            'author': h.author_username,
            'url': h.url,
            'message_url': h.message_url,
            'id': h.meta.id
        } for h in s.scan()]

        return result
    else:
        return ""

async def save_image_text(url, message):
    ocr_text = ""
    hash = ""

    channel_btag = sql_db.get_btag(message.guild.id, message.channel.id, message.author.id)
    print(f'[channel_btag]: {channel_btag}')
    with get_image_from_url(url) as image_file:
        hash = md5(image_file.read()).hexdigest()
        print(f'[HASH]: {hash}')

        if db_connect:
            if db.exists(str(message.guild.id), hash=hash):
                print(f"[INFO]: Image {url} already exists in index")
#                return

        image_file.seek(0)
        # Read the bytes of the BytesIO object
        image = vision.types.Image(content=image_file.read())

        filename = get_filename_from_url(url)
        response = detect_text(image)
        print(MessageToJson(response))
        ta_dict = MessageToDict(response)
        # for k, v in response_dict.items():
        #     print("Key:{}\nValue:{}".format(k, v))

        image_file.seek(0)
        im = Image.open(image_file)
        width, height = im.size
        crop_hints_params = vision.types.CropHintsParams(aspect_ratios=[1.77])
        image_context = vision.types.ImageContext(
            crop_hints_params=crop_hints_params)

        response = vision_client.crop_hints(image=image, image_context=image_context)
        hints = response.crop_hints_annotation.crop_hints
        for n, hint in enumerate(hints):
            print('\nCrop Hint: {}'.format(n))

            vertices = (['({},{})'.format(vertex.x, vertex.y)
                        for vertex in hint.bounding_poly.vertices])

            print('bounds: {}'.format(','.join(vertices)))

        ss = ScreenShot(ta_dict['textAnnotations'], width, height)

        if ss.section_type == None:
            print(f'[INFO]: No text detected in {filename}')
            return

        doc = TrekScreenShotDoc(timestamp=int(time.time()*1000), author_id=int(message.author.id),
             author_username=message.author.name+"#"+message.author.discriminator,
             channel=message.channel.name, category_id=message.channel.category_id,
             guild=message.guild.name, guild_id=message.guild.id,
             message_url=message.jump_url, url=url, text=ocr_text, hash=hash,
             filename=filename, tss_tag=channel_btag)

    em = Embed.from_dict({
        'title': ss.section_type.label,
        'type':  'rich',
        'color': 0xa763bd
    })
    author = message.author
    em.set_author(name ="{} - [{}]".format(author,author.id),icon_url=author.avatar_url or author.default_avatar_url)
    for fType, value in ss.__dict__["fields"].items():
        em.add_field(name=fType.label, value=' '.join(value), inline=True)
        doc[fType.es_field_name]=' '.join(value)

    if db_connect:
        db.save_attachment(doc, index_name)
        print("[INFO]: Attachment saved")
    else:
        print("No db_connect")

    await send_message(None, message.channel, em)
    return


def get_filename_from_url(url):
    filename = url[url.rfind("/")+1:]

    return filename


def get_image_from_url(url):
    """
        Return a BytesIO object of the image
    """
    r = requests.get(url, stream=True)
    image_file = io.BytesIO(r.content)

    return image_file


def detect_text(image):
    text_detection_response = vision_client.text_detection(image=image)

    return text_detection_response

    # if len(annotations) > 0:
    #     ss = ScreenShot(annotations)
    #     print(ss.fields)
    #     text = annotations[0].description
    # else:
    #     text = ''
    #
    # return text.replace('\n', ' ')


async def send_message(message, channel, embed):
    await channel.send(message, embed=embed)


def get_embed_fields(search_result):
    fields = {}
    fields['fields_data'] = []
    for i, doc in enumerate(search_result):
        filename = doc['filename']
        author = doc['author']
        url = doc['url']
        es_id = doc['id']
        try:
            message_url = doc['message_url']
        except KeyError:
            message_url = ''
        fields['fields_data'].append({
            'name': f'{i+1}. {author}',
            'value': f'[{filename}]({url}) - [jump]({message_url})'
        })

    return fields


async def search_command(ctx, args):
    search_phrase = ' '.join(args)
    search_result = search(search_phrase, ctx.guild.id)

    fields = get_embed_fields(search_result)

    fields['search_phrase'] = search_phrase
    pages = menus.MenuPages(source=MySource(
        fields), clear_reactions_after=True, timeout=30)
    await pages.start(ctx)

    return


async def bs_command(ctx, args):
    channel_btag = sql_db.get_btag(ctx.guild.id, ctx.channel.id, ctx.author.id)
    search_phrase = ' '.join(args)
    search_result = bs(search_phrase, ctx.guild.id, channel_btag)

    fields = get_embed_fields(search_result)

    fields['search_phrase'] = search_phrase
    pages = menus.MenuPages(source=MySource(
        fields), clear_reactions_after=True, timeout=30)
    await pages.start(ctx)

    return


async def ignore_command(ctx, args):
    channel = ctx.message.channel_mentions[0]
    channel_id = str(channel.id)
    guild_id = str(ctx.guild.id)
    author_id = str(ctx.author.id)

    # TODO - global guild admins and only refresh after an update to them, might need to make a new client for every guild
    guild_admins = sql_db.get_admins(ctx.guild.id)
    guild_admins.append(discord_secrets['owner-id'])

    if author_id in guild_admins:
        # TODO - If able to blacklist by channel if, check if channel is actually in guild before adding to db
        sql_db.add_blacklist_channel(guild_id, channel_id)

        await ctx.send(f"Channel {channel.mention} ignored :)")

        print(
            f"[BLACKLIST]: Channel {channel.name} - {channel.id} blacklisted")
    # Not admin
    else:
        await ctx.send(f'You must be an admin to do that :D')
        print(
            f"[BLACKLIST]: Non admin - {author_id} tried to blacklist channel {channel.name} - {channel.id}")


async def link_command(ctx, args):
    es_id = args[0]
    jump_url = db.get_jump_url_by_id(es_id)

    # TODO - Maybe deny before we get jump_url
    if db.exists(str(ctx.guild.id), es_id=es_id):
        await ctx.send(f"{jump_url}")
    else:
        await ctx.send(f'Document with ID: {es_id} not found.')

    return

async def btag_command(ctx, args):
    channel_id = str(ctx.message.channel.id)
    guild_id = str(ctx.guild.id)
    author_id = str(ctx.author.id)
    tag_name = ' '.join(args)

    if not tag_name:
        channel_btag = sql_db.get_btag(guild_id, channel_id, author_id)
        await ctx.send(f"Batch tag for {ctx.author.mention} is: {channel_btag}")
        return

    guild_admins = sql_db.get_admins(ctx.guild.id)
    guild_admins.append(discord_secrets['owner-id'])
    if author_id in guild_admins:
        # TODO - If able to blacklist by channel if, check if channel is actually in guild before adding to db
        sql_db.set_channel_author_tag(guild_id, channel_id, author_id, tag_name)

        await ctx.send(f"Batch tag for {ctx.author.mention} set: {tag_name}")

        print(
            f"[BATCHTAG]: Channel {ctx.message.channel.name} - {tag_name}")
    # Not admin
    else:
        await ctx.send(f'You must be an admin to do that :D')
        print(
            f"[BATCHTAG]: Non admin - {author_id} tried to batch tag channel {ctx.message.channel.name} - {channel_id}")


async def admin_command(ctx, args):
    guild_admins = sql_db.get_admins(ctx.guild.id)
    guild_admins.append(discord_secrets['owner-id'])
    print(
        f"[ADMINS]: Guild admins for guild {ctx.guild.name} are {guild_admins}")

    author_id = str(ctx.author.id)
    if author_id in guild_admins:
        user = ctx.message.mentions[0]
        user_id = str(user.id)

        if not user_id in guild_admins:
            sql_db.add_admin(ctx.guild.id, user.id)
            await ctx.send(f"{user.name} is now a bot admin :)")
        else:
            sql_db.remove_admin(ctx.guild.id, user.id)
            await ctx.send(f"{user.name} is no longer a bot admin :(")
    else:
        await ctx.send(f"You must be an admin to do that :D")
        print(
            f"[ADMIN]: Non admin - {ctx.author.id} tried to use admin command on {user.name}")
