# 🔒 UniBrowser Security - Developer Cheat Sheet

Quick reference for developers working with the secure connection.

---

## 🚀 Setup (Copy & Paste)

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run backend
python main.py

# In browser, get token:
curl -X POST http://127.0.0.1:8000/api/auth/token

# Response:
# {"token": "your_token_here", "expires_in": 86400}
```

---

## 🔑 API Endpoints

### Generate Token
```
POST /api/auth/token
Content-Type: application/json

Response: 200 OK
{
  "token": "secure_random_token",
  "expires_in": 86400
}
```

### Sync Bookmarks
```
POST /api/sync/bookmarks
Authorization: Bearer <token>
Content-Type: application/json

Request Body:
{
  "browser_name": "Chrome",
  "device_name": "Laptop",
  "profile_name": "Default",
  "bookmarks": [
    {
      "title": "Google",
      "url": "https://google.com",
      "folder_path": "Favorites",
      "created_at": "2025-11-18T10:30:00Z"
    }
  ]
}

Response: 200 OK
{
  "status": "ok",
  "inserted": 5,
  "updated": 2,
  "browser_id": 1
}

Rate Limit: 10 requests/minute
Returns 429: Too Many Requests if exceeded
Returns 401: Unauthorized if token invalid
```

### List Bookmarks
```
GET /api/bookmarks
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "browser_name": "Chrome",
    "device_name": "Laptop",
    "profile_name": "Default",
    "title": "Google",
    "url": "https://google.com",
    "folder_path": "Favorites",
    "created_at": "2025-11-18T10:30:00Z",
    "updated_at": "2025-11-18T10:30:00Z"
  }
]

Rate Limit: 30 requests/minute
Returns 429: Too Many Requests if exceeded
Returns 401: Unauthorized if token invalid
```

---

## 🔐 Curl Examples

### Get Token
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token \
  -H "Content-Type: application/json"
```

### Sync Bookmarks
```bash
TOKEN="your_token_here"

curl -X POST http://127.0.0.1:8000/api/sync/bookmarks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "browser_name": "Chrome",
    "device_name": "Laptop",
    "profile_name": "Default",
    "bookmarks": [
      {
        "title": "Test",
        "url": "https://test.com",
        "folder_path": "",
        "created_at": null
      }
    ]
  }'
```

### List Bookmarks
```bash
TOKEN="your_token_here"

curl -X GET http://127.0.0.1:8000/api/bookmarks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

---

## 🛠️ Extension Code Snippets

### Chrome: Get Token
```javascript
async function getToken() {
  const resp = await fetch('http://127.0.0.1:8000/api/auth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  
  const data = await resp.json();
  await chrome.storage.sync.set({ auth_token: data.token });
  return data.token;
}
```

### Chrome: Use Token
```javascript
async function syncWithToken(bookmarks) {
  const data = await chrome.storage.sync.get(['auth_token']);
  const token = data.auth_token;
  
  if (!token) {
    token = await getToken();
  }
  
  const resp = await fetch('http://127.0.0.1:8000/api/sync/bookmarks', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      browser_name: 'Chrome',
      device_name: 'Laptop',
      profile_name: 'Default',
      bookmarks: bookmarks
    })
  });
  
  if (resp.status === 401) {
    // Token expired, get new one
    token = await getToken();
    // Retry...
  }
  
  return resp.json();
}
```

### Firefox: Get Token
```javascript
async function getToken() {
  const resp = await fetch('http://127.0.0.1:8000/api/auth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  
  const data = await resp.json();
  await browser.storage.local.set({ auth_token: data.token });
  return data.token;
}
```

---

## 🔍 Debug & Testing

### Test Token Generation
```bash
curl -v -X POST http://127.0.0.1:8000/api/auth/token

# Should see:
# < HTTP/1.1 200 OK
# < content-type: application/json
```

### Test Rate Limiting
```bash
# Run 15 times in 1 minute
for i in {1..15}; do
  curl -X POST http://127.0.0.1:8000/api/sync/bookmarks \
    -H "Authorization: Bearer TEST_TOKEN" \
    -d '{}' &
done

# Should see 401 (invalid token) for first 10
# Then 429 (rate limit) for requests 11-15
```

### Test CORS
```bash
# From JavaScript console on external site:
fetch('http://127.0.0.1:8000/api/bookmarks')

# Should get CORS error (blocked by browser)
```

### View Backend Logs
```
Check terminal where python main.py is running
All requests logged with details
```

### View Extension Logs
```
Chrome: F12 → Application → Background Page (if available)
Firefox: about:debugging → Inspect background script
```

---

## 🚨 Error Codes Quick Ref

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Request processed |
| 401 | Unauthorized | Get new token |
| 403 | Forbidden | Check CORS origin |
| 429 | Too Many Requests | Wait 1 minute |
| 400 | Bad Request | Check request format |
| 422 | Invalid Data | Check required fields |
| 500 | Server Error | Check backend logs |

---

## 🔧 Backend Configuration

### File: `backend/main.py`

Rate Limits:
```python
@limiter.limit("10/minute")
def sync_bookmarks(...):
    # Sync endpoint

@limiter.limit("30/minute")
def list_bookmarks(...):
    # List endpoint
```

CORS:
```python
allow_origins=["http://127.0.0.1", "http://localhost"],
allow_methods=["GET", "POST", "OPTIONS"],
allow_headers=["Content-Type", "Authorization"],
```

Token Hashing:
```python
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
```

---

## 🔐 Security Checklist for Developers

Before committing code:

- [ ] Token included in Authorization header
- [ ] Using Bearer format: `Bearer <token>`
- [ ] Errors handled gracefully
- [ ] 401 triggers token refresh
- [ ] Tokens never logged
- [ ] CORS headers respected
- [ ] Rate limiting respected
- [ ] No hardcoded tokens

---

## 📊 Key Files Map

```
backend/main.py
├── Token Functions
│   ├── hash_token()
│   ├── generate_token()
│   ├── verify_token()
│   └── get_token_from_header()
│
├── Middleware
│   ├── CORSMiddleware
│   ├── TrustedHostMiddleware
│   └── RateLimitExceeded handler
│
└── Endpoints
    ├── POST /api/auth/token
    ├── POST /api/sync/bookmarks
    └── GET /api/bookmarks

chrome-extension/background.js
├── Token Functions
│   ├── getStoredToken()
│   ├── saveToken()
│   ├── isTokenExpired()
│   └── ensureValidToken()
│
└── API Functions
    └── syncBookmarks()

firefox-sync-extension/background.js
├── Token Functions
│   ├── getStoredToken()
│   ├── saveToken()
│   ├── isTokenExpired()
│   └── ensureValidToken()
│
└── API Functions
    └── syncBookmarks()
```

---

## ⚡ Performance Tips

1. **Token Validation**: Cached with LRU (fast)
2. **Rate Limiting**: Fast Redis-like tracking
3. **Database**: Indexed queries
4. **Requests**: Average <100ms per sync

---

## 🔄 Token Refresh Logic

```javascript
async function ensureValidToken() {
  // 1. Get stored token
  let token = await getStoredToken();
  
  // 2. Check expiry (7 days)
  if (token && !isTokenExpired()) {
    return token; // Still valid
  }
  
  // 3. Request new token
  const resp = await fetch('/api/auth/token', {
    method: 'POST'
  });
  
  // 4. Save new token
  const data = await resp.json();
  await saveToken(data.token);
  
  return data.token;
}
```

---

## 🧪 Testing Commands

### Unit Test: Token Generation
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token | jq .
```

### Integration Test: Full Sync
```bash
# 1. Get token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/token | jq -r .token)

# 2. Sync bookmarks
curl -X POST http://127.0.0.1:8000/api/sync/bookmarks \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"browser_name":"Chrome","bookmarks":[]}' | jq .

# 3. List bookmarks
curl -X GET http://127.0.0.1:8000/api/bookmarks \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### Load Test: Rate Limit
```bash
TOKEN="test_token"
ab -n 100 -c 10 \
  -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/api/bookmarks
```

---

## 📚 Related Docs

- Full API Spec: See `SECURITY.md`
- Architecture: See `SECURITY_ARCHITECTURE.md`
- Changes: See `REFACTOR_SUMMARY.md`
- Setup: See `SECURITY_QUICKREF.md`

---

## 🆘 Quick Troubleshooting

**Token Won't Generate**
→ Check backend is running
→ Check firewall not blocking port 8000

**401 Unauthorized**
→ Check Bearer format: `Bearer <token>`
→ Get new token if expired

**429 Too Many Requests**
→ Wait 1 minute
→ Check for retry loops

**CORS Error**
→ Ensure origin is localhost
→ Check browser console for details

---

*Last Updated: 2025-11-18*
*Version: 1.0*
