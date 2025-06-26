from fastapi import FastAPI, HTTPException, Header
import requests
from pydantic import BaseModel

app = FastAPI()

# Define the expected JSON body with exact keys as per DMVIC API spec
class LoginPayload(BaseModel):
    Username: str   # DMVIC account username (must match case)
    Password: str   # DMVIC account password (must match case)

# Endpoint to handle token requests
@app.post("/get-token")
def get_token(payload: LoginPayload, ClientID: str = Header(...)):
    # DMVIC API login URL (from latest docs)
    login_url = "https://uat-api.dmvic.com/api/V1/Account/Login"

    # PEM certificate files required for mutual TLS (already extracted from .pfx)
    cert_path = "client_cert.pem"  # The public certificate
    key_path = "client_key.pem"    # The private key

    try:
        # Make the secure POST request using mTLS
        response = requests.post(
            login_url,
            json={
                "Username": payload.Username,  # Match DMVIC casing exactly
                "Password": payload.Password
            },
            headers={
                "ClientID": ClientID,                  # Sent as a custom header
                "Content-Type": "application/json"     # Tell DMVIC you're sending JSON
            },
            cert=(cert_path, key_path),  # Attach the certificate and key for mTLS
            verify=True                  # Enforce valid SSL/TLS certificate
        )

        # If successful, return the response from DMVIC
        if response.status_code == 200:
            return response.json()
        else:
            # DMVIC returned an error (e.g. invalid credentials)
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except Exception as e:
        # Catch any unexpected errors (e.g. file not found, request error)
        raise HTTPException(status_code=500, detail=str(e))
