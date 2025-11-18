# Security Implementation Guide

## Overview
This document describes the security enhancements implemented for the extension-to-backend connection in UniBrowser.

## Security Features Implemented

### 1. **Token-Based Authentication**
- Extensions must obtain an authentication token before syncing
- Tokens are validated server-side using SHA-256 hashing
- Tokens automatically refresh every 7 days
- 401 Unauthorized errors trigger token renewal

### 2. **Rate Limiting**
- Bookmark sync: **10 requests per minute**
- Bookmark list: **30 requests per minute**
- Prevents abuse and DDoS attacks

### 3. **CORS Restrictions**
- Only `http://127.0.0.1` and `http://localhost` allowed
- Methods restricted to: `GET`, `POST`, `OPTIONS`
- Headers restricted to: `Content-Type`, `Authorization`

### 4. **Trusted Host Verification**
- Only localhost connections accepted
- Prevents requests from external hosts

### 5. **Secure Headers**
- Content-Type validation
- Authorization header requirements
- WWW-Authenticate header in 401 responses

### 6. **Content Security Policy (CSP)**
- `script-src 'self'` - Only inline scripts from extension
- `object-src 'self'` - Only extension objects

## Setup Instructions

### Step 1: Install Dependencies
```bash
pip install fastapi uvicorn slowapi pydantic
```

### Step 2: Start Backend Server
```bash
python backend/main.py
```

The backend will start on `http://127.0.0.1:8000`

### Step 3: Generate Authentication Token
First, get a token via the token endpoint:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token
```

Response:
```json
{
  "token": "your_secure_token_here",
  "expires_in": 86400
}
```

### Step 4: Configure Extension
The extension will automatically:
1. Request a token when first used
2. Store token in browser storage
3. Include token in all sync requests
4. Refresh token every 7 days

### Step 5: Sync Bookmarks
Extensions will automatically use the token in requests:

```bash
# Example request with token
curl -X POST http://127.0.0.1:8000/api/sync/bookmarks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "browser_name": "Chrome",
    "device_name": "Laptop",
    "profile_name": "Default",
    "bookmarks": []
  }'
```

## API Endpoints

### `POST /api/auth/token`
**Description**: Generate a new authentication token
**Authentication**: None required
**Rate Limit**: No limit
**Response**:
```json
{
  "token": "string",
  "expires_in": 86400
}
```

### `POST /api/sync/bookmarks`
**Description**: Sync bookmarks from extension
**Authentication**: Bearer token required
**Rate Limit**: 10 requests/minute
**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```
**Request Body**:
```json
{
  "browser_name": "string",
  "device_name": "string",
  "profile_name": "string",
  "bookmarks": [
    {
      "title": "string",
      "url": "string",
      "folder_path": "string",
      "created_at": "ISO8601 timestamp"
    }
  ]
}
```

### `GET /api/bookmarks`
**Description**: List all synced bookmarks
**Authentication**: Bearer token required
**Rate Limit**: 30 requests/minute
**Headers**:
```
Authorization: Bearer <token>
```

## HTTPS Setup (Optional but Recommended)

For production use, enable HTTPS:

### Generate Self-Signed Certificate:
```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

### Update `main.py`:
```python
uvicorn.run(
    "main:app",
    host="127.0.0.1",
    port=8000,
    ssl_keyfile="key.pem",
    ssl_certfile="cert.pem"
)
```

### Update Extension URLs:
Change `API_URL` from `http://` to `https://` in:
- `chrome-extension/background.js`
- `firefox-sync-extension/background.js`

## Token Management

### Token Lifecycle
1. **Created**: Via `/api/auth/token` endpoint
2. **Stored**: In browser storage (encrypted by browser)
3. **Validated**: SHA-256 hash checked against `auth_tokens.txt`
4. **Expired**: After 7 days of inactivity
5. **Refreshed**: Automatically when needed

### Token Storage Locations
- **Backend**: `auth_tokens.txt` (hashed tokens)
- **Chrome**: `chrome.storage.sync` (encrypted)
- **Firefox**: `browser.storage.local` (encrypted)

## Security Best Practices

### For Developers
- ✅ Never commit tokens to version control
- ✅ Use environment variables for sensitive config
- ✅ Keep FastAPI and dependencies updated
- ✅ Monitor `auth_tokens.txt` for suspicious activity
- ✅ Rotate tokens periodically

### For Users
- ✅ Keep browser extensions updated
- ✅ Only run backend on trusted networks
- ✅ Use HTTPS for production deployments
- ✅ Backup `auth_tokens.txt` securely

## Troubleshooting

### "Missing authorization token" Error
**Solution**: Ensure Authorization header is included
```
Authorization: Bearer <token>
```

### "Invalid or expired token" Error
**Solution**: Generate a new token via `/api/auth/token`

### "Too many requests" Error (429)
**Solution**: Wait 1 minute before retrying

### CORS Error
**Solution**: Ensure you're accessing from:
- `http://127.0.0.1`
- `http://localhost`

## Monitoring & Logging

The backend logs important security events:
- Token generation
- Authentication failures
- Rate limit violations
- CORS policy violations

View logs in the terminal where `main.py` is running.

## Future Enhancements

- [ ] OAuth2 flow support
- [ ] JWT token implementation
- [ ] Encrypted token storage
- [ ] Request signing/validation
- [ ] Audit logging to database
- [ ] Device fingerprinting
