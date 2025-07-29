from google.cloud import storage

def upload_file_to_gcs(file_data, filename, bucket_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_string(file_data)
    # If you want public access:
    blob.make_public()
    return blob.public_url
