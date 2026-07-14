#!/bin/sh
set -e

TIMESTAMP=$(date -u +"%Y-%m-%dT%H-%M-%S")
BACKUP_DIR="/tmp/backup/${TIMESTAMP}"
S3_PATH="s3://${S3_BUCKET}/backups/${TIMESTAMP}"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

echo "=== Backup iniciado: ${TIMESTAMP} ==="

mkdir -p "${BACKUP_DIR}"

# MongoDB
echo "[1/4] Respaldando MongoDB..."
mongodump --host mongodb --port 27017 --db WalletManager --archive --gzip > "${BACKUP_DIR}/mongodb.gz"
echo "  → MongoDB OK"

# n8n
echo "[2/4] Respaldando n8n..."
tar -czf "${BACKUP_DIR}/n8n.gz" -C /backup n8n 2>/dev/null
echo "  → n8n OK"

# Evolution API
echo "[3/4] Respaldando Evolution API..."
tar -czf "${BACKUP_DIR}/evolution.gz" -C /backup evolution 2>/dev/null
echo "  → Evolution OK"

# Media storage
echo "[4/4] Respaldando Media..."
tar -czf "${BACKUP_DIR}/media.gz" -C /backup media 2>/dev/null
echo "  → Media OK"

# Upload a S3
echo "Subiendo a S3..."
aws s3 cp "${BACKUP_DIR}" "${S3_PATH}/" --recursive --quiet
echo "  → Upload OK"

# Limpiar backups locales
rm -rf "${BACKUP_DIR}"

# Eliminar backups antiguos de S3
echo "Limpiando backups mayores a ${RETENTION_DAYS} días..."
CUTOFF_DATE=$(date -u -d "${RETENTION_DAYS} days" +"%Y-%m-%dT%H-%M-%S" 2>/dev/null || \
  date -u -v-${RETENTION_DAYS}d +"%Y-%m-%dT%H-%M-%S" 2>/dev/null)

if [ -n "${CUTOFF_DATE}" ]; then
  aws s3 ls "s3://${S3_BUCKET}/backups/" | awk '{print $2}' | tr -d '/' | while read -r FOLDER_DATE; do
    if [ -n "${FOLDER_DATE}" ] && [ "${FOLDER_DATE}" \< "${CUTOFF_DATE}" ]; then
      echo "  Eliminando: ${FOLDER_DATE}"
      aws s3 rm "s3://${S3_BUCKET}/backups/${FOLDER_DATE}/" --recursive --quiet
    fi
  done
fi

echo "=== Backup completado: $(date -u) ==="
