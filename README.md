# Kundalik Zikrlar (Desktop GUI)

Bu loyiha kundalik zikrlarni kompyuterda GUI (oyna) orqali boshqarish uchun tayyorlangan oddiy desktop dasturdir.

## Imkoniyatlar
- Zikr qo'shish: **nomi**, **uzun matni**, **kunlik miqdori**
- Zikrni tahrirlash va o'chirish
- Har bir zikr uchun bugungi progressni yuritish (`+1`, `+5`, `Reset`)
- Ma'lumotlarni lokal SQLite bazaga saqlash (`zikr_desktop.db`)

## Ishga tushirish
Talab: Python 3.10+ (standart kutubxonalar yetarli).

```bash
python3 app.py
```

## Fayllar
- `app.py` — asosiy Tkinter GUI dasturi
- `docs/desktop-app-spec.md` — desktop loyiha tavsifi
