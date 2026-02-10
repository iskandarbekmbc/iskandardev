# Kundalik zikr desktop dasturi — loyiha tavsifi

## Maqsad
Mobil o'rniga kompyuterda ishlaydigan GUI dastur: foydalanuvchi zikr nomi, zikr matni va kunlik miqdorini kiritadi va kundalik sanashni yuritadi.

## Asosiy funksiyalar
1. **CRUD**
   - Zikr qo'shish
   - Zikrni tahrirlash
   - Zikrni o'chirish
2. **Kundalik progress**
   - Har zikr uchun bugungi hisob (`current/target`)
   - `+1`, `+5`, `Reset`
3. **Excelga export**
   - Barcha zikrlar joriy holati (`Nomi`, `Zikr matni`, `Kunlik miqdor`, `Bugungi sanoq`, `Progress`, `Sana`) bilan `.xlsx` faylga chiqariladi
4. **Lokal saqlash**
   - SQLite bazada saqlanadi

## GUI tarkibi
- Chap panel: zikrlar ro'yxati (`Nomi`, `Miqdor`, `Bugun`)
- O'ng panel: tanlangan zikr matni va progress
- Tugmalar: `+ Yangi`, `Tahrirlash`, `O'chirish`, `Excelga export`, `+1`, `+5`, `Reset`

## Ma'lumotlar modeli
- `zikr(id, name, text, target_count, created_at, updated_at)`
- `daily_progress(id, zikr_id, day, current_count)`

## Validation qoidalari
- Nomi bo'sh bo'lmasligi kerak
- Matn bo'sh bo'lmasligi kerak
- Miqdor musbat butun son bo'lishi kerak

## Ishga tushirish
```bash
python3 app.py
```
