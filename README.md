# 🏠 Uy-Joy Bozori Telegram Bot

## Xususiyatlar
- 🏠 Uy / 🏢 Joy / 🌿 Yer — **sotish** va **ijara**
- 📍 **Lokatsiya** (Telegram'dan xarita yuborish)
- 🖼 **5 tagacha rasm** e'lon bilan
- 🔍 **Shahar → Tuman → Mahalla** bo'yicha qidirish
- 👤 **2 rejim**: Sotuvchi / Xaridor
- 🔑 **Admin panel** (foydalanuvchi ID orqali)
- 📢 **Reklama** — matnli va rasmli, barcha userlarga
- ✅ **Sotildi tugmasi** — egasi o'z e'lonini yopadi
- 🚫 **Bloklash** — muammoli foydalanuvchilarni bloklash

---

## O'rnatish

### 1. Python kutubxonalarini o'rnatish
```bash
pip install -r requirements.txt
```

### 2. config.py ni sozlash
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # @BotFather dan oling
ADMIN_IDS = [123456789]             # O'z Telegram ID raqamingiz
```

> ID raqamingizni bilish: botga /id yozing

### 3. Botni ishga tushirish
```bash
python bot.py
```

---

## Fayllar tuzilmasi
```
uy_bot/
├── bot.py              # Asosiy fayl
├── config.py           # Sozlamalar
├── database.py         # SQLite ma'lumotlar bazasi
├── keyboards.py        # Barcha tugmalar
├── states.py           # FSM holatlari
├── utils.py            # Yordamchi funksiyalar
├── requirements.txt    # Kutubxonalar
├── handlers/
│   ├── common.py       # /start, rejim tanlash
│   ├── seller.py       # E'lon berish
│   ├── buyer.py        # Qidirish, ko'rish
│   └── admin.py        # Admin panel
└── uylar.db            # Ma'lumotlar (avtomatik yaratiladi)
```

---

## Komandalar

### Foydalanuvchilar uchun
| Komanda | Tavsif |
|---------|--------|
| /start  | Botni boshlash, rejim tanlash |
| /id     | O'z ID raqamini ko'rish |
| /yordam | Yordam |

### Admin uchun
| Komanda | Tavsif |
|---------|--------|
| /admin  | Admin panelni ochish |

---

## E'lon berish jarayoni
```
➕ E'lon berish
  → Tur: Uy / Joy / Yer
  → Amal: Sotish / Ijara
  → Shahar
  → Tuman (ixtiyoriy)
  → Mahalla (ixtiyoriy)
  → Qo'shimcha manzil (ixtiyoriy)
  → 📍 Lokatsiya (ixtiyoriy)
  → Maydon (m²)
  → Xonalar soni (uy/joy uchun)
  → Holat (uy/joy uchun)
  → Narx
  → Telefon
  → Tavsif (ixtiyoriy)
  → 🖼 Rasmlar (5 tagacha, ixtiyoriy)
  → ✅ Tasdiqlash
```

---

## Admin panel imkoniyatlari
- 📊 **Statistika** — foydalanuvchilar va e'lonlar soni
- 📢 **Reklama yuborish** — barcha userlarga matn/rasm
- 👤 **Foydalanuvchi bloklash** — ID orqali
- 📋 **Barcha e'lonlar** — ko'rish va o'chirish
- 👥 **Barcha foydalanuvchilar** — ro'yxat

---

## Server (VPS) da ishlatish

### Systemd service
```ini
[Unit]
Description=Uy-Joy Bot
After=network.target

[Service]
WorkingDirectory=/home/user/uy_bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable uy_bot
sudo systemctl start uy_bot
```

---

Savollar uchun: @your_username
