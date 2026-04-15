# workflow-tools

Centraliserade GitHub Actions-verktyg för klassrumsmiljön i kursen Webbutveckling 1 (WEUWEB01).

Istället för att duplicera skript i varje elevrepo finns alla automatiseringsverktyg samlade här.

---

## Tillgängliga workflows

### `generate-plan.yml` – Generera modulplan från källkod

Analyserar HTML/CSS/JS-källkoden i en lektionsmapp och genererar en `plan.md` med Gemini AI.

| Input | Beskrivning | Exempel |
|---|---|---|
| `target_repo` | Elevrepot att analysera | `WEUWEB01-TE23A-TETEK23-ORG/lektioner-karimryde-nti` |
| `kapitel` | Kapitel-mappen att analysera | `kapitel-8` |

**Hur du kör den:**
1. Gå till `karye/workflow-tools` → fliken **Actions**
2. Välj **Generera plan.md från källkod**
3. Klicka **Run workflow**
4. Fyll i `target_repo` och `kapitel`
5. Klicka **Run workflow**

Resultatet sparas som `plan.md` i kapitel-mappen i elevrepot.

---

## Secrets som krävs

Lägg till dessa under `karye/workflow-tools → Settings → Secrets and variables → Actions`:

| Secret | Beskrivning |
|---|---|
| `GEMINI_API_KEY` | API-nyckel för Google Gemini |
| `GH_PAT` | Personal Access Token med `repo`-scope – krävs för att pusha till elevrepon |

### Skapa en GH_PAT
1. Gå till [github.com/settings/tokens](https://github.com/settings/tokens)
2. Klicka **Generate new token (classic)**
3. Ge den ett namn, t.ex. `workflow-tools-bot`
4. Bocka i scope: `repo`
5. Kopiera token och lägg till den som secret med namnet `GH_PAT`