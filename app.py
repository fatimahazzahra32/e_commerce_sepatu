import os
import uuid
import mysql.connector

from flask import (
    Flask, render_template, request,
    redirect, url_for, flash
)

from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash


# =====================================
# KONFIGURASI APLIKASI
# =====================================

load_dotenv()

app = Flask(
    __name__,
    template_folder="halaman_sepatu",
    static_folder="static"
)

app.secret_key = os.getenv("SECRET_KEY", "solestreet123")

UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

if os.path.isfile(UPLOAD_FOLDER):
    raise RuntimeError(
        "static/uploads adalah file, bukan folder. "
        "Hapus atau ubah nama file tersebut, lalu buat folder uploads."
    )

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


# =====================================
# KONEKSI DATABASE
# =====================================

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "db_ecommerce")
    )


# =====================================
# FUNGSI GAMBAR PRODUK
# =====================================

def simpan_gambar(file):

    if not file or file.filename == "":
        return None

    if "." not in file.filename:
        raise ValueError("File gambar tidak valid.")

    ekstensi = file.filename.rsplit(".", 1)[1].lower()

    if ekstensi not in ALLOWED_EXTENSIONS:
        raise ValueError("Gunakan gambar JPG, JPEG, PNG, atau WEBP.")

    nama_file = secure_filename(file.filename)
    nama_baru = f"{uuid.uuid4().hex}_{nama_file}"

    lokasi = os.path.join(
        app.config["UPLOAD_FOLDER"],
        nama_baru
    )

    file.save(lokasi)

    return nama_baru


def hapus_gambar(nama_file):

    if not nama_file:
        return

    lokasi = os.path.join(
        app.config["UPLOAD_FOLDER"],
        os.path.basename(nama_file)
    )

    if os.path.isfile(lokasi):
        os.remove(lokasi)


# =====================================
# HALAMAN BERANDA
# =====================================

@app.route("/")
def index():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM produk
            ORDER BY id_produk DESC
        """)

        products = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        "index.html",
        products=products
    )


# =====================================
# DASHBOARD ADMIN
# =====================================

@app.route("/admin")
def dashboard():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT COUNT(*) AS total FROM produk")
        total_produk = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM pelanggan")
        total_pelanggan = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM pesanan")
        total_pesanan = cursor.fetchone()["total"]

    finally:
        cursor.close()
        conn.close()

    return render_template(
        "dashboard.html",
        total_produk=total_produk,
        total_pelanggan=total_pelanggan,
        total_pesanan=total_pesanan
    )


# =====================================
# DAFTAR PRODUK ADMIN
# =====================================

@app.route("/admin/produk")
def daftar_produk():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM produk
            ORDER BY id_produk DESC
        """)

        products = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        "admin/produk/produk.html",
        products=products
    )


# =====================================
# TAMBAH PRODUK
# =====================================

@app.route("/admin/produk/tambah", methods=["GET", "POST"])
def tambah_produk():

    if request.method == "POST":

        nama_produk = request.form.get("nama_produk")
        merek = request.form.get("merek")
        kategori = request.form.get("kategori")
        ukuran = request.form.get("ukuran")
        warna = request.form.get("warna")
        harga = request.form.get("harga")
        stok = request.form.get("stok")
        deskripsi = request.form.get("deskripsi")

        conn = None
        cursor = None
        nama_gambar = None

        try:
            if not all([
                nama_produk, merek, kategori, ukuran,
                warna, harga, stok
            ]):
                raise ValueError("Lengkapi semua data produk.")

            nama_gambar = simpan_gambar(
                request.files.get("gambar")
            )

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO produk
                (
                    nama_produk, merek, kategori, ukuran,
                    warna, harga, stok, deskripsi, gambar
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                nama_produk, merek, kategori, ukuran,
                warna, harga, stok, deskripsi, nama_gambar
            ))

            conn.commit()

            flash("Produk berhasil ditambahkan!", "success")
            return redirect(url_for("daftar_produk"))

        except (ValueError, mysql.connector.Error) as error:
            if conn:
                conn.rollback()

            hapus_gambar(nama_gambar)
            flash(f"Gagal menambahkan produk: {error}", "danger")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("admin/produk/tambah.html")


# =====================================
# EDIT PRODUK
# =====================================

@app.route("/admin/produk/edit/<int:id>", methods=["GET", "POST"])
def edit_produk(id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM produk
            WHERE id_produk = %s
        """, (id,))

        product = cursor.fetchone()

        if product is None:
            flash("Produk tidak ditemukan!", "danger")
            return redirect(url_for("daftar_produk"))

        if request.method == "POST":

            nama_produk = request.form.get("nama_produk")
            merek = request.form.get("merek")
            kategori = request.form.get("kategori")
            ukuran = request.form.get("ukuran")
            warna = request.form.get("warna")
            harga = request.form.get("harga")
            stok = request.form.get("stok")
            deskripsi = request.form.get("deskripsi")

            gambar_baru = None

            try:
                if not all([
                    nama_produk, merek, kategori, ukuran,
                    warna, harga, stok
                ]):
                    raise ValueError("Lengkapi semua data produk.")

                gambar_baru = simpan_gambar(
                    request.files.get("gambar")
                )

                gambar_final = (
                    gambar_baru if gambar_baru else product["gambar"]
                )

                cursor.execute("""
                    UPDATE produk
                    SET
                        nama_produk=%s,
                        merek=%s,
                        kategori=%s,
                        ukuran=%s,
                        warna=%s,
                        harga=%s,
                        stok=%s,
                        deskripsi=%s,
                        gambar=%s
                    WHERE id_produk=%s
                """, (
                    nama_produk, merek, kategori, ukuran,
                    warna, harga, stok, deskripsi,
                    gambar_final, id
                ))

                conn.commit()

                if gambar_baru:
                    hapus_gambar(product["gambar"])

                flash("Produk berhasil diperbarui!", "success")
                return redirect(url_for("daftar_produk"))

            except (ValueError, mysql.connector.Error) as error:
                conn.rollback()
                hapus_gambar(gambar_baru)
                flash(f"Gagal memperbarui produk: {error}", "danger")

    finally:
        cursor.close()
        conn.close()

    return render_template(
        "admin/produk/edit.html",
        product=product
    )


# =====================================
# HAPUS PRODUK
# =====================================

@app.route("/admin/produk/hapus/<int:id>", methods=["POST"])
def hapus_produk(id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT gambar
            FROM produk
            WHERE id_produk = %s
        """, (id,))

        product = cursor.fetchone()

        if product is None:
            flash("Produk tidak ditemukan!", "danger")
            return redirect(url_for("daftar_produk"))

        cursor.execute("""
            DELETE FROM produk
            WHERE id_produk = %s
        """, (id,))

        conn.commit()

        hapus_gambar(product["gambar"])

        flash("Produk berhasil dihapus!", "success")

    except mysql.connector.Error as error:
        conn.rollback()
        flash(
            f"Gagal menghapus produk. Produk mungkin masih digunakan dalam pesanan: {error}",
            "danger"
        )

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("daftar_produk"))


# =====================================
# DAFTAR PELANGGAN
# =====================================

@app.route("/admin/pelanggan")
def daftar_pelanggan():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                id_pelanggan,
                nama_pelanggan,
                email,
                no_telepon,
                alamat,
                tanggal_daftar
            FROM pelanggan
            ORDER BY id_pelanggan DESC
        """)

        customers = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        "customers.html",
        customers=customers
    )


# =====================================
# TAMBAH PELANGGAN
# =====================================

@app.route("/admin/pelanggan/tambah", methods=["GET", "POST"])
def tambah_pelanggan():

    if request.method == "POST":

        nama = request.form.get("nama_pelanggan", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        telepon = request.form.get("no_telepon", "").strip()
        alamat = request.form.get("alamat", "").strip()

        if not nama or not email or not password:
            flash("Nama, email, dan password wajib diisi!", "danger")
            return redirect(url_for("tambah_pelanggan"))

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            password_hash = generate_password_hash(password)

            cursor.execute("""
                INSERT INTO pelanggan
                (
                    nama_pelanggan,
                    email,
                    password,
                    no_telepon,
                    alamat,
                    tanggal_daftar
                )
                VALUES (%s, %s, %s, %s, %s, CURDATE())
            """, (
                nama,
                email,
                password_hash,
                telepon,
                alamat
            ))

            conn.commit()

            flash("Pelanggan berhasil ditambahkan!", "success")
            return redirect(url_for("daftar_pelanggan"))

        except mysql.connector.Error as error:
            conn.rollback()
            flash(f"Gagal menambahkan pelanggan: {error}", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template("tambah_pelanggan.html")
# =====================================
# EDIT PELANGGAN
# =====================================

@app.route("/admin/pelanggan/edit/<int:id>", methods=["GET", "POST"])
def edit_pelanggan(id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                id_pelanggan,
                nama_pelanggan,
                email,
                no_telepon,
                alamat,
                tanggal_daftar
            FROM pelanggan
            WHERE id_pelanggan = %s
        """, (id,))

        customer = cursor.fetchone()

        if customer is None:
            flash("Pelanggan tidak ditemukan!", "danger")
            return redirect(url_for("daftar_pelanggan"))

        if request.method == "POST":

            nama = request.form.get("nama_pelanggan", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            telepon = request.form.get("no_telepon", "").strip()
            alamat = request.form.get("alamat", "").strip()

            if not nama or not email:
                flash("Nama dan email wajib diisi!", "danger")
                return redirect(url_for("edit_pelanggan", id=id))

            if password:
                cursor.execute("""
                    UPDATE pelanggan
                    SET
                        nama_pelanggan=%s,
                        email=%s,
                        password=%s,
                        no_telepon=%s,
                        alamat=%s
                    WHERE id_pelanggan=%s
                """, (
                    nama,
                    email,
                    generate_password_hash(password),
                    telepon,
                    alamat,
                    id
                ))

            else:
                cursor.execute("""
                    UPDATE pelanggan
                    SET
                        nama_pelanggan=%s,
                        email=%s,
                        no_telepon=%s,
                        alamat=%s
                    WHERE id_pelanggan=%s
                """, (
                    nama,
                    email,
                    telepon,
                    alamat,
                    id
                ))

            conn.commit()

            flash("Data pelanggan berhasil diperbarui!", "success")
            return redirect(url_for("daftar_pelanggan"))

    except mysql.connector.Error as error:
        conn.rollback()
        flash(f"Gagal memperbarui pelanggan: {error}", "danger")

    finally:
        cursor.close()
        conn.close()

    return render_template(
        "edit_pelanggan.html",
        customer=customer
    )


# =====================================
# HAPUS PELANGGAN
# =====================================

@app.route("/admin/pelanggan/hapus/<int:id>", methods=["POST"])
def hapus_pelanggan(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM pelanggan
            WHERE id_pelanggan = %s
        """, (id,))

        if cursor.rowcount == 0:
            flash("Pelanggan tidak ditemukan!", "danger")
        else:
            conn.commit()
            flash("Pelanggan berhasil dihapus!", "success")

    except mysql.connector.Error:
        conn.rollback()
        flash(
            "Pelanggan tidak dapat dihapus karena masih memiliki pesanan.",
            "danger"
        )

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("daftar_pelanggan"))


# =====================================
# DATA PESANAN
# =====================================

@app.route("/admin/pesanan")
def daftar_pesanan():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.id_pesanan,
                pl.nama_pelanggan,
                pr.nama_produk,
                p.tanggal_pesanan,
                p.jumlah,
                p.total_harga,
                p.metode_pembayaran,
                p.status_pesanan
            FROM pesanan p
            LEFT JOIN pelanggan pl
                ON p.id_pelanggan = pl.id_pelanggan
            LEFT JOIN produk pr
                ON p.id_produk = pr.id_produk
            ORDER BY p.id_pesanan DESC
        """)

        orders = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        "orders.html",
        orders=orders
    )


# =====================================
# UPDATE STATUS PESANAN
# =====================================

@app.route("/admin/pesanan/status/<int:id>", methods=["POST"])
def update_status_pesanan(id):

    status = request.form.get("status_pesanan")

    status_valid = [
        "Menunggu Pembayaran",
        "Diproses",
        "Dikirim",
        "Selesai",
        "Dibatalkan"
    ]

    if status not in status_valid:
        flash("Status pesanan tidak valid!", "danger")
        return redirect(url_for("daftar_pesanan"))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE pesanan
            SET status_pesanan = %s
            WHERE id_pesanan = %s
        """, (status, id))

        conn.commit()
        flash("Status pesanan berhasil diperbarui!", "success")

    except mysql.connector.Error as error:
        conn.rollback()
        flash(f"Gagal memperbarui status: {error}", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("daftar_pesanan"))


# =====================================
# TAMBAH PESANAN ADMIN
# =====================================

@app.route("/admin/pesanan/tambah", methods=["GET", "POST"])
def tambah_pesanan():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if request.method == "POST":

            id_pelanggan = request.form.get("id_pelanggan")
            id_produk = request.form.get("id_produk")
            metode = request.form.get("metode_pembayaran")
            jumlah_text = request.form.get("jumlah", "0")

            metode_valid = [
                "Transfer Bank",
                "COD",
                "E-Wallet"
            ]

            if (
                not id_pelanggan
                or not id_produk
                or metode not in metode_valid
            ):
                flash(
                    "Lengkapi semua data pesanan dengan benar!",
                    "danger"
                )
                return redirect(url_for("tambah_pesanan"))

            try:
                jumlah = int(jumlah_text)
            except (TypeError, ValueError):
                flash("Jumlah pesanan harus berupa angka.", "danger")
                return redirect(url_for("tambah_pesanan"))

            if jumlah < 1:
                flash("Jumlah pesanan minimal 1.", "danger")
                return redirect(url_for("tambah_pesanan"))

            cursor.execute("""
                SELECT id_pelanggan
                FROM pelanggan
                WHERE id_pelanggan = %s
            """, (id_pelanggan,))

            pelanggan = cursor.fetchone()

            if pelanggan is None:
                flash("Pelanggan tidak ditemukan.", "danger")
                return redirect(url_for("tambah_pesanan"))

            cursor.execute("""
                SELECT id_produk, harga, stok
                FROM produk
                WHERE id_produk = %s
                FOR UPDATE
            """, (id_produk,))

            produk = cursor.fetchone()

            if produk is None:
                flash("Produk tidak ditemukan.", "danger")
                return redirect(url_for("tambah_pesanan"))

            if jumlah > int(produk["stok"]):
                flash(
                    f"Stok tidak mencukupi. Stok tersedia: {produk['stok']}.",
                    "danger"
                )
                return redirect(url_for("tambah_pesanan"))

            total = produk["harga"] * jumlah

            cursor.execute("""
                INSERT INTO pesanan
                (
                    id_pelanggan,
                    id_produk,
                    tanggal_pesanan,
                    jumlah,
                    total_harga,
                    metode_pembayaran,
                    status_pesanan
                )
                VALUES (%s, %s, CURDATE(), %s, %s, %s, %s)
            """, (
                id_pelanggan,
                id_produk,
                jumlah,
                total,
                metode,
                "Menunggu Pembayaran"
            ))

            cursor.execute("""
                UPDATE produk
                SET stok = stok - %s
                WHERE id_produk = %s
            """, (jumlah, id_produk))

            conn.commit()

            flash("Pesanan berhasil ditambahkan!", "success")
            return redirect(url_for("daftar_pesanan"))

        cursor.execute("""
            SELECT id_pelanggan, nama_pelanggan
            FROM pelanggan
            ORDER BY nama_pelanggan ASC
        """)

        customers = cursor.fetchall()

        cursor.execute("""
            SELECT id_produk, nama_produk, harga, stok
            FROM produk
            ORDER BY nama_produk ASC
        """)

        products = cursor.fetchall()

        return render_template(
            "tambah_pesanan.html",
            customers=customers,
            products=products
        )

    except mysql.connector.Error as error:
        conn.rollback()
        flash(f"Gagal menyimpan pesanan: {error}", "danger")
        return redirect(url_for("daftar_pesanan"))

    finally:
        cursor.close()
        conn.close()


# =====================================
# HALAMAN KERANJANG
# =====================================

@app.route("/keranjang")
def keranjang():

    return render_template(
        "keranjang.html",
        cart_items=[],
        total=0
    )


# =====================================
# BATAS UKURAN UPLOAD
# =====================================

@app.errorhandler(413)
def file_too_large(error):

    flash("Ukuran gambar maksimal 5 MB.", "danger")
    return redirect(url_for("tambah_produk"))


# =====================================
# MENJALANKAN APLIKASI
# =====================================

if __name__ == "__main__":
    app.run(debug=True)