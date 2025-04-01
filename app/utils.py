import os

def ensure_upload_folder(path="uploads"):
    """Ensure the uploads folder exists at the given path."""
    if not os.path.exists(path):
        os.makedirs(path)
