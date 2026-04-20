#!/bin/bash
# Generates Trino catalog files from templates using .env values

if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Copy .env.example to .env and fill in your values."
    exit 1
fi

source .env

mkdir -p trino/etc/catalog

# Generate iceberg.properties
sed "s/S3_ACCESS_KEY_PLACEHOLDER/${S3_ACCESS_KEY}/g; s/S3_SECRET_KEY_PLACEHOLDER/${S3_SECRET_KEY}/g" \
    trino/etc/catalog/iceberg.properties.template > trino/etc/catalog/iceberg.properties

# Generate hive.properties
sed "s/S3_ACCESS_KEY_PLACEHOLDER/${S3_ACCESS_KEY}/g; s/S3_SECRET_KEY_PLACEHOLDER/${S3_SECRET_KEY}/g" \
    trino/etc/catalog/hive.properties.template > trino/etc/catalog/hive.properties

echo "✅ Trino catalog files generated successfully"
echo "Now run: docker compose up -d"
