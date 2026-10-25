REWE Kalorien-, Makro- und Budgetrechner – Live-Angebotsversion

Dateien:
- index.html: Rechner und Oberfläche
- server.py: kleiner lokaler Python-Server für den Live-Abruf

Start unter Windows:
1. Lege index.html und server.py in denselben Ordner.
2. Installiere Python 3, falls es noch nicht installiert ist.
3. Öffne den Ordner im Explorer, klicke in die Adressleiste, tippe cmd und drücke Enter.
4. Führe aus: py server.py
   (Alternativ: python server.py)
5. Öffne im Browser: http://127.0.0.1:8000/index.html
6. Klicke auf „Preise aktualisieren“ im Bereich „Live-Angebote aus Syke“.

Wichtig:
- Der Server läuft nur auf deinem eigenen Rechner und verwendet ausschließlich Pythons Standardbibliothek.
- Der Abruf liest öffentlich erreichbare Angebote von REWE Philip Monien in Syke aus. Das ist keine garantierte vollständige Produktpreisliste und keine offizielle REWE-API.
- REWE kann die Seitendarstellung ändern oder automatische Abrufe blockieren. In diesem Fall zeigt die Oberfläche eine Fehlermeldung und bietet weiterhin den Link zur offiziellen Angebotsseite.
- Live-Angebotspreise werden als Information angezeigt, aber nicht automatisch einem Lebensmittel zugeordnet, da Angebote häufig keine Nährwertdaten enthalten.
- Um den Rechner zu nutzen, muss das Serverfenster geöffnet bleiben. Beenden mit Strg+C.
