import json
import os

import firebase_admin
import segno
import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
from firebase_admin import credentials, storage

load_dotenv()

app = FastAPI()
firebaseConfig = json.loads(os.getenv("FIREBASE_CREDENTIALS", "{}"))
try:
    firebase_admin.initialize_app(
        credential=credentials.Certificate(firebaseConfig),
        options={"storageBucket": "qr-code-generator-f0b11.appspot.com"},
    )
except Exception:
    print("Firebase app already initialized")
bucket = storage.bucket()


async def _upload_file(folder_name: str, file: UploadFile, public: bool = False):
    blob = bucket.blob(f"{folder_name}/{file.filename}")
    blob.upload_from_file(file.file, content_type=file.content_type)
    if public:
        blob.make_public()
        return blob.public_url


async def _generate_qr_image(link: str, file_name: str):
    qr_file_name = f"{file_name}.png"
    qr_code = segno.make(link)
    qr_code.save(qr_file_name)
    return qr_file_name


def _clean_up(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)


@app.get("/")
async def health():
    return "Server Running"


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    file_name = file.filename
    url = await _upload_file("applications", file, public=True)
    qr_file_name = await _generate_qr_image(url, file_name)
    background_tasks.add_task(_clean_up, qr_file_name)
    return FileResponse(qr_file_name, media_type="image/png")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
