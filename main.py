from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel

app = FastAPI()

# Define the structure of the expected POST request body
class LoginPayload(BaseModel):
    username: str      # Your DMVIC username (email)
    password: str      # Your DMVIC password
    client_id: str     # Your assigned Client ID

@app.post("/get-token")
def get_token(payload: LoginPayload):
    # URL for DMVIC login
    login_url = "https://uat.dmvic.com/api/auth/login"
    
    # Path to the .pfx file — must be in the same directory as this script
    pfx_path = "BowmanUAT.pfx"

    try:
        # 🔐 PASTE YOUR .pfx PASSWORD BELOW (inside the quotes)
        cert_password = "cAwjRHWewmzFoOY"

        # Create a new requests session
        session = requests.Session()
        session.verify = True  # Enforce SSL certificate verification

        # Make the POST request to DMVIC with mutual TLS
        response = session.post(
            login_url,
            json={
                "username": payload.username,
                "password": payload.password
            },
            headers={
                "ClientID": payload.client_id
            },
            cert=(pfx_path, cert_password)  # Use the .pfx file and the password you pasted
        )

        # If login is successful, return the token
        if response.status_code == 200:
            return response.json()
        else:
            # If DMVIC responds with an error, return it
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except Exception as e:
        # Catch and return any unexpected errors
        raise HTTPException(status_code=500, detail=str(e))
