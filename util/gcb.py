import os
from google.cloud import storage
import base64
from io import BytesIO
import time

def uploadImage(image,name,type='sponser'):
    if image.startswith('data:image/'):
        header, image = image.split(';base64,')
    image_data = base64.b64decode(image)
    image_file = BytesIO(image_data)

    blob_name = f"{type}/{name}/{time.time()}.jpg"
    link = uploadToGcs(image_file, blob_name)
    return link

def uploadToGcs(file, destinationBlobName):
    storageClient = storage.Client()
    bucket = storageClient.bucket("pecfest")
    blob = bucket.blob(f"website2024/{destinationBlobName}")

    blob.upload_from_file(file, content_type='image/jpeg')
    # blob.upload_from_filename("namit.jpg")
    blob.make_public()
    return blob.public_url