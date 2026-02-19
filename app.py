from flask import Flask, render_template, request
import sqlite3
import os
import re

import cloudinary
import cloudinary.api

app = Flask(__name__)

# --- Discogs token (mag je laten staan als je het elders gebruikt) ---
MY_TOKEN = os.environ.get("bRVfNphNvpIQFGMHjnOmbnvthDTzUbUddawubXLi", "")

# --- Cloudinary creds komen uit Render Environment Variables ---
CLOUDINARY_CLOUD_NAME = os.environ.get("dq2wktt6i", "")
CLOUDINARY_API_KEY = os.environ.get("134723385821683", "")
CLOUDINARY_API_SECRET = os.environ.get("GrznISqUrlLq_RhuoyBBFhoZy10", "")

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)

# Pas dit aan als jouw root anders is
CLOUD_ROOT = "music/1mp3_Archief"


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


def slugify(s: str) -> str:
    if not s:
        return ""
    s = s.strip()
    s = re.sub(r"\s+", "_", s)
    s = s.replace("/", "_")
    s = re.sub(r"[^A-Za-z0-9_\-()]+", "", s)
    return s


def cloud_folder(artiest: str, titel: str) -> str:
    return f"{CLOUD_ROOT}/{slugify(artiest)}/{slugify(titel)}"


def list_mp3_urls(prefix: str):
    """
    Haalt alle audio/video assets onder een folder-prefix op.
    Cloudinary gebruikt 'video' resource_type voor mp3's.
    """
    urls = []
    next_cursor = None

    while True:
        resp = cloudinary.api.resources(
            type="upload",
            prefix=prefix + "/",          # belangrijk: trailing slash
            resource_type="video",        # mp3 staat onder video
            max_results=500,
            next_cursor=next_cursor
        )

        for r in resp.get("resources", []):
            # secure_url is de mp3 url
            urls.append({
                "naam": os.path.basename(r.get("public_id", "")) + (("." + r["format"]) if r.get("format") else ""),
                "url": r.get("secure_url", "")
            })

        next_cursor = resp.get("next_cursor")
        if not next_cursor:
            break

    # sorteer op naam zodat SideA/SideB toch netjes blijft als je naamgeving goed is
    urls.sort(key=lambda x: x["naam"].lower())
    return urls


@app.route('/')
def index():
    zoekterm = request.args.get('search', '')
    lp_lijst = haal_data_op(zoekterm)
    return render_template(
    'detail.html',
    tracks=bestaande_tracks,
    release_id=release_id,
    hoes=album['hoes_url'],
    mp3s=mp3s,
    artiest=artiest,
    titel=titel,
    jaar=album['jaar'],
    genre=album['genre'],
    label=album['label'],
    producer=album['producer'],
    bandleden=album['bandleden'],
    debug_msg="APP.PY NIEUWE VERSIE LIVE"
)


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

    folder = cloud_folder(artiest, titel)
    print("ZOEK MAP:", folder)  # debug in Render Logs

    mp3s = []
    try:
        mp3s = list_mp3_urls(folder)
print("MP3 COUNT:", len(mp3s))
    except Exception as e:
        print("Cloudinary fout:", e)

    cursor.execute('SELECT * FROM tracks WHERE release_id = ?', (release_id,))
    bestaande_tracks = cursor.fetchall()
    conn.close()

    return render_template(
        'detail.html',
        tracks=bestaande_tracks,
        release_id=release_id,
        hoes=album['hoes_url'],
        mp3s=mp3s,
        artiest=artiest,
        titel=titel,
        jaar=album['jaar'],
        genre=album['genre'],
        label=album['label'],
        producer=album['producer'],
        bandleden=album['bandleden']
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
