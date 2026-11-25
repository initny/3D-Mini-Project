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
    except PermissionError:
        print("Error: File CSV tidak dapat diakses.")
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
                or not 0 <= kelembapan < 100):
            raise ValueError

        return {"provinsi": row["Provinsi"].strip(), "tahun": tahun, "produksi": produksi, "luas_panen": luas_panen,
                "curah_hujan": curah_hujan, "kelembapan": kelembapan, "suhu": suhu}

    except (ValueError, TypeError):
        print(f"Peringatan: Data baris {nomor} tidak valid.")
        return None
data = baca_data_csv()

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

def regresi(x, y):
    jumlah_variabel = len(x[0])
    jumlah_data = len(x)
    matriks_augmented = []

    for baris_ke in range(jumlah_variabel):
        baris = []
        for kolom_ke in range(jumlah_variabel):
            jumlah = 0
            for indeks_data in range(jumlah_data):
                jumlah += (
                    x[indeks_data][baris_ke] *
                    x[indeks_data][kolom_ke]
                )
            baris.append(jumlah)

        jumlah = 0
        for indeks_data in range(jumlah_data):
            jumlah += (
                x[indeks_data][baris_ke] *
                y[indeks_data]
            )
        baris.append(jumlah)
        matriks_augmented.append(baris)



        