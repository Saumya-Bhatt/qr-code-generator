import json
import os
from datetime import datetime

import requests
import streamlit as st
import streamlit_authenticator as stauth
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv('BACKEND_URL')
authenticator = stauth.Authenticate(
    credentials=json.loads(os.getenv("WHITE_LISTED_USER", "{}")),
    cookie_name=os.getenv('COOKIE_NAME'),
    cookie_key=os.getenv('COOKIE_KEY'),
    cookie_expiry_days=int(os.getenv('COOKIE_EXPIRY_DAYS'))
)
name, authentication_status, username = authenticator.login('main', captcha=True)


if authentication_status:

    authenticator.logout('Logout', 'main')
    st.caption(f'Welcome *{name}*')

    st.title("QR Code Generator")

    request_col, response_col = st.columns([2, 1])
    request_col.write("Convert any static document to a publicly available QR code.")

    uploaded_file = request_col.file_uploader(
        "Upload document (less than 10 MB)", accept_multiple_files=False, type=["jpg", "jpeg", "png", "pdf"]
    )
    submit_request = request_col.button("Generate QR code")


    if uploaded_file is not None and submit_request:
        request_file = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        data = {"user":username}
        response = requests.post(
            url=f"{BACKEND_URL}/upload",
            files=request_file,
            data=data,
            headers={"accept": "application/json"},
        )
        if response.status_code == 200:
            file_content = response.content
            returned_filename = f"{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.png"
            response_col.image(file_content, caption=returned_filename)
            response_col.download_button(
                label="Download QR code PNG",
                data=file_content,
                file_name=returned_filename,
                mime="image/png",
            )
        else:
            response_col.error(f"Failed to upload file: {response.status_code}")
            response_col.write(response.text)


elif authentication_status is False:
    st.error('Username/password is incorrect')

elif authentication_status is None:
    st.info('Please enter your username and password')
