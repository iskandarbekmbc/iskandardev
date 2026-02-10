# Ish Kundaligi dasturini EXE va installer qilish

## 1) Kerakli dasturlar
Windows kompyuterda:
- Python 3.11+ (yoki sizda o'rnatilgan Python)
- `pip`
- (installer uchun) Inno Setup

## 2) Kutubxonani o'rnatish
```bash
python -m pip install -r requirements.txt
```

## 3) EXE yaratish
```bash
python build_windows_release.py
```

Natija:
- EXE: `dist/IshKundaligi/IshKundaligi.exe`
- Installer script: `installer/kundalik_installer.iss`

## 4) Kompyuterga o'rnatiladigan `.exe` installer yaratish
1. Inno Setup'ni o'rnating: https://jrsoftware.org/isinfo.php
2. `installer/kundalik_installer.iss` faylini oching.
3. **Compile** bosing.
4. Natijada `dist/IshKundaligiSetup.exe` hosil bo'ladi.

## 5) Foydalanuvchiga berish
Foydalanuvchiga `dist/IshKundaligiSetup.exe` faylini bering — shu fayl orqali dastur oddiy tarzda o'rnatiladi.
