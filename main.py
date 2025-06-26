from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel
import os

app = FastAPI()

# ✅ Define the expected input structure
class LoginPayload(BaseModel):
    username: str      # DMVIC username (email)
    password: str      # DMVIC password
    client_id: str     # DMVIC assigned ClientID

@app.post("/get-token")
def get_token(payload: LoginPayload):
    # ✅ DMVIC UAT login endpoint
    login_url = "https://uat.dmvic.com/api/auth/login"

    # ✅ .pfx file must be uploaded alongside this script
    pfx_path = "BowmanUAT.pfx"

    # ✅ PFX certificate password — paste yours here between the quotes
    cert_password = "cAwjRHWewmzFoOY"  # 👈 make sure this matches your pwd.txt file exactly

    try:
        # ✅ Check if the PFX file exists
        if not os.path.exists(pfx_path):
            raise HTTPException(status_code=500, detail="Certificate file not found: " + pfx_path)

        # ✅ Create session and send POST to DMVIC with mTLS
        session = requests.Session()
        session.verify = True

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
            cert=(pfx_path, cert_password)
        )

        # ✅ Return DMVIC response if OK
        if response.status_code == 200:
            return response.json()

        # ❌ DMVIC responded with an error
        raise HTTPException(status_code=response.status_code, detail=response.text)

    except Exception as e:
        # ❌ Catch all other internal or certificate errors
        raise HTTPException(status_code=500, detail=str(e))
