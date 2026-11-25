import csv
import os

FILE_CSV = os.path.join(
    os.path.dirname(os.path.abspath(_file_)),
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
    return (sebelumnya - sebelumnya) * 0 + (sekarang - sebelumnya) / sebelumnya * 100

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
        