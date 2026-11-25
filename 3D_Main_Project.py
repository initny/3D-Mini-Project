import csv
import os

FILE_CSV = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data_pertanian.csv"
)

KOLOM_WAJIB = [ "Provinsi", "Tahun", "Produksi", "Luas Panen", "Curah hujan", "Kelembapan", "Suhu rata-rata"]

FAKTOR = ["luas_panen", "curah_hujan", "kelembapan", "suhu"]

def baca_data_csv():
    data = []

    try:
        with open(FILE_CSV, "r", newline="", encoding="utf-8-sig") as file:
            baris_header = file.readline()
            pemisah = ";" if ";" in baris_header else ","
            nama_kolom = [h.strip() for h in baris_header.split(pemisah)]

            if not all(kolom in nama_kolom for kolom in KOLOM_WAJIB):
                print("Error: Kolom dataset tidak lengkap.")
                return []

            reader = csv.DictReader(file, fieldnames=nama_kolom, delimiter=pemisah)

            for nomor, row in enumerate(reader, start=2):
                rekam_valid = validasi_baris_csv(row, nomor)
                if rekam_valid is not None:
                    data.append(rekam_valid)

    except FileNotFoundError:
        print("Error: File CSV tidak ditemukan.")
        return []

    if not data:
        print("Error: Tidak ada data yang valid.")
        return data

    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if data[j]["tahun"] < data[i]["tahun"]:
                data[i], data[j] = data[j], data[i]

    return data

def validasi_baris_csv(row, nomor):
    try:
        if any(row[k] is None or not row[k].strip() for k in KOLOM_WAJIB):
            raise ValueError

        tahun = int(row["Tahun"])
        produksi = float(row["Produksi"])
        luas_panen = float(row["Luas Panen"])
        curah_hujan = float(row["Curah hujan"])
        kelembapan = float(row["Kelembapan"])
        suhu = float(row["Suhu rata-rata"])

        if (tahun <= 0 or produksi <0 or luas_panen <=0
                or curah_hujan < 0 or suhu < 0
                or kelembapan <= 0):
            raise ValueError

        return {"provinsi": row["Provinsi"].strip(), "tahun": tahun, "produksi": produksi, "luas_panen": luas_panen,
                "curah_hujan": curah_hujan, "kelembapan": kelembapan, "suhu": suhu}

    except (ValueError, TypeError):
        print(f"Peringatan: Data baris {nomor} tidak valid.")
        return None
def hitung_produktivitas(produksi, luas_panen):
    return produksi / luas_panen * 100


def hitung_pertumbuhan(sebelumnya, sekarang):
    if not sebelumnya:
        return None

    return (sekarang - sebelumnya) / sebelumnya * 100

def klasifikasi_lingkungan(curah_hujan, kelembapan, suhu):
    if curah_hujan > 2000:
       hujan = "Curah hujan diatas normal"
    elif curah_hujan >= 1000:
        hujan = "Curah hujan normal"
    else:
       hujan = "Curah hujan rendah"

    if 63 <= kelembapan <= 83:
        lembap = "Baik"
    else:
        lembap = "Kurang Baik"

    if suhu > 27:
        udara = "Suhu udara tinggi"
    elif suhu >= 19:
        udara = "suhu udara normal"
    else:
        udara = "suhu udara rendah"

    return hujan, lembap, udara

def hitung_regresi_sederhana(x, y):
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(i * j for i, j in zip(x, y))
    sum_x2 = sum(i * i for i in x)

    penyebut = n * sum_x2 - sum_x ** 2

    if penyebut == 0:
        raise ValueError("Data tahun tidak bervariasi, regresi tidak dapat dihitung.")

    a = (sum_y * sum_x2 - sum_x * sum_xy) / penyebut
    b = (n * sum_xy - sum_x * sum_y) / penyebut

    return [a, b]

def hitung_regresi(X, y):
    n = len(X)
    k = len(X[0])

    if n < k:
        raise ValueError(f"Minimal diperlukan {k} data valid untuk regresi.")

    A = [[sum(X[r][i] * X[r][j] for r in range(n)) for j in range(k)]
         for i in range(k)]
    b = [sum(X[r][i] * y[r] for r in range(n)) for i in range(k)]

    for i in range(k):
        p = i
        for r in range(i + 1, k):
            if abs(A[r][i]) > abs(A[p][i]):
                p = r

        A[i], A[p] = A[p], A[i]
        b[i], b[p] = b[p], b[i]

        if abs(A[i][i]) < 1e-12:
            raise ValueError("Matriks singular, regresi tidak dapat dihitung.")

        for r in range(i + 1, k):
            f = A[r][i] / A[i][i]
            for c in range(i, k):
                A[r][c] -= f * A[i][c]
            b[r] -= f * b[i]

    koef = [0.0] * k
    for i in range(k - 1, -1, -1):
        koef[i] = (b[i] - sum(A[i][j] * koef[j]
                              for j in range(i + 1, k))) / A[i][i]

    return koef

def estimasi_tahun(tahun, produksi_sebelumnya=None):
    if tahun in riwayat:
        return riwayat[tahun]

    hasil = {}
    for t in (tahun - 1, tahun):
        if t in riwayat:
            hasil[t] = riwayat[t]
        else:
            proyeksi = {n: tren[n][0] + tren[n][1] * t for n in FAKTOR}
            produksi = koef[0] + sum(
                koef[i + 1] * proyeksi[n] for i, n in enumerate(FAKTOR)
            )
            hasil[t] = {
                "provinsi": data[0]["provinsi"],
                "tahun": t,
                "produksi": produksi,
                **proyeksi
            }

    d = hasil[tahun]
    prod_prev = (
        produksi_sebelumnya
        if produksi_sebelumnya is not None
        else hasil[tahun - 1]["produksi"]
    )

    rekam = dict(d)
    rekam["produktivitas"] = hitung_produktivitas(d["produksi"], d["luas_panen"])
    rekam["pertumbuhan"] = hitung_pertumbuhan(prod_prev, d["produksi"])
    rekam["status_hujan"], rekam["status_kelembapan"], rekam["status_suhu"] = (
        klasifikasi_lingkungan(d["curah_hujan"], d["kelembapan"], d["suhu"])
    )

    return rekam

def minta_pilihan(pesan, pilihan):
    while True:
        teks = input(pesan).strip().lower()
        if teks in pilihan:
            return teks
        print(f"ERROR: Pilihan tidak tersedia. Silakan ketik {', '.join(pilihan)}.")

def minta_tahun(pesan):
    while True:
        teks = input(pesan).strip()
        if teks.isdigit() and int(teks) > 0:
            return int(teks)
        print("ERROR: Masukkan angka bilangan bulat positif.")

def tampilkan_tabel(judul, daftar):
    print("\n" + "=" * LEBAR)
    print(judul)
    print("=" * LEBAR)
    print(
        f"{'Tahun':<7} | {'Provinsi':<16} | {'Produktivitas (%)':>17} | "
        f"{'Pertumbuhan (%)':>15} | {'Curah Hujan':<26} | "
        f"{'Kelembapan':<15}| {'Suhu':<17}"
    )
    print("-" * LEBAR)

    for r in daftar:
        tahun_teks = str(r["tahun"])

        if r["pertumbuhan"] is None:
            teks_tumbuh = f"{'N/A (Awal)':>15}"
        else:
            teks_tumbuh = f"{r['pertumbuhan']:>14.2f}%"

        print(
            f"{tahun_teks:<7} | {r['provinsi']:<16} | "
            f"{r['produktivitas']:>16.2f}% | {teks_tumbuh} | "
            f"{r['status_hujan']:<26} | {r['status_kelembapan']:<15}| "
            f"{r['status_suhu']:<17}"
        )

    print("-" * LEBAR)

    for nama, kunci in (("Produktivitas", "produktivitas"),
                        ("Pertumbuhan  ", "pertumbuhan")):
        ada = [r for r in daftar if r[kunci] is not None]
        if not ada:
            continue

        tertinggi = ada[0]
        terendah = ada[0]
        for r in ada:
            if r[kunci] > tertinggi[kunci]:
                tertinggi = r
            if r[kunci] < terendah[kunci]:
                terendah = r
        rata = sum(r[kunci] for r in ada) / len(ada)

        print(
            f"{nama}  -> Rata-rata: {rata:.2f}% | "
            f"Tertinggi: {tertinggi[kunci]:.2f}% ({tertinggi['tahun']}) | "
            f"Terendah: {terendah[kunci]:.2f}% ({terendah['tahun']})"
        )

    print("=" * LEBAR)

def tampilkan_hasil_tahun(hasil):
    jenis = "data historis" if hasil["tahun"] in riwayat else "prediksi"

    print(f"\nHasil Analisis Tahun {hasil['tahun']} ({jenis})")
    print("-" * 50)
    print(f"Persentase Produktivitas  : {hasil['produktivitas']:.2f}%")

    if hasil["pertumbuhan"] is None:
        print("Laju Pertumbuhan Produksi : N/A (Tahun awal dataset)")
    else:
        print(f"Laju Pertumbuhan Produksi : {hasil['pertumbuhan']:.2f}%")

    print(f"Status Curah Hujan        : {hasil['status_hujan']}")
    print(f"Status Kelembapan         : {hasil['status_kelembapan']}")
    print(f"Status Suhu Rata-rata     : {hasil['status_suhu']}")


def tampilkan_perbandingan(h1, h2):
    p1 = h1["pertumbuhan"]
    p2 = h2["pertumbuhan"]

    print(f"\nPerbandingan Pertumbuhan Tahun {h1['tahun']} vs Tahun {h2['tahun']}")
    print("-" * 60)

    for h in (h1, h2):
        p = h["pertumbuhan"]
        print(f"Tahun {h['tahun']} : Pertumbuhan "
              + (f"{p:.2f}%" if p is not None else "N/A"))

    if p1 is not None and p2 is not None:
        selisih = p1 - p2
        if selisih > 0:
            ket = "lebih tinggi"
        elif selisih < 0:
            ket = "lebih rendah"
        else:
            ket = "sama"

        print(f"Selisih    : Laju pertumbuhan tahun {h1['tahun']} {ket} "
              f"sebesar {abs(selisih):.2f}% dibanding tahun {h2['tahun']}.")

def menu_analisis_tahun():
    tahun = minta_tahun("\nIngin analisis tahun berapa? ")
    tampilkan_hasil_tahun(estimasi_tahun(tahun))

    print("\n1. Analisis tahun lanjutan")
    print("2. Selesai / kembali")

    if minta_pilihan("Pilih (1/2): ", ["1", "2"]) == "2":
        return

    jumlah = minta_tahun(f"Mau lihat prediksi berapa tahun ke depan (dari tahun {tahun})? ")
    daftar = [estimasi_tahun(t) for t in range(tahun, tahun + jumlah + 1)]
    tampilkan_tabel(f"TABEL HASIL ANALISIS TAHUN {tahun} - {tahun + jumlah}", daftar)

    input("\nTekan Enter untuk kembali ke analisis lanjutan...")


def menu_perbandingan_tahun():
    while True:
        tahun_1 = minta_tahun("\nMasukkan tahun pertama yang ingin dibandingkan : ")
        tahun_2 = minta_tahun("Masukkan tahun kedua yang ingin dibandingkan   : ")

        while tahun_2 == tahun_1:
            print("ERROR: Tahun kedua harus berbeda dari tahun pertama.")
            tahun_2 = minta_tahun("Masukkan tahun kedua yang ingin dibandingkan   : ")

        tampilkan_perbandingan(estimasi_tahun(tahun_1), estimasi_tahun(tahun_2))

        print("\n1. Bandingkan tahun lain")
        print("2. Selesai / kembali")

        if minta_pilihan("Pilih (1/2): ", ["1", "2"]) == "2":
            break

data = baca_data_csv()
LEBAR = 130
if data:
    try:
        riwayat = {}
        for i, d in enumerate(data):
            sebelumnya = data[i - 1]["produksi"] if i > 0 else None
            riwayat[d["tahun"]] = buat_rekam_sementara = {
                **d,
                "produktivitas": hitung_produktivitas(d["produksi"], d["luas_panen"]),
                "pertumbuhan": hitung_pertumbuhan(sebelumnya, d["produksi"]),
                "status_hujan": klasifikasi_lingkungan(d["curah_hujan"], d["kelembapan"], d["suhu"])[0],
                "status_kelembapan": klasifikasi_lingkungan(d["curah_hujan"], d["kelembapan"], d["suhu"])[1],
                "status_suhu": klasifikasi_lingkungan(d["curah_hujan"], d["kelembapan"], d["suhu"])[2],
            }

   
        koef = hitung_regresi([[1.0] + [d[n] for n in FAKTOR] for d in data],
            [d["produksi"] for d in data])

        tren = {n: hitung_regresi_sederhana([d["tahun"] for d in data], [d[n] for d in data]) for n in FAKTOR}

    except ValueError as e:
        print(f"ERROR: Terjadi kesalahan dalam analisis data: {e}")
    else:
        print("\n" + "=" * LEBAR)
        print("PROGRAM ANALISIS KETERKAITAN LINGKUNGAN DENGAN PRODUKTIVITAS PANEN PADI DAN PERTUMBUHAN PRODUKSI PADI PER TAHUN".center(LEBAR))
        print(f"({len(data)} data valid)".center(LEBAR))
        print("=" * LEBAR)

        while True:
            print("\nMENU UTAMA")
            print("a. Tampilkan hasil analisis / rekap data")
            print("b. Analisis lanjutan")
            print("c. Keluar")

            menu = minta_pilihan("Pilih menu (a/b/c): ", ["a", "b", "c"])

            if menu == "a":
                tampilkan_tabel("TABEL HASIL ANALISIS: PRODUKTIVITAS, PERTUMBUHAN & KLASIFIKASI LINGKUNGAN", list(riwayat.values()))
                input("\nTekan Enter untuk kembali ke menu utama...")

            elif menu == "b":
                pilihan = ""
                while pilihan != "3":
                    print("\n" + "=" * 50)
                    print("ANALISIS LANJUTAN")
                    print("=" * 50)
                    print("1. Analisis tahun tertentu (dan prediksi tahun lanjutan)")
                    print("2. Perbandingan pertumbuhan dua tahun yang berbeda")
                    print("3. Kembali ke menu utama")

                    pilihan = minta_pilihan("Pilih (1/2/3): ", ["1", "2", "3"])

                    if pilihan == "1":
                        menu_analisis_tahun()
                    elif pilihan == "2":
                        menu_perbandingan_tahun()

            else:
                print("Program diakhiri. Terima kasih!")
                break