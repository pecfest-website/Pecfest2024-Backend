import os
from google.cloud import storage

def uploadToGcs(file, destinationBlobName):
    storageClient = storage.Client()
    bucket = storageClient.bucket("pecfest")
    blob = bucket.blob(f"website2024/{destinationBlobName}")

    # blob.upload_from_file(file)
    blob.upload_from_filename("namit.jpg")
    blob.make_public()
    return blob.public_url