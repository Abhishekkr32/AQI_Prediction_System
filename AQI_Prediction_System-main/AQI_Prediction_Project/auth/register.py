import streamlit as st

def register():
    st.subheader("📝 Register")

    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Register"):
        # Demo only (no DB)
        st.success("Registration successful! Please login.")
