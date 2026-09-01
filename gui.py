import threading
import tkinter as tk
from tkinter import scrolledtext

from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, RateLimitError

load_dotenv()

client = OpenAI()


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

    return quellen


def anfrage_senden():
    frage = frage_eingabe.get().strip()

    if not frage:
        status_text.set("Bitte gib zuerst eine Klimafrage ein.")
        return

    senden_button.config(state="disabled")
    status_text.set("KlimaMinute sucht und formuliert eine Antwort …")

    antwort_feld.config(state="normal")
    antwort_feld.delete("1.0", tk.END)
    antwort_feld.insert(tk.END, "Bitte einen Moment warten …")
    antwort_feld.config(state="disabled")

    thread = threading.Thread(
        target=antwort_laden,
        args=(frage,),
        daemon=True,
    )
    thread.start()


def antwort_laden(frage):
    try:
        antwort = client.responses.create(
            model="gpt-5-mini",
            tools=[{"type": "web_search"}],
            instructions=(
                "Du bist KlimaMinute, ein freundlicher Klima-Assistent. "
                "Antworte auf Deutsch, sachlich und leicht verständlich. "
                "Beschränke die eigentliche Antwort auf höchstens 150 Wörter. "
                "Nutze bei aktuellen Zahlen und Entwicklungen die Websuche. "
                "Bevorzuge wissenschaftliche und offizielle Quellen. "
                "Unterscheide Fakten klar von Unsicherheiten. "
                "Beantworte ausschließlich Fragen zu Klima, Umwelt, Energie "
                "und Nachhaltigkeit."
            ),
            input=frage,
        )

        text = antwort.output_text
        quellen = quellen_auslesen(antwort)

        if quellen:
            text += "\n\nQuellen:\n"

            for url, titel in quellen.items():
                text += f"\n• {titel}\n  {url}\n"

        fenster.after(0, ergebnis_anzeigen, text)

    except AuthenticationError:
        fenster.after(
            0,
            fehler_anzeigen,
            "Der API-Key ist ungültig.",
        )

    except RateLimitError:
        fenster.after(
            0,
            fehler_anzeigen,
            "Das API-Guthaben ist aufgebraucht oder die Anfragegrenze wurde erreicht.",
        )

    except Exception as fehler:
        fenster.after(
            0,
            fehler_anzeigen,
            f"Es ist ein Fehler aufgetreten:\n{fehler}",
        )


def ergebnis_anzeigen(text):
    antwort_feld.config(state="normal")
    antwort_feld.delete("1.0", tk.END)
    antwort_feld.insert(tk.END, text)
    antwort_feld.config(state="disabled")

    senden_button.config(state="normal")
    status_text.set("Antwort fertig")


def fehler_anzeigen(text):
    antwort_feld.config(state="normal")
    antwort_feld.delete("1.0", tk.END)
    antwort_feld.insert(tk.END, text)
    antwort_feld.config(state="disabled")

    senden_button.config(state="normal")
    status_text.set("Fehler")


def eingabetaste(event):
    anfrage_senden()


fenster = tk.Tk()
fenster.title("KlimaMinute")
fenster.geometry("760x600")
fenster.minsize(600, 450)
fenster.configure(bg="#eaf4ec")

titel = tk.Label(
    fenster,
    text="KlimaMinute",
    font=("Segoe UI", 24, "bold"),
    bg="#eaf4ec",
    fg="#176b3a",
)
titel.pack(pady=(20, 5))

untertitel = tk.Label(
    fenster,
    text="Dein KI-Assistent für Klima, Umwelt und Energie",
    font=("Segoe UI", 11),
    bg="#eaf4ec",
    fg="#355e45",
)
untertitel.pack(pady=(0, 20))

frage_rahmen = tk.Frame(fenster, bg="#eaf4ec")
frage_rahmen.pack(fill="x", padx=30)

frage_eingabe = tk.Entry(
    frage_rahmen,
    font=("Segoe UI", 12),
)
frage_eingabe.pack(
    side="left",
    fill="x",
    expand=True,
    ipady=8,
)
frage_eingabe.bind("<Return>", eingabetaste)

senden_button = tk.Button(
    frage_rahmen,
    text="Fragen",
    command=anfrage_senden,
    font=("Segoe UI", 11, "bold"),
    bg="#238b57",
    fg="white",
    activebackground="#176b3a",
    activeforeground="white",
    padx=18,
    pady=7,
)
senden_button.pack(side="left", padx=(10, 0))

antwort_feld = scrolledtext.ScrolledText(
    fenster,
    wrap=tk.WORD,
    font=("Segoe UI", 11),
    padx=15,
    pady=15,
)
antwort_feld.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=20,
)
antwort_feld.config(state="disabled")

status_text = tk.StringVar(value="Bereit")

status = tk.Label(
    fenster,
    textvariable=status_text,
    anchor="w",
    font=("Segoe UI", 9),
    bg="#d8eadc",
    fg="#355e45",
    padx=10,
    pady=6,
)
status.pack(fill="x", side="bottom")

frage_eingabe.focus()

fenster.mainloop()