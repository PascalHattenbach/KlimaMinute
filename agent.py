from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, RateLimitError

load_dotenv()

client = OpenAI()

print("KlimaMinute ist bereit.")
print("Stelle eine Klimafrage oder schreibe 'ende' zum Beenden.\n")


def zeige_quellen(antwort):
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
                    quellen[url] = titel

    if quellen:
        print("Quellen:")

        for url, titel in quellen.items():
            print(f"- {titel}: {url}")

        print()


while True:
    frage = input("Du: ").strip()

    if frage.lower() in ["ende", "exit", "quit"]:
        print("KlimaMinute: Bis bald!")
        break

    if not frage:
        print("KlimaMinute: Bitte gib eine Frage ein.\n")
        continue

    try:
        antwort = client.responses.create(
            model="gpt-5-mini",
            tools=[{"type": "web_search"}],
            instructions=(
                "Du bist KlimaMinute, ein freundlicher Klima-Assistent. "
                "Antworte auf Deutsch, sachlich und leicht verständlich. "
                "Beschränke deine eigentliche Antwort auf höchstens 150 Wörter. "
                "Nutze bei aktuellen Zahlen, Nachrichten oder Entwicklungen "
                "die Websuche. Bevorzuge wissenschaftliche und offizielle Quellen. "
                "Unterscheide klar zwischen gesicherten Fakten und Unsicherheit. "
                "Beantworte ausschließlich Fragen zu Klima, Umwelt, Energie "
                "und Nachhaltigkeit."
            ),
            input=frage,
        )

        print(f"\nKlimaMinute:\n{antwort.output_text}\n")
        zeige_quellen(antwort)

    except AuthenticationError:
        print("\nKlimaMinute: Der API-Key ist ungültig.\n")

    except RateLimitError:
        print(
            "\nKlimaMinute: Das Guthaben ist aufgebraucht "
            "oder die Anfragegrenze wurde erreicht.\n"
        )

    except Exception as fehler:
        print(f"\nKlimaMinute: Es ist ein Fehler aufgetreten: {fehler}\n")