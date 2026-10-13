
import secrets
import time

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from pwdlib import PasswordHash

app = FastAPI(title="IDOR Security Lab - Secure Version")

password_hash = PasswordHash.recommended()
security = HTTPBearer(auto_error=False)

# Comptes fictifs du laboratoire uniquement
users = {
    "alice": {
        "password_hash": password_hash.hash("AliceDemo2026!")
    },
    "bob": {
        "password_hash": password_hash.hash("BobDemo2026!")
    }
}

# Documents fictifs
documents = {
    101: {
        "owner": "alice",
        "title": "Alice Private Document",
        "content": "Confidential notes belonging to Alice"
    },
    202: {
        "owner": "bob",
        "title": "Bob Private Document",
        "content": "Confidential notes belonging to Bob"
    }
}

# Sessions stockées temporairement en mémoire
sessions = {}
SESSION_DURATION = 1800  # 30 minutes


class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/")
def home():
    return {"message": "Secure IDOR Security Lab is running"}


@app.post("/login")
def login(credentials: LoginRequest):
    user = users.get(credentials.username)

    if user is None or not password_hash.verify(
        credentials.password,
        user["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # Jeton aléatoire créé côté serveur
    token = secrets.token_urlsafe(32)

    sessions[token] = {
        "username": credentials.username,
        "expires_at": time.time() + SESSION_DURATION
    }

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": SESSION_DURATION
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    session = sessions.get(credentials.credentials)

    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid session"
        )

    if time.time() >= session["expires_at"]:
        sessions.pop(credentials.credentials, None)
        raise HTTPException(
            status_code=401,
            detail="Session expired"
        )

    return session["username"]


@app.get(
    "/documents/{document_id}",
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Access forbidden"},
        404: {"description": "Document not found"}
    }
)
def get_document(
    document_id: int,
    current_user: str = Depends(get_current_user)
):
    document = documents.get(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Contrôle d'autorisation côté serveur
    if document["owner"] != current_user:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    return {
        "requested_by": current_user,
        "document": document
    }
