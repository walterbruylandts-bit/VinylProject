import sqlite3
import csv

# De naam van jouw bestand (precies zoals het in je map staat)
csv_bestand = 'WalterDiscArch-collection-20260125-0938.csv'

# Verbinding maken met de database (maakt het bestand vinyl.db aan)
verbinding = sqlite3.connect('vinyl.db')
cursor = verbinding.cursor()

# De tabel 'collectie' aanmaken met kolommen voor je gegevens
cursor.execute('''
CREATE TABLE IF NOT EXISTS collectie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    release_id TEXT,
    artiest TEXT,
    titel TEXT,
    idrive_pad TEXT
)
''')

# We maken de tabel eerst even leeg om dubbele regels te voorkomen
cursor.execute('DELETE FROM collectie')

try:
    with open(csv_bestand, mode='r', encoding='utf-8') as bestand:
        lezer = csv.DictReader(bestand)
        
        aantal = 0
        for regel in lezer:
            # We halen de info uit de CSV-kolommen
            r_id = regel.get('release_id', '')
            artiest = regel.get('Artist', 'Onbekend')
            titel = regel.get('Title', 'Onbekend')
            
            # De info in de database stoppen
            cursor.execute('INSERT INTO collectie (release_id, artiest, titel) VALUES (?, ?, ?)', 
                           (r_id, artiest, titel))
            aantal += 1
    
    verbinding.commit()
    print(f"Gelukt! Er staan nu {aantal} elpees in je database 'vinyl.db'.")

except Exception as e:
    print(f"Er ging iets mis: {e}")

verbinding.close()