import os
import subprocess
import sys

from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Inget GEMINI_API_KEY hittades. Avbryter.")
    sys.exit(1)

MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
KAPITEL = os.environ.get("KAPITEL")
if not KAPITEL:
    print("Ingen KAPITEL angiven. Avbryter.")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

ALLOWED_EXTENSIONS = {".html", ".css", ".js"}
MAX_CHARS_PER_FILE = 3000


def collect_source_files(kapitel_path):
    """Samla alla HTML/CSS/JS-filer rekursivt, hoppa över dolda mappar."""
    files = {}
    for root, dirs, filenames in os.walk(kapitel_path):
        # Filtrera bort dolda mappar (börjar med '.')
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, kapitel_path)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(MAX_CHARS_PER_FILE)
                    files[rel_path] = content
                except Exception as e:
                    print(f"Kunde inte läsa {full_path}: {e}")
    return files


def build_prompt(kapitel, source_files):
    files_text = ""
    for path, content in source_files.items():
        files_text += f"\n### {path}\n```\n{content}\n```\n"

    return f"""Du är en pedagogisk assistent för en gymnasielärare i webbutveckling (kursen Webbutveckling 1, WEUWEB01).

Analysera källkoden nedan från lektionsmappen "{kapitel}" och generera en modulplan på svenska i Markdown-format.

Källkod:
{files_text}

Generera en plan.md med exakt denna struktur och svenska skrivregler (meningsversal i rubriker):

# Modulplan: {kapitel} – <kort beskrivning av vad kapitlet handlar om>

## Mål
- Punktlista med konkreta lärandemål utifrån vad källkoden visar att eleverna ska lära sig

## Förkunskaper
- Vilka förkunskaper krävs? (om detta är kapitel-1, skriv "Inga.")

## Nya begrepp

### HTML
Lista alla HTML-taggar som används i koden (t.ex. `<h1>`, `<img>`)

### CSS
Lista alla CSS-egenskaper och koncept som används (t.ex. `color`, `flexbox`)

### JavaScript
Lista alla JS-koncept som används – om inga finns, utelämna denna sektion

## Pedagogiska grundregler
- Kort lista med pedagogiska principer som kan utläsas av kodens upplägg och progression

## Lektioner
För varje undermapp i kapitlet, skapa en undersektion:

### Lektion X: <mappnamn>
- Vad byggdes i den här lektionen utifrån källkoden?
- Vilka nya koncept introducerades?

## Vanliga misstag
- Lista vanliga nybörjarmisstag kopplade till de koncept som finns i koden

Svara ENDAST med Markdown-innehållet, ingen inledande text eller förklaring.
"""


def main():
    kapitel_path = KAPITEL

    if not os.path.isdir(kapitel_path):
        print(f"Mappen '{kapitel_path}' hittades inte.")
        sys.exit(1)

    print(f"Analyserar källkod i: {kapitel_path}")
    source_files = collect_source_files(kapitel_path)

    if not source_files:
        print(f"Inga HTML/CSS/JS-filer hittades i '{kapitel_path}'. Avbryter.")
        sys.exit(0)

    print(f"Hittade {len(source_files)} källkodsfil(er):")
    for path in source_files:
        print(f"  - {path}")

    prompt = build_prompt(KAPITEL, source_files)

    print(f"Skickar till Gemini ({MODEL})...")
    response = client.models.generate_content(model=MODEL, contents=prompt)
    plan_content = response.text.strip()

    # Ta bort eventuella markdown-kodblock-wrappers
    if plan_content.startswith("```markdown"):
        plan_content = plan_content[11:]
    if plan_content.startswith("```"):
        plan_content = plan_content[3:]
    if plan_content.endswith("```"):
        plan_content = plan_content[:-3]
    plan_content = plan_content.strip()

    plan_path = os.path.join(kapitel_path, "plan.md")
    with open(plan_path, "w", encoding="utf-8") as f:
        f.write(plan_content)
    print(f"Sparade {plan_path}")

    # Committa och pusha
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", plan_path], check=True)

    result = subprocess.run(["git", "diff", "--staged", "--quiet"])
    if result.returncode == 0:
        print("Inga ändringar att committa.")
    else:
        subprocess.run(["git", "commit", "-m", f"docs: AI-genererad plan för {KAPITEL} [skip ci]"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Pushade ändringar till repot.")


if __name__ == "__main__":
    main()