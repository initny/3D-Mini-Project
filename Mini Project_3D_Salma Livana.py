import csv
import os

file_csv = "data_pertanian.csv"

daftar_kolom_wajib = [
    "Provinsi",
    "Tahun",
    "Produksi",
    "Luas Panen",
    "Curah hujan",
    "Kelembapan",
    "Suhu rata-rata"
]

data = []

def baca_data(file_csv):
    if not os.path.exists(file_csv):
        print(f"ERROR: File {file_csv} tidak ditemukan.")
        return None

    with open(file_csv, "r", encoding="utf-8_sig") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            print(f"ERROR: Header {file_csv} tidak ditemukan")
            return None
        kolom_hilang = []
        for kolom in daftar_kolom_wajib:
            if kolom not in reader.fieldnames:
                kolom_hilang.append(kolom)

        if len(kolom_hilang) > 0:
            print("ERROR: Kolom data pertanian tidak lengkap")
            for kolom in kolom_hilang:
                print (f"- kolom {kolom} tidak ditemukan")
            return None
        return list (reader)

def validasi_data(data):
    for nomor_baris, baris in enumerate(reader, start=2):
        jumlah_sel_terisi = 0
        for nilai_sel in baris.values():
            if nilai_sel is not None and nilai_sel.strip() != "":
                jumlah_sel_terisi += 1

        if jumlah_sel_terisi == 0:
            print(f"ERROR: Baris ke-{nomor_baris} kosong sehingga dilewati")
            continue

        ada_kolom_kosong = False
        for kolom in daftar_kolom_wajib:
            if baris[kolom] is None or baris [kolom].strip() == "":
                print(f"ERROR: Data pada baris ke-{nomor_baris} kolom {kolom} kosong")
                ada_kolom_kosong = True
                break

        if ada_kolom_kosong:
            continue

        try:
            provinsi = str (baris["Provinsi"])
            tahun = int (baris["Tahun"])
            nilai_produksi = float (baris["Produksi"])
            nilai_luas_panen = float (baris["Luas Panen"])
            curah = float (baris["Curah hujan"])
            kelembapan = float(baris["kelembapan"])
            suhu_rata = float (baris["Suhu rata-rata"])
        except ValueError:
            print(f"ERROR: Data pada baris ke-{nomor_baris} tidak valid.")
            continue

        if (
            tahun < 0
            or nilai_produksi < 0
            or nilai_luas_panen < 0
            or curah < 0
            or kelembapan < 0
            or suhu_rata < 0
        ):
            print(f"ERROR: Data angka pada baris ke-{nomor_baris} bernilai negatif sehingga dilewati")
            continue

def hitung_persentase_produktivitas(nilai_produksi, nilai_luas_panen):
    if nilai_luas_panen == 0:
        return 0.0
    persentase_produktivitas = (nilai_produksi / nilai_luas_panen) * 100
    return persentase_produktivitas

def hitung_laju_pertumbuhan(nilai_sebelumnya, nilai_sekarang):
    if nilai_sebelumnya is None or nilai_sebelumnya == 0:
        return None
    persentase_pertumbuhan = ((nilai_sekarang - nilai_sebelumnya) / nilai_sebelumnya) * 100
    return persentase_pertumbuhan

def validasi(curah,kelembapan,suhu_rata):
    if curah >=1500 or curah<=2000:
        status_curah=("CURAH HUJAN BAIK")
    elif curah>2000:
        status_curah=("CURAH HUJAN TINGGI")
    else:
        status_curah=("CURAH HUJAN RENDAH")

    if suhu_rata >=23 or suhu_rata<=32:
        status_suhu=("SUHU OPTIMAL")
    elif suhu_rata<23:
        status_suhu=("SUHU RENDAH")
    else:
        status_suhu=("SUHU TINGGI")

    if kelembapan >0.5:
        status_kelembapan=("BASAH")
    elif kelembapan>=0.4 or kelembapan <=0.5:
        status_kelembapan=("LEMBAB")
    else:
        status_kelembapan=("KERING")
    return status_curah, status_suhu, status_kelembapan

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



        