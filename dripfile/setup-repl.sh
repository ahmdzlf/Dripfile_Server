#!/bin/bash

echo "🕒 Menunggu MySQL container siap..."
sleep 20

# Define mysql client docker run command
MYSQL_CLIENT="docker run --rm mysql:8.0 mysql -h 192.168.18.35 -P 3306 -uroot -proot"

# Ambil posisi binlog dari kedua database
LOG_FILE_1=$(docker exec dripfile-db-1 mysql -uroot -proot -e "SHOW MASTER STATUS\G" | grep File | awk '{print $2}')
LOG_POS_1=$(docker exec dripfile-db-1 mysql -uroot -proot -e "SHOW MASTER STATUS\G" | grep Position | awk '{print $2}')

LOG_FILE_2=$($MYSQL_CLIENT -e "SHOW MASTER STATUS\G" | grep File | awk '{print $2}')
LOG_POS_2=$($MYSQL_CLIENT -e "SHOW MASTER STATUS\G" | grep Position | awk '{print $2}')

if [[ -z "$LOG_FILE_1" || -z "$LOG_FILE_2" ]]; then
  echo "❌ Gagal mengambil posisi binlog. Cek koneksi dan konfigurasi MySQL."
  exit 1
fi

echo "🔁 Konfigurasi replikasi dari db1 (Windows) → db2 (Ubuntu)..."
$MYSQL_CLIENT -e "
STOP SLAVE;
RESET SLAVE ALL;
CHANGE MASTER TO
  MASTER_HOST='192.168.18.14',
  MASTER_USER='replica',
  MASTER_PASSWORD='replica_pass',
  MASTER_LOG_FILE='$LOG_FILE_1',
  MASTER_LOG_POS=$LOG_POS_1;
START SLAVE;
"

echo "🔁 Konfigurasi replikasi dari db2 (Ubuntu) → db1 (Windows)..."
docker exec dripfile-db-1 mysql -uroot -proot -e "
STOP SLAVE;
RESET SLAVE ALL;
CHANGE MASTER TO
  MASTER_HOST='192.168.18.35',
  MASTER_USER='replica',
  MASTER_PASSWORD='replica_pass',
  MASTER_LOG_FILE='$LOG_FILE_2',
  MASTER_LOG_POS=$LOG_POS_2;
START SLAVE;
"

echo "✅ Replikasi Master-Master selesai."
