# Kundalik Zikrlar (Desktop GUI)

Bu loyiha kundalik zikrlarni kompyuterda GUI (oyna) orqali boshqarish uchun tayyorlangan oddiy desktop dasturdir.

## Imkoniyatlar
- Zikr qo'shish: **nomi**, **uzun matni**, **kunlik miqdori**
- Zikrni tahrirlash va o'chirish
- Har bir zikr uchun bugungi progressni yuritish (`+1`, `+5`, `Reset`)
- Zikrlarni joriy holatda **Excel (`.xlsx`)** ga export qilish
- Ma'lumotlarni lokal SQLite bazaga saqlash (`zikr_desktop.db`)

## Ishga tushirish
Talab: Python 3.10+ (standart kutubxonalar yetarli).

```bash
python3 app.py
```

## Windows uchun EXE va installer
- EXE build: `scripts\build_windows_exe.bat`
- Installer build yo'riqnomasi: `docs/windows-exe-build.md`
- Inno Setup script: `installer/zikr_setup.iss`

## Fayllar
- `app.py` — asosiy Tkinter GUI dasturi
- `docs/desktop-app-spec.md` — desktop loyiha tavsifi
- `docs/windows-exe-build.md` — `.exe` va `Setup.exe` build qadamlari
- `scripts/build_windows_exe.bat` — PyInstaller build skripti
- `installer/zikr_setup.iss` — Windows installer skripti
