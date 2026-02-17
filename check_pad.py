import os

# Kopieer hier exact het pad uit je app.py
IDRIVE_PATH = "/Users/walterbruylandts/Cloud-Drive/ElpeeCollectie"

# Vul hier de artiest en titel in van het album dat NIET werkt
test_artiest = "NAAM_ARTIEST" 
test_titel = "NAAM_ALBUM"

volledig_pad = os.path.join(IDRIVE_PATH, test_artiest, test_titel)

print(f"--- Diagnose Start ---")
print(f"1. Ik zoek in de map: {volledig_pad}")

if os.path.exists(volledig_pad):
    print("2. ✓ De map is gevonden!")
    bestanden = os.listdir(volledig_pad)
    print(f"3. Inhoud van de map ({len(bestanden)} bestanden):")
    for f in bestanden:
        print(f"   - {f}")
else:
    print("2. ✗ FOUT: De map bestaat niet volgens Python.")
    # Check of de hoofdmap wel bestaat
    if os.path.exists(IDRIVE_PATH):
        print(f"   Tip: De hoofdmap '{IDRIVE_PATH}' bestaat wel.")
        print("   Mogelijke mappen in deze hoofdmap:")
        print(os.listdir(IDRIVE_PATH)[:5], "... (en meer)")
    else:
        print(f"   Tip: Zelfs de hoofdmap '{IDRIVE_PATH}' is niet vindbaar!")