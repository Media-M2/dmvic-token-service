from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel

app = FastAPI()

# Define the expected structure of the incoming POST body
class LoginPayload(BaseModel):
    username: str      # DMVIC username (email)
    password: str      # DMVIC password

# FastAPI route to get DMVIC token
@app.post("/get-token")
def get_token(payload: LoginPayload):
    # ✅ Correct DMVIC UAT API URL (from your API docs section 4.1)
    login_url = "https://uat-api.dmvic.com/api/V1/Account/Login"

    # ✅ These PEM files should be uploaded alongside main.py in your Render project
    cert_path = "client_cert.pem"  # Certificate PEM file
    key_path = "client_key.pem"    # Private Key PEM file

    try:
        # Create a session for HTTPS requests with mTLS
        session = requests.Session()
        session.verify = True  # Enforce SSL verification

        # POST to DMVIC login API using JSON body and required headers
        response = session.post(
            login_url,
            json={
                "Username": payload.username,     # ✅ Must match DMVIC expected JSON key
                "Password": payload.password
            },
            headers={
                "ClientID": payload.client_id     # ✅ Must be in the headers
            },
            cert=(cert_path, key_path)            # ✅ Use mTLS (certificate + key)
        )

        # If login successful (status code 200), return full JSON response (includes token)
        if response.status_code == 200:
            return response.json()
        else:
            # DMVIC API responded with an error, forward that to the client
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except Exception as e:
        # Handle internal errors (e.g., file not found, SSL issues, etc.)
        raise HTTPException(status_code=500, detail=str(e))
