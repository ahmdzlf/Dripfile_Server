# 🌐 Distributed File Transfer (Dripfile) System using Flask + MySQL + Docker + Nginx Load Balancer

Proyek ini adalah sistem server distribusi file berbasis Python Flask yang berjalan pada dua server terpisah (`server_1` dan `server_2`) menggunakan:
- 🐳 Docker & Docker Compose
- 🐍 Flask (Python)
- 🐬 MySQL (dengan replikasi Master-Master)
- 🌐 Nginx sebagai Load Balancer
- ⚙️ `setup-repl.sh` sebagai script setup replikasi (dijalankan manual via Git Bash di Windows)

---

## 🧱 Arsitektur

```
Host Windows (server_1)
├── Flask App + MySQL DB (db1)
├── Nginx (Load Balancer)
└── setup-repl.sh (manual via Git Bash)

VM Ubuntu Server (server_2)
└── Flask App + MySQL DB (db2)
```

---

## 📦 Prasyarat

### Di Host Windows:
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Git Bash](https://gitforwindows.org/) (untuk menjalankan shell script)
- Akses Internet

### Di VM Ubuntu Server:
- Ubuntu Server 20.04 atau lebih baru
- Install Docker dan Docker Compose:
  ```bash
  sudo apt update
  sudo apt install docker.io docker-compose -y
  sudo systemctl enable docker
  sudo systemctl start docker
  ```

- Pastikan VM bisa **ping ke Host Windows** dan sebaliknya  
  (gunakan network mode **Bridge** di VirtualBox/VMware)

---

## ⚙️ Langkah Instalasi dan Menjalankan

### 🖥️ SERVER_1 (HOST WINDOWS)

1. **Clone repositori**
   ```bash
   git clone https://github.com/ahmdzlf/Dripfile_Server
   cd server_1
   ```

2. **Jalankan container `server_1`**
   ```bash
   docker-compose -f docker-compose-server1.yml up -d --build
   ```

3. **Cek Akses Aplikasi**
   - Buka browser dan akses:  
     [http://localhost](http://localhost)

4. **Jalankan Setup Replikasi MySQL (Manual via Git Bash)**
   - Pastikan `server_2` sudah aktif
   - Buka **Git Bash** di direktori project, lalu jalankan:
     ```bash
     ./setup-repl.sh
     ```

---

### 🖥️ SERVER_2 (VM UBUNTU SERVER)

1. **Clone repositori**
   ```bash
   git clone https://github.com/ahmdzlf/Dripfile_Server
   cd server_2
   ```

2. **Jalankan container `server_2`**
   ```bash
   docker-compose -f docker-compose-server2.yml up -d --build
   ```

3. **Cek Akses Aplikasi**
   - Cek IP address VM:
     ```bash
     ip a
     ```
   - Akses di browser:  
     `http://<IP_VM>:5000`

---

## 🔁 Replikasi MySQL Master-Master

Script `setup-repl.sh` akan secara otomatis:

- Membuat user `repl` di kedua database
- Mengatur `MASTER_LOG_FILE` dan `MASTER_LOG_POS`
- Menghubungkan `db1` dan `db2` sebagai master satu sama lain
- Menjalankan perintah `START SLAVE`

### ✅ Pastikan:
- Port MySQL (`3306`) terbuka dan bisa diakses antar container
- IP address container atau host sudah sesuai di dalam `setup-repl.sh`

---

## 🌐 Konfigurasi NGINX Load Balancer

File konfigurasi: `nginx/nginx.conf`

Contoh:
```nginx
http {
  upstream flask_servers {
    server server_1:5000;
    server server_2:5000;
  }

  server {
    listen 80;

    location / {
      proxy_pass http://flask_servers;
    }
  }
}
```

> Nginx akan otomatis melakukan load balancing antara `server_1` dan `server_2`

---

## 🗂️ Struktur Folder Proyek

```
.
├── server1/
│   ├── app/             # Aplikasi Flask server_1
│   ├── Dockerfile
│   └── my.cnf           # Konfigurasi MySQL server_1
├── server2/
│   ├── app/             # Aplikasi Flask server_2
│   ├── Dockerfile
│   └── my.cnf           # Konfigurasi MySQL server_2
├── nginx/
│   └── nginx.conf       # Konfigurasi Nginx Load Balancer
├── docker-compose-server1.yml
├── docker-compose-server2.yml
├── setup-repl.sh        # Script replikasi MySQL (manual via Git Bash)
└── README.md
```

---

## 🧪 Testing & Troubleshooting

### 🔄 Ping antar container:
```bash
docker exec server_1 ping server_2
```

### 🛠️ Jika `ping` tidak ditemukan:
```bash
apt update && apt install iputils-ping -y
```

### 🔎 Cek status replikasi MySQL:
```bash
docker exec -it server1_db mysql -u root -p
```

Setelah login ke MySQL:
```sql
SHOW SLAVE STATUS\G
```

---

## 👨‍💻 Developer

- Nama: Ahmad_Zulfa_Aulia_Rahman & Kelompok 3
- Proyek: Sistem File Terdistribusi  
- Email: julpaahmad7@gmail.com
