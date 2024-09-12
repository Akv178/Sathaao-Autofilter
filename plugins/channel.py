# This code has been modified by Safaridev
# Please do not remove this credit

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import CHANNELS, GRP_LNK
from database.ia_filterdb import save_file, get_file_details
from utils import get_poster, get_size, temp
from os import environ
import logging
import re

collected_files = []
post_active = False

media_filter = filters.document | filters.video | filters.audio

POST_CHANNELS = list(map(int, (channel.strip() for channel in environ.get('POST_CHANNELS', '-1001883539506').split(','))))

BLACKLIST = ['tamilblaster', 'filmyzilla', 'streamershub', 'xyz', 'cine', 'www', 'http', 'https',
                'cloudsmoviesstore', 'moviez2you', 'bkp', 'cinema', 'filmy', 'flix', 'cutemoviez',
                '4u', 'hub', 'movies', 'otthd', 'telegram', 'hoichoihok', '@', ']', '[', 'missqueenbotx',
                'filmy', 'films', 'cinema', 'join', 'club', 'apd', 'F-Press', 'GDTOT', 'mkv', 'NETFLIX_OFFICIAL',
                'backup', 'primeroom', 'theprofffesorr', 'premium', 'vip', '4wap', 'toonworld4all', 'mlwbd',
                'Telegram@alpacinodump', 'bollywood', "AllNewEnglishMovie", "7MovieRulz", "1TamilMV",
                'Bazar', '_Corner20', 'CornersOfficial', 'support', 'iMediaShare', 'Uᴘʟᴏᴀᴅᴇᴅ', 'Bʏ', 'PFM', 'alpacinodump', 
                "Us", "boxoffice", "Links", "Linkz", "Villa", "Original", "bob", "Files1", "MW", "LinkZ", "}", "{" 
                ]

def clean_filename(file_name):
    for word in BLACKLIST:
        escaped_word = re.escape(word)  # Escape the word to make it regex-safe
        file_name = re.sub(escaped_word, '', file_name, flags=re.IGNORECASE) 
    return file_name

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    global post_active, collected_files

    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return

    media.file_type = file_type
    media.caption = message.caption
    success, file_id = await save_file(media)

    if success and file_id:
        file_details = await get_file_details(file_id)
        if file_details:
            file_id = file_details[0]['file_id']

    if success and "count post" in (media.caption or "").lower():
        post_active = True
        collected_files = []

    if post_active:
        clean_name = clean_filename(media.file_name.replace('_', ' '))
        collected_files.append((file_id, clean_name, media.caption, media.file_size))

    if success and "send post" in (media.caption or "").lower():
        post_active = False 

        if collected_files:
            imdb_info = None

            for file_id, file_name, caption, file_size in collected_files:
                size_text = get_size(file_size)
                file_url = f"😍 [{size_text}]👇\n<a href='https://t.me/{temp.U_NAME}?start=files_{file_id}'>{file_name}</a>"

                if imdb_info is None:
                    try:
                        movie_name = caption.split('|')[0].strip()
                        logging.info(f"Searching IMDb for: {movie_name}")
                        imdb_info = await get_poster(movie_name)
                        if not imdb_info:
                            logging.error(f"IMDb information not found for: {movie_name}")
                            return
                    except Exception as e:
                        logging.error(f"Error while fetching IMDb info: {str(e)}")
                        return

            if imdb_info:
                title = imdb_info.get('title', 'N/A')
                rating = imdb_info.get('rating', 'N/A')
                genre = imdb_info.get('genres', 'N/A')
                description = imdb_info.get('plot', 'N/A')
                poster_url = imdb_info.get('poster', None)
                year = imdb_info.get('year', 'N/A')
                year = imdb_info.get('year', 'N/A')

                urls_text = "\n\n".join([f"😍 [{get_size(size)}]👇\n<a href='https://t.me/{temp.U_NAME}?start=files_{file_id}'>{file_name}</a>" for file_id, file_name, caption, size in collected_files])
                caption = f"<b>🏷 Title: {title}\n🎭 Genres: {genre}\n📆 Year: {year}\n🌟 Rating: {rating}\n\n{urls_text}</b>" 
                reply_markup=InlineKeyboardMarkup([[
                     InlineKeyboardButton('🔰 𝗦ᴇᴀʀᴄʜ 𝗚ʀᴏᴜᴘ 🔍', url=GRP_LNK)],
                     [InlineKeyboardButton("🎁 𝗕ᴜʏ 𝗣ʀᴇᴍɪᴜᴍ ✨", url=f'https://t.me/{temp.U_NAME}?start=Safaridev')]
                ])
                for channel in POST_CHANNELS:
                    if poster_url:
                        try:
                            await bot.send_photo(
                                chat_id=channel,
                                photo=poster_url,
                                caption=caption,
                                parse_mode=enums.ParseMode.HTML,
                                reply_markup=reply_markup, 
                                has_spoiler=True
                            )
                        except Exception as e:
                            logging.error(f"Error sending poster to channel {channel}: {str(e)}")
                            # Fallback to sending text if the poster fails
                            await bot.send_message(
                                chat_id=channel,
                                text=caption,
                                parse_mode=enums.ParseMode.HTML,
                                reply_markup=reply_markup
                            )
                    else:
                        url_text = "\n\n".join([f"😍 [{get_size(size)}]👇\n<a href='https://t.me/{temp.U_NAME}?start=files_{file_id}'>{file_name}</a>" for file_id, file_name, caption, size in collected_files])
                        captionn = f"<b>#Information_Not_Available\n\nTotal Files: {len(collected_files)}\n\n{url_text}</b>"
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton('🔰 𝗦ᴇᴀʀᴄʜ 𝗚ʀᴏᴜᴘ 🔍', url=GRP_LNK)],
                            [InlineKeyboardButton("🎁 𝗕ᴜʏ 𝗣ʀᴇᴍɪᴜᴍ ✨", url=f'https://t.me/{temp.U_NAME}?start=Safaridev')]
                        ])
                        await bot.send_message(
                            chat_id=channel,
                            text=captionn,
                            parse_mode=enums.ParseMode.HTML,
                            reply_markup=reply_markup
                        )
        collected_files = []
