# keyboards.py — Barcha tugmalar

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove
)

REMOVE = ReplyKeyboardRemove()

# ========== ASOSIY MENYULAR ==========

def main_menu_xaridor() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔍 E'lon qidirish")],
        [KeyboardButton(text="🏠 Uylar"), KeyboardButton(text="🏢 Joylar"), KeyboardButton(text="🌿 Yerlar")],
        [KeyboardButton(text="🚗 Mashinalar")],
        [KeyboardButton(text="📌 Mening so'rovlarim"), KeyboardButton(text="⚙️ Sozlamalar")],
        [KeyboardButton(text="📦 Arxiv"), KeyboardButton(text="🔄 Rejimni almashtirish")],
        [KeyboardButton(text="🔄 Rejimni almashtirish")],
    ], resize_keyboard=True)

def main_menu_sotuvchi() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="➕ E'lon berish")],
        [KeyboardButton(text="📋 Mening e'lonlarim"), KeyboardButton(text="🔍 E'lon qidirish")],
        [KeyboardButton(text="🚗 Mashinalar")],
        [KeyboardButton(text="⚙️ Sozlamalar"), KeyboardButton(text="🔄 Rejimni almashtirish")],
    ], resize_keyboard=True)

def rejim_tanlash() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛒 Sotib olish / Ijaraga olish")],
        [KeyboardButton(text="📢 Sotish / Ijaraga berish")],
    ], resize_keyboard=True)

# ========== E'LON BERISH ==========

def tur_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🏠 Uy"), KeyboardButton(text="🏢 Joy"), KeyboardButton(text="🌿 Yer")],
        [KeyboardButton(text="🔙 Orqaga")],
    ], resize_keyboard=True, one_time_keyboard=True)

def amal_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="💰 Sotish"), KeyboardButton(text="🔑 Ijaraga berish")],
        [KeyboardButton(text="🔙 Orqaga")],
    ], resize_keyboard=True, one_time_keyboard=True)

def holat_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="✨ Evro ta'mirlangan"), KeyboardButton(text="🔧 O'rta ta'mirlangan")],
        [KeyboardButton(text="🏗 Ta'mirsiz"), KeyboardButton(text="🆕 Yangi qurilish")],
        [KeyboardButton(text="🔙 Orqaga")],
    ], resize_keyboard=True, one_time_keyboard=True)

def xonalar_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3")],
        [KeyboardButton(text="4"), KeyboardButton(text="5"), KeyboardButton(text="5+")],
        [KeyboardButton(text="🔙 Orqaga")],
    ], resize_keyboard=True, one_time_keyboard=True)

def skip_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="⏭ O'tkazib yuborish")],
        [KeyboardButton(text="🔙 Orqaga")],
    ], resize_keyboard=True, one_time_keyboard=True)

def lokatsiya_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📍 Joylashuvni yuborish", request_location=True)],
        [KeyboardButton(text="⏭ O'tkazib yuborish")],
        [KeyboardButton(text="🔙 Orqaga")],
    ], resize_keyboard=True, one_time_keyboard=True)

def foto_yuborib_boldi_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="✅ Tayyor, davom etish")],
        [KeyboardButton(text="⏭ Fotosiz davom etish")],
        [KeyboardButton(text="🔙 Orqaga")],
    ], resize_keyboard=True, one_time_keyboard=True)

def tasdiqlash_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="✅ Tasdiqlash va e'lon berish")],
        [KeyboardButton(text="✏️ Qaytadan to'ldirish"), KeyboardButton(text="❌ Bekor qilish")],
    ], resize_keyboard=True, one_time_keyboard=True)

# ========== QIDIRISH ==========

def qidiruv_tur_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🏠 Uy"), KeyboardButton(text="🏢 Joy"), KeyboardButton(text="🌿 Yer")],
        [KeyboardButton(text="🔁 Barchasi")],
        [KeyboardButton(text="🔙 Orqaga")],
    ], resize_keyboard=True, one_time_keyboard=True)

def qidiruv_amal_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="💰 Sotish"), KeyboardButton(text="🔑 Ijara")],
        [KeyboardButton(text="🔁 Barchasi")],
        [KeyboardButton(text="🔙 Orqaga")],
    ], resize_keyboard=True, one_time_keyboard=True)

# ========== INLINE ==========

def elon_inline(elon_id: int, user_id: int, owner_id: int, is_admin: bool = False) -> InlineKeyboardMarkup:
    buttons = []
    if is_admin or user_id == owner_id:
        buttons.append([
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"del_{elon_id}"),
            InlineKeyboardButton(text="✅ Sotildi/Ijaralandi", callback_data=f"sold_{elon_id}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None

def pagination_kb(offset: int, total: int, limit: int, prefix: str) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    if offset > 0:
        row.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"{prefix}_prev_{offset}_{limit}"))
    if offset + limit < total:
        row.append(InlineKeyboardButton(text="➡️ Keyingi", callback_data=f"{prefix}_next_{offset}_{limit}"))
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None

def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="adm_stat")],
        [InlineKeyboardButton(text="📢 Reklama yuborish", callback_data="adm_reklama")],
        [InlineKeyboardButton(text="👤 Foydalanuvchi bloklash", callback_data="adm_block")],
        [InlineKeyboardButton(text="📋 Barcha e'lonlar", callback_data="adm_elonlar")],
        [InlineKeyboardButton(text="👥 Barcha foydalanuvchilar", callback_data="adm_users")],
    ])

def reklama_tur_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📝 Matnli reklama")],
        [KeyboardButton(text="🖼 Rasmli reklama")],
        [KeyboardButton(text="❌ Bekor qilish")],
    ], resize_keyboard=True, one_time_keyboard=True)
