# database.py — SQLite ma'lumotlar bazasi

import aiosqlite
import json
from config import DB_FILE

async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS elon (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                username    TEXT,
                full_name   TEXT,
                tur         TEXT NOT NULL,
                amal        TEXT NOT NULL,
                shahar      TEXT NOT NULL,
                tuman       TEXT,
                mahalla     TEXT,
                manzil      TEXT,
                lat         REAL,
                lon         REAL,
                narx        TEXT NOT NULL,
                maydon      TEXT,
                xonalar     TEXT,
                holat       TEXT,
                tavsif      TEXT,
                telefon     TEXT NOT NULL,
                foto_ids    TEXT,
                video_id    TEXT,
                faol        INTEGER DEFAULT 1,
                holati      TEXT DEFAULT 'faol',
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Eski DB ga yangi ustunlar qo'shish (migration)
        for col, typedef in [
            ("video_id", "TEXT"),
            ("holati", "TEXT DEFAULT 'faol'")
        ]:
            try:
                await db.execute(f"ALTER TABLE elon ADD COLUMN {col} {typedef}")
            except:
                pass
        await db.execute("""
            CREATE TABLE IF NOT EXISTS foydalanuvchi (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                full_name   TEXT,
                rejim       TEXT DEFAULT 'xaridor',
                bloklangan  INTEGER DEFAULT 0,
                joined_at   DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reklama (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                matn        TEXT,
                media_id    TEXT,
                media_tur   TEXT,
                yuborilgan  INTEGER DEFAULT 0,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

# ===== FOYDALANUVCHI =====
async def get_or_create_user(user_id: int, username: str, full_name: str) -> dict:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM foydalanuvchi WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
        if row:
            return dict(row)
        await db.execute(
            "INSERT INTO foydalanuvchi (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name)
        )
        await db.commit()
        return {"user_id": user_id, "username": username,
                "full_name": full_name, "rejim": "xaridor", "bloklangan": 0}

async def set_rejim(user_id: int, rejim: str):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("UPDATE foydalanuvchi SET rejim = ? WHERE user_id = ?", (rejim, user_id))
        await db.commit()

async def get_user(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM foydalanuvchi WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
        return dict(row) if row else None

async def block_user(user_id: int, bloklangan: int):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "UPDATE foydalanuvchi SET bloklangan = ? WHERE user_id = ?", (bloklangan, user_id)
        )
        await db.commit()

async def get_all_users() -> list:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM foydalanuvchi WHERE bloklangan = 0") as cur:
            rows = await cur.fetchall()
        return [dict(r) for r in rows]

# ===== E'LON =====
async def add_elon(data: dict) -> int:
    async with aiosqlite.connect(DB_FILE) as db:
        cur = await db.execute("""
            INSERT INTO elon
              (user_id, username, full_name, tur, amal, shahar, tuman,
               mahalla, manzil, lat, lon, narx, maydon, xonalar,
               holat, tavsif, telefon, foto_ids, video_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data["user_id"], data.get("username"), data.get("full_name"),
            data["tur"], data["amal"], data["shahar"], data.get("tuman"),
            data.get("mahalla"), data.get("manzil"),
            data.get("lat"), data.get("lon"),
            data["narx"], data.get("maydon"), data.get("xonalar"),
            data.get("holat"), data.get("tavsif"),
            data["telefon"],
            json.dumps(data.get("foto_ids", [])),
            data.get("video_id")
        ))
        await db.commit()
        return cur.lastrowid

async def get_elon(elon_id: int) -> dict | None:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM elon WHERE id = ?", (elon_id,)) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        e = dict(row)
        e["foto_ids"] = json.loads(e["foto_ids"] or "[]")
        return e

async def search_elon(tur: str = None, amal: str = None,
                      shahar: str = None, tuman: str = None,
                      mahalla: str = None, offset: int = 0,
                      limit: int = 5, arxiv: bool = False) -> list:
    conditions = []
    params = []

    if arxiv:
        conditions.append("faol = 0")
    else:
        conditions.append("faol = 1")

    if tur:
        conditions.append("tur = ?"); params.append(tur)
    if amal:
        conditions.append("amal = ?"); params.append(amal)
    if shahar:
        conditions.append("LOWER(shahar) LIKE ?"); params.append(f"%{shahar.lower()}%")
    if tuman:
        # tuman, mahalla yoki manzil ichida qidirish
        t = tuman.lower()
        conditions.append(
            "(LOWER(tuman) LIKE ? OR LOWER(mahalla) LIKE ? OR LOWER(manzil) LIKE ?)"
        )
        params.extend([f"%{t}%", f"%{t}%", f"%{t}%"])
    if mahalla:
        m = mahalla.lower()
        conditions.append(
            "(LOWER(mahalla) LIKE ? OR LOWER(tuman) LIKE ? OR LOWER(manzil) LIKE ?)"
        )
        params.extend([f"%{m}%", f"%{m}%", f"%{m}%"])

    where = " AND ".join(conditions)
    params.extend([limit, offset])

    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            f"SELECT * FROM elon WHERE {where} ORDER BY id DESC LIMIT ? OFFSET ?", params
        ) as cur:
            rows = await cur.fetchall()
    result = []
    for r in rows:
        e = dict(r)
        e["foto_ids"] = json.loads(e["foto_ids"] or "[]")
        result.append(e)
    return result

async def get_user_elonlar(user_id: int) -> list:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM elon WHERE user_id = ? ORDER BY id DESC", (user_id,)
        ) as cur:
            rows = await cur.fetchall()
    result = []
    for r in rows:
        e = dict(r)
        e["foto_ids"] = json.loads(e["foto_ids"] or "[]")
        result.append(e)
    return result

async def deactivate_elon(elon_id: int, user_id: int = None, holati: str = "yopildi") -> bool:
    """faol=0 qilish (sotildi/o'chirildi belgisi bilan)"""
    async with aiosqlite.connect(DB_FILE) as db:
        if user_id:
            cur = await db.execute(
                "UPDATE elon SET faol=0, holati=? WHERE id=? AND user_id=?",
                (holati, elon_id, user_id)
            )
        else:
            cur = await db.execute(
                "UPDATE elon SET faol=0, holati=? WHERE id=?", (holati, elon_id)
            )
        await db.commit()
        return cur.rowcount > 0

async def delete_elon(elon_id: int, user_id: int = None) -> bool:
    """Serverdan TO'LIQ o'chirish"""
    async with aiosqlite.connect(DB_FILE) as db:
        if user_id:
            cur = await db.execute(
                "DELETE FROM elon WHERE id=? AND user_id=?", (elon_id, user_id)
            )
        else:
            cur = await db.execute("DELETE FROM elon WHERE id=?", (elon_id,))
        await db.commit()
        return cur.rowcount > 0

async def get_stats() -> dict:
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT COUNT(*) FROM elon WHERE faol=1") as c:
            faol = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM elon") as c:
            jami = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM elon WHERE faol=0") as c:
            arxiv = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM foydalanuvchi") as c:
            users = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM elon WHERE tur='uy' AND faol=1") as c:
            uylar = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM elon WHERE tur='joy' AND faol=1") as c:
            joylar = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM elon WHERE tur='yer' AND faol=1") as c:
            yerlar = (await c.fetchone())[0]
    return {
        "faol": faol, "jami": jami, "arxiv": arxiv,
        "users": users, "uylar": uylar, "joylar": joylar, "yerlar": yerlar
    }

async def add_reklama(matn: str, media_id: str = None, media_tur: str = None) -> int:
    async with aiosqlite.connect(DB_FILE) as db:
        cur = await db.execute(
            "INSERT INTO reklama (matn, media_id, media_tur) VALUES (?, ?, ?)",
            (matn, media_id, media_tur)
        )
        await db.commit()
        return cur.lastrowid

# ===== MASHINA =====
async def init_mashina_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mashina (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                username    TEXT,
                full_name   TEXT,
                marka       TEXT NOT NULL,
                model       TEXT,
                yil         TEXT,
                rang        TEXT,
                probeg      TEXT,
                dvigatel    TEXT,
                uzatma      TEXT,
                yoqilgi     TEXT,
                holat       TEXT,
                urish       TEXT,
                navorot     TEXT,
                petno       TEXT,
                shahar      TEXT,
                narx        TEXT NOT NULL,
                telefon     TEXT NOT NULL,
                tavsif      TEXT,
                foto_ids    TEXT,
                video_id    TEXT,
                faol        INTEGER DEFAULT 1,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def add_mashina(data: dict) -> int:
    async with aiosqlite.connect(DB_FILE) as db:
        cur = await db.execute("""
            INSERT INTO mashina
              (user_id, username, full_name, marka, model, yil, rang,
               probeg, dvigatel, uzatma, yoqilgi, holat, urish, navorot,
               petno, shahar, narx, telefon, tavsif, foto_ids, video_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data["user_id"], data.get("username"), data.get("full_name"),
            data["marka"], data.get("model"), data.get("yil"), data.get("rang"),
            data.get("probeg"), data.get("dvigatel"), data.get("uzatma"),
            data.get("yoqilgi"), data.get("holat"), data.get("urish"),
            data.get("navorot"), data.get("petno"), data.get("shahar"),
            data["narx"], data["telefon"], data.get("tavsif"),
            json.dumps(data.get("foto_ids", [])), data.get("video_id")
        ))
        await db.commit()
        return cur.lastrowid

async def search_mashina(marka: str = None, yil_dan: str = None,
                          yil_ga: str = None, shahar: str = None,
                          offset: int = 0, limit: int = 5) -> list:
    conditions = ["faol = 1"]
    params = []
    if marka:
        conditions.append(
            "(LOWER(marka) LIKE ? OR LOWER(model) LIKE ?)"
        )
        params.extend([f"%{marka.lower()}%", f"%{marka.lower()}%"])
    if yil_dan:
        conditions.append("CAST(yil AS INTEGER) >= ?"); params.append(int(yil_dan))
    if yil_ga:
        conditions.append("CAST(yil AS INTEGER) <= ?"); params.append(int(yil_ga))
    if shahar:
        conditions.append("LOWER(shahar) LIKE ?"); params.append(f"%{shahar.lower()}%")

    where = " AND ".join(conditions)
    params.extend([limit, offset])

    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            f"SELECT * FROM mashina WHERE {where} ORDER BY id DESC LIMIT ? OFFSET ?", params
        ) as cur:
            rows = await cur.fetchall()
    result = []
    for r in rows:
        e = dict(r)
        e["foto_ids"] = json.loads(e["foto_ids"] or "[]")
        result.append(e)
    return result

async def get_mashina(mashina_id: int) -> dict | None:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM mashina WHERE id = ?", (mashina_id,)) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        e = dict(row)
        e["foto_ids"] = json.loads(e["foto_ids"] or "[]")
        return e

async def get_user_mashinalar(user_id: int) -> list:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM mashina WHERE user_id = ? ORDER BY id DESC", (user_id,)
        ) as cur:
            rows = await cur.fetchall()
    result = []
    for r in rows:
        e = dict(r)
        e["foto_ids"] = json.loads(e["foto_ids"] or "[]")
        result.append(e)
    return result

async def delete_mashina(mashina_id: int, user_id: int = None) -> bool:
    async with aiosqlite.connect(DB_FILE) as db:
        if user_id:
            cur = await db.execute(
                "DELETE FROM mashina WHERE id=? AND user_id=?", (mashina_id, user_id)
            )
        else:
            cur = await db.execute("DELETE FROM mashina WHERE id=?", (mashina_id,))
        await db.commit()
        return cur.rowcount > 0

async def deactivate_mashina(mashina_id: int) -> bool:
    async with aiosqlite.connect(DB_FILE) as db:
        cur = await db.execute(
            "UPDATE mashina SET faol=0 WHERE id=?", (mashina_id,)
        )
        await db.commit()
        return cur.rowcount > 0
