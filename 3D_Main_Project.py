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

def hitung_laju_pertumbuhan(nilai_sebelumnya, nilai_sekarang):
    if nilai_sebelumnya is None or nilai_sebelumnya == 0:
        return None
    persentase_pertumbuhan = ((nilai_sekarang - nilai_sebelumnya) / nilai_sebelumnya) * 100
    return persentase_pertumbuhan

