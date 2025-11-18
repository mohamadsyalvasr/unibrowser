# 🌀 UniBrowse — Cross-Browser Personal Sync Tool

UniBrowse is a **personal tool** that synchronizes browser data (bookmarks, history, etc.) from multiple browsers such as **Chrome** and **Firefox**, and stores everything into a single **FastAPI + SQLite backend** locally.

This tool consists of:

* **Backend API (FastAPI)** — storage & database management.
* **Chrome/Chromium Extension** — data grabber.
* **Firefox Extension** — data grabber.
* Features:

  * Manual sync from extension UI.
  * **Auto Sync** based on a configurable minute interval.
  * Stores complete bookmark data:

    * title
    * url
    * folder_path
    * created_at
    * browser_name
    * device_name
    * profile_name

---

## ✨ Key Features

* Sync bookmarks from **Chrome / Edge / Brave / Opera** (Manifest V3)
* Sync bookmarks from **Firefox** (WebExtension)
* Input **Browser Name**, **Device Name**, **Profile Name** from extension UI
* Auto-sync every X minutes (configurable)
* Simple and fast backend (FastAPI + SQLite)
* All data stays **local** on your machine
* Great for users with many browsers / many devices

---

# 📁 Project Structure

```
unibrowse/
│
├─ backend/
│   └─ main.py          # FastAPI server + SQLite
│
├─ chrome-extension/
│   ├─ manifest.json
│   ├─ background.js
│   ├─ popup.html
│   └─ popup.js
│
└─ firefox-extension/
    ├─ manifest.json
    ├─ background.js
    ├─ popup.html
    └─ popup.js
```

---

# 🚀 How to Run

Below are the complete steps to run everything locally.

---

# 1. Backend — FastAPI + SQLite

### Install dependencies

```bash
cd backend
pip install fastapi uvicorn
```

### Run server

```bash
python main.py
# or
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Access:

* Swagger Docs → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* View bookmarks → [http://127.0.0.1:8000/api/bookmarks](http://127.0.0.1:8000/api/bookmarks)

---

# 2. Chrome / Edge / Brave Extension

### Install

1. Open Chrome → `chrome://extensions`
2. Enable **Developer Mode**
3. Click **Load Unpacked**
4. Select the **chrome-extension/** folder

### Usage

* Click the extension icon
* Fill in:

  * Browser Name
  * Device Name
  * Profile Name
* (Optional) enable **Auto Sync** and set the interval
* Click **Sync Now**

---

# 3. Firefox Extension

### Install

1. Open Firefox → `about:debugging#/runtime/this-firefox`
2. Click **Load Temporary Add-on…**
3. Select `manifest.json` from the **firefox-extension/** folder

### Usage

Same as Chrome.

---

# 📝 API Endpoint

### POST /api/sync/bookmarks

Payload:

```json
{
  "browser_name": "Chrome",
  "device_name": "Home Laptop",
  "profile_name": "Default",
  "bookmarks": [
    {
      "title": "GitHub",
      "url": "https://github.com/",
      "folder_path": "Bookmarks Bar/Dev",
      "created_at": "2023-05-12T10:00:00Z"
    }
  ]
}
```

Response:

```json
{
  "status": "ok",
  "inserted": 50,
  "updated": 10,
  "browser_id": 1
}
```

---

# 📊 Database Schema (SQLite)

### Table: browsers

| field        | type   |
| ------------ | ------ |
| id           | int PK |
| name         | text   |
| device_name  | text   |
| profile_name | text   |

### Table: bookmarks

| field       | type   |
| ----------- | ------ |
| id          | int PK |
| browser_id  | FK     |
| title       | text   |
| url         | text   |
| folder_path | text   |
| created_at  | text   |
| updated_at  | text   |

---

# 🧩 Auto Sync Engine

Chrome uses `chrome.alarms`
Firefox uses `browser.alarms`

The sync interval is stored in browser storage to persist settings.

---

# 🛠 Development Notes

### Change API URL

If the backend runs on a different port:

```js
const API_URL = "http://localhost:5000/api/sync/bookmarks";
```

### Build extension

```bash
zip -r chrome-extension.zip chrome-extension/
zip -r firefox-extension.zip firefox-extension/
```

---

# ❤️ License

MIT
