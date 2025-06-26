import os
import time
import logging
from typing import Optional, Callable
from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)


# OAuth2 scopes required for full access to Drive
SCOPES = ['https://www.googleapis.com/auth/drive']


def get_drive_service(credentials_path: str) -> Resource:
    """
    Authenticate with a service account and return the Google Drive service client.

    Args:
        credentials_path: Path to the service account JSON file.

    Returns:
        Authenticated Google Drive API client (v3).
    """
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=SCOPES
    )
    return build('drive', 'v3', credentials=credentials)


def with_retries(fn: Callable, retries: int = 3, delay: float = 2.0):
    """
    Execute a function with automatic retry handling for transient Drive API errors.

    Args:
        fn: The function to call (typically a lambda).
        retries: Maximum number of attempts.
        delay: Delay between attempts in seconds.

    Returns:
        Result of the function if successful.

    Raises:
        The last exception if all retries fail.
    """
    for attempt in range(1, retries + 1):
        try:
            return fn()
        except HttpError as e:
            logger.warning(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                logger.error("All retry attempts failed.")
                raise


def create_folder(service: Resource, folder_name: str, parent_id: Optional[str] = None) -> str:
    """
    Create a new folder in Google Drive.

    Args:
        service: Authenticated Google Drive service client.
        folder_name: Desired name of the folder.
        parent_id: Optional parent folder ID (for nesting).

    Returns:
        ID of the newly created folder.
    """
    metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    # Add parent folder if nesting is desired
    if parent_id:
        metadata['parents'] = [parent_id]

    try:
        # Create the folder using Drive API with retry wrapper
        folder = with_retries(lambda: service.files().create(
            body=metadata,
            fields='id'
        ).execute())
        folder_id = folder.get('id')
        logger.info(f"Folder '{folder_name}' created with ID: {folder_id}")
        return folder_id
    except HttpError as error:
        logger.exception("Error while creating folder.")
        raise RuntimeError(f"Failed to create folder: {error}") from error


def upload_pdf_to_folder(service: Resource, pdf_path: str, folder_id: str) -> str:
    """
    Upload a PDF file to a specific folder in Google Drive.

    Args:
        service: Authenticated Google Drive client.
        pdf_path: Path to the local PDF file.
        folder_id: Destination Drive folder ID.

    Returns:
        File ID of the uploaded PDF.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF not found at: {pdf_path}")

    metadata = {
        'name': os.path.basename(pdf_path),
        'parents': [folder_id]
    }

    media = MediaFileUpload(pdf_path, mimetype='application/pdf')

    try:
        # Upload the file with retry logic
        uploaded = with_retries(lambda: service.files().create(
            body=metadata,
            media_body=media,
            fields='id'
        ).execute())
        file_id = uploaded.get('id')
        logger.info(f"PDF '{pdf_path}' uploaded successfully with ID: {file_id}")
        return file_id
    except HttpError as error:
        logger.exception("Error while uploading PDF.")
        raise RuntimeError(f"Failed to upload PDF: {error}") from error


def run_upload_flow(credentials_path: str, order_number: str, pdf_path: str,
                    parent_folder_id: Optional[str] = None) -> str:
    """
    Run the complete upload process: authenticate, create folder, and upload PDF.

    Args:
        credentials_path: Path to service account credentials.
        order_number: Used as the name of the folder.
        pdf_path: Full path to the PDF file to be uploaded.
        parent_folder_id: Optional parent folder ID in Drive.

    Returns:
        File ID of the uploaded PDF.
    """
    logger.info("Starting Google Drive upload flow...")

    # Step 1: Get Drive API client
    service = get_drive_service(credentials_path)

    # Step 2: Create destination folder using order number
    logger.info(f"Creating Drive folder for order '{order_number}'")
    folder_id = create_folder(service, folder_name=order_number, parent_id=parent_folder_id)

    # Step 3: Upload the PDF into that folder
    logger.info(f"Uploading PDF file '{pdf_path}' to folder ID '{folder_id}'")
    file_id = upload_pdf_to_folder(service, pdf_path=pdf_path, folder_id=folder_id)

    return file_id
