"""
🏠 UY-JOY BOZORI BOT
=====================
Versiya: 2.0 (Professional)
Muallif: Claude

Xususiyatlar:
- Uy / Joy / Yer — sotish & ijara
- Lokatsiya (koordinata + harita)
- Admin panel (foydalanuvchi ID orqali)
- Reklama yuborish
- E'lonni o'chirish (egasi + admin)
- 2 tur foydalanuvchi: Sotuvchi va Xaridor

O'rnatish:
    pip install aiogram==3.7.0 aiosqlite

Ishga tushirish:
    python bot.py
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database import init_db
from handlers import common, seller, buyer, admin, car

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

from aiogram.client.default import DefaultBotProperties
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

async def main():
    await init_db()
    from database import init_mashina_db
    await init_mashina_db()
    logger.info("✅ Ma'lumotlar bazasi tayyor")

    dp.include_router(common.router)
    dp.include_router(seller.router)
    dp.include_router(buyer.router)
    dp.include_router(admin.router)
    dp.include_router(car.router)

    logger.info("🏠 Uy-Joy Bot ishga tushdi!")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
