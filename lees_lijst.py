import csv

# We vertellen Python hoe je bestand heet
bestandsnaam = 'WalterDiscArch-collection-20260125-0938.csv'

try:
    with open(bestandsnaam, mode='r', encoding='utf-8') as bestand:
        # De CSV-lezer klaarmaken
        lezer = csv.DictReader(bestand)
        
        print("Ik begin met het lezen van je collectie...\n")
        
        aantal = 0
        for regel in lezer:
            # We halen de artiest en titel uit de kolommen
            # Let op: Discogs noemt deze kolommen vaak 'Artist' en 'Title'
            artiest = regel.get('Artist', 'Onbekende artiest')
            titel = regel.get('Title', 'Onbekende titel')
            
            print(f"{aantal + 1}: {artiest} - {titel}")
            aantal += 1
            
        print(f"\nKlaar! Ik heb {aantal} elpees geteld.")

except FileNotFoundError:
    print(f"Oeps! Ik kan het bestand '{bestandsnaam}' niet vinden in deze map.")
except Exception as e:
    print(f"Er ging iets mis: {e}")