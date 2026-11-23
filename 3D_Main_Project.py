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
def hitung_persentase_produktivitas(nilai_produksi, nilai_luas_panen):
    if nilai_luas_panen == 0:
        return 0.0
    persentase_produktivitas = (nilai_produksi / nilai_luas_panen) * 100
    return persentase_produktivitas