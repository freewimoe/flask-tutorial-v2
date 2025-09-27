# Flask Claude Example

Eine vollständige Flask-Webanwendung mit Benutzerauthentifizierung, Datenbankintegration und File-Upload-Funktionalität.

## Features

- 🔐 **Benutzerauthentifizierung**: Registrierung und Anmeldung
- 📝 **Blog-System**: Erstellen und Anzeigen von Posts
- 📁 **File Upload**: Hochladen von Dateien (jpg, png, pdf, txt)
- 🗄️ **Datenbank**: SQLite mit SQLAlchemy ORM
- 🔒 **Sicherheit**: CSRF-Schutz mit Flask-WTF
- 🎨 **Frontend**: Responsive HTML/CSS Templates
- 🌐 **API**: RESTful Endpoints für Posts und Benutzer

## Installation

1. **Repository klonen:**
   ```bash
   git clone https://github.com/[IHR_USERNAME]/flask-claude-example.git
   cd flask-claude-example
   ```

2. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Datenbank initialisieren:**
   ```bash
   python -m flask --app flask_claude_example.py init-db
   ```

4. **Anwendung starten:**
   ```bash
   python -m flask --app flask_claude_example.py run
   ```

5. **Browser öffnen:**
   Gehen Sie zu `http://127.0.0.1:5000`

## Projektstruktur

```
flask-claude-example/
│
├── flask_claude_example.py    # Hauptanwendung
├── requirements.txt           # Python-Abhängigkeiten
├── .gitignore                # Git-Ignorierdateien
│
├── templates/                 # HTML-Templates
│   ├── home.html
│   ├── register.html
│   ├── login.html
│   ├── create_post.html
│   ├── upload_file.html
│   ├── dashboard.html
│   ├── 404.html
│   └── 500.html
│
├── static/                    # Statische Dateien
│   └── style.css
│
└── uploads/                   # Hochgeladene Dateien (wird automatisch erstellt)
```

## API Endpoints

- `GET /api/posts` - Alle Posts abrufen
- `GET /api/user/<id>` - Benutzerinformationen abrufen
- `GET /api/weather?city=<city>` - Wetter-Demo API
- `GET /api/search?q=<query>` - Posts durchsuchen
- `POST /ask_claude` - LLM Integration (Demo)

## Technologien

- **Backend**: Flask 2.3.3
- **Datenbank**: SQLite mit Flask-SQLAlchemy
- **Formulare**: Flask-WTF
- **Sicherheit**: Werkzeug Password Hashing
- **Frontend**: HTML5, CSS3
- **HTTP Client**: Requests

## Entwicklung

Zum Entwickeln mit Debug-Modus:

```bash
python -m flask --app flask_claude_example.py run --debug
```

## Lizenz

MIT License - siehe LICENSE Datei für Details.

## Autor

Erstellt mit GitHub Copilot