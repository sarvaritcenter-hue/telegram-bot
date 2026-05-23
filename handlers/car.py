# handlers/car.py — Mashina sotish va qidirish

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from database import (
    add_mashina, get_mashina, search_mashina,
    get_user_mashinalar, delete_mashina, deactivate_mashina, get_user
)
from keyboards import (
    skip_kb, foto_yuborib_boldi_kb, main_menu_sotuvchi,
    main_menu_xaridor, REMOVE
)
from states import MashinaElon, MashinaQidiruv
from utils import is_admin
from config import ADMIN_IDS

router = Router()

# ===== YORDAMCHI FUNKSIYALAR =====

def mashina_matn(m: dict, full: bool = True) -> str:
    urish_s = f"\n🔨 <b>Urilgan joy:</b> {m['urish']}" if m.get("urish") else ""
    navorot_s = f"\n🔧 <b>Navorotlar:</b> {m['navorot']}" if m.get("navorot") else ""
    petno_s = "✅ Bor" if m.get("petno") == "ha" else "❌ Yo'q"

    text = (
        f"🚗 <b>{m['marka']} {m.get('model', '')}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
    )
    if m.get("yil"):       text += f"📅 <b>Yil:</b> {m['yil']}\n"
    if m.get("rang"):      text += f"🎨 <b>Rang:</b> {m['rang']}\n"
    if m.get("probeg"):    text += f"🛣 <b>Probeg:</b> {m['probeg']} km\n"
    if m.get("dvigatel"):  text += f"⚙️ <b>Dvigatel:</b> {m['dvigatel']} L\n"
    if m.get("uzatma"):    text += f"🔁 <b>Uzatma qutisi:</b> {m['uzatma']}\n"
    if m.get("yoqilgi"):   text += f"⛽ <b>Yoqilg'i:</b> {m['yoqilgi']}\n"
    if m.get("holat"):     text += f"🚘 <b>Holat:</b> {m['holat']}\n"
    text += f"{urish_s}"
    text += f"{navorot_s}"
    text += f"\n📋 <b>Petnos:</b> {petno_s}\n"
    if m.get("shahar"):    text += f"📍 <b>Shahar:</b> {m['shahar']}\n"
    text += f"💵 <b>Narx:</b> {m['narx']}\n"
    if full:
        if m.get("tavsif"): text += f"\n📝 <b>Tavsif:</b> {m['tavsif']}\n"
        text += f"\n📞 <b>Aloqa:</b> {m['telefon']}\n"
        if m.get("username"): text += f"👤 @{m['username']}\n"
        if m.get("video_id"): text += f"🎥 <i>Video mavjud</i>\n"
        text += f"\n🆔 Mashina #{m['id']}"
    return text

def mashina_inline(mid: int, uid: int, owner_id: int, admin: bool = False):
    if admin or uid == owner_id:
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Sotildi", callback_data=f"car_sold_{mid}"),
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"car_del_{mid}"),
        ]])
    return None

async def send_mashina(bot: Bot, chat_id: int, m: dict, reply_markup=None):
    fotos = m.get("foto_ids", [])
    video_id = m.get("video_id")
    text = mashina_matn(m)
    from aiogram.types import InputMediaPhoto
    if video_id:
        await bot.send_video(chat_id, video_id, caption=text, reply_markup=reply_markup)
    elif fotos:
        if len(fotos) == 1:
            await bot.send_photo(chat_id, fotos[0], caption=text, reply_markup=reply_markup)
        else:
            media = [InputMediaPhoto(media=f) for f in fotos]
            media[0].caption = text
            await bot.send_media_group(chat_id, media)
            if reply_markup:
                await bot.send_message(chat_id, "☝️ Yuqoridagi mashina", reply_markup=reply_markup)
    else:
        await bot.send_message(chat_id, text, reply_markup=reply_markup)

# ===== ASOSIY MENYUDAN KIRISH =====

@router.message(F.text == "🚗 Mashinalar")
async def mashinalar_menu(msg: Message):
    await msg.answer(
        "🚗 <b>Mashinalar bo'limi</b>\n\n"
        "Nima qilmoqchisiz?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Mashina qidirish", callback_data="car_search")],
            [InlineKeyboardButton(text="➕ Mashina sotish", callback_data="car_add")],
            [InlineKeyboardButton(text="📋 Mening mashinalarim", callback_data="car_my")],
        ])
    )

@router.callback_query(F.data == "car_add")
async def car_add_start(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(MashinaElon.marka)
    await call.message.answer(
        "🚗 <b>Mashina e'loni berish</b>\n\n"
        "Mashina <b>markasini</b> kiriting:\n"
        "<i>Masalan: Chevrolet, BMW, Toyota, Nexia...</i>",
        reply_markup=REMOVE
    )
    await call.answer()

@router.callback_query(F.data == "car_search")
async def car_search_start(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(MashinaQidiruv.marka)
    await call.message.answer(
        "🔍 <b>Mashina qidirish</b>\n\n"
        "Marka yoki model kiriting:\n"
        "<i>Masalan: Cobalt, BMW, Nexia...</i>\n"
        "Barchasi uchun ⏭",
        reply_markup=skip_kb()
    )
    await call.answer()

@router.callback_query(F.data == "car_my")
async def car_my(call: CallbackQuery, bot: Bot):
    mashinalar = await get_user_mashinalar(call.from_user.id)
    faol = [m for m in mashinalar if m["faol"]]
    if not faol:
        await call.message.answer("📭 Sizda mashina e'loni yo'q.")
        await call.answer(); return
    await call.message.answer(f"📋 <b>Mening mashinalarim</b> — {len(faol)} ta:")
    for m in faol[:5]:
        kb = mashina_inline(m["id"], call.from_user.id, m["user_id"])
        await send_mashina(bot, call.message.chat.id, m, reply_markup=kb)
    await call.answer()

# ===== E'LON BERISH BOSQICHLARI =====

def skip_or_back_kb(back_text="🔙 Orqaga"):
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="⏭ O'tkazib yuborish")],
        [KeyboardButton(text=back_text)],
    ], resize_keyboard=True, one_time_keyboard=True)

def choice_kb(choices: list, back: bool = True):
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    rows = [[KeyboardButton(text=c) for c in choices[i:i+2]] for i in range(0, len(choices), 2)]
    if back:
        rows.append([KeyboardButton(text="🔙 Orqaga")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, one_time_keyboard=True)

# Marka
@router.message(StateFilter(MashinaElon.marka), F.text == "🔙 Orqaga")
async def car_marka_orqaga(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("🏠 Asosiy menyu", reply_markup=main_menu_sotuvchi())

@router.message(StateFilter(MashinaElon.marka))
async def car_marka(msg: Message, state: FSMContext):
    await state.update_data(marka=msg.text.strip())
    await state.set_state(MashinaElon.model)
    await msg.answer("🚗 <b>Model</b>ni kiriting:\n<i>Masalan: Cobalt, 3 seriya, Camry...</i>",
                     reply_markup=skip_or_back_kb())

# Model
@router.message(StateFilter(MashinaElon.model), F.text == "🔙 Orqaga")
async def car_model_orqaga(msg: Message, state: FSMContext):
    await state.set_state(MashinaElon.marka)
    await msg.answer("🚗 Markani kiriting:", reply_markup=REMOVE)

@router.message(StateFilter(MashinaElon.model))
async def car_model(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(model=val)
    await state.set_state(MashinaElon.yil)
    await msg.answer("📅 <b>Ishlab chiqarilgan yil</b>:\n<i>Masalan: 2018, 2021...</i>",
                     reply_markup=skip_or_back_kb())

# Yil
@router.message(StateFilter(MashinaElon.yil), F.text == "🔙 Orqaga")
async def car_yil_orqaga(msg: Message, state: FSMContext):
    await state.set_state(MashinaElon.model)
    await msg.answer("🚗 Modelni kiriting:", reply_markup=skip_or_back_kb())

@router.message(StateFilter(MashinaElon.yil))
async def car_yil(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(yil=val)
    await state.set_state(MashinaElon.rang)
    await msg.answer("🎨 <b>Rang</b>:\n<i>Masalan: Oq, Qora, Kumush, Qizil...</i>",
                     reply_markup=choice_kb(["Oq", "Qora", "Kumush", "Qizil", "Ko'k", "Boshqa"]))

# Rang
@router.message(StateFilter(MashinaElon.rang), F.text == "🔙 Orqaga")
async def car_rang_orqaga(msg: Message, state: FSMContext):
    await state.set_state(MashinaElon.yil)
    await msg.answer("📅 Yilni kiriting:", reply_markup=skip_or_back_kb())

@router.message(StateFilter(MashinaElon.rang))
async def car_rang(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(rang=val)
    await state.set_state(MashinaElon.probeg)
    await msg.answer("🛣 <b>Probeg</b> (km):\n<i>Masalan: 45000, 120000...</i>",
                     reply_markup=skip_or_back_kb())

# Probeg
@router.message(StateFilter(MashinaElon.probeg), F.text == "🔙 Orqaga")
async def car_probeg_orqaga(msg: Message, state: FSMContext):
    await state.set_state(MashinaElon.rang)
    await msg.answer("🎨 Rangni tanlang:", reply_markup=choice_kb(["Oq", "Qora", "Kumush", "Qizil", "Ko'k", "Boshqa"]))

@router.message(StateFilter(MashinaElon.probeg))
async def car_probeg(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(probeg=val)
    await state.set_state(MashinaElon.dvigatel)
    await msg.answer("⚙️ <b>Dvigatel hajmi</b> (litr):\n<i>Masalan: 1.5, 2.0, 3.5...</i>",
                     reply_markup=skip_or_back_kb())

# Dvigatel
@router.message(StateFilter(MashinaElon.dvigatel), F.text == "🔙 Orqaga")
async def car_dvigatel_orqaga(msg: Message, state: FSMContext):
    await state.set_state(MashinaElon.probeg)
    await msg.answer("🛣 Probegni kiriting:", reply_markup=skip_or_back_kb())

@router.message(StateFilter(MashinaElon.dvigatel))
async def car_dvigatel(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(dvigatel=val)
    await state.set_state(MashinaElon.uzatma)
    await msg.answer("🔁 <b>Uzatma qutisi</b>:",
                     reply_markup=choice_kb(["Mexanik", "Avtomat", "Variator", "Robot"]))

# Uzatma
@router.message(StateFilter(MashinaElon.uzatma), F.text == "🔙 Orqaga")
async def car_uzatma_orqaga(msg: Message, state: FSMContext):
    await state.set_state(MashinaElon.dvigatel)
    await msg.answer("⚙️ Dvigatel hajmini kiriting:", reply_markup=skip_or_back_kb())

@router.message(StateFilter(MashinaElon.uzatma))
async def car_uzatma(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(uzatma=val)
    await state.set_state(MashinaElon.yoqilgi)
    await msg.answer("⛽ <b>Yoqilg'i turi</b>:",
                     reply_markup=choice_kb(["Benzin", "Dizel", "Gaz", "Elektr", "Gibrid"]))

# Yoqilgi
@router.message(StateFilter(MashinaElon.yoqilgi), F.text == "🔙 Orqaga")
async def car_yoqilgi_orqaga(msg: Message, state: FSMContext):
    await state.set_state(MashinaElon.uzatma)
    await msg.answer("🔁 Uzatma qutisini tanlang:", reply_markup=choice_kb(["Mexanik", "Avtomat", "Variator", "Robot"]))

@router.message(StateFilter(MashinaElon.yoqilgi))
async def car_yoqilgi(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(yoqilgi=val)
    await state.set_state(MashinaElon.holat)
    await msg.answer("🚘 <b>Mashina holati</b>:",
                     reply_markup=choice_kb(["Ideal", "Yaxshi", "O'rta", "Ta'mirga muhtoj"]))

# Holat
@router.message(StateFilter(MashinaElon.holat), F.text == "🔙 Orqaga")
async def car_holat_orqaga(msg: Message, state: FSMContext):
    await state.set_state(MashinaElon.yoqilgi)
    await msg.answer("⛽ Yoqilg'i turini tanlang:", reply_markup=choice_kb(["Benzin", "Dizel", "Gaz", "Elektr", "Gibrid"]))

@router.message(StateFilter(MashinaElon.holat))
async def car_holat(msg: Message, state: FSMContext):
    await state.update_data(holat=msg.text.strip())
    await state.set_state(MashinaElon.urish)
    await msg.answer(
        "🔨 <b>Urilgan joyi bormi?</b>\n"
        "<i>Masalan: Old bamper, O'ng qanot — yoki 'Yo'q' deb yozing</i>",
        reply_markup=choice_kb(["Yo'q (toza)", "Old qism", "Orqa qism", "Yon qism", "Boshqa"])
    )

# Urish
@router.message(StateFilter(MashinaElon.urish), F.text == "🔙 Orqaga")
async def car_urish_orqaga(msg: Message, state: FSMContext):
    await state.set_state(MashinaElon.holat)
    await msg.answer("🚘 Holatni tanlang:", reply_markup=choice_kb(["Ideal", "Yaxshi", "O'rta", "Ta'mirga muhtoj"]))

@router.message(StateFilter(MashinaElon.urish))
async def car_urish(msg: Message, state: FSMContext):
    val = msg.text.strip()
    await state.update_data(urish=val if val != "Yo'q (toza)" else None)
    await state.set_state(MashinaElon.navorot)
    await msg.answer(
        "🔧 <b>Qanday navorotlar qilingan?</b>\n"
        "<i>Masalan: Konditsioner, Signalizatsiya, Muzika, Kamera, Teri salon...</i>\n"
        "Yo'q bo'lsa ⏭ bosing",
        reply_markup=skip_or_back_kb()
    )

# Navorot
@router.message(StateFilter(MashinaElon.navorot), F.text == "🔙 Orqaga")
async def car_navorot_orqaga(msg: Message, state: FSMContext):
    await state.set_state(MashinaElon.urish)
    await msg.answer("🔨 Urilgan joyini kiriting:", reply_markup=choice_kb(["Yo'q (toza)", "Old qism", "Orqa qism", "Yon qism", "Boshqa"]))

@router.message(StateFilter(MashinaElon.navorot))
async def car_navorot(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(navorot=val)
    await state.set_state(MashinaElon.petno)
    await msg.answer("📋 <b>Petnos (texnik pasport) bormi?</b>",
                     reply_markup=choice_kb(["✅ Ha, bor", "❌ Yo'q"]))

# Petno
@router.message(StateFilter(MashinaElon.petno), F.text == "🔙 Orqaga")
async def car_petno_orqaga(msg: Message, state: FSMContext):
    await state.set_state(MashinaElon.navorot)
    await msg.answer("🔧 Navorotlarni kiriting:", reply_markup=skip_or_back_kb())

@router.message(StateFilter(MashinaElon.petno))
async def car_petno(msg: Message, state: FSMContext):
    val = "ha" if "Ha" in msg.text else "yoq"
    await state.update_data(petno=val)
    await state.set_state(MashinaElon.shahar)
    await msg.answer("📍 <b>Qaysi shaharda</b>?", reply_markup=skip_or_back_kb())

# Shahar
@router.message(StateFilter(MashinaElon.shahar), F.text == "🔙 Orqaga")
async def car_shahar_orqaga(msg: Message, state: FSMContext):
    await state.set_state(MashinaElon.petno)
    await msg.answer("📋 Petnos bormi?", reply_markup=choice_kb(["✅ Ha, bor", "❌ Yo'q"]))

@router.message(StateFilter(MashinaElon.shahar))
async def car_shahar(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(shahar=val)
    await state.set_state(MashinaElon.narx)
    await msg.answer("💵 <b>Narx</b> (USD yoki so'm):", reply_markup=REMOVE)

# Narx
@router.message(StateFilter(MashinaElon.narx), F.text == "🔙 Orqaga")
async def car_narx_orqaga(msg: Message, state: FSMContext):
    await state.set_state(MashinaElon.shahar)
    await msg.answer("📍 Shaharda:", reply_markup=skip_or_back_kb())

@router.message(StateFilter(MashinaElon.narx))
async def car_narx(msg: Message, state: FSMContext):
    await state.update_data(narx=msg.text.strip())
    await state.set_state(MashinaElon.telefon)
    await msg.answer("📞 <b>Telefon raqam</b>:", reply_markup=REMOVE)

# Telefon
@router.message(StateFilter(MashinaElon.telefon), F.text == "🔙 Orqaga")
async def car_telefon_orqaga(msg: Message, state: FSMContext):
    await state.set_state(MashinaElon.narx)
    await msg.answer("💵 Narxni kiriting:", reply_markup=REMOVE)

@router.message(StateFilter(MashinaElon.telefon))
async def car_telefon(msg: Message, state: FSMContext):
    await state.update_data(telefon=msg.text.strip())
    await state.set_state(MashinaElon.tavsif)
    await msg.answer("📝 <b>Qo'shimcha ma'lumot</b>:", reply_markup=skip_or_back_kb())

# Tavsif
@router.message(StateFilter(MashinaElon.tavsif), F.text == "🔙 Orqaga")
async def car_tavsif_orqaga(msg: Message, state: FSMContext):
    await state.set_state(MashinaElon.telefon)
    await msg.answer("📞 Telefon raqamni kiriting:", reply_markup=REMOVE)

@router.message(StateFilter(MashinaElon.tavsif))
async def car_tavsif(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(tavsif=val, foto_ids=[], video_id=None)
    await state.set_state(MashinaElon.foto)
    await msg.answer(
        "🖼🎥 <b>Rasmlar yoki video</b> (ixtiyoriy, 5 tagacha rasm)\n\n"
        "📸 Rasm yuboring\n🎥 Qisqa video yuboring\n\nTugagach ✅ bosing.",
        reply_markup=foto_yuborib_boldi_kb()
    )

@router.message(StateFilter(MashinaElon.foto), F.photo)
async def car_foto(msg: Message, state: FSMContext):
    data = await state.get_data()
    fotos = data.get("foto_ids", [])
    if len(fotos) < 5:
        fotos.append(msg.photo[-1].file_id)
        await state.update_data(foto_ids=fotos)
        await msg.answer(f"✅ Rasm ({len(fotos)}/5)", reply_markup=foto_yuborib_boldi_kb())

@router.message(StateFilter(MashinaElon.foto), F.video)
async def car_video(msg: Message, state: FSMContext):
    await state.update_data(video_id=msg.video.file_id)
    await msg.answer("🎥 Video qabul qilindi!", reply_markup=foto_yuborib_boldi_kb())

@router.message(StateFilter(MashinaElon.foto), F.text == "🔙 Orqaga")
async def car_foto_orqaga(msg: Message, state: FSMContext):
    await state.set_state(MashinaElon.tavsif)
    await msg.answer("📝 Tavsif kiriting:", reply_markup=skip_or_back_kb())

@router.message(StateFilter(MashinaElon.foto),
                F.text.in_(["✅ Tayyor, davom etish", "⏭ Fotosiz davom etish"]))
async def car_foto_tayyor(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.set_state(MashinaElon.tasdiq)
    preview = mashina_matn({**data, "id": "yangi", "username": msg.from_user.username or ""})
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="✅ Tasdiqlash va e'lon berish")],
        [KeyboardButton(text="❌ Bekor qilish")],
    ], resize_keyboard=True)
    await msg.answer(preview + "\n\n<i>Ma'lumotlar to'g'rimi?</i>", reply_markup=kb)

@router.message(StateFilter(MashinaElon.tasdiq), F.text == "✅ Tasdiqlash va e'lon berish")
async def car_tasdiq(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    data.update(user_id=msg.from_user.id,
                username=msg.from_user.username or "",
                full_name=msg.from_user.full_name or "")
    mid = await add_mashina(data)
    await msg.answer(f"✅ <b>Mashina e'loni joylashtirildi!</b>\n🆔 #{mid}",
                     reply_markup=main_menu_sotuvchi())

@router.message(StateFilter(MashinaElon.tasdiq), F.text == "❌ Bekor qilish")
async def car_tasdiq_bekor(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Bekor qilindi.", reply_markup=main_menu_sotuvchi())

# ===== QIDIRISH =====

@router.message(StateFilter(MashinaQidiruv.marka))
async def car_q_marka(msg: Message, state: FSMContext):
    val = None if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(marka=val)
    await state.set_state(MashinaQidiruv.yil_dan)
    await msg.answer("📅 <b>Yil (dan)</b>:\n<i>Masalan: 2015 yoki ⏭</i>", reply_markup=skip_or_back_kb())

@router.message(StateFilter(MashinaQidiruv.yil_dan))
async def car_q_yil_dan(msg: Message, state: FSMContext):
    val = None if msg.text in ["⏭ O'tkazib yuborish", "🔙 Orqaga"] else msg.text.strip()
    await state.update_data(yil_dan=val)
    await state.set_state(MashinaQidiruv.yil_ga)
    await msg.answer("📅 <b>Yil (gacha)</b>:\n<i>Masalan: 2023 yoki ⏭</i>", reply_markup=skip_or_back_kb())

@router.message(StateFilter(MashinaQidiruv.yil_ga))
async def car_q_yil_ga(msg: Message, state: FSMContext):
    val = None if msg.text in ["⏭ O'tkazib yuborish", "🔙 Orqaga"] else msg.text.strip()
    await state.update_data(yil_ga=val)
    await state.set_state(MashinaQidiruv.shahar)
    await msg.answer("📍 <b>Shahar</b>:", reply_markup=skip_or_back_kb())

@router.message(StateFilter(MashinaQidiruv.shahar))
async def car_q_shahar(msg: Message, state: FSMContext, bot: Bot):
    val = None if msg.text in ["⏭ O'tkazib yuborish", "🔙 Orqaga"] else msg.text.strip()
    data = await state.get_data()
    await state.clear()

    mashinalar = await search_mashina(
        marka=data.get("marka"),
        yil_dan=data.get("yil_dan"),
        yil_ga=data.get("yil_ga"),
        shahar=val
    )

    user = await get_user(msg.from_user.id)
    rejim = user.get("rejim", "xaridor") if user else "xaridor"
    menu_kb = main_menu_sotuvchi() if rejim == "sotuvchi" else main_menu_xaridor()

    if not mashinalar:
        await msg.answer("😔 Mos mashina topilmadi.", reply_markup=menu_kb); return

    await msg.answer(f"✅ <b>{len(mashinalar)} ta mashina topildi:</b>", reply_markup=menu_kb)
    for m in mashinalar:
        kb = mashina_inline(m["id"], msg.from_user.id, m["user_id"], is_admin(msg.from_user.id))
        await send_mashina(bot, msg.chat.id, m, reply_markup=kb)

# ===== SOTILDI / O'CHIRISH =====

@router.callback_query(F.data.startswith("car_sold_"))
async def car_sotildi(call: CallbackQuery):
    mid = int(call.data.split("_")[2])
    m = await get_mashina(mid)
    if not m: await call.answer("Topilmadi", show_alert=True); return
    if m["user_id"] != call.from_user.id and call.from_user.id not in ADMIN_IDS:
        await call.answer("Ruxsat yo'q", show_alert=True); return
    await deactivate_mashina(mid)
    try:
        await call.message.edit_text(call.message.text + "\n\n✅ <b>SOTILDI</b>")
    except: pass
    await call.answer("✅ Sotildi!")

@router.callback_query(F.data.startswith("car_del_"))
async def car_ochir(call: CallbackQuery):
    mid = int(call.data.split("_")[2])
    m = await get_mashina(mid)
    if not m: await call.answer("Topilmadi", show_alert=True); return
    if m["user_id"] != call.from_user.id and call.from_user.id not in ADMIN_IDS:
        await call.answer("Ruxsat yo'q", show_alert=True); return
    uid = call.from_user.id if call.from_user.id not in ADMIN_IDS else None
    await delete_mashina(mid, uid)
    try:
        await call.message.edit_text("🗑 <b>Mashina e'loni o'chirildi</b>")
    except: pass
    await call.answer("🗑 O'chirildi!")
