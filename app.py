import streamlit as st
st.set_page_config(page_title="Secure Data Vault", page_icon="🛡️")  # ✅ Must be first Streamlit command

import hashlib
from cryptography.fernet import Fernet
from datetime import datetime

# -----------------------------
# 🔐 Key and Cipher Setup
# -----------------------------
@st.cache_resource
def get_cipher():
    key = Fernet.generate_key()
    return Fernet(key)

cipher = get_cipher()

# -----------------------------
# 📦 In-Memory Storage
# -----------------------------
if "stored_data" not in st.session_state:
    st.session_state.stored_data = {}  # {encrypted_text: {"passkey": ..., "user": ..., "timestamp": ...}}

if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

# -----------------------------
# 🔑 Utility Functions
# -----------------------------
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

def encrypt_data(text, passkey):
    return cipher.encrypt(text.encode()).decode()

def decrypt_data(encrypted_text, passkey):
    hashed = hash_passkey(passkey)
    entry = st.session_state.stored_data.get(encrypted_text)

    if entry and entry["passkey"] == hashed:
        st.session_state.failed_attempts = 0
        return cipher.decrypt(encrypted_text.encode()).decode()
    else:
        st.session_state.failed_attempts += 1
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
    - 🚫 Too many failed attempts? Re-login required.
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
                st.error(f"❌ Incorrect passkey! Attempts left: {attempts_left}")
                if st.session_state.failed_attempts >= 3:
                    st.warning("🚫 Too many failed attempts. Redirecting to login.")
                    st.experimental_rerun()
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

    if st.button("🔁 Reauthorize"):
        if login_input == "admin123":
            st.session_state.failed_attempts = 0
            st.success("✅ Reauthorized. Back to Retrieve Page.")
            st.rerun()
        else:
            st.error("❌ Incorrect admin password!")
