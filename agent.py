from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, RateLimitError

load_dotenv()

client = OpenAI()

print("KlimaMinute ist bereit.")
print("Stelle eine Klimafrage oder schreibe 'ende' zum Beenden.\n")

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
            instructions=(
                "Du bist KlimaMinute, ein freundlicher Klima-Assistent. "
                "Antworte auf Deutsch, sachlich und leicht verständlich. "
                "Beschränke deine Antwort auf höchstens 150 Wörter. "
                "Wenn du bei einer aktuellen Zahl unsicher bist, sage das offen. "
                "Beantworte ausschließlich Fragen zu Klima, Umwelt, Energie "
                "und Nachhaltigkeit. Weise bei anderen Themen freundlich darauf hin."
            ),
            input=frage,
        )

        print(f"\nKlimaMinute: {antwort.output_text}\n")

    except AuthenticationError:
        print("\nKlimaMinute: Der API-Key ist ungültig.\n")

    except RateLimitError:
        print("\nKlimaMinute: Das API-Guthaben ist aufgebraucht oder die Anfragegrenze wurde erreicht.\n")

    except Exception as fehler:
        print(f"\nKlimaMinute: Es ist ein Fehler aufgetreten: {fehler}\n")