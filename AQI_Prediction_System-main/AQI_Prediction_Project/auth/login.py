import streamlit as st

def login():
    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state["authenticated"] = True
            st.session_state["user"] = username
            st.success("Login successful")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")


def is_authenticated():
    return st.session_state.get("authenticated", False)


def logout():
    st.session_state["authenticated"] = False
    st.experimental_rerun()
