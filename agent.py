from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

frage = input("Welche Klimafrage hast du? ")

antwort = client.responses.create(
    model="gpt-5-mini",
    instructions=(
        "Du bist KlimaMinute, ein freundlicher Klima-Assistent. "
        "Antworte auf Deutsch, sachlich und leicht verständlich. "
        "Beschränke deine Antwort auf höchstens 150 Wörter. "
        "Wenn du bei einer aktuellen Zahl unsicher bist, sage das offen."
    ),
    input=frage,
)

print("\nKlimaMinute:\n")
print(antwort.output_text)