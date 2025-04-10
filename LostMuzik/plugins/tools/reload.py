#
# Copyright (C) 2021-2023 by LostBots@Github, < https://github.com/LostBots >.
#
# This file is part of < https://github.com/LostBots/LostMuzik > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/LostBots/LostMuzik/blob/master/LICENSE >
#
# All rights reserved.
#

import asyncio

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import CallbackQuery, Message

from config import BANNED_USERS, MUSIC_BOT_NAME, adminlist, lyrical
from strings import get_command
from LostMuzik import app
from LostMuzik.core.call import LostMuzik
from LostMuzik.misc import db
from LostMuzik.utils.database import get_authuser_names, get_cmode
from LostMuzik.utils.decorators import (ActualAdminCB, AdminActual,
                                         language)
from LostMuzik.utils.formatters import alpha_to_int

### Multi-Lang Commands
RELOAD_COMMAND = get_command("RELOAD_COMMAND")
RESTART_COMMAND = get_command("RESTART_COMMAND")


@app.on_message(
    filters.command(RELOAD_COMMAND)
    & filters.group
    & ~BANNED_USERS
)
@language
async def reload_admin_cache(client, message: Message, _):
    try:
        chat_id = message.chat.id
        admins = app.get_chat_members(
            chat_id, filter=ChatMembersFilter.ADMINISTRATORS
        )
        authusers = await get_authuser_names(chat_id)
        adminlist[chat_id] = []
        async for user in admins:
            if user.privileges.can_manage_video_chats:
                adminlist[chat_id].append(user.user.id)
        for user in authusers:
            user_id = await alpha_to_int(user)
            adminlist[chat_id].append(user_id)
        await message.reply_text(_["admin_20"])
    except:
        await message.reply_text(
            "**Yönetici önbelleği yüklenemedi. Botun grubunuzda yönetici olduğundan emin olun.**"
        )


@app.on_message(
    filters.command(RESTART_COMMAND)
    & filters.group
    & ~BANNED_USERS
)
@AdminActual
async def restartbot(client, message: Message, _):
    mystic = await message.reply_text(
        f"**Lütfen Bekleyin.. {MUSIC_BOT_NAME} Yeniden Başlatılıyor...**"
    )
    await asyncio.sleep(1)
    try:
        db[message.chat.id] = []
        await LostMuzik.stop_stream(message.chat.id)
    except:
        pass
    chat_id = await get_cmode(message.chat.id)
    if chat_id:
        try:
            await app.get_chat(chat_id)
        except:
            pass
        try:
            db[chat_id] = []
            await LostMuzik.stop_stream(chat_id)
        except:
            pass
    return await mystic.edit_text(
        "**Bot Başarılı Bir Şekilde Yeniden Başlatıldı..**"
    )


@app.on_callback_query(filters.regex("close") & ~BANNED_USERS)
async def close_menu(_, CallbackQuery):
    try:
        await CallbackQuery.message.delete()
        await CallbackQuery.answer()
    except:
        return


@app.on_callback_query(filters.regex("close") & ~BANNED_USERS)
async def close_menu(_, CallbackQuery):
    try:
        await CallbackQuery.message.delete()
        await CallbackQuery.answer()
    except:
        return


@app.on_callback_query(
    filters.regex("stop_downloading") & ~BANNED_USERS
)
@ActualAdminCB
async def stop_download(client, CallbackQuery: CallbackQuery, _):
    message_id = CallbackQuery.message.message_id
    task = lyrical.get(message_id)
    if not task:
        return await CallbackQuery.answer(
            "İndirme zaten tamamlandı.", show_alert=True
        )
    if task.done() or task.cancelled():
        return await CallbackQuery.answer(
            "İndirme zaten tamamlandı veya iptal edildi.",
            show_alert=True,
        )
    if not task.done():
        try:
            task.cancel()
            try:
                lyrical.pop(message_id)
            except:
                pass
            await CallbackQuery.answer(
                "İndirme iptal edildi.", show_alert=True
            )
            return await CallbackQuery.edit_message_text(
                f"İndirme {CallbackQuery.from_user.mention} tarafından iptal edildi."
            )
        except:
            return await CallbackQuery.answer(
                "İndirme işlemi durdurulamadı.", show_alert=True
            )
    await CallbackQuery.answer(
        "Çalışan görev tanınamadı.", show_alert=True
    )
