#!/usr/bin/env python3
"""
code2md - Flatten project code into a single Markdown file.

Exports all relevant source files from a project directory into a structured
Markdown document, including directory tree and syntax-highlighted code blocks.
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


# =============================================================================
# Projekttyp-Definitionen
# =============================================================================

PROJECT_TYPES: dict[str, dict] = {
    "python": {
        "extensions": [".py", ".pyi", ".pyw"],
        "syntax": "python",
        "description": "Python-Projekte",
    },
    "arduino": {
        "extensions": [".ino", ".cpp", ".c", ".h", ".hpp"],
        "syntax": "cpp",
        "description": "Arduino/C++ Projekte",
    },
    "vue": {
        "extensions": [".vue", ".js", ".ts", ".jsx", ".tsx", ".json", ".css", ".scss", ".sass", ".less"],
        "syntax": "vue",
        "description": "Vue.js Projekte",
    },
    "react": {
        "extensions": [".jsx", ".tsx", ".js", ".ts", ".json", ".css", ".scss", ".sass", ".less"],
        "syntax": "jsx",
        "description": "React.js Projekte",
    },
    "web": {
        "extensions": [".html", ".htm", ".css", ".scss", ".sass", ".less", ".js", ".ts"],
        "syntax": "html",
        "description": "Web-Projekte (HTML/CSS/JS)",
    },
    "php": {
        "extensions": [".php", ".phtml", ".php3", ".php4", ".php5", ".phps"],
        "syntax": "php",
        "description": "PHP-Projekte",
    },
    "node": {
        "extensions": [".js", ".ts", ".mjs", ".cjs", ".json"],
        "syntax": "javascript",
        "description": "Node.js Projekte",
    },
    "flutter": {
        "extensions": [".dart", ".yaml", ".json"],
        "syntax": "dart",
        "description": "Flutter/Dart Projekte",
    },
    "rust": {
        "extensions": [".rs", ".toml"],
        "syntax": "rust",
        "description": "Rust Projekte",
    },
    "go": {
        "extensions": [".go", ".mod", ".sum"],
        "syntax": "go",
        "description": "Go Projekte",
    },
    "java": {
        "extensions": [".java", ".xml", ".gradle", ".properties"],
        "syntax": "java",
        "description": "Java Projekte",
    },
    "csharp": {
        "extensions": [".cs", ".csproj", ".sln", ".xaml"],
        "syntax": "csharp",
        "description": "C# Projekte",
    },
    "config": {
        "extensions": [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env"],
        "syntax": "yaml",
        "description": "Konfigurationsdateien",
    },
    "docs": {
        "extensions": [".md", ".rst", ".txt", ".adoc"],
        "syntax": "markdown",
        "description": "Dokumentationsdateien",
    },
}

# Standard-Ausschlüsse
DEFAULT_EXCLUDES = [
    # Abhängigkeiten
    "node_modules",
    "vendor",
    "packages",
    ".pub-cache",
    # Python
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "venv",
    ".venv",
    "env",
    ".env",
    "*.egg-info",
    # Build-Ordner
    "dist",
    "build",
    "out",
    "target",
    "bin",
    "obj",
    # IDE/Editor
    ".idea",
    ".vscode",
    ".vs",
    "*.swp",
    "*.swo",
    # Versionskontrolle
    ".git",
    ".svn",
    ".hg",
    # OS
    ".DS_Store",
    "Thumbs.db",
    # Logs & temporäre Dateien
    "*.log",
    "logs",
    "tmp",
    "temp",
    ".tmp",
    # Coverage & Tests
    "coverage",
    ".coverage",
    "htmlcov",
    ".tox",
    ".nox",
]

# Syntax-Highlighting Mapping für Dateiendungen
SYNTAX_MAP = {
    ".py": "python",
    ".pyi": "python",
    ".pyw": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".jsx": "jsx",
    ".tsx": "tsx",
    ".vue": "vue",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".less": "less",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
    ".md": "markdown",
    ".rst": "rst",
    ".php": "php",
    ".phtml": "php",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".ino": "cpp",
    ".rs": "rust",
    ".go": "go",
    ".dart": "dart",
    ".java": "java",
    ".kt": "kotlin",
    ".cs": "csharp",
    ".rb": "ruby",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "zsh",
    ".fish": "fish",
    ".ps1": "powershell",
    ".sql": "sql",
    ".graphql": "graphql",
    ".dockerfile": "dockerfile",
    ".ini": "ini",
    ".cfg": "ini",
    ".conf": "ini",
    ".env": "dotenv",
    ".gitignore": "gitignore",
}


# =============================================================================
# Hilfsfunktionen
# =============================================================================

def get_syntax_for_file(filepath: Path) -> str:
    """Ermittelt die Syntax-Highlighting-Sprache für eine Datei."""
    suffix = filepath.suffix.lower()
    name = filepath.name.lower()
    
    # Spezialfälle für Dateien ohne Endung oder mit speziellem Namen
    if name == "dockerfile":
        return "dockerfile"
    if name == "makefile":
        return "makefile"
    if name.startswith(".env"):
        return "dotenv"
    if name == ".gitignore":
        return "gitignore"
    
    return SYNTAX_MAP.get(suffix, "")


def should_exclude(path: Path, excludes: list[str], base_path: Path) -> bool:
    """Prüft, ob ein Pfad ausgeschlossen werden soll."""
    rel_path = path.relative_to(base_path)
    path_parts = rel_path.parts
    path_name = path.name
    
    for exclude in excludes:
        # Wildcard-Pattern (z.B. *.log)
        if exclude.startswith("*"):
            if path_name.endswith(exclude[1:]):
                return True
        # Exakter Namens-Match
        elif exclude in path_parts or path_name == exclude:
            return True
        # Pfad-Pattern
        elif exclude in str(rel_path):
            return True
    
    return False


def collect_files(
    base_path: Path,
    extensions: set[str],
    excludes: list[str]
) -> list[Path]:
    """Sammelt alle relevanten Dateien rekursiv."""
    files = []
    
    for root, dirs, filenames in os.walk(base_path):
        root_path = Path(root)
        
        # Ausgeschlossene Ordner überspringen
        dirs[:] = [
            d for d in dirs 
            if not should_exclude(root_path / d, excludes, base_path)
        ]
        
        for filename in filenames:
            filepath = root_path / filename
            
            # Ausgeschlossene Dateien überspringen
            if should_exclude(filepath, excludes, base_path):
                continue
            
            # Nur Dateien mit passender Endung
            if filepath.suffix.lower() in extensions:
                files.append(filepath)
    
    # Sortieren für konsistente Ausgabe
    files.sort(key=lambda p: str(p.relative_to(base_path)).lower())
    return files


def generate_tree(
    base_path: Path,
    extensions: set[str],
    excludes: list[str],
    prefix: str = ""
) -> list[str]:
    """Generiert eine Baumdarstellung der Ordnerstruktur."""
    lines = []
    
    items = sorted(base_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    
    # Filtern
    filtered_items = []
    for item in items:
        if should_exclude(item, excludes, base_path.parent if prefix else base_path):
            continue
        if item.is_file() and item.suffix.lower() not in extensions:
            continue
        filtered_items.append(item)
    
    for i, item in enumerate(filtered_items):
        is_last = i == len(filtered_items) - 1
        connector = "└── " if is_last else "├── "
        
        if item.is_dir():
            # Prüfen ob Ordner relevante Dateien enthält
            has_relevant = any(
                f.suffix.lower() in extensions
                for f in item.rglob("*")
                if f.is_file() and not should_exclude(f, excludes, base_path.parent if prefix else base_path)
            )
            if not has_relevant:
                continue
            
            lines.append(f"{prefix}{connector}{item.name}/")
            extension = "    " if is_last else "│   "
            lines.extend(
                generate_tree(item, extensions, excludes, prefix + extension)
            )
        else:
            lines.append(f"{prefix}{connector}{item.name}")
    
    return lines


def read_file_content(filepath: Path) -> str:
    """Liest den Inhalt einer Datei sicher aus."""
    encodings = ["utf-8", "latin-1", "cp1252"]
    
    for encoding in encodings:
        try:
            return filepath.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    
    return f"[Fehler: Datei konnte nicht gelesen werden - Encoding-Problem]"


def generate_markdown(
    base_path: Path,
    files: list[Path],
    extensions: set[str],
    excludes: list[str],
    project_name: str
) -> str:
    """Generiert das vollständige Markdown-Dokument."""
    lines = []
    
    # Header
    lines.append(f"# {project_name}")
    lines.append("")
    lines.append(f"> Generiert am {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"> Basisverzeichnis: `{base_path.absolute()}`")
    lines.append(f"> Anzahl Dateien: {len(files)}")
    lines.append("")
    
    # Inhaltsverzeichnis
    lines.append("## Inhaltsverzeichnis")
    lines.append("")
    lines.append("1. [Ordnerstruktur](#ordnerstruktur)")
    lines.append("2. [Dateien](#dateien)")
    
    for filepath in files:
        rel_path = filepath.relative_to(base_path)
        anchor = str(rel_path).replace("/", "").replace("\\", "").replace(".", "").replace("_", "-").lower()
        lines.append(f"   - [`{rel_path}`](#{anchor})")
    
    lines.append("")
    
    # Ordnerstruktur
    lines.append("---")
    lines.append("")
    lines.append("## Ordnerstruktur")
    lines.append("")
    lines.append("```")
    lines.append(f"{project_name}/")
    tree = generate_tree(base_path, extensions, excludes)
    lines.extend(tree)
    lines.append("```")
    lines.append("")
    
    # Dateien
    lines.append("---")
    lines.append("")
    lines.append("## Dateien")
    lines.append("")
    
    for filepath in files:
        rel_path = filepath.relative_to(base_path)
        syntax = get_syntax_for_file(filepath)
        content = read_file_content(filepath)
        
        lines.append(f"### `{rel_path}`")
        lines.append("")
        lines.append(f"```{syntax}")
        lines.append(content.rstrip())
        lines.append("```")
        lines.append("")
    
    return "\n".join(lines)


# =============================================================================
# CLI
# =============================================================================

def list_types():
    """Listet alle verfügbaren Projekttypen auf."""
    print("\nVerfügbare Projekttypen:\n")
    for name, config in PROJECT_TYPES.items():
        exts = ", ".join(config["extensions"])
        print(f"  {name:12} - {config['description']}")
        print(f"               Endungen: {exts}\n")


def main():
    parser = argparse.ArgumentParser(
        prog="code2md",
        description="Exportiert Projektcode in eine strukturierte Markdown-Datei.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s ./mein-projekt --type python
  %(prog)s ./fullstack-app --type vue,python --output projekt.md
  %(prog)s ./app --type react --ext .env .graphql
  %(prog)s ./code --type node --exclude tests/ fixtures/
  %(prog)s --list-types
        """
    )
    
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Projektverzeichnis (Standard: aktuelles Verzeichnis)"
    )
    
    parser.add_argument(
        "-t", "--type",
        dest="types",
        help="Projekttyp(en), kommasepariert (z.B. python,vue,config)"
    )
    
    parser.add_argument(
        "-e", "--ext",
        dest="extensions",
        nargs="+",
        default=[],
        help="Zusätzliche Dateiendungen (z.B. .env .graphql)"
    )
    
    parser.add_argument(
        "-x", "--exclude",
        dest="excludes",
        nargs="+",
        default=[],
        help="Zusätzliche Ausschlüsse (Ordner/Dateien/Patterns)"
    )
    
    parser.add_argument(
        "-o", "--output",
        dest="output",
        help="Ausgabedatei (Standard: <projektname>_code.md)"
    )
    
    parser.add_argument(
        "-n", "--name",
        dest="name",
        help="Projektname für den Header (Standard: Ordnername)"
    )
    
    parser.add_argument(
        "--no-tree",
        action="store_true",
        help="Ordnerstruktur-Baum nicht ausgeben"
    )
    
    parser.add_argument(
        "--list-types",
        action="store_true",
        help="Zeigt alle verfügbaren Projekttypen an"
    )
    
    parser.add_argument(
        "--no-default-excludes",
        action="store_true",
        help="Standard-Ausschlüsse deaktivieren"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Ausführliche Ausgabe"
    )
    
    args = parser.parse_args()
    
    # Liste der Typen anzeigen
    if args.list_types:
        list_types()
        sys.exit(0)
    
    # Validierung
    if not args.types and not args.extensions:
        parser.error("Bitte mindestens --type oder --ext angeben. Nutze --list-types für verfügbare Typen.")
    
    # Basisverzeichnis
    base_path = Path(args.directory).resolve()
    if not base_path.exists():
        print(f"Fehler: Verzeichnis '{base_path}' existiert nicht.", file=sys.stderr)
        sys.exit(1)
    if not base_path.is_dir():
        print(f"Fehler: '{base_path}' ist kein Verzeichnis.", file=sys.stderr)
        sys.exit(1)
    
    # Extensions sammeln
    extensions: set[str] = set()
    
    if args.types:
        for type_name in args.types.split(","):
            type_name = type_name.strip().lower()
            if type_name not in PROJECT_TYPES:
                print(f"Fehler: Unbekannter Projekttyp '{type_name}'.", file=sys.stderr)
                print("Nutze --list-types für verfügbare Typen.", file=sys.stderr)
                sys.exit(1)
            extensions.update(PROJECT_TYPES[type_name]["extensions"])
    
    # Zusätzliche Extensions
    for ext in args.extensions:
        if not ext.startswith("."):
            ext = "." + ext
        extensions.add(ext.lower())
    
    # Excludes
    excludes = [] if args.no_default_excludes else DEFAULT_EXCLUDES.copy()
    excludes.extend(args.excludes)
    
    # Projektname
    project_name = args.name or base_path.name
    
    # Ausgabedatei
    if args.output:
        output_path = Path(args.output)
    else:
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in project_name)
        output_path = base_path / f"{safe_name}_code.md"
    
    # Verbose Output
    if args.verbose:
        print(f"\n{'='*60}")
        print(f"code2md - Projekt-Export")
        print(f"{'='*60}")
        print(f"Projektverzeichnis: {base_path}")
        print(f"Projektname:        {project_name}")
        print(f"Ausgabedatei:       {output_path}")
        print(f"Dateiendungen:      {', '.join(sorted(extensions))}")
        print(f"Ausschlüsse:        {len(excludes)} Patterns")
        print(f"{'='*60}\n")
    
    # Dateien sammeln
    print("Sammle Dateien...")
    files = collect_files(base_path, extensions, excludes)
    
    if not files:
        print("Keine passenden Dateien gefunden.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Gefunden: {len(files)} Dateien")
    
    if args.verbose:
        for f in files:
            print(f"  - {f.relative_to(base_path)}")
    
    # Markdown generieren
    print("Generiere Markdown...")
    markdown = generate_markdown(base_path, files, extensions, excludes, project_name)
    
    # Ausgabe schreiben
    output_path.write_text(markdown, encoding="utf-8")
    
    # Statistik
    file_size = output_path.stat().st_size
    size_str = f"{file_size:,}".replace(",", ".") + " Bytes"
    if file_size > 1024 * 1024:
        size_str = f"{file_size / (1024*1024):.2f} MB"
    elif file_size > 1024:
        size_str = f"{file_size / 1024:.2f} KB"
    
    print(f"\n✓ Export abgeschlossen!")
    print(f"  Datei: {output_path}")
    print(f"  Größe: {size_str}")
    print(f"  Dateien: {len(files)}")


if __name__ == "__main__":
    main()

