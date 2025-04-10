# 🛡️ Secure Data Vault

A Streamlit-based secure data encryption and retrieval system with enhanced protection, lockout mechanisms, and admin override functionality.

## 🔧 Features

- 🔐 **Encrypt Data** with a passkey using Fernet encryption.
- 🔓 **Decrypt Data** using the correct passkey.
- 🚫 **Lock Mechanism**: After 3 failed decryption attempts, the data is locked for 5 minutes.
- 🔄 **Live Countdown**: Shows remaining lock time on failed access attempts.
- 🔑 **Admin Access** to unlock encrypted data early using a master password.
- 💾 **Persistent Storage** in `data.json` and `lock.json`.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Streamlit
- Cryptography

Install dependencies:

```bash
pip install streamlit cryptography
