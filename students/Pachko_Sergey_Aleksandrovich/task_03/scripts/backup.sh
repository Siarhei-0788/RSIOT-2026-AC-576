#!/bin/bash
# Скрипт резервного копирования Redis
# Вариант 14 - Пачко Сергей Александрович

NAMESPACE="state-230489-v14"
POD_NAME="redis-0"
REDIS_PASSWORD="password123"
BACKUP_PATH="/backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="redis_${TIMESTAMP}.rdb"

echo "Starting Redis backup at $(date)"

# Выполняем SAVE (создаёт snapshot в /data/dump.rdb)
kubectl exec -n ${NAMESPACE} ${POD_NAME} -- redis-cli -a ${REDIS_PASSWORD} SAVE

# Копируем dump.rdb в backup папку
kubectl cp ${NAMESPACE}/${POD_NAME}:/data/dump.rdb /tmp/${BACKUP_FILE}

# Здесь можно добавить загрузку в S3

echo "Backup completed: ${BACKUP_FILE}"