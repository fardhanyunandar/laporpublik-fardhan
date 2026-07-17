# 🛡️ LaporPublik
### Platform Pengaduan Masyarakat Berbasis Web

> Sistem manajemen pengaduan publik yang memungkinkan masyarakat melaporkan masalah infrastruktur & pelayanan secara real-time, dilengkapi integrasi GPS, Google Maps, dan notifikasi in-app otomatis.

![Tech Stack](https://skillicons.dev/icons?i=python,html,css,js,mysql)

---

## 🌟 Tentang Project

LaporPublik adalah aplikasi web full-stack yang dibangun untuk menjembatani masyarakat dan pemerintah/instansi dalam penanganan pengaduan publik. Sistem ini mendukung pelaporan dengan foto/video, pelacakan status real-time, dan notifikasi otomatis dalam aplikasi.

**Use case nyata:** Warga bisa melaporkan jalan rusak, lampu mati, atau masalah lingkungan — lengkap dengan foto dan lokasi GPS — lalu memantau progres penanganannya secara langsung.

---

## ✨ Fitur Utama

### 👤 Untuk Masyarakat
- Laporan dengan 10 kategori + subkategori + prioritas
- Deteksi lokasi GPS otomatis & klik di peta interaktif
- Upload foto/video bukti (drag-and-drop)
- Mode laporan anonim
- Pelacakan status real-time via nomor tiket
- Tombol SOS darurat dengan koordinat GPS

### 🔧 Untuk Admin
- Dashboard analitik dengan 4 jenis chart
- Peta interaktif sebaran laporan & SOS
- Notifikasi in-app otomatis ke pelapor saat status diperbarui
- Manajemen user (aktifkan/nonaktifkan akun)
- Dark mode & auto-refresh notifikasi setiap 60 detik

### 🔐 Keamanan
- Password hashing (PBKDF2 via Werkzeug)
- Role-based access control (user / admin / superadmin)
- Proteksi XSS, SQL Injection (parameterized queries), CSRF
- Validasi file upload (tipe & ukuran)

---

## 🛠️ Tech Stack

| Layer | Teknologi |
|---|---|
| Backend | Python (Flask) |
| Frontend | HTML5, CSS3, JavaScript |
| Database | MySQL |
| Maps | Google Maps JavaScript API + Geocoding API |
| Auth | Session-based + Werkzeug PBKDF2 |

---

## 🚀 Cara Menjalankan

### 1. Clone Repository
```bash
git clone https://github.com/fardhanyunandar/LaporPublik.git
cd LaporPublik
```

### 2. Install Dependensi
```bash
pip install -r requirements.txt
```

### 3. Setup Database
```sql
CREATE DATABASE IF NOT EXISTS lapor_publik
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

### 4. Konfigurasi Environment
Edit variabel di `app.py` atau buat file `.env`:
```
DB_HOST=localhost
DB_USER=root
DB_PASS=password_mysql_anda
DB_NAME=lapor_publik
SECRET_KEY=ganti_dengan_string_random
```

### 5. Jalankan Aplikasi
```bash
python app.py
```
Akses di: `http://localhost:5000`

### Login Admin Default
- Email: `admin@lapor.id`
- Password: `Admin@2026!`
- ⚠️ Segera ganti password setelah login pertama!

---

## 📁 Struktur Project

```
LaporPublik/
├── app.py                    ← Backend Flask (API & routing)
├── requirements.txt          ← Dependensi Python
├── templates/
│   ├── index.html            ← Landing page publik
│   ├── login.html            ← Login & registrasi
│   ├── dashboard-user.html   ← Dashboard masyarakat
│   └── dashboard-admin.html  ← Dashboard admin
└── static/
    └── uploads/              ← Penyimpanan file upload
```

---

## 📡 API Endpoints

| Method | Endpoint | Deskripsi |
|---|---|---|
| POST | `/api/auth/register` | Registrasi user |
| POST | `/api/auth/login` | Login |
| POST | `/api/reports` | Buat laporan baru |
| GET | `/api/reports/my` | Riwayat laporan user |
| GET | `/api/reports/track/{ticket}` | Lacak laporan (publik) |
| POST | `/api/sos` | Kirim SOS darurat |
| GET | `/api/admin/stats` | Statistik dashboard admin |
| PUT | `/api/admin/reports/{id}/status` | Update status laporan |

> Lihat dokumentasi lengkap di [API Endpoints](#) *(coming soon)*

---

## 👨‍💻 Developer

**Fardhan Maulana Yunandar**
Junior Full-Stack Developer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-fardhanmaulana-blue?logo=linkedin)](https://linkedin.com/in/fardhanmaulana)
[![GitHub](https://img.shields.io/badge/GitHub-fardhanyunandar-black?logo=github)](https://github.com/fardhanyunandar)
[![Email](https://img.shields.io/badge/Email-fardhanyundr@gmail.com-red?logo=gmail)](mailto:fardhanyundr@gmail.com)

---
