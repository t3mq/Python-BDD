from db_init import collection_player, collection_personnages, collection_items
from colorama import Fore, Style
import sys
import tty
import termios
import os
import random

characters = list(collection_personnages.find())
personnages = characters

"""
Créer une liste vide pour l'équipe 
Créer une copie des personnages disponibles 
Pour chaque slot (On a 3 slot au total):
    - On appele la fonction choisir_personnage() pour sélectionner un personnage
    - On Ajoute le personnage sélectionné à l'équipe
On enregistre l'équipe dans la base de donnée avec save_team()
On retourne l'équipe
"""
def select_player(player):
    equipe = []
    disponibles = [dict(p) for p in personnages]

    for slot in range(3):
        perso = choisir_personnage(slot, equipe, disponibles)
        equipe.append(perso)

    save_team(player, equipe)
    return equipe

"""
On initialise sélection à 0 (premier personnage de la liste)
Tant que l'utilisateur n'a pas validé :
    - On affiche la sélection actuelle avec afficher_selection()
    - Lire la touche du joueur avec get_key()
    - Si fléche du haut (\x1b[A) -> on décrémente la selection
    - Si flèche du bas (\x1b[B) -> on incrémente la selection
    - Si touche entrée (\r) :
        1. Retirer le personnage choisi de la notre liste disponibles
        2. Afficher l'équipe avec ce personnage avec la fonction afficher_equipe()
        3. On retourne le personnage choisi
"""
def choisir_personnage(slot, equipe, disponibles):
    selection = 0

    while True:
        afficher_selection(slot, equipe, disponibles, selection)
        key = get_key()

        if key == "\x1b[A":
            selection = (selection - 1) % len(disponibles)

        elif key == "\x1b[B":
            selection = (selection + 1) % len(disponibles) 
        elif key == "\r":
            perso = disponibles.pop(selection)
            afficher_equipe(equipe + [perso])
            return perso
        
"""
On efface l'écran avec os.system("clear")
On affiche les noms des personnages déjà choisi (equipe)
On affiche le message "Choisis ton personnage x/3"
Pour chaque personnage disponible:
    - On affiche nom | ATK | DEF | PV
    - Si c'est le personnage sélectionné -> on l'affiche en vert
    - Sinon -> on l'affiche en blanc
"""
def afficher_selection(slot, equipe, disponibles, selection):
    os.system("clear")

    equipe_str = ", ".join(p['nom'] for p in equipe) if equipe else ""
    print(f"Equipe : {equipe_str}")
    print(f"\nChoisis ton personnage {slot +1}/3")

    for i, p in enumerate(disponibles):
        stats = f"{p['nom']} | ATK : {p['atk']} | DEF : {p['def']} | PV : {p['pv']}"

        if i == selection:
            print(Fore.GREEN + "> " + stats + Style.RESET_ALL)
        else:
            print(" " + stats)

"""
On affiche les personnages dans l'équipe
"""
def afficher_equipe(equipe):
    equipe_str = ",  ".join(p['nom'] for p in equipe)
    print("---")
    print(f"\nEquipe : {equipe_str}")

"""
Pour chaque personnage de l'équipe on garde _id, nom, pv, atk, def
On met à jour l'équipe du joueur dans la db
"""
def save_team(player, equipe):
    collection_player.update_one(
        {"nom": player},
        {"$set": {
            "equipe": [
                {
                    "_id": p["_id"],
                    "nom": p["nom"],
                    "pv": p["pv"],
                    "atk": p["atk"],
                    "def": p["def"]
                }
                for p in equipe
            ]
        }}
    )

"""
On affiche "Tableau des scores"
On récupère les 3 joueurs avec le meilleur score avec collection_player
Si aucun joueur -> on affiche "Aucun score enregistré"
Sinon, pour chaque joueur :
    - Choisir une couleur selon le rang
    - On affiche le rang, le nom et le score en vague
"""
def leaderboard():
    os.system("clear")
    print("Tableau des scores :")
    
    players = list(collection_player.find().sort("score", -1).limit(3))

    if not players:
        print("Aucun score enregistré...")
        return
    
    colors = [Fore.YELLOW, "\033[38;5;208m", Fore.RED]

    for i, player in enumerate(players):
        color = colors[i] if i < len(colors) else Style.RESET_ALL
        print(
            f"{color}{i + 1}. {player['nom']} |"
            f" Score : {player['score']} vagues survécues {Style.RESET_ALL}"
        )

"""
Tant que le pseudo n'est pas valide :
    - Demander le pseudo au joueur
    - Si longueur entre 3 et 20 caractères:
        1. Ajouter le joueur dans la db avec score=0
        2. Afficher un message de bienvenue
        3. Retourner le pseudo
    - Sinon -> on affiche un message d'erreur
"""
def save_player():
    while True:
        player = input("Veuillez saisir un pseudo : ")
        if 3 <= len(player) <= 20:
            collection_player.insert_one({"nom":  player, "score": 0})
            print(f"Bienvenue, {player} ! Votre nom a été enregistré.")
            return player
        
        print("Le pseudo doit contenir entre 3-20 caractères.")

"""

"""
def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)

        if ch1 == "\x1b":
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch1 + ch2 + ch3

        return ch1

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

"""
On récupère tous les items disponibles dans la base de données
On tire un nombre aléatoire r entre 0 et 1
On parcour chaque item :
    - On ajoute la probabilité de drop à un total cumulatif
    - Si r <= total on retourne cet item
Si aucun item sélectionné -> on retourne None
"""
def open_box(items):
    items = list(collection_items.find())

    r = random.random()
    total = 0

    for item in items:
        total += item["drop"]

        if r <= total:
            return item
    
    return None