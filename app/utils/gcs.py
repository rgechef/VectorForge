# app/utils/gcs.py
import os
from google.cloud import storage

GCS_BUCKET = os.getenv("GCS_BUCKET", "vectorforge-uploads")
GCS_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/etc/secrets/gcp-key.json")

def get_gcs_client():
    return storage.Client.from_service_account_json(GCS_CREDENTIALS)

def upload_to_gcs(file_obj, filename, folder="outputs"):
    client = get_gcs_client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(f"{folder}/{filename}")
    blob.upload_from_file(file_obj)
    blob.make_public()
    return blob.public_url

def download_from_gcs(filename, folder="outputs"):
    client = get_gcs_client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(f"{folder}/{filename}")
    return blob.download_as_bytes()
