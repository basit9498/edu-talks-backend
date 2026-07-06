from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime
from app.config import settings


def get_calendar_service(user):
    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
    )
    return build("calendar", "v3", credentials=creds)


def get_drive_service(user):
    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
    )

    return build("drive", "v3", credentials=creds)


def get_drive_doc_service(user):
    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=[
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/documents",
        ],
    )

    drive_service = build("drive", "v3", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)

    return {"drive_service": drive_service, "docs_service": docs_service}


def create_folder(drive_service):
    folder_metadata = {
        "name": "ai_base_data",
        "mimeType": "application/vnd.google-apps.folder",
    }

    folder = drive_service.files().create(body=folder_metadata, fields="id").execute()

    return folder["id"]


def get_or_create_folder(
    drive_service, folder_name: str = "EduTalk AI Base Documents"
) -> str:
    # Search for folder
    query = (
        f"name='{folder_name}' and "
        "mimeType='application/vnd.google-apps.folder' and "
        "trashed=false"
    )

    results = (
        drive_service.files()
        .list(q=query, spaces="drive", fields="files(id, name)")
        .execute()
    )

    files = results.get("files", [])

    # If exists → return folder id
    if files:
        return files[0]["id"]

    # Else create folder
    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }

    folder = drive_service.files().create(body=folder_metadata, fields="id").execute()

    return folder["id"]


def create_google_doc(
    docs_service, drive_service, folder_id, file_name: str = "AI Base Document"
):
    # Create empty document
    doc = docs_service.documents().create(body={"title": file_name}).execute()

    document_id = doc["documentId"]

    # Move document into folder
    drive_service.files().update(
        fileId=document_id,
        addParents=folder_id,
        removeParents="root",
        fields="id, parents",
    ).execute()

    return document_id


def write_text_to_doc(
    docs_service, document_id, text: str = "Hello 👋\n\nThis document is created by AI."
):
    requests = [
        {
            "insertText": {
                "location": {"index": 1},
                "text": text,
            }
        }
    ]

    docs_service.documents().batchUpdate(
        documentId=document_id, body={"requests": requests}
    ).execute()


# AI Tools calling


async def tool_save_google_drive(user, text: str):
    # Time
    now = datetime.now()
    timestamp = now.strftime("%d-%b-%Y %H:%M")
    file_name = f"AI Base Road {timestamp}"

    # main logic
    access = get_drive_doc_service(user)
    folder_id = get_or_create_folder(access["drive_service"])
    doc_id = create_google_doc(
        access["docs_service"], access["drive_service"], folder_id, file_name=file_name
    )
    write_text_to_doc(access["docs_service"], doc_id, text=text)
