# Instruksi Penggunaan

Gua tau, lo pada kadang sulit pake bahasa asing, disini gua bakalan kasih info pake bahasa kite-kite orang. Nah, ini adalah petunjuk singkat dan tidak jelas di Armora Grenade ini.
Oke bro, kita akan bahas dari struktur.
---

## Struktur Folder Final Armora Grenade

```
Armora-Grenade/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── libvirt_manager.py
│   │   └── config_manager.py
│   ├── web/
│   │   ├── templates/
│   │   │   └── index.html
│   │   └── static/
│   │       ├── css/
│   │       │   └── style.css
│   │       ├── js/
│   │       │   └── script.js
│   │       └── images/
│   │           ├── logo.png
│   │           └── favicon.ico
│   ├── __init__.py
│   └── main.py              # Flask server
├── bin/
│   └── run_armora_grenade.sh # Skrip untuk menjalankan aplikasi
├── docs/
│   ├── setup.md
│   └── usage.md
├── tests/                   # Opsional, bisa dihapus di deployment
│   ├── __init__.py
│   └── test_libvirt_manager.py
├── .gitignore
├── LICENSE.txt
├── CONTRIBUTING.md
└── README.md
```


## Skrip Launcher: `bin/run_armora_grenade.sh`

Ini adalah "tombol klik" kamu, bro. Skrip `bash` ini akan memastikan lingkungan Python yang tepat aktif dan kemudian menjalankan server Flask.

Penting untuk memberi hak kepada `Armora-Grenade/bin/run_armora_grenade.sh` untuk eksekusi (`chmod +x bin/run_armora_grenade.sh`).

---

## Instruksi Penggunaan (untuk User)

Ini adalah bagian paling penting agar *user* bisa "tinggal klik."

### 1. Persiapan Awal (Hanya Sekali)

Sebelum menjalankan untuk pertama kali, *user* harus memastikan beberapa hal:

* **Instal Python 3 dan `python3-venv`**:
    ```bash
    sudo pkg install python3 py39-venv # Sesuaikan versi py39 dengan versi Python kamu
    ```
* **Instal `libvirt` dan `qemu`**:
    ```bash
    sudo pkg install libvirt qemu
    ```
* **Mulai dan Aktifkan Layanan `libvirtd`**:
    ```bash
    sudo sysrc libvirtd_enable="YES"
    sudo service libvirtd start
    ```
* **Tambahkan User ke Grup `libvirt`**: Ini krusial agar aplikasi bisa berinteraksi dengan `libvirt` tanpa `sudo`.
    ```bash
    sudo pw groupadd libvirt # Jika grup belum ada
    sudo pw groupmod libvirt -m $USER # Ganti $USER dengan username kamu
    # Logout dan Login kembali agar perubahan grup diterapkan
    ```
* **Buat Direktori Log**: Walaupun skrip `run_armora_grenade.sh` akan membuatnya, tidak ada salahnya memastikan.
    ```bash
    mkdir -p Armora-Grenade/logs
    ```

### 2. Mengunduh Aplikasi (Jika dari GitHub)

```bash
git clone https://github.com/Armora-Security/Grenade.git Armora-Grenade
cd Armora-Grenade
```

### 3. Memberi Hak Eksekusi pada Skrip Launcher

```bash
chmod +x bin/run_armora_grenade.sh
```

### 4. Menjalankan Aplikasi (Tinggal Klik!)

Sekarang, untuk menjalankan aplikasinya, *user* hanya perlu masuk ke folder `Armora-Grenade` dan menjalankan skrip launcher:

```bash
cd Armora-Grenade
./bin/run_armora_grenade.sh
```

### 5. Mengakses GUI Web

Setelah menjalankan skrip, kamu akan melihat output di terminal yang mirip dengan:

```
Armora Grenade started successfully with PID 12345.
Access the application at http://127.0.0.1:5000
Log file: /path/to/Armora-Grenade/logs/armora_grenade.log
To stop the application, run: kill 12345
```

Buka *web browser* kamu dan kunjungi **`http://127.0.0.1:5000`**. Voila!

### 6. Menghentikan Aplikasi

Untuk menghentikan aplikasi, cari PID yang tertera di output saat menjalankan (`PID 12345` pada contoh di atas), lalu jalankan:

```bash
kill 12345
```
(Ganti `12345` dengan PID yang sebenarnya.)
