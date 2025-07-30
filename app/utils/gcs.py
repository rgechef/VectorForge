import os
from google.cloud import storage

# Load GCP credentials automatically from Render's secret mount
GCP_CREDENTIALS_PATH = "/etc/secrets/gcp-key.json"
BUCKET_NAME = "vectorforge-uploads"

def get_gcs_client():
    return storage.Client.from_service_account_json(GCP_CREDENTIALS_PATH)

async def upload_to_gcs(file, folder="outputs"):
    client = get_gcs_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"{folder}/{file.filename}")
    blob.upload_from_file(file.file, content_type=file.content_type)
    blob_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{folder}/{file.filename}"
    return blob_url

async def download_from_gcs(filename, folder="outputs"):
    client = get_gcs_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"{folder}/{filename}")
    return blob.download_as_bytes()
