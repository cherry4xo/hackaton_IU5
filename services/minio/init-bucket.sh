#!/bin/bash

# Wait for MinIO to be ready
echo "Waiting for MinIO to be ready..."
until curl -s http://minio:9000/minio/health/live; do
  sleep 1
done

echo "MinIO is ready. Setting up bucket..."

# Install mc (MinIO client) if not present
if ! command -v mc &> /dev/null; then
  echo "Installing MinIO client..."
  apt-get update && apt-get install -y wget
  wget https://dl.min.io/client/mc/release/linux-amd64/mc
  chmod +x mc
  mv mc /usr/local/bin/
fi

# Configure mc
mc alias set myminio http://minio:9000 "${MINIO_ROOT_USER}" "${MINIO_ROOT_PASSWORD}"

# Create bucket
echo "Creating bucket: ${MINIO_BUCKET_NAME}"
mc mb myminio/"${MINIO_BUCKET_NAME}" || true

# Set bucket policy to allow public read access for uploaded images
echo "Setting bucket policy..."
cat > /tmp/bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": ["*"]
      },
      "Action": [
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::${MINIO_BUCKET_NAME}/*"
      ]
    }
  ]
}
EOF

mc anonymous set-json /tmp/bucket-policy.json myminio/"${MINIO_BUCKET_NAME}"

echo "Bucket setup completed."
