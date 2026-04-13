import os
from azure.storage.blob import BlobServiceClient

def load_pdfs_from_blob():
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER")

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    os.makedirs("data", exist_ok=True)
    pdf_files = []

    for blob in container_client.list_blobs():
        if blob.name.endswith(".pdf"):
            file_path = os.path.join("data", blob.name)

            with open(file_path, "wb") as f:
                data = container_client.download_blob(blob.name).readall()
                f.write(data)

            pdf_files.append(file_path)

    return pdf_files