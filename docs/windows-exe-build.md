# Windows EXE va Installer tayyorlash

Ushbu loyiha Python/Tkinter asosida yozilgan. Windows kompyuterga o'rnatiladigan dastur tayyorlash uchun quyidagi yo'l tavsiya qilinadi:

## 1) EXE build (PyInstaller)
Repo rootda:

```bat
scripts\build_windows_exe.bat
```

Natija:
- `dist\KundalikZikrlar\KundalikZikrlar.exe`

## 2) Installer (`Setup.exe`) build (Inno Setup)
1. Inno Setup 6+ o'rnating.
2. `installer\zikr_setup.iss` faylini oching.
3. **Build** tugmasini bosing.

Natija:
- `dist_installer\KundalikZikrlarSetup.exe`

## Eslatmalar
- Dastur ma'lumotlari `zikr_desktop.db` faylida saqlanadi.
- Installer orqali o'rnatilganda ham ilova ishlashi uchun `dist\KundalikZikrlar\` ichidagi barcha fayllar paketlanadi.
- Versiyani yangilash uchun `installer\zikr_setup.iss` ichidagi `MyAppVersion` ni oshiring.
