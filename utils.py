# utils.py — Yordamchi funksiyalar

from aiogram import Bot
from aiogram.types import InputMediaPhoto
from config import ADMIN_IDS

TUR_EMOJI = {"uy": "🏠", "joy": "🏢", "yer": "🌿"}
AMAL_EMOJI = {"sotish": "💰", "ijara": "🔑"}

def elon_matn(e: dict, full: bool = True) -> str:
    tur_e  = TUR_EMOJI.get(e["tur"], "🏠")
    amal_e = AMAL_EMOJI.get(e["amal"], "💰")
    amal_s = "Sotish" if e["amal"] == "sotish" else "Ijara"
    tur_s  = {"uy": "Uy", "joy": "Joy", "yer": "Yer"}.get(e["tur"], e["tur"])

    manzil_parts = []
    if e.get("shahar"):  manzil_parts.append(e["shahar"])
    if e.get("tuman"):   manzil_parts.append(e["tuman"])
    if e.get("mahalla"): manzil_parts.append(e["mahalla"])
    if e.get("manzil"):  manzil_parts.append(e["manzil"])
    manzil = ", ".join(manzil_parts)

    text = (
        f"{tur_e} <b>{tur_s} — {amal_e} {amal_s}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 <b>Manzil:</b> {manzil}\n"
    )
    if e.get("maydon"):
        text += f"📐 <b>Maydon:</b> {e['maydon']} m²\n"
    if e.get("xonalar") and e["tur"] != "yer":
        text += f"🛏 <b>Xonalar:</b> {e['xonalar']}\n"
    if e.get("holat") and e["tur"] != "yer":
        text += f"🔧 <b>Holat:</b> {e['holat']}\n"
    if e.get("narx"):
        narx_s = e["narx"]
        if e["amal"] == "ijara":
            narx_s += " / oy"
        text += f"💵 <b>Narx:</b> {narx_s}\n"
    if full:
        if e.get("tavsif"):
            text += f"\n📝 <b>Tavsif:</b> {e['tavsif']}\n"
        text += f"\n📞 <b>Aloqa:</b> {e['telefon']}\n"
        if e.get("username"):
            text += f"👤 @{e['username']}\n"
        if e.get("video_id"):
            text += f"🎥 <i>Video mavjud</i>\n"
        text += f"\n🆔 E'lon #{e['id']}"
        if e.get("lat") and e.get("lon"):
            text += "\n📍 <i>Joylashuv xaritada</i>"
    return text

async def send_elon(bot: Bot, chat_id: int, elon: dict,
                    reply_markup=None, show_location: bool = True):
    """E'lonni rasm/video va lokatsiya bilan yuborish"""
    fotos = elon.get("foto_ids", [])
    video_id = elon.get("video_id")
    text = elon_matn(elon)

    if video_id:
        # Video bor — avval video, keyin lokatsiya
        await bot.send_video(chat_id, video_id, caption=text, reply_markup=reply_markup)
    elif fotos:
        if len(fotos) == 1:
            await bot.send_photo(chat_id, fotos[0], caption=text, reply_markup=reply_markup)
        else:
            media = [InputMediaPhoto(media=f) for f in fotos]
            media[0].caption = text
            await bot.send_media_group(chat_id, media)
            if reply_markup:
                await bot.send_message(chat_id, "☝️ Yuqoridagi e'lon", reply_markup=reply_markup)
    else:
        await bot.send_message(chat_id, text, reply_markup=reply_markup)

    if show_location and elon.get("lat") and elon.get("lon"):
        await bot.send_location(chat_id, latitude=elon["lat"], longitude=elon["lon"])

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS
