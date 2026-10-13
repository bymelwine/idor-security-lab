
# IDOR Security Lab
[![API Security Tests](https://github.com/bymelwine/idor-security-lab/actions/workflows/security-tests.yml/badge.svg?branch=main)](https://github.com/bymelwine/idor-security-lab/actions/workflows/security-tests.yml)

A hands-on cybersecurity project demonstrating how Insecure Direct Object Reference (IDOR) vulnerabilities occur in REST APIs, how they can be identified, and how to remediate them using server-side authorization controls.

Built with Python, FastAPI, and Pytest.

## Project Objectives

- Understand IDOR and Broken Object Level Authorization (BOLA).
- Reproduce unauthorized access in a controlled local environment.
- Implement object-level authorization checks.
- Introduce password hashing using Argon2.
- Implement server-side session management.
- Automate security regression tests.

## Technologies

- Python 3.11
- FastAPI
- Uvicorn
- Pytest
- HTTPX
- pwdlib / Argon2
- Burp Suite Community Edition

## Vulnerability Demonstration

The initial API included two fictional users:

| User | Document ID | Owner |
|------|-------------|-------|
| Alice | 101 | Alice |
| Bob | 202 | Bob |

The vulnerable endpoint retrieved documents without checking ownership.

Example:

GET /documents/202
X-Demo-User: alice

The application returned Bob's document to Alice.

This demonstrated missing object-level authorization. The original demo identity header was also untrusted.

## Security Remediation

The improved implementation includes:

1. Argon2 password hashing and verification.
2. Random bearer session tokens generated server-side.
3. Session expiration after 30 minutes.
4. Authentication checks for protected endpoints.
5. Object ownership verification before returning private data.
6. HTTP 401 responses for invalid or expired sessions.
7. HTTP 403 responses for unauthorized document access.

The application no longer trusts the X-Demo-User header for authentication.

## Installation

Clone the repository and create a Python virtual environment.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Running the API

```powershell
uvicorn main:app --host 127.0.0.1 --port 8000
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## Automated Security Testing

Run the test suite:

```powershell
python -m pytest -v
```

Eight automated tests cover:

| Test | Expected Result |
|------|-----------------|
| Alice accesses her document | 200 OK |
| Alice accesses Bob's document | 403 Forbidden |
| Unauthenticated access | 401 Unauthorized |
| Bob accesses his document | 200 OK |
| Identity spoofing via header | 403 Forbidden |
| Invalid session token | 401 Unauthorized |
| Incorrect password | 401 Unauthorized |
| Expired session token | 401 Unauthorized |

**Latest local test result: 8/8 passed.**

## Security Limitations

This project is an educational demonstration, not a production-ready authentication system.

- Users and test passwords are defined in source code.
- Sessions are stored in process memory.
- Password hashes are regenerated on application startup.
- Rate limiting, persistent session storage, and full account management are not implemented.
- The application is intended to run locally on 127.0.0.1.

A production application requires additional security controls, secure secret management, HTTPS, monitoring, and thorough security testing.

## Key Lessons

Authentication and authorization are different security controls.

A valid session does not automatically grant access to every resource.

Every protected endpoint must verify that the authenticated user is authorized to perform the requested operation on the specific resource.

## Disclaimer

This project is intended exclusively for cybersecurity education, defensive research, and authorized testing.

All accounts and documents are fictional.
