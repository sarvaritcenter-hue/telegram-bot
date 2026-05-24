# handlers/common.py — Umumiy komandalar

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from database import get_or_create_user, set_rejim, get_user
from keyboards import (
    rejim_tanlash, main_menu_xaridor, main_menu_sotuvchi, REMOVE
)
from utils import is_admin

router = Router()

# ========== START ==========
@router.message(Command("start"))
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    user = await get_or_create_user(
        msg.from_user.id,
        msg.from_user.username or "",
        msg.from_user.full_name or ""
    )
    if user.get("bloklangan"):
        await msg.answer("⛔️ Siz bloklangansiz. Admin bilan bog'laning.")
        return

    name = msg.from_user.first_name or "Foydalanuvchi"
    await msg.answer(
        f"👋 Assalomu alaykum, <b>{name}</b>!\n\n"
        f"🏠 <b>Uy-Joy Bozori</b>ga xush kelibsiz!\n\n"
        f"Uy, joy va yerlarni:\n"
        f"• 💰 Sotish / 🔑 Ijaraga berish\n"
        f"• 🔍 Qidirish / Ko'rish\n\n"
        f"Quyidagi rejimdan birini tanlang 👇",
        reply_markup=rejim_tanlash()
    )

# ========== REJIM TANLASH ==========
@router.message(F.text == "🛒 Sotib olish / Ijaraga olish")
async def rejim_xaridor(msg: Message, state: FSMContext):
    await state.clear()
    await set_rejim(msg.from_user.id, "xaridor")
    await msg.answer(
        "✅ <b>Xaridor / Ijarachi rejimi</b>\n\n"
        "Endi siz e'lonlarni ko'rishingiz va qidirishingiz mumkin.",
        reply_markup=main_menu_xaridor()
    )

@router.message(F.text == "📢 Sotish / Ijaraga berish")
async def rejim_sotuvchi(msg: Message, state: FSMContext):
    await state.clear()
    await set_rejim(msg.from_user.id, "sotuvchi")
    await msg.answer(
        "✅ <b>Sotuvchi / Ijaraga beruvchi rejimi</b>\n\n"
        "Endi siz e'lon berishingiz mumkin.",
        reply_markup=main_menu_sotuvchi()
    )

# ========== REJIMNI ALMASHTIRISH ==========
@router.message(F.text == "🔄 Rejimni almashtirish")
async def rejim_almashtirish(msg: Message, state: FSMContext):
    await state.clear()
    user = await get_user(msg.from_user.id)
    rejim = user.get("rejim", "xaridor")
    rejim_s = "Xaridor / Ijarachi" if rejim == "xaridor" else "Sotuvchi / Ijaraga beruvchi"
    await msg.answer(
        f"🔄 <b>Rejimni almashtirish</b>\n\n"
        f"Hozirgi rejim: <b>{rejim_s}</b>\n\n"
        f"Qaysi rejimga o'tmoqchisiz?",
        reply_markup=rejim_tanlash()
    )

# ========== ADMIN BILAN BOG'LANISH ==========
@router.message(F.text == "📞 Admin bilan bog'lanish")
async def admin_boglanish(msg: Message):
    await msg.answer(
        "📞 <b>Admin bilan bog'lanish</b>\n\n"
        "Savol, taklif yoki muammo bo'lsa:\n\n"
        "👤 Admin: @master_sarvar\n\n"
        "<i>Ish vaqti: 09:00 — 22:00</i>"
    )


@router.message(F.text == "🔁 Boshlash")
async def qayta_boshlash(msg: Message, state: FSMContext):
    await state.clear()
    user = await get_user(msg.from_user.id)
    rejim = user.get("rejim", "xaridor") if user else "xaridor"
    if rejim == "sotuvchi":
        await msg.answer("🏠 Asosiy menyu", reply_markup=main_menu_sotuvchi())
    else:
        await msg.answer("🏠 Asosiy menyu", reply_markup=main_menu_xaridor())
async def orqaga(msg: Message, state: FSMContext):
    await state.clear()
    user = await get_user(msg.from_user.id)
    rejim = user.get("rejim", "xaridor") if user else "xaridor"
    if rejim == "sotuvchi":
        await msg.answer("🏠 Asosiy menyu", reply_markup=main_menu_sotuvchi())
    else:
        await msg.answer("🏠 Asosiy menyu", reply_markup=main_menu_xaridor())

# ========== SOZLAMALAR ==========
@router.message(F.text == "⚙️ Sozlamalar")
async def sozlamalar(msg: Message):
    user = await get_user(msg.from_user.id)
    rejim = user.get("rejim", "xaridor")
    rejim_s = "🛒 Xaridor / Ijarachi" if rejim == "xaridor" else "📢 Sotuvchi / Ijaraga beruvchi"
    await msg.answer(
        f"⚙️ <b>Sozlamalar</b>\n\n"
        f"👤 ID: <code>{msg.from_user.id}</code>\n"
        f"📛 Ism: {msg.from_user.full_name}\n"
        f"🔧 Rejim: {rejim_s}\n\n"
        f"Rejimni o'zgartirish: 🔄 <b>Rejimni almashtirish</b> tugmasini bosing",
    )

# ========== ID ==========
@router.message(Command("id"))
async def cmd_id(msg: Message):
    await msg.answer(f"🆔 Sizning ID raqamingiz: <code>{msg.from_user.id}</code>")

# ========== YORDAM ==========
@router.message(Command("yordam"))
async def cmd_yordam(msg: Message):
    await msg.answer(
        "📖 <b>Yordam</b>\n\n"
        "🔄 <b>Rejim almashtirish:</b> Sotuvchi ↔ Xaridor\n"
        "🔙 <b>Orqaga:</b> Istalgan vaqtda asosiy menyuga\n"
        "🔍 <b>Qidirish:</b> Shahar, tuman, mahalla bo'yicha\n"
        "📢 <b>E'lon berish:</b> Sotuvchi rejimida\n"
        "📍 <b>Lokatsiya:</b> Telefonda ishlaydi\n"
        "🖼 <b>Rasmlar:</b> 5 tagacha rasm yuborish\n"
        "✅ <b>Sotildi:</b> O'z e'loningizni yopish\n\n"
        "❓ Muammo bo'lsa: /start"
    )
