"""Storage abstraction for file uploads (local / S3 stub)."""
import os
from datetime import datetime


class LocalStorage:
    def __init__(self, base_path):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def save(self, file_stream, filename):
        path = os.path.join(self.base_path, filename)
        with open(path, 'wb') as f:
            f.write(file_stream.read())
        return path

    def get_url(self, path):
        # For local dev, return relative path for serving via Flask
        return path


class S3Storage:
    def __init__(self, bucket_name, client=None):
        self.bucket = bucket_name
        self.client = client

    def save(self, file_stream, filename):
        # Placeholder: implement boto3 upload
        raise NotImplementedError('S3Storage.save not implemented')

    def get_url(self, key):
        # Placeholder: return presigned URL
        raise NotImplementedError('S3Storage.get_url not implemented')
