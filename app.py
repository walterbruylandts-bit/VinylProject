from flask import Flask, render_template, request
import sqlite3
import os
import cloudinary
import cloudinary.api

app = Flask(__name__)

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

CLOUD_BASE = "music/1mp3_Archief"


def haal_data_op(zoekterm=None):
    verbinding = sqlite3.connect("vinyl.db")
    verbinding.row_factory = sqlite3.Row
    cursor = verbinding.cursor()

    if zoekterm:
        query = "SELECT * FROM collectie WHERE artiest LIKE ? OR titel LIKE ? ORDER BY artiest ASC"
        cursor.execute(query, (f"%{zoekterm}%", f"%{zoekterm}%"))
    else:
        cursor.execute("SELECT * FROM collectie ORDER BY artiest ASC")

    data = cursor.fetchall()
    verbinding.close()
    return data


def cloud_folder(artiest, titel):
    a = (artiest or "").strip().replace(" ", "_")
    t = (titel or "").strip().replace(" ", "_")
    return f"{CLOUD_BASE}/{a}/{t}"


def list_mp3_urls(folder_prefix):
    res = cloudinary.api.resources(
        type="upload",
        resource_type="video",
        prefix=folder_prefix,
        max_results=500
    )

    urls = []
    for r in res.get("resources", []):
        url = r.get("secure_url")
        if url and url.lower().endswith(".mp3"):
            urls.append(url)

    urls.sort()
    return urls


@app.route("/")
def index():
    zoekterm = request.args.get("search", "")
    lp_lijst = haal_data_op(zoekterm)
    return render_template("index.html", albums=lp_lijst, zoekterm=zoekterm)


@app.route("/album/<release_id>")
def album_detail(release_id):
    conn = sqlite3.connect("vinyl.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM collectie WHERE release_id = ?", (release_id,))
    album = cursor.fetchone()

    if not album:
        conn.close()
        return "Album niet gevonden", 404

    artiest = album["artiest"]
    titel = album["titel"]

    cursor.execute("SELECT * FROM tracks WHERE release_id = ?", (release_id,))
    bestaande_tracks = cursor.fetchall()
    conn.close()

    mp3_bestanden = []

    try:
        folder = cloud_folder(artiest, titel)
        print("ZOEK MAP:", folder)

        urls = list_mp3_urls(folder)
        print("MP3 COUNT:", len(urls))

        for u in urls:
            fname = u.split("/")[-1]
            naam = fname.replace(".mp3", "").replace("_", " ")
            mp3_bestanden.append({
                "naam": naam,
                "url": u
            })

    except Exception as e:
        print("Cloudinary fout:", e)

    return render_template(
        "detail.html",
        tracks=bestaande_tracks,
        release_id=release_id,
        hoes=album["hoes_url"],
        mp3s=mp3_bestanden,
        artiest=artiest,
        titel=titel,
        jaar=album["jaar"],
        genre=album["genre"],
        label=album["label"],
        producer=album["producer"],
        bandleden=album["bandleden"]
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
