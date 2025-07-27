#(c) Adarsh-Goel
#(c) @biisal
import os
import asyncio
from asyncio import TimeoutError
from biisal.bot import StreamBot
from biisal.utils.database import Database
from biisal.utils.human_readable import humanbytes
from biisal.vars import Var
from urllib.parse import quote_plus
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
#from utils_bot import get_shortlink

from biisal.utils.file_properties import get_name, get_hash, get_media_file_size, get_fname, get_fsize
db = Database(Var.DATABASE_URL, Var.name)


MY_PASS = os.environ.get("MY_PASS", None)
pass_dict = {}
pass_db = Database(Var.DATABASE_URL, "ag_passwords")

msg_text1 ="""<b>‣ ʏᴏᴜʀ ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ! 😎

‣ Fɪʟᴇ ɴᴀᴍᴇ : <i>{}</i>
‣ Fɪʟᴇ ꜱɪᴢᴇ : {}

🔻 <a href="{}">𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗</a>
🔺 <a href="{}">𝗪𝗔𝗧𝗖𝗛 𝗢𝗡𝗟𝗜𝗡𝗘</a>

‣ ɢᴇᴛ <a href="https://t.me/+PA8OPL2Zglk3MDM1">ᴍᴏʀᴇ ғɪʟᴇs</a></b> 🤡"""
msg_text = "**📄 File Name:** {}\n**📦 Size:** {}\n\n🔗 [Download Link]({})\n▶️ [Stream Link]({})"



from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, FloodWait
import asyncio
from urllib.parse import quote

@StreamBot.on_message(
    filters.private & (filters.document | filters.video | filters.audio | filters.photo),
    group=4
)
async def private_receive_handler(c: Client, m: Message):
    """Handle private media messages from users."""

    user_id = m.from_user.id
    first_name = m.from_user.first_name or "User"

    # 1. Add new user to database
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id)
        await c.send_message(
            Var.BIN_CHANNEL,
            f"📥 **New User Joined!**\n\n👤 Name: [{first_name}](tg://user?id={user_id}) started your bot."
        )

    # 2. Check updates channel subscription
    if Var.UPDATES_CHANNEL != "None":
        try:
            user = await c.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
            if user.status == "kicked":
                await c.send_message(
                    chat_id=m.chat.id,
                    text=(
                        "🚫 You are banned!\n\n"
                        "📩 **Contact Support:** [Support](https://t.me/bisal_files)"
                    ),
                    disable_web_page_preview=True
                )
                return
        except UserNotParticipant:
            await c.send_photo(
                chat_id=m.chat.id,
                photo="https://telegra.ph/file/5eb253f28ed7ed68cb4e6.png",
                caption=(
                    "<b>👋 Hey there!\n\n"
                    "Please join our updates channel to use me! 😊\n\n"
                    "Due to server overload, only subscribers can use this bot.</b>"
                ),
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton("Join Now 🚩", url=f"https://t.me/{Var.UPDATES_CHANNEL}")
                    ]]
                ),
                parse_mode="html"
            )
            return
        except Exception as e:
            await m.reply_text(str(e))
            await c.send_message(
                chat_id=m.chat.id,
                text="⚠️ **Something went wrong. Contact support:** [Support](https://t.me/bisal_files)",
                disable_web_page_preview=True
            )
            return

    # 3. Check if user is banned
    if await db.is_banned(user_id) is True:
        return await m.reply(Var.BAN_ALERT)

    try:
        # 4. Forward message to bin channel
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        base_url = Var.URL.rstrip("/")
        fid = log_msg.id

        m_name_raw = get_fname(log_msg)
        m_name = m_name_raw.decode("utf-8", errors="replace") if isinstance(m_name_raw, bytes) else str(m_name_raw)
        m_size_hr = humanbytes(get_fsize(log_msg))
        enc_fname = quote(m_name)
        f_hash = get_hash(log_msg)

        stream_link = f"{base_url}/watch/{f_hash}{fid}/{enc_fname}"
        online_link = f"{base_url}/{f_hash}{fid}/{enc_fname}"

        # 5. Log to bin
        await log_msg.reply_text(
            text=(
                f"**📥 Requested by:** [{first_name}](tg://user?id={user_id})\n"
                f"**🆔 User ID:** `{user_id}`\n"
                f"**🔗 Stream Link:** {stream_link}"
            ),
            disable_web_page_preview=True,
            quote=True
        )

        # 6. Send stream/download links to user
        await m.reply_text(
            text=msg_text.format(get_name(log_msg), m_size_hr, online_link, stream_link),
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔺 Stream", url=stream_link),
                    InlineKeyboardButton("🔻 Download", url=online_link)
                ]
            ])
        )

    except FloodWait as e:
        print(f"⚠️ Sleeping for {e.x} seconds due to FloodWait")
        await asyncio.sleep(e.x)
        await c.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=(
                f"⚠️ Got FloodWait of {e.x} seconds from "
                f"[{first_name}](tg://user?id={user_id})\n\n"
                f"🆔 **User ID:** `{user_id}`"
            ),
            disable_web_page_preview=True
        )
        
@StreamBot.on_message(filters.channel & ~filters.group & (filters.document | filters.video | filters.photo)  & ~filters.forwarded, group=-1)
async def channel_receive_handler(bot, broadcast):
    if int(broadcast.chat.id) in Var.BAN_CHNL:
        print("chat trying to get straming link is found in BAN_CHNL,so im not going to give stram link")
        return
    ban_chk = await db.is_banned(int(broadcast.chat.id))
    if (int(broadcast.chat.id) in Var.BANNED_CHANNELS) or (ban_chk == True):
        await bot.leave_chat(broadcast.chat.id)
        return
    try:
        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = f"{Var.URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        online_link = f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        await log_msg.reply_text(
            text=f"**Channel Name:** `{broadcast.chat.title}`\n**CHANNEL ID:** `{broadcast.chat.id}`\n**Rᴇǫᴜᴇsᴛ ᴜʀʟ:** {stream_link}",
            quote=True
        )
        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.id,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("sᴛʀᴇᴀᴍ 🔺", url=stream_link),
                    InlineKeyboardButton('ᴅᴏᴡɴʟᴏᴀᴅ 🔻', url=online_link)] 
                ]
            )
        )
    except FloodWait as w:
        print(f"Sleeping for {str(w.x)}s")
        await asyncio.sleep(w.x)
        await bot.send_message(chat_id=Var.BIN_CHANNEL,
                            text=f"GOT FLOODWAIT OF {str(w.x)}s FROM {broadcast.chat.title}\n\n**CHANNEL ID:** `{str(broadcast.chat.id)}`",
                            disable_web_page_preview=True)
    except Exception as e:
        await bot.send_message(chat_id=Var.BIN_CHANNEL, text=f"**#ERROR_TRACKEBACK:** `{e}`", disable_web_page_preview=True)
        print(f"Cᴀɴ'ᴛ Eᴅɪᴛ Bʀᴏᴀᴅᴄᴀsᴛ Mᴇssᴀɢᴇ!\nEʀʀᴏʀ:  **Give me edit permission in updates and bin Channel!{e}**")

