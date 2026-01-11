# code2md

> Projektcode übersichtlich in einer Markdown-Datei zusammenfassen

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/downloads/)

---

## Was macht code2md?

**code2md** ist ein Kommandozeilen-Werkzeug, das den gesamten Quellcode eines Projekts in eine einzige, übersichtliche Markdown-Datei exportiert. Das Ergebnis ist ein strukturiertes Dokument mit Ordnerübersicht und allen Code-Dateien – perfekt lesbar und mit Syntax-Highlighting.

### Wofür ist das nützlich?

- **Dokumentation** – Erstellen Sie eine Übersicht Ihres Projekts für Kollegen oder Kunden
- **Code-Reviews** – Teilen Sie Ihren Code ohne Zugang zum Repository
- **KI-Assistenten** – Übergeben Sie Ihr gesamtes Projekt an ChatGPT, Claude & Co.
- **Archivierung** – Speichern Sie einen lesbaren Snapshot Ihres Codes
- **Lernen** – Studieren Sie fremde Projekte in einem übersichtlichen Format

---

## Installation

### Voraussetzungen

- Python 3.10 oder neuer

### Download

```bash
# Repository klonen
git clone https://github.com/m0h1nd4/code2md.git
cd code2md

# Oder nur die Datei herunterladen
curl -O https://raw.githubusercontent.com/m0h1nd4/code2md/main/code2md.py
```

### Optional: Global verfügbar machen

```bash
# Ausführbar machen
chmod +x code2md.py

# In den PATH verschieben (Linux/macOS)
sudo mv code2md.py /usr/local/bin/code2md
```

---

## Schnellstart

### Einfaches Beispiel

```bash
# Python-Projekt exportieren
python code2md.py ./mein-projekt --type python
```

Das erstellt eine Datei `mein-projekt_code.md` mit folgendem Aufbau:

```markdown
# mein-projekt

> Generiert am 2024-01-15 14:30:00
> Anzahl Dateien: 12

## Ordnerstruktur

mein-projekt/
├── src/
│   ├── main.py
│   └── utils/
│       └── helpers.py
└── config.json

## Dateien

### `src/main.py`

def main():
    print("Hello, World!")

### `src/utils/helpers.py`

def greet(name):
    return f"Hallo, {name}!"
```

---

## Verwendung

### Grundsyntax

```bash
python code2md.py [VERZEICHNIS] --type [PROJEKTTYP] [OPTIONEN]
```

### Projekttypen

code2md kennt viele gängige Projekttypen und weiß automatisch, welche Dateien dazugehören:

| Typ | Beschreibung | Dateiendungen |
|-----|--------------|---------------|
| `python` | Python-Projekte | `.py`, `.pyi`, `.pyw` |
| `arduino` | Arduino & C++ | `.ino`, `.cpp`, `.c`, `.h`, `.hpp` |
| `vue` | Vue.js | `.vue`, `.js`, `.ts`, `.css`, `.scss` |
| `react` | React.js | `.jsx`, `.tsx`, `.js`, `.ts`, `.css` |
| `web` | HTML/CSS/JS | `.html`, `.css`, `.js`, `.ts` |
| `php` | PHP | `.php`, `.phtml` |
| `node` | Node.js | `.js`, `.ts`, `.mjs`, `.json` |
| `flutter` | Flutter/Dart | `.dart`, `.yaml`, `.json` |
| `rust` | Rust | `.rs`, `.toml` |
| `go` | Go | `.go`, `.mod`, `.sum` |
| `java` | Java | `.java`, `.xml`, `.gradle` |
| `csharp` | C# | `.cs`, `.csproj`, `.sln` |
| `config` | Konfiguration | `.json`, `.yaml`, `.toml`, `.env` |
| `docs` | Dokumentation | `.md`, `.rst`, `.txt` |

Alle Typen anzeigen:

```bash
python code2md.py --list-types
```

---

## Praxisbeispiele

### Mehrere Projekttypen kombinieren

Für ein Full-Stack-Projekt mit Vue.js-Frontend und Python-Backend:

```bash
python code2md.py ./meine-app --type vue,python,config
```

### Eigene Dateiendungen hinzufügen

Zusätzlich `.env` und `.graphql` Dateien einschließen:

```bash
python code2md.py ./projekt --type react --ext .env .graphql .prisma
```

### Ordner und Dateien ausschließen

Tests und Mock-Dateien ignorieren:

```bash
python code2md.py ./app --type node --exclude tests/ mocks/ *.test.js *.spec.ts
```

### Eigenen Dateinamen und Projektnamen wählen

```bash
python code2md.py ./src --type python --output dokumentation.md --name "Mein Projekt v2"
```

### Ausführliche Ausgabe

Zeigt alle gefundenen Dateien während der Verarbeitung:

```bash
python code2md.py ./projekt --type python -v
```

---

## Alle Optionen

| Option | Kurzform | Beschreibung |
|--------|----------|--------------|
| `--type` | `-t` | Projekttyp(en), kommasepariert |
| `--ext` | `-e` | Zusätzliche Dateiendungen |
| `--exclude` | `-x` | Ordner/Dateien/Muster ausschließen |
| `--output` | `-o` | Name der Ausgabedatei |
| `--name` | `-n` | Projektname im Dokument |
| `--verbose` | `-v` | Ausführliche Ausgabe |
| `--list-types` | | Zeigt alle Projekttypen |
| `--no-tree` | | Ordnerstruktur nicht anzeigen |
| `--no-default-excludes` | | Standard-Ausschlüsse deaktivieren |

---

## Automatische Ausschlüsse

Folgende Ordner und Dateien werden standardmäßig ignoriert:

- **Abhängigkeiten:** `node_modules`, `vendor`, `venv`, `.venv`
- **Build-Ordner:** `dist`, `build`, `target`, `bin`, `obj`
- **Cache:** `__pycache__`, `.pytest_cache`, `.mypy_cache`
- **IDE-Dateien:** `.idea`, `.vscode`, `.vs`
- **Versionskontrolle:** `.git`, `.svn`
- **System:** `.DS_Store`, `Thumbs.db`
- **Logs:** `*.log`, `logs/`, `tmp/`

Mit `--no-default-excludes` können Sie diese Ausschlüsse deaktivieren.

---

## Häufige Fragen

### Kann ich nur bestimmte Dateien exportieren?

Ja, nutzen Sie `--ext` mit nur den gewünschten Endungen:

```bash
python code2md.py ./projekt --ext .py .json
```

### Warum fehlen manche Dateien?

Prüfen Sie mit `-v` (verbose), welche Dateien gefunden werden. Möglicherweise liegt die Datei in einem automatisch ausgeschlossenen Ordner oder hat eine nicht erkannte Endung.

### Kann ich die Ausgabe in die Zwischenablage kopieren?

Unter Linux/macOS:

```bash
python code2md.py ./projekt --type python --output /dev/stdout | pbcopy  # macOS
python code2md.py ./projekt --type python --output /dev/stdout | xclip   # Linux
```

---

## Mitwirken

Beiträge sind willkommen! Öffnen Sie gerne ein Issue oder Pull Request auf GitHub.

1. Repository forken
2. Feature-Branch erstellen (`git checkout -b feature/neue-funktion`)
3. Änderungen committen (`git commit -m 'Neue Funktion hinzugefügt'`)
4. Branch pushen (`git push origin feature/neue-funktion`)
5. Pull Request öffnen

---

## Lizenz

Dieses Projekt steht unter der **MIT-Lizenz**. Sie dürfen den Code frei verwenden, verändern und weitergeben – auch in kommerziellen Projekten.

Siehe [LICENSE](LICENSE) für Details.

---

## Autor

Entwickelt von [m0h1nd4](https://github.com/m0h1nd4)

---

<p align="center">
  <sub>⭐ Wenn Ihnen dieses Tool gefällt, freue ich mich über einen Stern auf GitHub!</sub>
</p>

