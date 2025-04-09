# 🛡️ Secure Data Encryption System (Streamlit)

A **Streamlit-based secure data storage and retrieval app** that allows users to:
- Encrypt and store sensitive data using a **passkey**.
- Decrypt stored data using the **correct passkey**.
- Redirect to a login page after **multiple failed attempts** for added security.
- All data is stored **in-memory** (no external database required).

---

## 🚀 Features

- 🔐 **AES-based encryption** using Python's `cryptography` (Fernet).
- 🔑 **SHA-256 passkey hashing** for secure verification.
- ❗ **Three-strike lockout** mechanism for failed decryption attempts.
- 🔁 **Login reauthorization** after failed attempts.
- 🧠 Intuitive and user-friendly **Streamlit UI**.
- 🧪 Fully **in-memory** solution — perfect for demos and learning encryption basics.

---

## 📦 Tech Stack

| Component       | Description                    |
|----------------|--------------------------------|
| `Streamlit`     | UI Framework                   |
| `cryptography`  | Fernet encryption module       |
| `hashlib`       | SHA-256 hashing of passkeys    |
| `Python`        | Core logic and encryption flow |

---

## 🖥️ How It Works

### 1. Store Data
- User enters plain text and a passkey.
- The text is encrypted using **Fernet** and the passkey is hashed using **SHA-256**.
- Both are stored in an in-memory dictionary.

### 2. Retrieve Data
- User enters the **encrypted text** and their **original passkey**.
- If the hashed passkey matches, data is decrypted and displayed.
- If not, a failed attempt is counted.
- On 3rd failed attempt, the user is redirected to the **login page**.

### 3. Login Page
- Requires a hardcoded admin password (`admin123`) to reset failed attempts.

---

## 🛠️ Installation & Usage

### 🔧 Requirements
- Python 3.8+
- Required packages:
  ```bash
  pip install streamlit cryptography
