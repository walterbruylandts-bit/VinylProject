from flask import Flask, render_template, request, send_from_directory
import sqlite3
import os

app = Flask(__name__)

# --- CONFIGURATIE ---
MY_TOKEN = "bRVfNphNvpIQFGMHjnOmbnvthDTzUbUddawubXLi"
IDRIVE_PATH = "/Users/walterbruylandts/Cloud-Drive/ElpeeCollectie"
# --------------------

@app.route('/play/<path:filename>')
def play_file(filename):
    full_path = filename if filename.startswith("/") else "/" + filename
    directory = os.path.dirname(full_path)
    file = os.path.basename(full_path)
    return send_from_directory(directory, file)

def haal_data_op(zoekterm=None):
    verbinding = sqlite3.connect('vinyl.db')
    verbinding.row_factory = sqlite3.Row
    cursor = verbinding.cursor()
    if zoekterm:
        query = "SELECT * FROM collectie WHERE artiest LIKE ? OR titel LIKE ? ORDER BY artiest ASC"
        cursor.execute(query, (f'%{zoekterm}%', f'%{zoekterm}%'))
    else:
        cursor.execute('SELECT * FROM collectie ORDER BY artiest ASC')
    data = cursor.fetchall()
    verbinding.close()
    return data

def schoon_naam(tekst):
    if not tekst: return ""
    return "".join(e for e in tekst if e.isalnum()).lower()

@app.route('/')
def index():
    zoekterm = request.args.get('search', '')
    lp_lijst = haal_data_op(zoekterm)
    return render_template('index.html', albums=lp_lijst, zoekterm=zoekterm)

@app.route('/album/<release_id>')
def album_detail(release_id):
    conn = sqlite3.connect('vinyl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM collectie WHERE release_id = ?', (release_id,))
    album = cursor.fetchone()

    if not album:
        conn.close()
        return "Album niet gevonden", 404

    artiest = album['artiest']
    titel = album['titel']
    
    gevonden_album_pad = None
    
    if os.path.exists(IDRIVE_PATH):
        try:
            artiesten_mappen = os.listdir(IDRIVE_PATH)
            s_doel_artiest = schoon_naam(artiest)
            
            for a_map in artiesten_mappen:
                s_a_map = schoon_naam(a_map)
                # Verbeterde match: kijkt of de namen op elkaar lijken (bijv. Credence vs Creedence)
                if s_a_map in s_doel_artiest or s_doel_artiest in s_a_map:
                    artiest_pad = os.path.join(IDRIVE_PATH, a_map)
                    album_mappen = os.listdir(artiest_pad)
                    s_doel_titel = schoon_naam(titel)
                    
                    for alb_map in album_mappen:
                        s_alb_map = schoon_naam(alb_map)
                        if s_alb_map in s_doel_titel or s_doel_titel in s_alb_map:
                            gevonden_album_pad = os.path.join(artiest_pad, alb_map)
                            break
        except Exception as e:
            print(f"Fout: {e}")

    mp3_bestanden = []
    extensies = ('.mp3', '.m4a', '.wav', '.flac')
    
    if gevonden_album_pad and os.path.exists(gevonden_album_pad):
        for root, dirs, files in os.walk(gevonden_album_pad):
            for file in files:
                if file.lower().endswith(extensies):
                    mp3_bestanden.append({'naam': file, 'pad': os.path.join(root, file)})
    
    mp3_bestanden.sort(key=lambda x: x['naam'])
    cursor.execute('SELECT * FROM tracks WHERE release_id = ?', (release_id,))
    bestaande_tracks = cursor.fetchall()
    conn.close()

    return render_template('detail.html', 
                           tracks=bestaande_tracks, 
                           release_id=release_id, 
                           hoes=album['hoes_url'], 
                           mp3s=mp3_bestanden, 
                           artiest=artiest, 
                           titel=titel, 
                           jaar=album['jaar'], 
                           genre=album['genre'], 
                           label=album['label'],
                           producer=album['producer'], 
                           bandleden=album['bandleden'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)