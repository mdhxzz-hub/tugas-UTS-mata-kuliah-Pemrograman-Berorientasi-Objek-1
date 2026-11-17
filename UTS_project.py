import json
import os


class Tiket:
    def __init__(self, kode_kursi, judul_film, harga_dasar):
        self.kode_kursi = kode_kursi
        self.judul_film = judul_film
        self.__harga_dasar = harga_dasar  # Private attribute (Encapsulation)
        self.nama_pemesan = None

    def get_harga_dasar(self):
        return self.__harga_dasar

    # Method dasar untuk Polymorphism
    def hitung_total_harga(self):
        return self.__harga_dasar

    def get_fasilitas(self):
        return "Kursi standar"

    # Mengubah atribut objek menjadi dictionary agar bisa disimpan ke JSON
    def to_dict(self):
        return {
            "kode_kursi": self.kode_kursi,
            "kategori": self.__class__.__name__,
            "judul_film": self.judul_film,
            "nama_pemesan": self.nama_pemesan,
            "fasilitas": self.get_fasilitas(),
            "total_harga": self.hitung_total_harga(),
        }

    def __str__(self):
        return (
            f"\n=== STRUK TIKET BIOSKOP ===\n"
            f"Film     : {self.judul_film}\n"
            f"Pemesan  : {self.nama_pemesan}\n"
            f"Kursi    : {self.kode_kursi} ({self.__class__.__name__})\n"
            f"Fasilitas: {self.get_fasilitas()}\n"
            f"Total    : Rp{self.hitung_total_harga():,}\n"
            f"==========================="
        )


class TiketReguler(Tiket):
    def __init__(self, kode_kursi, judul_film):
        super().__init__(kode_kursi, judul_film, harga_dasar=40000)

    def get_fasilitas(self):
        return "Kursi Reguler + Air Mineral"


class TiketVIP(Tiket):
    def __init__(self, kode_kursi, judul_film):
        super().__init__(kode_kursi, judul_film, harga_dasar=75000)
        self.biaya_layanan = 10000

    def hitung_total_harga(self):
        return self.get_harga_dasar() + self.biaya_layanan

    def get_fasilitas(self):
        return "Kursi Recliner + Popcorn & Minuman"


class StudioBioskop:
    def __init__(self, nama_studio, judul_film, nama_file="data_pemesanan.json"):
        self.nama_studio = nama_studio
        self.judul_film = judul_film
        self.nama_file = nama_file
        self.daftar_kursi = {
            "A1": TiketReguler("A1", judul_film),
            "A2": TiketReguler("A2", judul_film),
            "A3": TiketReguler("A3", judul_film),
            "B1": TiketVIP("B1", judul_film),
            "B2": TiketVIP("B2", judul_film),
        }
        # Otomatis memuat data pemesanan sebelumnya saat program dijalankan
        self.muat_data()

    def simpan_data(self):
        data_terpesan = [
            tiket.to_dict()
            for tiket in self.daftar_kursi.values()
            if tiket.nama_pemesan is not None
        ]
        with open(self.nama_file, "w", encoding="utf-8") as file:
            json.dump(data_terpesan, file, indent=4)

    def muat_data(self):
        if not os.path.exists(self.nama_file):
            return

        try:
            with open(self.nama_file, "r", encoding="utf-8") as file:
                data_tersimpan = json.load(file)
                for item in data_tersimpan:
                    kode = item.get("kode_kursi")
                    if kode in self.daftar_kursi:
                        self.daftar_kursi[kode].nama_pemesan = item.get("nama_pemesan")
        except (json.JSONDecodeError, IOError):
            print("[Info] File JSON kosong atau rusak, memulai dengan data baru.")

    def tampilkan_kursi(self):
        print(f"\n--- Denah Kursi {self.nama_studio} | Film: {self.judul_film} ---")
        for kode, tiket in self.daftar_kursi.items():
            if tiket.nama_pemesan is not None:
                status = f"TERISI ({tiket.nama_pemesan})"
            else:
                status = f"KOSONG - Rp{tiket.hitung_total_harga():,}"

            kategori = "VIP" if isinstance(tiket, TiketVIP) else "Reguler"
            print(f"Kursi {kode} [{kategori}] : {status}")

    def pesan_tiket(self, kode_kursi, nama_pemesan):
        kode_kursi = kode_kursi.upper().strip()
        nama_pemesan = nama_pemesan.strip()

        if kode_kursi not in self.daftar_kursi:
            print(f"[Gagal] Kursi '{kode_kursi}' tidak tersedia di studio ini.")
            return

        if not nama_pemesan:
            print("[Gagal] Nama pemesan wajib diisi.")
            return

        tiket = self.daftar_kursi[kode_kursi]

        if tiket.nama_pemesan is not None:
            print(f"[Gagal] Kursi {kode_kursi} sudah dipesan oleh {tiket.nama_pemesan}.")
            return

        tiket.nama_pemesan = nama_pemesan
        self.simpan_data()  # Perbarui file JSON
        print("\n[Berhasil] Pemesanan tiket sukses dan tersimpan ke JSON!")
        print(tiket)

    def batalkan_tiket(self, kode_kursi, nama_pemesan):
        kode_kursi = kode_kursi.upper().strip()
        nama_pemesan = nama_pemesan.strip()

        if kode_kursi not in self.daftar_kursi:
            print(f"[Gagal] Kursi '{kode_kursi}' tidak ditemukan.")
            return

        tiket = self.daftar_kursi[kode_kursi]

        # Validasi 1: Pastikan kursi memang sedang terisi
        if tiket.nama_pemesan is None:
            print(f"[Gagal] Kursi {kode_kursi} masih kosong, tidak ada yang bisa dibatalkan.")
            return

        # Validasi 2: Cocokkan nama pemesan agar tidak dibatalkan orang lain
        if tiket.nama_pemesan.lower() != nama_pemesan.lower():
            print(f"[Gagal] Nama pemesan tidak cocok dengan data pada kursi {kode_kursi}.")
            return

        tiket.nama_pemesan = None
        self.simpan_data()  # Perbarui file JSON setelah dibatalkan
        print(f"\n[Berhasil] Pemesanan kursi {kode_kursi} atas nama {nama_pemesan} telah dibatalkan.")

    def lihat_riwayat_json(self):
        print(f"\n--- Isi File {self.nama_file} ---")
        if not os.path.exists(self.nama_file):
            print("Belum ada riwayat pemesanan tersimpan.")
            return

        with open(self.nama_file, "r", encoding="utf-8") as file:
            print(file.read())


def main():
    studio = StudioBioskop("Studio 1", "Interstellar Re-Release")

    while True:
        print("\n=== MENU PEMESANAN TIKET BIOSKOP ===")
        print("1. Lihat Denah & Harga Kursi")
        print("2. Pesan Tiket")
        print("3. Batalkan Tiket")
        print("4. Lihat Riwayat Tersimpan (JSON)")
        print("5. Keluar")
        pilihan = input("Pilih menu (1-5): ")

        if pilihan == "1":
            studio.tampilkan_kursi()
        elif pilihan == "2":
            studio.tampilkan_kursi()
            kursi = input("\nMasukkan kode kursi yang dipesan (contoh: A1): ")
            nama = input("Masukkan nama pemesan: ")
            studio.pesan_tiket(kursi, nama)
        elif pilihan == "3":
            studio.tampilkan_kursi()
            kursi = input("\nMasukkan kode kursi yang ingin dibatalkan: ")
            nama = input("Konfirmasi nama pemesan: ")
            studio.batalkan_tiket(kursi, nama)
        elif pilihan == "4":
            studio.lihat_riwayat_json()
        elif pilihan == "5":
            print("Program selesai. Data terakhir aman tersimpan di JSON.")
            break
        else:
            print("Input tidak valid, pilih angka 1 sampai 5.")


if __name__ == "__main__":
    main()