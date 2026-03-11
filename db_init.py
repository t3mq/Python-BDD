from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["game"]

# Personnages
collection_personnages = db["personnages"]

personnages = [
    { "nom": "Guerrier", "atk": 15, "def": 10, "pv": 100 },
    { "nom": "Mage", "atk": 20, "def": 5, "pv": 80 },
    { "nom": "Archer", "atk": 18, "def": 7, "pv": 90 },
    { "nom": "Voleur", "atk": 22, "def": 8, "pv": 85 },
    { "nom": "Paladin", "atk": 14, "def": 12, "pv": 110 },
    { "nom": "Sorcier", "atk": 25, "def": 3, "pv": 70 },
    { "nom": "Chevalier", "atk": 17, "def": 15, "pv": 120 },
    { "nom": "Moine", "atk": 19, "def": 9, "pv": 95 },
    { "nom": "Berserker", "atk": 23, "def": 6, "pv": 105 },
    { "nom": "Chasseur", "atk": 16, "def": 11, "pv": 100 } 
]

# Monstres
collection_monstres = db["monstres"]
monstres = [
    { "nom": "Gobelin", "atk": 10, "def": 5, "pv": 50 },
    { "nom": "Orc", "atk": 12, "def": 8, "pv": 70 },
    { "nom": "Troll", "atk": 15, "def": 10, "pv": 100 },
    { "nom": "Dragon", "atk": 25, "def": 20, "pv": 200 },
    { "nom": "Loup-garou", "atk": 18, "def": 12, "pv": 80 },
    { "nom": "Vampire", "atk": 20, "def": 15, "pv": 90 },
    { "nom": "Démon", "atk": 22, "def": 18, "pv": 110 },
    { "nom": "Golem", "atk": 17, "def": 25, "pv": 150 },
    { "nom": "Squelette", "atk": 8, "def": 3, "pv": 40 },
    { "nom": "Zombi", "atk": 9, "def": 4, "pv": 60 }
]

# Items
collection_items = db["items"]
items = [
{ "nom": "Petite potion de soin", "effets": 20, "drop": 0.20 },
{ "nom": "Potion de soin", "effets": 50, "drop": 0.25 },
{ "nom": "Grande potion de soin", "effets": 100, "drop": 0.08 },
{ "nom": "Élixir de vie", "effets": 999, "drop": 0.02 },

{ "nom": "Potion de force", "effets": 10, "drop": 0.12 },
{ "nom": "Potion de défense", "effets": 10, "drop": 0.12 },
{ "nom": "Potion de vitesse", "effets": 5, "drop": 0.10 },
{ "nom": "Potion critique", "effets": 25, "drop": 0.07 },

{ "nom": "Épée rouillée", "effets": 5, "drop": 0.18 },
{ "nom": "Épée enchantée", "effets": 15, "drop": 0.10 },
{ "nom": "Épée légendaire", "effets": 30, "drop": 0.02 },

{ "nom": "Bouclier en bois", "effets": 5, "drop": 0.18 },
{ "nom": "Bouclier en fer", "effets": 10, "drop": 0.12 },
{ "nom": "Armure du dragon", "effets": 25, "drop": 0.03 },

{ "nom": "Anneau de régénération", "effets": 5, "drop": 0.06 },
{ "nom": "Amulette magique", "effets": 8, "drop": 0.07 },
{ "nom": "Amulette du héros", "effets": 15, "drop": 0.03 },

{ "nom": "Parchemin de feu", "effets": 20, "drop": 0.10 },
{ "nom": "Parchemin de glace", "effets": 15, "drop": 0.10 },
{ "nom": "Parchemin de foudre", "effets": 30, "drop": 0.05 },

{ "nom": "Bombe artisanale", "effets": 25, "drop": 0.08 },
{ "nom": "Totem de protection", "effets": 15, "drop": 0.06 },

{ "nom": "Champignon étrange", "effets": 0, "drop": 0.07 },
{ "nom": "Potion instable", "effets": 0, "drop": 0.05 },
{ "nom": "Coffre piégé", "effets": -20, "drop": 0.04 },
{ "nom": "Pièce maudite", "effets": -10, "drop": 0.04 },
{ "nom": "Trèfle porte-bonheur", "effets": 100, "drop": 0.01 },
{ "nom": "Rien", "effets": 0, "drop": 0.25}
]
collection_player = db["joueurs"]

def init_db():
    collection_personnages.drop()
    collection_monstres.drop()
    collection_items.drop()
    collection_personnages.insert_many(personnages)
    collection_monstres.insert_many(monstres)
    collection_items.insert_many(items)
    print("Seed terminé...")