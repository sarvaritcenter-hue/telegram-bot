# handlers/buyer.py — Qidirish va ko'rish (xaridor)

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from database import search_elon, get_user
from keyboards import (
    qidiruv_tur_kb, qidiruv_amal_kb, skip_kb,
    main_menu_xaridor, main_menu_sotuvchi, pagination_kb,
    elon_inline, REMOVE
)
from states import Qidiruv
from utils import send_elon, is_admin
from config import PAGE_SIZE, ADMIN_IDS

router = Router()

# ========== YORDAMCHI: asosiy menyuga qaytish ==========

async def _asosiy_menyu(msg: Message, state: FSMContext):
    await state.clear()
    user = await get_user(msg.from_user.id)
    rejim = user.get("rejim", "xaridor") if user else "xaridor"
    if rejim == "sotuvchi":
        await msg.answer("🏠 Asosiy menyu", reply_markup=main_menu_sotuvchi())
    else:
        await msg.answer("🏠 Asosiy menyu", reply_markup=main_menu_xaridor())

# ========== TEZKOR KATEGORIYA ==========

@router.message(F.text == "🏠 Uylar")
async def uylar(msg: Message, bot: Bot):
    await _show_category(msg, bot, tur="uy")

@router.message(F.text == "🏢 Joylar")
async def joylar(msg: Message, bot: Bot):
    await _show_category(msg, bot, tur="joy")

@router.message(F.text == "🌿 Yerlar")
async def yerlar(msg: Message, bot: Bot):
    await _show_category(msg, bot, tur="yer")

async def _show_category(msg: Message, bot: Bot, tur: str):
    elonlar = await search_elon(tur=tur, limit=PAGE_SIZE)
    if not elonlar:
        await msg.answer(f"😔 Hozircha bu kategoriyada e'lon yo'q.")
        return
    tur_s = {"uy": "Uylar", "joy": "Joylar", "yer": "Yerlar"}[tur]
    await msg.answer(f"📋 <b>{tur_s}</b> — {len(elonlar)} ta e'lon:")
    uid = msg.from_user.id
    for e in elonlar:
        kb = elon_inline(e["id"], uid, e["user_id"], is_admin(uid))
        await send_elon(bot, msg.chat.id, e, reply_markup=kb)

# ========== QIDIRISH ==========

@router.message(F.text == "🔍 E'lon qidirish")
async def qidiruv_start(msg: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Qidiruv.tur)
    await msg.answer(
        "🔍 <b>E'lon qidirish</b>\n\nQaysi turdagi mulk?",
        reply_markup=qidiruv_tur_kb()
    )

@router.message(StateFilter(Qidiruv.tur), F.text == "🔙 Orqaga")
async def q_tur_orqaga(msg: Message, state: FSMContext):
    await _asosiy_menyu(msg, state)

@router.message(StateFilter(Qidiruv.tur))
async def q_tur(msg: Message, state: FSMContext):
    tur_map = {"🏠 Uy": "uy", "🏢 Joy": "joy", "🌿 Yer": "yer", "🔁 Barchasi": None}
    tur = tur_map.get(msg.text)
    await state.update_data(tur=tur)
    await state.set_state(Qidiruv.amal)
    await msg.answer("💼 Qanday amal?", reply_markup=qidiruv_amal_kb())

@router.message(StateFilter(Qidiruv.amal), F.text == "🔙 Orqaga")
async def q_amal_orqaga(msg: Message, state: FSMContext):
    await state.set_state(Qidiruv.tur)
    await msg.answer("🔍 Qaysi turdagi mulk?", reply_markup=qidiruv_tur_kb())

@router.message(StateFilter(Qidiruv.amal))
async def q_amal(msg: Message, state: FSMContext):
    amal_map = {"💰 Sotish": "sotish", "🔑 Ijara": "ijara", "🔁 Barchasi": None}
    await state.update_data(amal=amal_map.get(msg.text))
    await state.set_state(Qidiruv.shahar)
    await msg.answer(
        "🏙 <b>Shahar / Viloyat</b>:\n"
        "<i>Masalan: Toshkent, Shahrisabz, Samarqand...</i>\n"
        "Hamma joyni qidirish uchun ⏭",
        reply_markup=skip_kb()
    )

@router.message(StateFilter(Qidiruv.shahar), F.text == "🔙 Orqaga")
async def q_shahar_orqaga(msg: Message, state: FSMContext):
    await state.set_state(Qidiruv.amal)
    await msg.answer("💼 Qanday amal?", reply_markup=qidiruv_amal_kb())

@router.message(StateFilter(Qidiruv.shahar))
async def q_shahar(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(shahar=val)
    await state.set_state(Qidiruv.tuman)
    await msg.answer(
        "🗺 <b>Ko'cha / Tuman</b>:\n"
        "<i>Masalan: 9-yo'l, Yunusobod, Bog'ishamol...\n"
        "Yozganingiz tuman, mahalla va manzildan qidiriladi</i>",
        reply_markup=skip_kb()
    )

@router.message(StateFilter(Qidiruv.tuman), F.text == "🔙 Orqaga")
async def q_tuman_orqaga(msg: Message, state: FSMContext):
    await state.set_state(Qidiruv.shahar)
    await msg.answer("🏙 Shahar / Viloyatni kiriting:", reply_markup=skip_kb())

@router.message(StateFilter(Qidiruv.tuman))
async def q_tuman(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(tuman=val)
    await state.set_state(Qidiruv.mahalla)
    await msg.answer(
        "🏘 <b>Mahalla</b>:\n"
        "<i>Masalan: Yashil Diyor, Bog'ishamol...</i>",
        reply_markup=skip_kb()
    )

@router.message(StateFilter(Qidiruv.mahalla), F.text == "🔙 Orqaga")
async def q_mahalla_orqaga(msg: Message, state: FSMContext):
    await state.set_state(Qidiruv.tuman)
    await msg.answer("🗺 Tuman / Ko'chani kiriting:", reply_markup=skip_kb())

@router.message(StateFilter(Qidiruv.mahalla))
async def q_mahalla(msg: Message, state: FSMContext, bot: Bot):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    data = await state.get_data()
    await state.clear()

    elonlar = await search_elon(
        tur=data.get("tur"),
        amal=data.get("amal"),
        shahar=data.get("shahar"),
        tuman=data.get("tuman"),
        mahalla=val,
        limit=PAGE_SIZE
    )

    user = await get_user(msg.from_user.id)
    rejim = user.get("rejim", "xaridor") if user else "xaridor"
    kb = main_menu_sotuvchi() if rejim == "sotuvchi" else main_menu_xaridor()

    if not elonlar:
        await msg.answer(
            "😔 <b>Mos e'lon topilmadi.</b>\n\n"
            "Qidiruv shartlarini kengaytiring yoki boshqa joyni sinab ko'ring.",
            reply_markup=kb
        )
        return

    uid = msg.from_user.id
    await msg.answer(f"✅ <b>{len(elonlar)} ta e'lon topildi:</b>", reply_markup=kb)
    for e in elonlar:
        ikb = elon_inline(e["id"], uid, e["user_id"], is_admin(uid))
        await send_elon(bot, msg.chat.id, e, reply_markup=ikb)

# ========== SO'ROVLAR ==========

@router.message(F.text == "📌 Mening so'rovlarim")
async def mening_sorovlar(msg: Message):
    await msg.answer(
        "📌 <b>So'rovlar</b>\n\n"
        "Bu funksiya tez orada qo'shiladi.\n"
        "Hozircha 🔍 Qidirish orqali e'lonlarni toping."
    )

# ========== ARXIV QIDIRISH (sotilgan/ijaralangan) ==========

@router.message(F.text == "📦 Arxiv")
async def arxiv_start(msg: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Qidiruv.tur)
    await state.update_data(arxiv=True)
    await msg.answer(
        "📦 <b>Arxiv</b> — Sotilgan / Ijaralangan e'lonlar\n\n"
        "Qaysi turdagi mulk?",
        reply_markup=qidiruv_tur_kb()
    )
