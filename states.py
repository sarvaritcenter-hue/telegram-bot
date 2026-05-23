# states.py — FSM holatlari

from aiogram.fsm.state import State, StatesGroup

class ElonBerish(StatesGroup):
    tur       = State()
    amal      = State()
    shahar    = State()
    tuman     = State()
    mahalla   = State()
    manzil    = State()
    lokatsiya = State()
    maydon    = State()
    xonalar   = State()
    holat     = State()
    narx      = State()
    telefon   = State()
    tavsif    = State()
    foto      = State()
    tasdiq    = State()

class Qidiruv(StatesGroup):
    tur     = State()
    amal    = State()
    shahar  = State()
    tuman   = State()
    mahalla = State()

class AdminReklama(StatesGroup):
    tur        = State()
    foto       = State()
    matn       = State()
    tasdiqlash = State()

class AdminBlock(StatesGroup):
    user_id = State()

class AdminElon(StatesGroup):
    elon_id = State()

class MashinaElon(StatesGroup):
    marka      = State()   # Marka: Cobalt, Nexia, BMW...
    model      = State()   # Model: 3 seriya, Damas...
    yil        = State()   # Ishlab chiqarilgan yil
    rang       = State()   # Rang
    probeg     = State()   # Necha km yurgan
    dvigatel   = State()   # Dvigatel hajmi
    uzatma     = State()   # Mexanik / Avtomat / Variator
    yoqilgi    = State()   # Benzin / Dizel / Gaz / Elektr / Gibrid
    holat      = State()   # Urilganmi, ta'mirlanganmi
    urish      = State()   # Urilgan joyi (ixtiyoriy)
    navorot    = State()   # Qanday navorotlar
    petno      = State()   # Petnosi bormi
    shahar     = State()   # Qaysi shahar
    narx       = State()   # Narx
    telefon    = State()   # Telefon
    tavsif     = State()   # Qo'shimcha
    foto       = State()   # Rasmlar
    tasdiq     = State()   # Tasdiqlash

class MashinaQidiruv(StatesGroup):
    marka   = State()
    yil_dan = State()
    yil_ga  = State()
    shahar  = State()
