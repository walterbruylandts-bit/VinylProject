import sqlite3
import requests
import time

# --- CONFIGURATIE ---
MY_TOKEN = "bRVfNphNvpIQFGMHjnOmbnvthDTzUbUddawubXLi"
# --------------------

def update_alle_metadata():
    conn = sqlite3.connect('vinyl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # We zoeken nu ook naar albums waar bandleden nog leeg zijn
    cursor.execute("SELECT release_id, artiest, titel FROM collectie WHERE bandleden IS NULL")
    albums = cursor.fetchall()

    print(f"Gevonden: {len(albums)} albums om volledig te verrijken...")

    for index, album in enumerate(albums):
        release_id = album['release_id']
        print(f"[{index+1}/{len(albums)}] Analyseren: {album['artiest']} - {album['titel']}...")

        url = f"https://api.discogs.com/releases/{release_id}"
        headers = {"Authorization": f"Discogs token={MY_TOKEN}"}
        
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                d = r.json()
                
                # Basis info
                jaar = d.get('year')
                genre = ", ".join(d.get('genres', []))
                label = d.get('labels', [{}])[0].get('name', 'Onbekend')
                
                # Bandleden & Producers filteren uit extraartists
                extra_artists = d.get('extraartists', [])
                producers = [a['name'] for a in extra_artists if 'Producer' in a.get('role', '')]
                # Let op: Discogs heeft bandleden vaak in de main artist 'members' sectie, 
                # maar voor verzamelalbums staan ze vaak in de credits.
                credits = [f"{a['name']} ({a['role']})" for a in extra_artists if a.get('role') and 'Producer' not in a.get('role')]

                producer_str = ", ".join(producers[:3]) # Pak de eerste 3 producers
                band_str = "; ".join(credits[:10]) # Pak de eerste 10 belangrijke credits/leden

                cursor.execute('''UPDATE collectie SET jaar = ?, genre = ?, label = ?, 
                                producer = ?, bandleden = ? WHERE release_id = ?''', 
                                (jaar, genre, label, producer_str, band_str, release_id))
                conn.commit()
                print(f"   ✓ Opgeslagen: {jaar} | Producer: {producer_str}")
            elif r.status_code == 429:
                print("   ! Rate limit bereikt. 30 sec pauze...")
                time.sleep(30)
        except Exception as e:
            print(f"   ! Fout: {e}")

        time.sleep(1.2) # Discogs vriendelijk blijven

    conn.close()
    print("\nKlaar! Alles is bijgewerkt.")

if __name__ == "__main__":
    update_alle_metadata()