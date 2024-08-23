import io
import json
import os

import firebase_admin
import segno
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from firebase_admin import credentials, storage

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


async def _generate_qr_image(link: str):
    qr_code = segno.make(link)
    img_byte_arr = io.BytesIO()
    qr_code.save(img_byte_arr, kind="png", scale=5)
    img_byte_arr.seek(0)
    return img_byte_arr


@app.get("/")
async def health():
    return "Server Running"


@app.post("/upload")
async def upload_file(file: UploadFile = File(...), user: str = Form(...)):
    url = await _upload_file("applications", file, public=True)
    qr_image = await _generate_qr_image(url)
    return StreamingResponse(qr_image, media_type="image/png")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
