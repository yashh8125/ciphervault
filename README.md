# 🔐 CipherVault

> A secure, self-hosted password manager with AES-256 encryption, breach detection, and password strength analysis — fully containerized with Docker.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Django](https://img.shields.io/badge/Django-6.0-green?logo=django)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)
![Nginx](https://img.shields.io/badge/Nginx-Reverse%20Proxy-green?logo=nginx)

---

## 📌 About

CipherVault is a full-stack cybersecurity web application built from scratch. It allows users to securely store, manage, and audit their passwords. All passwords are encrypted using AES-256-GCM before being stored in the database — meaning even if the database is compromised, passwords remain unreadable.

---

## ✨ Features

- 🔒 **AES-256-GCM Encryption** — passwords encrypted before storing in MySQL
- 💪 **Password Strength Checker** — real-time scoring with feedback
- 🎲 **Password Generator** — cryptographically secure random passwords
- 🔍 **Breach Detection** — checks against HaveIBeenPwned API using k-anonymity (your password is never sent)
- 👤 **User Authentication** — register, login, logout with Django auth
- 📊 **Security Dashboard** — overview of total, weak, and strong passwords
- 📱 **Mobile Responsive** — hamburger nav, responsive layout

---

## 🏗️ Architecture

```
Browser
   ↓
Nginx (port 80)          ← Reverse proxy
   ↓
Gunicorn (port 8000)     ← Python WSGI server
   ↓
Django                   ← Application logic + AES encryption
   ↓
MySQL 8.0                ← Encrypted password storage
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Django 6.0 |
| Database | MySQL 8.0 |
| Encryption | Python `cryptography` (AES-256-GCM) |
| Server | Gunicorn |
| Reverse Proxy | Nginx |
| Containerization | Docker, Docker Compose |
| Breach Detection | HaveIBeenPwned API |

---

## 📁 Project Structure

```
ciphervault/
├── vault/
│   ├── models.py          # PasswordEntry model
│   ├── views.py           # All views (auth, vault, breach, generator)
│   ├── urls.py            # URL routes
│   ├── crypto.py          # AES-256 encrypt/decrypt + strength checker
│   └── templates/vault/   # HTML templates
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── add_password.html
│       ├── generate.html
│       └── breach_check.html
├── ciphervault/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── requirements.txt
└── .env                   # secrets (not committed)
```

---

## 🚀 Getting Started

### Prerequisites
- Docker
- Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/yashh8125/ciphervault.git
cd ciphervault
```

### 2. Create your `.env` file

```bash
nano .env
```

```env
CIPHER_KEY=your-generated-key-here
MYSQL_DB=ciphervaultdb
MYSQL_USER=vaultuser
MYSQL_PASSWORD=vaultpassword
MYSQL_HOST=db
MYSQL_PORT=3306
```

Generate your `CIPHER_KEY`:
```bash
python3 -c "import os, base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
```

### 3. Build and run

```bash
docker compose up --build
```

### 4. Open in browser

```
http://localhost
```

---

## 🔐 How Encryption Works

1. A random 12-byte **nonce** is generated for every password
2. Password is encrypted using **AES-256-GCM** with the nonce
3. `nonce + ciphertext` is base64 encoded and stored in MySQL
4. On retrieval, nonce is extracted from the first 12 bytes and used to decrypt

```python
# Encrypt
nonce = os.urandom(12)
encrypted = AESGCM(key).encrypt(nonce, password.encode(), None)
stored = base64.urlsafe_b64encode(nonce + encrypted)

# Decrypt
decoded = base64.urlsafe_b64decode(stored)
nonce, ciphertext = decoded[:12], decoded[12:]
password = AESGCM(key).decrypt(nonce, ciphertext, None).decode()
```

---

## 🔍 Breach Detection (k-Anonymity)

CipherVault uses the **HaveIBeenPwned** Pwned Passwords API with k-anonymity — your full password is **never sent** over the network:

1. SHA-1 hash of the password is computed locally
2. Only the **first 5 characters** of the hash are sent to the API
3. API returns all hashes starting with those 5 characters
4. The rest of the matching is done **locally**

---

## 📱 Mobile Support

- Responsive CSS with media queries
- Hamburger navigation menu on mobile
- Touch-friendly buttons and inputs
- Tested on Android Chrome

---

## ⚙️ Environment Variables

| Variable | Description |
|---|---|
| `CIPHER_KEY` | Base64 encoded 32-byte AES key |
| `MYSQL_DB` | MySQL database name |
| `MYSQL_USER` | MySQL username |
| `MYSQL_PASSWORD` | MySQL password |
| `MYSQL_HOST` | MySQL host (use `db` for Docker) |
| `MYSQL_PORT` | MySQL port (default `3306`) |

---

## 🛡️ Security Notes

- Passwords are encrypted **before** hitting the database
- The `CIPHER_KEY` is loaded from environment variables — never hardcoded
- Django's built-in CSRF protection enabled on all forms
- `@login_required` decorator protects all vault views
- Breach check uses k-anonymity — password never leaves your machine in plaintext

---

## 👨‍💻 Author

**Yash Mistry**
- GitHub: [@yashh8125](https://github.com/yashh8125)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
