import sqlite3

def fix():
    conn = sqlite3.connect('vinyl.db')
    cursor = conn.cursor()
    try:
        # Voeg de kolom hoes_url toe aan de tabel collectie
        cursor.execute('ALTER TABLE collectie ADD COLUMN hoes_url TEXT')
        print("Kolom 'hoes_url' succesvol toegevoegd!")
    except sqlite3.OperationalError:
        print("De kolom bestond al of er is iets anders mis.")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix()