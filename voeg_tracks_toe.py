import sqlite3

verbinding = sqlite3.connect('vinyl.db')
cursor = verbinding.cursor()

# We maken een nieuwe tabel speciaal voor de tracks
cursor.execute('''
CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    release_id TEXT,
    kant TEXT,
    positie TEXT,
    titel TEXT,
    duur TEXT,
    idrive_link TEXT
)
''')

verbinding.commit()
verbinding.close()
print("De database is nu klaar om tracks op te slaan!")