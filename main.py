from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import traceback
import os

app = FastAPI()

# ✅ Define the structure of the expected request payload
class LoginPayload(BaseModel):
    username: str      # DMVIC username (email)
    password: str      # DMVIC password
    client_id: str     # Your assigned DMVIC ClientID

@app.post("/get-token")
def get_token(payload: LoginPayload):
    # ✅ DMVIC UAT token endpoint
    login_url = "https://uat.dmvic.com/api/auth/login"

    # ✅ Path to your .pfx certificate file (must be uploaded in the same folder)
    pfx_path = "BowmanUAT.pfx"

    # ✅ Paste the password from your pwd.txt file exactly between the quotes
    cert_password = "cAwjRHWewmzFoOY"  # 👈 Make sure this is correct

    try:
        # ✅ Confirm the .pfx file exists
        if not os.path.exists(pfx_path):
            raise HTTPException(status_code=500, detail=f"Certificate file not found: {pfx_path}")

        # ✅ Create a secure session and call DMVIC
        session = requests.Session()
        session.verify = True  # Enables SSL verification

        response = session.post(
            login_url,
            json={
                "username": payload.username,
                "password": payload.password
            },
            headers={
                "ClientID": payload.client_id,
                "Content-Type": "application/json"
            },
            cert=(pfx_path, cert_password)  # This activates mutual TLS
        )

        # ✅ Return token if successful
        if response.status_code == 200:
            return response.json()

        # ❌ DMVIC returned an error (401, 403, 400, etc.)
        raise HTTPException(status_code=response.status_code, detail=response.text)

    except Exception as e:
        # 🛠 Print full error trace to Render logs for debugging
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
