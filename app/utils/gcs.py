from google.cloud import storage

def upload_file_to_gcs(file_data, filename, bucket_name="3dshapesnap-uploads"):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_string(file_data)
    blob.make_public()  # Comment out if you want to keep private
    return blob.public_url
