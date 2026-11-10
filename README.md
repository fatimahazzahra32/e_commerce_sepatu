# SOLESTREET – Shoe Store

SOLESTREET merupakan aplikasi e-commerce berbasis web yang dikembangkan untuk penjualan dan pengelolaan produk sepatu. Aplikasi ini dibuat menggunakan Python Flask sebagai framework backend dan MySQL sebagai database.

## Fitur Aplikasi

### Admin

* Dashboard untuk melihat ringkasan data.
* Mengelola data produk (tambah, lihat, edit, dan hapus).
* Mengelola data pelanggan.
* Mengelola data pesanan.
* Menambahkan pesanan pelanggan.
* Memperbarui status pesanan.
* Mengelola stok produk.

### Pelanggan

* Melihat katalog produk sepatu.
* Melihat informasi produk.
* Fitur keranjang belanja (pengembangan).

## Teknologi yang Digunakan

* Python
* Flask
* MySQL
* HTML
* CSS
* Bootstrap
* Git dan GitHub

## Struktur Database

Database yang digunakan bernama `db_ecommerce`, dengan tabel:

1. `produk` – menyimpan informasi produk sepatu.
2. `pelanggan` – menyimpan data pelanggan.
3. `pesanan` – menyimpan transaksi pesanan.

## Instalasi dan Menjalankan Aplikasi

### 1. Clone Repository

```bash
git clone https://github.com/fatimahazzahra32/e_commerce_sepatu.git
```

### 2. Masuk ke Folder Project

```bash
cd e_commerce_sepatu
```

### 3. Membuat Virtual Environment

```bash
python -m venv .venv
```

### 4. Mengaktifkan Virtual Environment

```bash
.venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install flask mysql-connector-python python-dotenv werkzeug
```

### 6. Konfigurasi Database

Buat database dengan nama `db_ecommerce` melalui MySQL.

Buat file `.env` di folder utama project dan sesuaikan konfigurasi berikut:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=db_ecommerce
SECRET_KEY=your_secret_key
```

Sesuaikan struktur tabel database dengan kebutuhan aplikasi.

### 7. Menjalankan Aplikasi

```bash
python app.py
```

### 8. Membuka Aplikasi

Buka browser dan akses:

```text
http://127.0.0.1:5000
```

## Anggota Kelompok

**UMI KULSUM TEAM**

| No. | Nama            | NIM        |
| --- | --------------- | ---------- |
| 1   | Fatimah Azzahra | 2522105080 |
| 2   | Umi Kulsum      | 2522105024 |

---

**SOLESTREET – Find Your Perfect Step!**
