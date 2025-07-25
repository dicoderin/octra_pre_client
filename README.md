## Octra Private Client

Selamat datang di Octra Private Client, sebuah command-line interface (CLI) yang powerful dan modern untuk berinteraksi dengan blockchain testnet Octra. Dibangun dengan Python dan asyncio, client ini menawarkan pengalaman yang responsif dan kaya fitur, termasuk dukungan penuh untuk transaksi privat, staking, dan deployment smart contract.


| Kategori | Fitur | Deskripsi |
|---|---|---|
| 💼 Wallet | Cek Saldo & Nonce | Lihat saldo publik, saldo terenkripsi, dan nonce terakhir secara real-time. |
|  | Riwayat Transaksi | Tampilan riwayat 50 transaksi terakhir dengan status (pending/epoch). |
|  | Ekspor Kunci | Opsi untuk menampilkan private key atau menyimpan seluruh data wallet ke file JSON. |
| 💸 Transaksi | Kirim Transaksi | Mengirim token OCT ke alamat lain dengan pesan opsional. |
|  | Multi-Send | Mengirim token ke banyak alamat sekaligus dalam satu perintah. |
| 🔒 Transaksi Privat | Enkripsi & Dekripsi Saldo | Memindahkan saldo dari publik ke privat (terenkripsi) dan sebaliknya. |
|  | Transfer Privat | Mengirim token secara rahasia dari saldo terenkripsi Anda ke pengguna lain. |
|  | Klaim Transfer | Menerima token dari transfer privat yang ditujukan untuk Anda. |
| 📈 Staking | Stake & Unstake | Mengunci token Anda di kontrak validator untuk mendapatkan reward. |
|  | Klaim Reward | Mengambil reward yang telah terkumpul dari aktivitas staking. |
| 📄 Smart Contract | Deploy Kontrak | Deploy smart contract baru ke blockchain dari file bytecode (.wasm). |
| 🖥️ UI | Tampilan Terminal Modern | Antarmuka berbasis teks yang interaktif dengan warna dan layout yang jelas. |
|  | Asynchronous | Semua operasi jaringan bersifat non-blocking, membuat UI tetap responsif. |
🚀 Instalasi
Untuk menjalankan client ini, pastikan Anda memiliki Python 3.8 atau versi yang lebih baru.
 * Clone Repositori 

```bash
   git clone https://github.com/dicoderin/octra_pre_client.git
```

```bash
cd octra_pre_client
```

 * Buat Virtual Environment (Sangat Direkomendasikan)
   # Untuk Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

# Untuk Windows

```bash
python -m venv venv
.\venv\Scripts\activate
```

 * Instal Dependensi
```bash
pip install -r requirements.txt
```

⚙️ Konfigurasi
Sebelum menjalankan client, Anda harus membuat file konfigurasi wallet bernama wallet.json di direktori yang sama dengan skrip.
 * Buat file wallet.json.
 * Isi dengan struktur berikut menggunakan data wallet Anda:
```bash
{
  "priv": "PRIVATE_KEY_ANDA_DALAM_BENTUK_BASE64",
  "addr": "ALAMAT_WALLET_OCTRA_ANDA",
  "rpc": "http://ALAMAT_IP_RPC_NODE:8080"
}
```

> PENTING: Jaga kerahasiaan file wallet.json Anda! File ini berisi private key yang memberikan akses penuh ke dana Anda.
> 
▶️ Menjalankan Client
Setelah instalasi dan konfigurasi selesai, jalankan client dengan perintah:
```bash
python client.py
```

(Asumsikan nama file utama Anda adalah client.py)
Anda akan disambut dengan tampilan utama yang menampilkan informasi wallet dan daftar perintah yang tersedia.
🗺️ Navigasi Menu
Gunakan tombol angka atau huruf yang tertera di menu untuk melakukan berbagai aksi:
 * [1] Kirim Transaksi: Memulai alur pengiriman token standar.
 * [4] Enkripsi Saldo: Memulai alur untuk menyembunyikan saldo publik Anda.
 * [S] Staking: Membuka submenu untuk staking, unstaking, dan klaim reward.
 * [D] Deploy Contract: Memulai alur untuk deploy smart contract baru.
 * [0] Keluar: Menutup aplikasi.
📝 Contoh Alur Kerja
1. Deploy Smart Contract
 * Siapkan file bytecode smart contract Anda yang sudah terkompilasi (misalnya my_contract.wasm).
 * Jalankan client.
 * Tekan D untuk masuk ke menu Deploy Contract.
 * Masukkan path lengkap ke file .wasm Anda saat diminta.
 * Konfirmasi detail transaksi.
 * Client akan mengirim transaksi dan menampilkan alamat kontrak baru jika berhasil.
2. Melakukan Transfer Privat
 * Pastikan Anda memiliki saldo terenkripsi. Jika tidak, gunakan menu [4] untuk mengenkripsi sebagian saldo publik Anda.
 * Tekan [6] untuk masuk ke menu Private Transfer.
 * Masukkan alamat penerima dan jumlah yang ingin dikirim.
 * Konfirmasi transaksi. Token akan dikirim secara privat dan dapat diklaim oleh penerima menggunakan menu [7].

## 🤝 Berkontribusi
Kontribusi dari komunitas sangat kami hargai! Jika Anda ingin membantu mengembangkan proyek ini, silakan ikuti langkah-langkah berikut:
 * Fork repositori ini.
 * Buat branch baru untuk fitur Anda (git checkout -b fitur/nama-fitur).
 * Lakukan perubahan dan commit (git commit -m 'Menambahkan fitur X').
 * Push ke branch Anda (git push origin fitur/nama-fitur).
 * Buat Pull Request baru.
