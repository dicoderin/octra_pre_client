# Octra CLI Wallet - Terminal Wallet untuk Jaringan Octra

Sebuah dompet command-line interaktif untuk berinteraksi dengan blockchain **Octra Network**. Dompet ini menyediakan antarmuka terminal yang kaya fitur dengan visualisasi transaksi real-time, manajemen aset, dan kemampuan transaksi batch.

```bash
#!/usr/bin/env python3
# Kode lengkap tersedia di atas
```

## 🌟 Fitur Utama

- **Antarmuka Pengguna Terminal yang Kaya**:
  - Visualisasi saldo dan transaksi real-time
  - Warna dan tata letak intuitif
  - Animasi spinner untuk operasi jaringan

- **Manajemen Aset**:
  - Cek saldo dan nonce
  - Riwayat transaksi dengan status real-time
  - Detail transaksi lengkap (hash, jumlah, penerima)

- **Transaksi**:
  - Pengiriman single transaction
  - **Multi-send transaction** (batch ke banyak alamat)
  - **Fitur Baru**: Kirim 1 OCT ke banyak alamat dari file `list.txt`
  - Estimasi biaya transaksi otomatis

- **Keamanan**:
  - Ekspor kunci pribadi (dengan peringatan keamanan)
  - Penyimpanan dompet terenkripsi
  - Validasi alamat OCTRA

- **Fitur Tambahan**:
  - Manajemen transaksi tertunda (staging)
  - Penyortiran transaksi berdasarkan waktu
  - Pelacakan transaksi gagal dan ekspor ke `failed.txt`

## ⚙️ Persyaratan Sistem

- Python 3.7+
- Dependencies:
  ```bash
  pip install aiohttp base58 pyperclick nacl
  ```

## 🚀 Memulai

1. **Siapkan dompet**:
   ```bash
   echo '{"priv":"your_private_key","addr":"your_address","rpc":"https://octra.network"}' > wallet.json
   ```

2. **Jalankan aplikasi**:
   ```bash
   chmod +x cli.py
   ./cli.py
   ```

3. **Gunakan menu utama**:
   ```
   [1] send tx       [4] export keys
   [2] refresh       [5] clear history
   [3] multi send    [6] send 1 OCT to list
   ```

## 🆕 Fitur Baru: Kirim ke Banyak Alamat

Fitur unggulan terbaru memungkinkan pengiriman 1 OCT ke banyak alamat sekaligus dari file teks:

1. Buat file `list.txt` berisi alamat-alamat OCTRA (satu alamat per baris)
2. Pilih menu `[6] send 1 OCT to list`
3. Sistem akan:
   - Otomatis validasi alamat
   - Hitung total OCT yang dibutuhkan
   - Proses pengiriman batch
   - Simpan alamat gagal ke `failed.txt`

```plaintext
found 120 valid addresses in list.txt
total required: 123.456789 OCT
[23/120] sent 1 OCT to oct1abc...xyz
completed: 118 success, 2 failed
```

 ##🛠️ Teknologi Dibawah Hood

- **Asynchronous** I/O dengan `aiohttp` untuk kinerja maksimal
- **Kriptografi** menggunakan `nacl.signing` untuk keamanan transaksi
- **Manajemen Thread** dengan `ThreadPoolExecutor`
- **Antarmuka Terminal** dinamis dengan kontrol kursor ANSI
- **Format Transaksi** sesuai standar Octra Network

## ⚠️ Catatan Penting

- **Dompet Testnet**: Hanya gunakan dengan token testnet!
- **Jaga Kunci Pribadi**: Jangan pernah bagikan `wallet.json`
- **Konfirmasi Transaksi**: Selalu verifikasi detail sebelum mengirim
- **Backup Reguler**: Simpan salinan aman dari `wallet.json`

 ##📜 Lisensi

```plaintext
Octra CLI Wallet - Terminal Wallet for Octra Network
Copyright (C) 2024 Octra Project

Program ini adalah perangkat lunak gratis: Anda dapat menyebarluaskannya dan/atau memodifikasi
dibawah ketentuan GNU General Public License versi 3.
```

> **Disclaimer**: Ini adalah versi pengembangan (dev) - laporkan masalah di [tracker issue](https://github.com/octra/cli-wallet/issues)
