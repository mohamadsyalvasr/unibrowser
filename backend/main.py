from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from datetime import datetime
import threading
import os
import ssl

DB_PATH = "sync_browser.db"
API_TOKEN = os.getenv("UNIBROWSER_API_TOKEN", "unibrowser-local-token-2024")
CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"

db_lock = threading.Lock()

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS browsers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                device_name TEXT NOT NULL,
                profile_name TEXT NOT NULL,
                UNIQUE(name, device_name, profile_name)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                browser_id INTEGER NOT NULL,
                title TEXT,
                url TEXT NOT NULL,
                folder_path TEXT,
                created_at TEXT,
                updated_at TEXT,
                UNIQUE(browser_id, url, folder_path),
                FOREIGN KEY (browser_id) REFERENCES browsers(id)
            )
            """
        )
        conn.commit()

class BookmarkIn(BaseModel):
    title: Optional[str] = ""
    url: str
    folder_path: Optional[str] = ""
    created_at: Optional[str] = None

class SyncBookmarksPayload(BaseModel):
    browser_name: str
    device_name: str
    profile_name: str
    bookmarks: List[BookmarkIn]

app = FastAPI(title="Local Browser Sync")

# CORS biar bisa diakses dari extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization[7:]
    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    return token

@app.on_event("startup")
def on_startup():
    init_db()

def get_or_create_browser_id(name: str, device_name: str, profile_name: str) -> int:
    with db_lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id FROM browsers 
            WHERE name = ? AND device_name = ? AND profile_name = ?
            """,
            (name, device_name, profile_name),
        )
        row = cur.fetchone()
        if row:
            return row["id"]
        cur.execute(
            """
            INSERT INTO browsers (name, device_name, profile_name)
            VALUES (?, ?, ?)
            """,
            (name, device_name, profile_name),
        )
        conn.commit()
        return cur.lastrowid

@app.post("/api/sync/bookmarks")
def sync_bookmarks(payload: SyncBookmarksPayload, authorization: Optional[str] = Header(None)):
    verify_token(authorization)
    
    browser_id = get_or_create_browser_id(
        payload.browser_name,
        payload.device_name,
        payload.profile_name,
    )

    now = datetime.utcnow().isoformat()

    with db_lock:
        conn = get_conn()
        cur = conn.cursor()
        inserted = 0
        updated = 0

        for b in payload.bookmarks:
            cur.execute(
                """
                SELECT id FROM bookmarks
                WHERE browser_id = ? AND url = ? AND IFNULL(folder_path, '') = ?
                """,
                (browser_id, b.url, b.folder_path or ""),
            )
            row = cur.fetchone()
            if row:
                cur.execute(
                    """
                    UPDATE bookmarks
                    SET title = ?, created_at = COALESCE(?, created_at), updated_at = ?
                    WHERE id = ?
                    """,
                    (b.title, b.created_at, now, row["id"]),
                )
                updated += 1
            else:
                cur.execute(
                    """
                    INSERT INTO bookmarks (browser_id, title, url, folder_path, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        browser_id,
                        b.title,
                        b.url,
                        b.folder_path or "",
                        b.created_at,
                        now,
                    ),
                )
                inserted += 1

        conn.commit()

    return {
        "status": "ok",
        "inserted": inserted,
        "updated": updated,
        "browser_id": browser_id,
    }

@app.get("/api/bookmarks")
def list_bookmarks(authorization: Optional[str] = Header(None)):
    verify_token(authorization)
    
    with db_lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT b.id, br.name as browser_name, br.device_name, br.profile_name,
                   b.title, b.url, b.folder_path, b.created_at, b.updated_at
            FROM bookmarks b
            JOIN browsers br ON br.id = b.browser_id
            ORDER BY b.updated_at DESC
            """
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]

def generate_self_signed_cert():
    """Generate self-signed certificate if not exists"""
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        return
    
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    from datetime import timedelta
    import ipaddress
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Build certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Local"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Local"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"UniBrowser"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"127.0.0.1"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.IPAddress(ipaddress.IPv4Address(u"127.0.0.1")),
            x509.DNSName(u"localhost"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256(), default_backend())
    
    # Write certificate
    with open(CERT_FILE, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    # Write private key
    with open(KEY_FILE, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    print(f"Generated self-signed certificate: {CERT_FILE}, {KEY_FILE}")

if __name__ == "__main__":
    import uvicorn
    generate_self_signed_cert()
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        ssl_keyfile=KEY_FILE,
        ssl_certfile=CERT_FILE,
        reload=True
    )
