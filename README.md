# 🌴 Carioca – Smart Nutrition & Workout Tracker (v27 Modular)

Carioca, bireylerin beslenme, antrenman ve vücut ölçülerini tek bir arayüzde takip edebilmesi için tasarlanmış **Streamlit tabanlı kişisel planlama uygulamasıdır**.

Uygulama tamamen **modüler yapıdadır** ve hem masaüstü hem de mobil tarayıcılarda sorunsuz çalışır.

---

## 🚀 Özellikler
- 🧬 **Profil Yönetimi:** Boy, kilo, bel ölçüsü, aktivite seviyesi, hedefler, oruç tipi (fasting) vb.
- 🍽️ **Besin Takibi:** OpenFoodFacts + USDA FDC entegrasyonu, gram bazlı makro hesaplama.
- 💪 **Antrenman Planı:** Program türüne göre otomatik öneriler, manuel set/rep girişi, kalori hesaplama.
- 📈 **Progress Grafiği:** Ağırlık ve bel ölçüsü aynı grafikte; yanlış giriş silinebilir.
- 🔥 **Deficit Hesaplayıcı:** Günlük/haftalık/3 aylık hedef ağırlık tahminleri.
- ⏱️ **Otomatik Hatırlatıcılar:** Su içme & duruş bildirimi (bildirim + sesli uyarı).
- 🧾 **Özet Ekranı:** Gün/hafta/ay bazında net kalori açığı, yakılan yağ tahmini.
- 🎨 **Tropik & Minimal Tema Seçenekleri**
- 🔑 **Enter ile Login**, “Remember Me” desteği
- 👥 Çoklu kullanıcı desteği (SQLite DB üzerinden)

---

## 🗂️ Dizin Yapısı

carioca_v27_modular_refactor/
├── app.py
├── requirements.txt
├── core/
│ ├── db.py
│ ├── auth.py
│ ├── theme.py
│ ├── calc.py
│ ├── api_food.py
│ └── README.md
├── features/
│ ├── profile.py
│ ├── deficit.py
│ ├── nutrition.py
│ ├── workout.py
│ ├── progress.py
│ ├── reminders.py
│ ├── summary.py
│ └── README.md
└── assets/
└── (optional static files)
