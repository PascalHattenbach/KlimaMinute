import hmac

import streamlit as st


def zugang_erlaubt():
    try:
        richtiges_passwort = st.secrets["APP_PASSWORD"]
    except KeyError:
        st.error(
            "Der Zugangsschutz ist noch nicht eingerichtet. "
            "APP_PASSWORD fehlt in den Streamlit-Secrets."
        )
        return False

    if st.session_state.get("angemeldet"):
        return True

    st.title("🔒 KlimaMinute")
    st.write("Bitte gib das Zugangspasswort ein.")

    eingegebenes_passwort = st.text_input(
        "Passwort",
        type="password",
    )

    if st.button("Anmelden"):
        if hmac.compare_digest(
            eingegebenes_passwort,
            richtiges_passwort,
        ):
            st.session_state["angemeldet"] = True
            st.rerun()
        else:
            st.error("Das Passwort ist nicht korrekt.")

    return False
