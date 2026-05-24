# handlers/seller.py — E'lon berish, o'chirish

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from database import add_elon, get_user_elonlar, deactivate_elon, delete_elon, get_elon
from keyboards import (
    tur_kb, amal_kb, holat_kb, xonalar_kb, skip_kb,
    lokatsiya_kb, foto_yuborib_boldi_kb, tasdiqlash_kb,
    main_menu_sotuvchi, main_menu_xaridor, elon_inline, REMOVE
)
from states import ElonBerish
from utils import send_elon, elon_matn
from config import MAX_ELON_PER_USER, ADMIN_IDS

router = Router()

# ========== E'LON BERISH ==========

@router.message(F.text == "➕ E'lon berish")
async def elon_berish_start(msg: Message, state: FSMContext):
    await state.clear()
    elonlar = await get_user_elonlar(msg.from_user.id)
    faollar = [e for e in elonlar if e["faol"]]
    if len(faollar) >= MAX_ELON_PER_USER:
        await msg.answer(f"⚠️ Maksimal {MAX_ELON_PER_USER} ta faol e'lon. Avval birini o'chiring.")
        return
    await state.set_state(ElonBerish.tur)
    await msg.answer("📢 <b>E'lon berish</b>\n\nQaysi turdagi mulk?", reply_markup=tur_kb())

@router.message(StateFilter(ElonBerish.tur), F.text == "🔙 Orqaga")
async def elon_tur_orqaga(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("🏠 Asosiy menyu", reply_markup=main_menu_sotuvchi())

@router.message(StateFilter(ElonBerish.tur), F.text.in_(["🏠 Uy", "🏢 Joy", "🌿 Yer"]))
async def elon_tur(msg: Message, state: FSMContext):
    tur_map = {"🏠 Uy": "uy", "🏢 Joy": "joy", "🌿 Yer": "yer"}
    await state.update_data(tur=tur_map[msg.text])
    await state.set_state(ElonBerish.amal)
    await msg.answer("💼 Qanday amal?", reply_markup=amal_kb())

@router.message(StateFilter(ElonBerish.amal), F.text == "🔙 Orqaga")
async def elon_amal_orqaga(msg: Message, state: FSMContext):
    await state.set_state(ElonBerish.tur)
    await msg.answer("🏠 Mulk turini tanlang:", reply_markup=tur_kb())

@router.message(StateFilter(ElonBerish.amal), F.text.in_(["💰 Sotish", "🔑 Ijaraga berish"]))
async def elon_amal(msg: Message, state: FSMContext):
    amal_map = {"💰 Sotish": "sotish", "🔑 Ijaraga berish": "ijara"}
    await state.update_data(amal=amal_map[msg.text])
    await state.set_state(ElonBerish.shahar)
    await msg.answer("🏙 <b>Shahar / Viloyat</b>:\n<i>Masalan: Toshkent, Shahrisabz...</i>", reply_markup=REMOVE)

@router.message(StateFilter(ElonBerish.shahar), F.text == "🔙 Orqaga")
async def elon_shahar_orqaga(msg: Message, state: FSMContext):
    await state.set_state(ElonBerish.amal)
    await msg.answer("💼 Qanday amal?", reply_markup=amal_kb())

@router.message(StateFilter(ElonBerish.shahar))
async def elon_shahar(msg: Message, state: FSMContext):
    await state.update_data(shahar=msg.text.strip())
    await state.set_state(ElonBerish.tuman)
    await msg.answer("🗺 <b>Tuman / Ko'cha</b>:\n<i>Masalan: 9-yo'l, Mirzo Ulug'bek...</i>", reply_markup=skip_kb())

@router.message(StateFilter(ElonBerish.tuman), F.text == "🔙 Orqaga")
async def elon_tuman_orqaga(msg: Message, state: FSMContext):
    await state.set_state(ElonBerish.shahar)
    await msg.answer("🏙 Shahar / Viloyatni kiriting:", reply_markup=REMOVE)

@router.message(StateFilter(ElonBerish.tuman))
async def elon_tuman(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(tuman=val)
    await state.set_state(ElonBerish.mahalla)
    await msg.answer("🏘 <b>Mahalla</b> nomini kiriting:", reply_markup=skip_kb())

@router.message(StateFilter(ElonBerish.mahalla), F.text == "🔙 Orqaga")
async def elon_mahalla_orqaga(msg: Message, state: FSMContext):
    await state.set_state(ElonBerish.tuman)
    await msg.answer("🗺 Tuman / Ko'chani kiriting:", reply_markup=skip_kb())

@router.message(StateFilter(ElonBerish.mahalla))
async def elon_mahalla(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(mahalla=val)
    await state.set_state(ElonBerish.manzil)
    await msg.answer("📝 <b>Qo'shimcha manzil</b>:", reply_markup=skip_kb())

@router.message(StateFilter(ElonBerish.manzil), F.text == "🔙 Orqaga")
async def elon_manzil_orqaga(msg: Message, state: FSMContext):
    await state.set_state(ElonBerish.mahalla)
    await msg.answer("🏘 Mahalla nomini kiriting:", reply_markup=skip_kb())

@router.message(StateFilter(ElonBerish.manzil))
async def elon_manzil(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(manzil=val)
    await state.set_state(ElonBerish.lokatsiya)
    await msg.answer(
        "📍 <b>Joylashuv (lokatsiya)</b>\n\nTelefonda: 📎 → Lokatsiya\nYoki o'tkazib yuborishingiz mumkin.",
        reply_markup=lokatsiya_kb()
    )

@router.message(StateFilter(ElonBerish.lokatsiya), F.location)
async def elon_lokatsiya(msg: Message, state: FSMContext):
    await state.update_data(lat=msg.location.latitude, lon=msg.location.longitude)
    await _so_maydon(msg, state)

@router.message(StateFilter(ElonBerish.lokatsiya), F.text == "🔙 Orqaga")
async def elon_lokatsiya_orqaga(msg: Message, state: FSMContext):
    await state.set_state(ElonBerish.manzil)
    await msg.answer("📝 Qo'shimcha manzil:", reply_markup=skip_kb())

@router.message(StateFilter(ElonBerish.lokatsiya), F.text == "⏭ O'tkazib yuborish")
async def elon_lokatsiya_skip(msg: Message, state: FSMContext):
    await _so_maydon(msg, state)

async def _so_maydon(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.set_state(ElonBerish.maydon)
    birlik = "sotix yoki m²" if data.get("tur") == "yer" else "m²"
    await msg.answer(f"📐 <b>Maydon</b>ni kiriting ({birlik}):", reply_markup=skip_kb())

@router.message(StateFilter(ElonBerish.maydon), F.text == "🔙 Orqaga")
async def elon_maydon_orqaga(msg: Message, state: FSMContext):
    await state.set_state(ElonBerish.lokatsiya)
    await msg.answer("📍 Lokatsiyani yuboring:", reply_markup=lokatsiya_kb())

@router.message(StateFilter(ElonBerish.maydon))
async def elon_maydon(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(maydon=val)
    data = await state.get_data()
    if data.get("tur") == "yer":
        await state.set_state(ElonBerish.narx)
        await msg.answer("💵 <b>Narx</b>ini kiriting:", reply_markup=REMOVE)
    else:
        await state.set_state(ElonBerish.xonalar)
        await msg.answer("🛏 <b>Xonalar soni</b>:", reply_markup=xonalar_kb())

@router.message(StateFilter(ElonBerish.xonalar), F.text == "🔙 Orqaga")
async def elon_xonalar_orqaga(msg: Message, state: FSMContext):
    await state.set_state(ElonBerish.maydon)
    await msg.answer("📐 Maydonni kiriting:", reply_markup=skip_kb())

@router.message(StateFilter(ElonBerish.xonalar))
async def elon_xonalar(msg: Message, state: FSMContext):
    await state.update_data(xonalar=msg.text.strip())
    await state.set_state(ElonBerish.holat)
    await msg.answer("🔧 <b>Holati</b>:", reply_markup=holat_kb())

@router.message(StateFilter(ElonBerish.holat), F.text == "🔙 Orqaga")
async def elon_holat_orqaga(msg: Message, state: FSMContext):
    await state.set_state(ElonBerish.xonalar)
    await msg.answer("🛏 Xonalar soni:", reply_markup=xonalar_kb())

@router.message(StateFilter(ElonBerish.holat))
async def elon_holat(msg: Message, state: FSMContext):
    await state.update_data(holat=msg.text.strip())
    await state.set_state(ElonBerish.narx)
    data = await state.get_data()
    label = "Ijara narxi (oylik, USD)" if data.get("amal") == "ijara" else "Sotuv narxi (USD)"
    await msg.answer(f"💵 <b>{label}</b>:", reply_markup=REMOVE)

@router.message(StateFilter(ElonBerish.narx), F.text == "🔙 Orqaga")
async def elon_narx_orqaga(msg: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("tur") == "yer":
        await state.set_state(ElonBerish.maydon)
        await msg.answer("📐 Maydonni kiriting:", reply_markup=skip_kb())
    else:
        await state.set_state(ElonBerish.holat)
        await msg.answer("🔧 Holatni tanlang:", reply_markup=holat_kb())

@router.message(StateFilter(ElonBerish.narx))
async def elon_narx(msg: Message, state: FSMContext):
    await state.update_data(narx=msg.text.strip())
    await state.set_state(ElonBerish.telefon)
    await msg.answer("📞 <b>Telefon raqam</b>:\n<i>+998 90 123 45 67</i>", reply_markup=REMOVE)

@router.message(StateFilter(ElonBerish.telefon), F.text == "🔙 Orqaga")
async def elon_telefon_orqaga(msg: Message, state: FSMContext):
    await state.set_state(ElonBerish.narx)
    await msg.answer("💵 Narxni kiriting:", reply_markup=REMOVE)

@router.message(StateFilter(ElonBerish.telefon))
async def elon_telefon(msg: Message, state: FSMContext):
    await state.update_data(telefon=msg.text.strip())
    await state.set_state(ElonBerish.tavsif)
    await msg.answer("📝 <b>Qisqacha tavsif</b>:", reply_markup=skip_kb())

@router.message(StateFilter(ElonBerish.tavsif), F.text == "🔙 Orqaga")
async def elon_tavsif_orqaga(msg: Message, state: FSMContext):
    await state.set_state(ElonBerish.telefon)
    await msg.answer("📞 Telefon raqamni kiriting:", reply_markup=REMOVE)

@router.message(StateFilter(ElonBerish.tavsif))
async def elon_tavsif(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(tavsif=val, foto_ids=[], video_id=None)
    await state.set_state(ElonBerish.foto)
    await msg.answer(
        "🖼🎥 <b>Rasm yoki qisqa video</b> (ixtiyoriy, 5 tagacha rasm)\n\n"
        "📸 Rasm yuboring\n"
        "🎥 Qisqa video yuboring (max 50MB)\n\n"
        "Tugagach ✅ bosing.",
        reply_markup=foto_yuborib_boldi_kb()
    )

@router.message(StateFilter(ElonBerish.foto), F.photo)
async def elon_foto(msg: Message, state: FSMContext):
    data = await state.get_data()
    fotos = data.get("foto_ids", [])
    if len(fotos) < 5:
        fotos.append(msg.photo[-1].file_id)
        await state.update_data(foto_ids=fotos)
        await msg.answer(f"✅ Rasm qabul qilindi ({len(fotos)}/5)", reply_markup=foto_yuborib_boldi_kb())
    else:
        await msg.answer("⚠️ Maksimal 5 ta rasm.")

@router.message(StateFilter(ElonBerish.foto), F.video)
async def elon_video(msg: Message, state: FSMContext):
    await state.update_data(video_id=msg.video.file_id)
    await msg.answer("🎥 Video qabul qilindi!", reply_markup=foto_yuborib_boldi_kb())

@router.message(StateFilter(ElonBerish.foto), F.text == "🔙 Orqaga")
async def elon_foto_orqaga(msg: Message, state: FSMContext):
    await state.set_state(ElonBerish.tavsif)
    await msg.answer("📝 Tavsif kiriting:", reply_markup=skip_kb())

@router.message(StateFilter(ElonBerish.foto),
                F.text.in_(["✅ Tayyor, davom etish", "⏭ Fotosiz davom etish"]))
async def elon_foto_tayyor(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.set_state(ElonBerish.tasdiq)
    preview_data = {**data, "id": "yangi", "username": msg.from_user.username}
    preview_text = elon_matn(preview_data) + "\n\n<i>Ma'lumotlar to'g'rimi?</i>"
    await msg.answer(preview_text, reply_markup=tasdiqlash_kb())

@router.message(StateFilter(ElonBerish.tasdiq), F.text == "✅ Tasdiqlash va e'lon berish")
async def elon_tasdiq(msg: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()
    elon_data = {**data, "user_id": msg.from_user.id,
                 "username": msg.from_user.username or "",
                 "full_name": msg.from_user.full_name or ""}
    elon_id = await add_elon(elon_data)

    # Foydalanuvchiga xabar
    await msg.answer(
        f"✅ <b>E'loningiz qabul qilindi!</b>\n"
        f"🆔 E'lon #{elon_id}\n\n"
        f"⏳ Admin ko'rib chiqgach, e'loningiz e'lon taxtasida ko'rinadi.",
        reply_markup=main_menu_sotuvchi()
    )

    # Adminga yuborish
    from utils import elon_matn, send_elon
    elon = await __import__('database').get_elon(elon_id)
    if elon:
        moderation_kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ma'qul", callback_data=f"approve_{elon_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{elon_id}"),
            ]
        ])
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    f"🔔 <b>Yangi e'lon #{elon_id} — tekshirish kutilmoqda</b>\n\n"
                    f"👤 Foydalanuvchi: {msg.from_user.full_name} "
                    f"(@{msg.from_user.username or 'username yoq'})\n"
                    f"🆔 ID: <code>{msg.from_user.id}</code>"
                )
                await send_elon(bot, admin_id, elon, reply_markup=moderation_kb, show_location=True)
            except:
                pass

@router.message(StateFilter(ElonBerish.tasdiq), F.text == "✏️ Qaytadan to'ldirish")
async def elon_qaytadan(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("🔄 Qaytadan: '➕ E'lon berish'", reply_markup=main_menu_sotuvchi())

@router.message(StateFilter(ElonBerish.tasdiq), F.text == "❌ Bekor qilish")
async def elon_bekor(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Bekor qilindi.", reply_markup=main_menu_sotuvchi())

# ========== MENING E'LONLARIM ==========

@router.message(F.text.in_(["📋 Mening e'lonlarim", "/mening_elon"]))
async def mening_elonlar(msg: Message, bot: Bot):
    elonlar = await get_user_elonlar(msg.from_user.id)
    if not elonlar:
        await msg.answer("📭 Sizda hali e'lon yo'q.")
        return
    faollar = [e for e in elonlar if e["faol"]]
    yopilgan = [e for e in elonlar if not e["faol"]]
    await msg.answer(
        f"📋 <b>Mening e'lonlarim</b>\n\n✅ Faol: {len(faollar)} ta\n🔴 Yopilgan: {len(yopilgan)} ta"
    )
    for e in faollar[:5]:
        kb = elon_inline(e["id"], msg.from_user.id, e["user_id"])
        await send_elon(bot, msg.chat.id, e, reply_markup=kb)

# ========== SOTILDI ==========

@router.callback_query(F.data.startswith("sold_"))
async def elon_sotildi(call: CallbackQuery):
    elon_id = int(call.data.split("_")[1])
    elon = await get_elon(elon_id)
    if not elon:
        await call.answer("E'lon topilmadi", show_alert=True); return
    if elon["user_id"] != call.from_user.id and call.from_user.id not in ADMIN_IDS:
        await call.answer("Ruxsat yo'q", show_alert=True); return
    await deactivate_elon(elon_id, holati="sotildi")
    try:
        await call.message.edit_text(call.message.text + "\n\n✅ <b>SOTILDI / IJARALANDI</b>")
    except:
        pass
    await call.answer("✅ E'lon yopildi!")

# ========== O'CHIRISH (serverdan to'liq) ==========

@router.callback_query(F.data.startswith("del_"))
async def elon_ochir(call: CallbackQuery):
    elon_id = int(call.data.split("_")[1])
    elon = await get_elon(elon_id)
    if not elon:
        await call.answer("E'lon topilmadi", show_alert=True); return
    if elon["user_id"] != call.from_user.id and call.from_user.id not in ADMIN_IDS:
        await call.answer("Ruxsat yo'q", show_alert=True); return

    # Foydalanuvchi o'zi o'chirsa — serverdan to'liq o'chadi
    if call.from_user.id not in ADMIN_IDS:
        await delete_elon(elon_id, call.from_user.id)
    else:
        await delete_elon(elon_id)

    try:
        await call.message.edit_text("🗑 <b>E'lon o'chirildi (serverdan ham)</b>")
    except:
        pass
    await call.answer("🗑 Serverdan o'chirildi!")
