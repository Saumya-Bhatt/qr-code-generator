from datetime import datetime

import requests
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

BACKEND_URL = "http://127.0.0.1:8000"
with open('users.secrets.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)
name, authentication_status, username = authenticator.login('main', captcha=True)


if authentication_status:

    authenticator.logout('Logout', 'main')
    st.caption(f'Welcome *{name}*')

    st.title("QR Code Generator")
    st.write("Convert any static document to a publicly available QR code.")

    request_col, response_col = st.columns([2, 1])

    uploaded_file = request_col.file_uploader(
        "Upload document", accept_multiple_files=False, type=["jpg", "jpeg", "png", "pdf"]
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
            returned_filename = f"{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.jpg"
            response_col.image(file_content, caption=returned_filename)
            response_col.download_button(
                label="Download QR code",
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
