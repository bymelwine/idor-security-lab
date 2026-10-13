
from fastapi.testclient import TestClient
from main import app, sessions

# ==========================================
# IDOR SECURITY LAB
# Automated Security Tests with Pytest
# ==========================================

client = TestClient(app)


# Fonction utilitaire : authentification
def login(username, password):
    response = client.post(
        "/login",
        json={
            "username": username,
            "password": password
        }
    )

    assert response.status_code == 200
    return response.json()["access_token"]


# ==========================================
# TEST 1 : Accès légitime d'Alice
# ==========================================
def test_alice_own_document():
    token = login("alice", "AliceDemo2026!")

    response = client.get(
        "/documents/101",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["requested_by"] == "alice"
    assert response.json()["document"]["owner"] == "alice"


# ==========================================
# TEST 2 : Protection contre l'IDOR
# ==========================================
def test_alice_cannot_access_bob_document():
    token = login("alice", "AliceDemo2026!")

    response = client.get(
        "/documents/202",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"
    assert "document" not in response.json()


# ==========================================
# TEST 3 : Accès sans authentification
# ==========================================
def test_unauthenticated_access():
    response = client.get("/documents/101")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


# ==========================================
# TEST 4 : Accès légitime de Bob
# ==========================================
def test_bob_own_document():
    token = login("bob", "BobDemo2026!")

    response = client.get(
        "/documents/202",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["requested_by"] == "bob"
    assert response.json()["document"]["owner"] == "bob"


# ==========================================
# TEST 5 : Tentative d'usurpation d'identité
# ==========================================
def test_identity_spoofing():
    token = login("alice", "AliceDemo2026!")

    response = client.get(
        "/documents/202",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Demo-User": "bob"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"


# ==========================================
# TEST 6 : Jeton de session invalide
# ==========================================
def test_invalid_token_rejected():
    response = client.get(
        "/documents/101",
        headers={
            "Authorization": "Bearer invalid_token"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid session"


# ==========================================
# TEST 7 : Mot de passe incorrect
# ==========================================
def test_wrong_password_rejected():
    response = client.post(
        "/login",
        json={
            "username": "alice",
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
    assert "access_token" not in response.json()


# ==========================================
# TEST 8 : Expiration du jeton de session
# ==========================================
def test_expired_token_rejected():
    # Connexion d'Alice
    token = login("alice", "AliceDemo2026!")

    # Simulation d'une session expirée
    sessions[token]["expires_at"] = 0

    # Tentative d'accès avec le jeton expiré
    response = client.get(
        "/documents/101",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    # Le serveur doit rejeter la session
    assert response.status_code == 401
    assert response.json()["detail"] == "Session expired"

    # Vérifier que le jeton expiré a été supprimé
    assert token not in sessions
