import streamlit as st
st.set_page_config(page_title="Secure Data Vault", page_icon="🛡️")

import hashlib
import json
import os
import time
from cryptography.fernet import Fernet
from datetime import datetime

# -----------------------------
# 📁 JSON File Handling
# -----------------------------
DATA_FILE = "data.json"
LOCK_FILE = "lock.json"


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_locks():
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_locks(data):
    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# -----------------------------
# 🔐 Key and Cipher Setup
# -----------------------------
@st.cache_resource
def get_cipher():
    key = Fernet.generate_key()
    return Fernet(key)

cipher = get_cipher()

# -----------------------------
# 📦 Load Data into Session State
# -----------------------------
stored_data = load_data()
locks = load_locks()

if "stored_data" not in st.session_state:
    st.session_state.stored_data = stored_data

if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

if "locks" not in st.session_state:
    st.session_state.locks = locks

# -----------------------------
# 🔑 Utility Functions
# -----------------------------
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()


def encrypt_data(text, passkey):
    return cipher.encrypt(text.encode()).decode()


def decrypt_data(encrypted_text, passkey):
    current_time = time.time()
    lock_info = st.session_state.locks.get(encrypted_text)

    # Check if data is locked and if the lock time has expired
    if lock_info:
        unlock_time = lock_info.get("unlock_time", 0)
        remaining_time = unlock_time - current_time

        # If the remaining time is greater than 0, data is still locked
        if remaining_time > 0:
            st.warning(f"🔒 This data is temporarily locked. {int(remaining_time)} seconds remaining.")
            return None
        else:
            # Lock has expired, remove it
            st.session_state.locks.pop(encrypted_text, None)
            save_locks(st.session_state.locks)  # Save updated lock status
            st.info("🔓 The lock has expired. You can now access the data.")

    hashed = hash_passkey(passkey)
    entry = st.session_state.stored_data.get(encrypted_text)

    if entry and entry["passkey"] == hashed:
        st.session_state.failed_attempts = 0
        return cipher.decrypt(encrypted_text.encode()).decode()
    else:
        st.session_state.failed_attempts += 1
        if st.session_state.failed_attempts >= 3:
            st.session_state.locks[encrypted_text] = {
                "unlock_time": current_time + 300  # 5 minutes from now
            }
            save_locks(st.session_state.locks)
        return None

# -----------------------------
# 🌐 Streamlit Interface
# -----------------------------
st.title("🛡️ Advanced Secure Data Encryption")

# Sidebar Navigation
menu = ["Home", "Store Data", "Retrieve Data", "View Entries", "Login"]
choice = st.sidebar.radio("🔍 Navigation", menu)

# -----------------------------
# 🏠 Home Page
# -----------------------------
if choice == "Home":
    st.subheader("🏠 Welcome to Your Encrypted Vault")
    st.markdown("""
    - 🔐 Encrypt your data with a secret passkey.
    - 🔓 Retrieve it using the correct key.
    - 🚫 Too many failed attempts? Data is locked for 5 minutes.
    - 🔑 Use Admin login to unlock early.
    """)
    st.info("Use the sidebar to explore features.")

# -----------------------------
# 💾 Store Data Page
# -----------------------------
elif choice == "Store Data":
    st.subheader("📂 Store Encrypted Data")

    username = st.text_input("👤 Your Name:")
    user_data = st.text_area("📝 Enter Secret Data:")
    passkey = st.text_input("🔑 Create Passkey:", type="password")

    if st.button("🔐 Encrypt & Save"):
        if user_data and passkey and username:
            encrypted = encrypt_data(user_data, passkey)
            st.session_state.stored_data[encrypted] = {
                "passkey": hash_passkey(passkey),
                "user": username,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_data(st.session_state.stored_data)
            st.success("✅ Data encrypted and saved!")
            with st.expander("📦 Encrypted Text (click to view)"):
                st.code(encrypted, language="text")
        else:
            st.error("⚠️ All fields are required!")

# -----------------------------
# 🔓 Retrieve Data Page
# -----------------------------
elif choice == "Retrieve Data":
    st.subheader("🔍 Retrieve Your Data")

    encrypted_input = st.text_area("🔐 Enter Encrypted Text:")
    passkey_input = st.text_input("🔑 Enter Passkey:", type="password")

    if st.button("🧩 Decrypt"):
        if encrypted_input and passkey_input:
            decrypted = decrypt_data(encrypted_input, passkey_input)

            if decrypted:
                st.success("✅ Decrypted Data:")
                st.code(decrypted, language="text")
            else:
                attempts_left = max(0, 3 - st.session_state.failed_attempts)
                if encrypted_input in st.session_state.locks:
                    st.warning("🔒 Data is locked for 5 minutes or until admin login.")
                else:
                    st.error(f"❌ Incorrect passkey! Attempts left: {attempts_left}")
        else:
            st.error("⚠️ Please provide both encrypted text and passkey.")

# -----------------------------
# 📄 View Entries
# -----------------------------
elif choice == "View Entries":
    st.subheader("📑 Stored Entries")
    if st.session_state.stored_data:
        for i, (enc, details) in enumerate(st.session_state.stored_data.items(), 1):
            with st.expander(f"🧾 Entry {i} — {details['user']} at {details['timestamp']}"):
                st.text(f"Encrypted: {enc}")
                st.text(f"User: {details['user']}")
                st.text(f"Stored At: {details['timestamp']}")
    else:
        st.info("📭 No data stored yet.")

# -----------------------------
# 🔐 Login Page
# -----------------------------
elif choice == "Login":
    st.subheader("🔐 Admin Reauthorization")

    login_input = st.text_input("Enter Admin Password:", type="password")
    encrypted_input = st.text_area("🔓 Unlock Encrypted Data (optional):")

    if st.button("🔁 Reauthorize"):
        if login_input == "admin123":
            st.session_state.failed_attempts = 0
            if encrypted_input:
                st.session_state.locks.pop(encrypted_input, None)
                save_locks(st.session_state.locks)
                st.success("✅ Data unlocked successfully!")
            else:
                st.success("✅ Reauthorized. Back to Retrieve Page.")
            st.rerun()
        else:
            st.error("❌ Incorrect admin password!")
