# 💡 Features Module – Carioca Functional Pages

Bu klasör, her biri **bağımsız sekme olarak çalışan** uygulama bölümlerini içerir.  
Her dosyada `render(conn, user_row)` fonksiyonu bulunur; `app.py` bu fonksiyonları çağırır.

---

## 📁 Dosya Yapısı

| Dosya | İşlev |
|--------|--------|
| **profile.py** | Kullanıcı profili, ölçüler, fasting, plan tipi, e-posta, API anahtarı |
| **deficit.py** | Günlük/haftalık kalori açığı & kilo tahminleri |
| **nutrition.py** | Besin arama, gram bazlı ekleme, makro hedef grafikleri |
| **workout.py** | Program türüne göre antrenman önerisi, manuel set/rep girişi, kalori hesabı |
| **progress.py** | Ağırlık ve bel ölçüsü takibi, grafik + silme özelliği |
| **reminders.py** | Su içme ve duruş bildirim sistemi (bildirim + ses) |
| **summary.py** | Seçilen aralıkta (1w, 1m, 6m, custom) net kalori açığı ve yağ kaybı grafiği |

---

## 🔧 Geliştirme Rehberi

### Yeni Sekme Eklemek
1. Yeni bir dosya oluştur: `features/new_feature.py`
2. İçine şu yapıyı ekle:
```python
import streamlit as st
def render(conn, user_row):
    st.subheader("Yeni Sekme")
    st.write("Buraya içerik gelecek.")
