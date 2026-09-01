import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, RateLimitError

load_dotenv()

client = OpenAI()

st.set_page_config(
    page_title="KlimaMinute",
    page_icon="🌍",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #edf7ef;
    }

    .klima-titel {
        color: #176b3a;
        font-size: 2.6rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0;
    }

    .klima-untertitel {
        color: #416c50;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="klima-titel">🌍 KlimaMinute</p>',
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="klima-untertitel">'
    'Dein KI-Assistent für Klima, Umwelt und Energie'
    '</p>',
    unsafe_allow_html=True,
)


def quellen_auslesen(antwort):
    quellen = {}

    for element in antwort.output:
        if getattr(element, "type", "") != "message":
            continue

        for inhalt in element.content:
            if getattr(inhalt, "type", "") != "output_text":
                continue

            for quelle in inhalt.annotations:
                if getattr(quelle, "type", "") == "url_citation":
                    titel = getattr(quelle, "title", "Quelle")
                    url = getattr(quelle, "url", "")

                    if url:
                        quellen[url] = titel

    return [
        {"titel": titel, "url": url}
        for url, titel in quellen.items()
    ]


if "nachrichten" not in st.session_state:
    st.session_state.nachrichten = []


with st.sidebar:
    st.header("Über KlimaMinute")
    st.write(
        "KlimaMinute beantwortet verständliche Fragen zu Klima, "
        "Umwelt, Energie und Nachhaltigkeit."
    )

    st.warning(
        "KI-Antworten können Fehler enthalten. "
        "Prüfe wichtige Angaben anhand der genannten Quellen."
    )

    if st.button("Gespräch löschen"):
        st.session_state.nachrichten = []
        st.rerun()


for nachricht in st.session_state.nachrichten:
    with st.chat_message(nachricht["rolle"]):
        st.markdown(nachricht["text"])

        for quelle in nachricht.get("quellen", []):
            st.markdown(
                f"- [{quelle['titel']}]({quelle['url']})"
            )


frage = st.chat_input("Stelle eine Klimafrage …")

if frage:
    st.session_state.nachrichten.append(
        {
            "rolle": "user",
            "text": frage,
        }
    )

    with st.chat_message("user"):
        st.markdown(frage)

    with st.chat_message("assistant"):
        with st.spinner("KlimaMinute recherchiert …"):
            try:
                antwort = client.responses.create(
                    model="gpt-5-mini",
                    tools=[{"type": "web_search"}],
                    instructions=(
                        "Du bist KlimaMinute, ein freundlicher "
                        "Klima-Assistent. Antworte auf Deutsch, "
                        "sachlich und leicht verständlich. "
                        "Beschränke die eigentliche Antwort auf "
                        "höchstens 150 Wörter. Nutze bei aktuellen "
                        "Zahlen und Entwicklungen die Websuche. "
                        "Bevorzuge wissenschaftliche und offizielle "
                        "Quellen. Unterscheide Fakten klar von "
                        "Unsicherheiten. Beantworte ausschließlich "
                        "Fragen zu Klima, Umwelt, Energie und "
                        "Nachhaltigkeit."
                    ),
                    input=frage,
                )

                antwort_text = antwort.output_text
                quellen = quellen_auslesen(antwort)

                st.markdown(antwort_text)

                if quellen:
                    st.markdown("**Quellen:**")

                    for quelle in quellen:
                        st.markdown(
                            f"- [{quelle['titel']}]({quelle['url']})"
                        )

                st.session_state.nachrichten.append(
                    {
                        "rolle": "assistant",
                        "text": antwort_text,
                        "quellen": quellen,
                    }
                )

            except AuthenticationError:
                st.error("Der OpenAI-API-Key ist ungültig.")

            except RateLimitError:
                st.error(
                    "Das API-Guthaben ist aufgebraucht oder "
                    "die Anfragegrenze wurde erreicht."
                )

            except Exception as fehler:
                st.error(f"Es ist ein Fehler aufgetreten: {fehler}")