# Work1: Secure REST API & CVE-2021-34429 Vulnerability Lab
## Project Overview
This project contains two parts:
1. A secure REST API developed with Python Flask, equipped with OWASP Top10 security controls.
2. Vulnerability reproduction and remediation verification for **CVE-2021-34429 (Jetty Unicode Path Traversal)** based on Vulhub and Docker Compose.

---
## API Endpoints & Usage
Base URL: `http://127.0.0.1:5000`

| Method | Endpoint | Description | Access Control |
|--------|----------|-------------|----------------|
| POST | `/auth/login` | Accept username and password, return a valid JWT token after credential check. | Public |
| GET | `/api/data` | Return protected business data. Valid JWT required in request header. | Authenticated only |
| GET | `/api/user` | Return basic user profile information. Valid JWT required. | Authenticated only |
| GET | `/api/profile` | Return detailed user profile information. Valid JWT required. | Authenticated only |


### Example call
Login to get token:
```bash
curl -X POST http://127.0.0.1:5000/auth/login -H "Content-Type: application/json" -d '{"username":"test","password":"test123"}'
```

Access protected resource with token:

```
curl http://127.0.0.1:5000/api/data -H "Authorization: Bearer [YOUR_JWT_TOKEN]"
```

---

## Implemented Security Measures

### 1. Protection against SQL Injection

This project uses an ORM library to interact with the database. All user inputs are passed as parameterised variables instead of being concatenated into raw SQL strings. There is no dynamic SQL construction from user-controllable data, which eliminates SQL injection risks.

### 2. Protection against XSS

All user-controlled content returned by API responses is properly escaped before output. The API sanitises special HTML characters to prevent injection of malicious scripts.

### 3. Authentication Implementation

- User passwords are not stored in plaintext. Passwords are hashed using `bcrypt` with automatic salt generation before being saved into the database.
- After successful login, the server issues a time-limited JWT token.
- A custom middleware checks the validity and expiry of the JWT for every protected endpoint. Requests without a valid token will be rejected with 401 Unauthorized.

---

## SAST & SCA Scan Results

Static security scanning and dependency scanning are integrated into GitHub Actions CI/CD pipeline.

- SAST tool: `bandit` — scans Python source code for insecure patterns.
- SCA tool: `safety` — scans installed Python packages for known CVEs.

> 
> Screenshots of the SAST and SCA reports are attached below:
