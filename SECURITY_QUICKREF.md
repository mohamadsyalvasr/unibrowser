# UniBrowser Security - Quick Reference

## 🚀 Quick Start

### 1. Install & Run Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 2. Get Authentication Token
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token
# Returns: {"token": "...", "expires_in": 86400}
```

### 3. Load Extension
- **Chrome**: `chrome://extensions/` → Load unpacked → `chrome-extension/`
- **Firefox**: `about:debugging` → This Firefox → Load Temporary Add-on → `firefox-sync-extension/manifest.json`

### 4. Sync Bookmarks
Click extension icon → Click "Sync Now"
(Extensions handle token management automatically)

---

## 🔐 Security Architecture

```
Extension                           Backend
┌─────────────────┐               ┌──────────────────────┐
│ Chrome/Firefox  │               │ FastAPI + SQLite     │
├─────────────────┤               ├──────────────────────┤
│ • Collect Books │──────────────>│ • Token Validation   │
│ • Get Token     │<──────────────│ • Store Books        │
│ • Attach Bearer │               │ • Rate Limiting      │
│ • Send Data     │               │ • CORS Restricted    │
└─────────────────┘               └──────────────────────┘
```

---

## 📋 API Reference

| Method | Endpoint | Auth | Rate Limit | Purpose |
|--------|----------|------|-----------|---------|
| POST | `/api/auth/token` | None | ∞ | Generate token |
| POST | `/api/sync/bookmarks` | Bearer | 10/min | Send bookmarks |
| GET | `/api/bookmarks` | Bearer | 30/min | Retrieve bookmarks |

---

## 🔑 Token Format

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🛡️ Security Checks

✅ Token-based authentication  
✅ Rate limiting (prevents abuse)  
✅ CORS restricted to localhost  
✅ Trusted host verification  
✅ SHA-256 token hashing  
✅ CSP policy enabled  
✅ Input validation  
✅ Error handling  

---

## 📁 File Locations

```
auth_tokens.txt          # Token hashes (backend)
sync_browser.db          # SQLite database (backend)
chrome-extension/        # Chrome extension code
firefox-sync-extension/  # Firefox extension code
backend/main.py          # Secure backend server
SECURITY.md              # Detailed documentation
requirements.txt         # Python dependencies
```

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Generate new token or wait for auto-refresh |
| 429 Too Many Requests | Wait 1 minute, check rate limits |
| CORS Error | Verify running on `http://127.0.0.1:8000` |
| Token Not Stored | Check browser storage permissions |
| Sync Fails | Check backend logs, verify token validity |

---

## 🔄 Token Lifecycle

```
1. Extension starts → No token stored
2. First sync attempt → Request token from /api/auth/token
3. Token received → Save to chrome.storage.sync / browser.storage.local
4. Token attached → Include in Authorization header
5. Days pass... (7 days max)
6. Token expired → Automatically request new one
```

---

## 🌐 Supported Environments

- **OS**: Windows, macOS, Linux
- **Browsers**: Chrome, Firefox
- **Backend**: Python 3.8+
- **Network**: Localhost only (127.0.0.1, localhost)

---

## 📝 Logging

Backend logs include:
- ✓ Token generation events
- ✓ Authentication failures
- ✓ Rate limit violations
- ✓ CORS policy blocks
- ✓ Sync success/failures

View in terminal where `main.py` runs.

---

## 🔒 Security Tips

1. **Never share tokens** - Keep them private
2. **Rotate regularly** - Tokens refresh every 7 days automatically
3. **Use HTTPS** - For production deployments (see SECURITY.md)
4. **Update dependencies** - `pip install --upgrade -r requirements.txt`
5. **Monitor logs** - Watch for suspicious activity

---

## 📚 Full Documentation

See `SECURITY.md` for:
- Detailed setup instructions
- HTTPS configuration
- Troubleshooting guide
- Future enhancements
- Best practices
