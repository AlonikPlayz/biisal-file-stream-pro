from pyrogram import Client
from typing import Any, Optional
from pyrogram.types import Message
from pyrogram.file_id import FileId
from pyrogram.raw.types.messages import Messages
from biisal.server.exceptions import FileNotFound


async def parse_file_id(message: "Message") -> Optional[FileId]:
    media = get_media_from_message(message)
    if media:
        return FileId.decode(media.file_id)

async def parse_file_unique_id(message: "Messages") -> Optional[str]:
    media = get_media_from_message(message)
    if media:
        return media.file_unique_id

async def get_file_ids(client: Client, chat_id: int, id: int) -> Optional[FileId]:
    message = await client.get_messages(chat_id, id)
    if message.empty:
        raise FileNotFound
    media = get_media_from_message(message)
    file_unique_id = await parse_file_unique_id(message)
    file_id = await parse_file_id(message)
    setattr(file_id, "file_size", getattr(media, "file_size", 0))
    setattr(file_id, "mime_type", getattr(media, "mime_type", ""))
    setattr(file_id, "file_name", getattr(media, "file_name", ""))
    setattr(file_id, "unique_id", file_unique_id)
    return file_id

def get_media_from_message(message: "Message") -> Any:
    media_types = (
        "audio",
        "document",
        "photo",
        "sticker",
        "animation",
        "video",
        "voice",
        "video_note",
    )
    for attr in media_types:
        media = getattr(message, attr, None)
        if media:
            return media


def get_hash(media_msg: Message) -> str:
    media = get_media_from_message(media_msg)
    return getattr(media, "file_unique_id", "")[:6]

def get_name(media_msg: Message) -> str:
    media = get_media_from_message(media_msg)
    return getattr(media, 'file_name', "")

def get_media_file_size(m):
    media = get_media_from_message(m)
    return getattr(media, "file_size", 0)

def get_uniqid(message: Message) -> Optional[str]:
    media = get_media(message)
    return getattr(media, 'file_unique_id', None)

def get_fname(msg: Message) -> str:
    media = get_media(msg)
    fname = None
    
    if media:
        fname = getattr(media, 'file_name', None)
    
    if not fname:
        media_type_str = "unknown_media"
        if msg.media:
            media_type_value = msg.media.value
            if media_type_value:
                media_type_str = str(media_type_value)
        
        ext = "bin"
        if media and hasattr(media, '_file_type'):
            file_type = media._file_type
            if file_type == "photo":
                ext = "jpg"
            elif file_type == "audio":
                ext = "mp3"
            elif file_type == "voice":
                ext = "ogg"
            elif file_type in ["video", "animation", "video_note"]:
                ext = "mp4"
            elif fil
