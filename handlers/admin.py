# handlers/admin.py — Admin panel

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from database import (
    get_stats, get_all_users, block_user,
    search_elon, deactivate_elon, add_reklama
)
from keyboards import admin_menu_kb, REMOVE
from states import AdminReklama, AdminBlock
from utils import send_elon
from config import ADMIN_IDS, PAGE_SIZE

router = Router()

# ========== ADMIN MENYU ==========

@router.message(Command("admin"))
async def cmd_admin(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        await msg.answer(
            "⛔️ Ruxsat yo'q.\n\n"
            f"Sizning ID: <code>{msg.from_user.id}</code>"
        )
        return
    await msg.answer("🔑 <b>Admin panel</b>", reply_markup=admin_menu_kb())

# ========== STATISTIKA ==========

@router.callback_query(F.data == "adm_stat")
async def adm_stat(call: CallbackQuery):
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("Ruxsat yo'q", show_alert=True); return
    stats = await get_stats()
    await call.message.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{stats['users']}</b>\n\n"
        f"📋 E'lonlar:\n"
        f"  ✅ Faol: <b>{stats['faol']}</b>\n"
        f"  📦 Jami: <b>{stats['jami']}</b>\n\n"
        f"Turlari:\n"
        f"  🏠 Uylar: <b>{stats['uylar']}</b>\n"
        f"  🏢 Joylar: <b>{stats['joylar']}</b>\n"
        f"  🌿 Yerlar: <b>{stats['yerlar']}</b>"
    )
    await call.answer()

# ========== FOYDALANUVCHILAR ==========

@router.callback_query(F.data == "adm_users")
async def adm_users(call: CallbackQuery):
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("Ruxsat yo'q", show_alert=True); return
    users = await get_all_users()
    if not users:
        await call.message.answer("Foydalanuvchilar yo'q.")
        await call.answer(); return
    matn = f"👥 <b>Foydalanuvchilar ({len(users)} ta):</b>\n\n"
    for u in users[:30]:
        username = f"@{u['username']}" if u.get('username') else "—"
        rejim = "🛒" if u.get("rejim") == "xaridor" else "📢"
        matn += f"{rejim} <code>{u['user_id']}</code> {username} — {u.get('full_name','')}\n"
    await call.message.answer(matn)
    await call.answer()

# ========== BLOKLASH ==========

@router.callback_query(F.data == "adm_block")
async def adm_block_start(call: CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("Ruxsat yo'q", show_alert=True); return
    await state.set_state(AdminBlock.user_id)
    await call.message.answer(
        "👤 <b>Bloklash / Blokdan chiqarish</b>\n\n"
        "Foydalanuvchi ID kiriting:\n"
        "<i>Bloklash: 12345678\nBlokdan chiqarish: -12345678</i>",
        reply_markup=REMOVE
    )
    await call.answer()

@router.message(StateFilter(AdminBlock.user_id))
async def adm_block_exec(msg: Message, state: FSMContext, bot: Bot):
    if msg.from_user.id not in ADMIN_IDS:
        await state.clear(); return
    try:
        user_id_str = msg.text.strip()
        bloklash = not user_id_str.startswith("-")
        user_id = int(user_id_str.lstrip("-"))
        await block_user(user_id, 1 if bloklash else 0)
        await state.clear()
        if bloklash:
            await msg.answer(f"🚫 <code>{user_id}</code> bloklandi.")
            try: await bot.send_message(user_id, "⛔️ Siz botdan bloklangansiz.")
            except: pass
        else:
            await msg.answer(f"✅ <code>{user_id}</code> blokdan chiqarildi.")
            try: await bot.send_message(user_id, "✅ Blokingiz olib tashlandi. /start bosing.")
            except: pass
    except ValueError:
        await msg.answer("❌ Noto'g'ri format. Raqam kiriting.")

# ========== BARCHA E'LONLAR ==========

@router.callback_query(F.data == "adm_elonlar")
async def adm_elonlar(call: CallbackQuery, bot: Bot):
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("Ruxsat yo'q", show_alert=True); return
    elonlar = await search_elon(limit=10)
    if not elonlar:
        await call.message.answer("E'lonlar yo'q.")
        await call.answer(); return
    await call.message.answer(f"📋 <b>So'nggi {len(elonlar)} ta e'lon:</b>")
    from keyboards import elon_inline
    for e in elonlar:
        kb = elon_inline(e["id"], call.from_user.id, e["user_id"], True)
        await send_elon(bot, call.message.chat.id, e, reply_markup=kb)
    await call.answer()

# ========== REKLAMA ==========

def reklama_tur_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Matnli", callback_data="rek_matn")],
        [InlineKeyboardButton(text="🖼 Rasmli", callback_data="rek_rasm")],
        [InlineKeyboardButton(text="🎥 Videoli", callback_data="rek_video")],
        [InlineKeyboardButton(text="🎥📝 Video + Matn", callback_data="rek_video_matn")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="rek_bekor")],
    ])

def tasdiqlash_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Yuborish", callback_data="rek_yuborish")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="rek_bekor")],
    ])

@router.callback_query(F.data == "adm_reklama")
async def adm_reklama_start(call: CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("Ruxsat yo'q", show_alert=True); return
    await state.set_state(AdminReklama.tur)
    await call.message.answer(
        "📢 <b>Reklama yuborish</b>\n\nReklama turini tanlang:",
        reply_markup=reklama_tur_kb()
    )
    await call.answer()

# --- Matnli ---
@router.callback_query(F.data == "rek_matn", StateFilter(AdminReklama.tur))
async def rek_matnli(call: CallbackQuery, state: FSMContext):
    await state.update_data(tur="matn", media_id=None)
    await state.set_state(AdminReklama.matn)
    await call.message.answer("✏️ Reklama matnini kiriting:")
    await call.answer()

# --- Rasmli ---
@router.callback_query(F.data == "rek_rasm", StateFilter(AdminReklama.tur))
async def rek_rasmli(call: CallbackQuery, state: FSMContext):
    await state.update_data(tur="rasm")
    await state.set_state(AdminReklama.foto)
    await call.message.answer("🖼 Reklama rasmini yuboring:")
    await call.answer()

# --- Videoli (faqat video) ---
@router.callback_query(F.data == "rek_video", StateFilter(AdminReklama.tur))
async def rek_videoli(call: CallbackQuery, state: FSMContext):
    await state.update_data(tur="video")
    await state.set_state(AdminReklama.foto)
    await call.message.answer("🎥 Reklama videosini yuboring:")
    await call.answer()

# --- Video + Matn ---
@router.callback_query(F.data == "rek_video_matn", StateFilter(AdminReklama.tur))
async def rek_video_matnli(call: CallbackQuery, state: FSMContext):
    await state.update_data(tur="video_matn")
    await state.set_state(AdminReklama.foto)
    await call.message.answer("🎥 Avval videoni yuboring, keyin matn so'rayman:")
    await call.answer()

# --- Media qabul qilish (rasm yoki video) ---
@router.message(StateFilter(AdminReklama.foto), F.photo)
async def rek_foto_qabul(msg: Message, state: FSMContext):
    await state.update_data(media_id=msg.photo[-1].file_id)
    await state.set_state(AdminReklama.matn)
    await msg.answer("✏️ Endi reklama matnini kiriting:")

@router.message(StateFilter(AdminReklama.foto), F.video)
async def rek_video_qabul(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(media_id=msg.video.file_id)
    if data.get("tur") == "video":
        # Faqat video, matn shart emas
        await state.update_data(matn="")
        await state.set_state(AdminReklama.tasdiqlash)
        await msg.answer(
            "🎥 Video qabul qilindi!\n\n"
            "Matn qo'shmoqchimisiz?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✏️ Matn qo'shish", callback_data="rek_matn_qosh")],
                [InlineKeyboardButton(text="✅ Matnsiz yuborish", callback_data="rek_yuborish")],
                [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="rek_bekor")],
            ])
        )
    else:
        await state.set_state(AdminReklama.matn)
        await msg.answer("✏️ Endi reklama matnini kiriting:")

@router.callback_query(F.data == "rek_matn_qosh")
async def rek_matn_qosh(call: CallbackQuery, state: FSMContext):
    await state.set_state(AdminReklama.matn)
    await call.message.answer("✏️ Matnni kiriting:")
    await call.answer()

# --- Matn qabul qilish ---
@router.message(StateFilter(AdminReklama.matn))
async def rek_matn_qabul(msg: Message, state: FSMContext):
    await state.update_data(matn=msg.text.strip())
    await state.set_state(AdminReklama.tasdiqlash)
    data = await state.get_data()

    tur_s = {"matn": "📝 Matnli", "rasm": "🖼 Rasmli",
             "video": "🎥 Videoli", "video_matn": "🎥📝 Video+Matn"}.get(data.get("tur"), "")
    await msg.answer(
        f"📢 <b>Reklama tayyorlandi</b>\n\n"
        f"Tur: {tur_s}\n"
        f"Matn: {data.get('matn', '—')[:100]}\n\n"
        f"Tasdiqlaysizmi?",
        reply_markup=tasdiqlash_kb()
    )

# --- Yuborish ---
@router.callback_query(F.data == "rek_yuborish")
async def rek_yuborish(call: CallbackQuery, state: FSMContext, bot: Bot):
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("Ruxsat yo'q", show_alert=True); return
    data = await state.get_data()
    await state.clear()

    users = await get_all_users()
    yuborilgan = 0
    xato = 0

    status_msg = await call.message.answer(f"📤 Yuborilmoqda... (0/{len(users)})")

    for i, user in enumerate(users):
        try:
            uid = user["user_id"]
            matn = data.get("matn", "")
            media_id = data.get("media_id")
            tur = data.get("tur", "matn")
            caption = f"📢 <b>Reklama</b>\n\n{matn}" if matn else "📢 <b>Reklama</b>"

            if tur == "matn":
                await bot.send_message(uid, caption)
            elif tur == "rasm":
                await bot.send_photo(uid, media_id, caption=caption)
            elif tur in ("video", "video_matn"):
                await bot.send_video(uid, media_id, caption=caption if matn else None)

            yuborilgan += 1
        except:
            xato += 1

        if (i + 1) % 20 == 0:
            try:
                await status_msg.edit_text(f"📤 Yuborilmoqda... ({i+1}/{len(users)})")
            except:
                pass

    await add_reklama(data.get("matn", ""), data.get("media_id"))
    await status_msg.edit_text(
        f"✅ <b>Reklama yuborildi!</b>\n\n"
        f"✅ Muvaffaqiyatli: {yuborilgan}\n"
        f"❌ Xato: {xato}"
    )
    await call.answer()

# --- Bekor qilish ---
@router.callback_query(F.data == "rek_bekor")
async def rek_bekor(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Reklama bekor qilindi.")
    await call.answer()
