from utils import save_player, select_player, open_box
from db_init import collection_items, collection_monstres, collection_player
from colorama import Fore, Style

import random
import time

"""
On demande au joueur de saisir son pseudo avec la fonction save_player()
Permet au joueur de choisir son équipe avec la fonction select_player()
On démarre le jeu avec la fonction start(player, squad)
"""
def start_game():
    player = save_player()
    squad = select_player(player)
    start(player, squad)

"""
On récupère tous les monstres disponibles
On initialise la vague (1)
On initialise l'index du combattant à 0
Tant que le jeu n'est aps terminé :
    - Afficher "vague X"
    - Sélectionner 3 monstres pour cette vague avec la fonction choisir_monstres()
    - Pour chaque monstre :
        1. Afficher le monstre (afficher_monstre)
        2. Lancer le combat avec tour_combat
        3. Si l'équipe perd, afficher la fin de partie avec la fonction fin_partie() et quitter la boucle
    - Passer à la vague suivante
"""
def start(player, squad):
    monsters = list(collection_monstres.find())
    vague = 1
    fighter_index = 0

    while True:
        print(f"\n---- VAGUE {vague} ----")
        enemies = choisir_monstres(monsters, vague)

        for enemy in enemies:
            afficher_monstre(enemy)
            victoire, fighter_index = tour_combat(squad, enemy, player, fighter_index)
            if not victoire:
                fin_partie(player, vague)
                return

        vague += 1

"""
Si la vague < 5 : on garde que les monstres faibles (PV <= 80)
Sinon on utilise tous les monstres
On sélectionne aléatoirement 3 monstres parmi ceux disponibles
On retourne la liste des monstres choisis
"""
def choisir_monstres(monsters, vague):
    if vague < 5:
        dispo = [m for m in monsters if m["pv"] <= 80]
    else:
        dispo = monsters

    return [dict(m) for m in random.sample(dispo, min(3, len(dispo)))]

"""
On affiche le nom et les PV du monstre
On attend 1 seconde
"""
def afficher_monstre(enemy):
    print(f"\nUn {enemy['nom']} apparaît ! (PV : {enemy['pv']})")
    time.sleep(1)

"""
Pour chaque membre de l'équipe (à partir de start_index):
    - Si le personnage est mort (pv < 0) on passe au suivant
    - Sinon : 
        1. Afficher que le personnage attaque
        2. Lancer le combat avec combat()
        3.Si défaire :
            - Mettre les PV à 0
            - On affiche que le personnage a perdu
            - On lance la fonction drop_item()
        4. Si victoire :
            - On affiche que le personnage a gagné
            - On lance la fonction drop_item()
            - On retourne la victoire et index du prochain combattant
Si aucun personnage ne gagne, on retourne "défaite" et index le prochain combattant
"""
def tour_combat(squad, enemy, player, start_index=0):
    n = len(squad)
    current = start_index

    for _ in range(n):
        fighter = squad[current % n]
        next_index = (current + 1) % n
        current += 1

        if fighter["pv"] <= 0:
            continue

        print(f"{fighter['nom']} part au combat !")
        result = combat(fighter, enemy, player)

        if result == "defaite":
            fighter["pv"] = 0
            print(Fore.RED + f"{fighter['nom']} est vaincu !" + Style.RESET_ALL)
            drop_item(fighter)
        else:
            print(Fore.GREEN + f"{fighter['nom']} gagne !" + Style.RESET_ALL)
            drop_item(fighter)
            return True, current % n

    return False, next_index

"""
On afficher que l'équipe a perdu à la vague X
Enregistrer le score du joueur dans la base de données
On affiche le score
"""
def fin_partie(player, vague):
    print(Fore.RED + f"\nVotre équipe a perdu à la vague {vague}" + Style.RESET_ALL)

    collection_player.update_one(
        {"nom": player},
        {"$set": {"score": vague}}
    )

    print(Fore.YELLOW + f"Score enregistré : {vague}" + Style.RESET_ALL)


"""
On sélectionne aléatoirement un object avec open_box()
Si un objet est trouvé : 
    - On affiche le nom de l'objet
    - On applique l'effet sur le personnage avec apply_effect()
"""
def drop_item(perso):
    items = list(collection_items.find())
    item = open_box(items)

    if item:
        print(Fore.YELLOW + f"Objet obtenu : {item['nom']}" + Style.RESET_ALL)
        apply_effect(item, perso)

""" 
On initialise les PV du perso et du monstre
Tant que PV perso > 0 et PV monstre > 0
    - Le perso inflige des dégâts au monstre (ATK - DEF)
    - Vérifier si le monstre est mort : si oui, on save les PV et on retourne "Victoire"
    - Le monstre inflige des dégâts au perso (ATK - DEF)
Mettre à jour les PV du perso dans la db avec save_pv()
On retourne "Victoire" si PV perso > 0 sinon "Défaite"
"""
def combat(perso, monster, player):
    pv_perso = perso["pv"]
    pv_monster = monster["pv"]

    while pv_perso > 0 and pv_monster > 0:
        degats = max(0, perso['atk'] - monster['def'])
        pv_monster -= degats
        print(f"{perso['nom']} inflige {degats} dégâts")
        time.sleep(0.4)

        if pv_monster <= 0:
            perso["pv"] = pv_perso
            monster["pv"] = 0
            save_pv(player, perso)
            return "victoire"

        degats = max(0, monster["atk"] - perso["def"])
        pv_perso -= degats
        print(f"{monster['nom']} inflige {degats} dégâts !")
        time.sleep(0.4)

    perso["pv"] = max(0, pv_perso)
    save_pv(player, perso)

    return "victoire" if pv_perso > 0 else "defaite"

def save_pv(player, perso):
    collection_player.update_one(
        {"nom": player, "equipe._id": perso["_id"]},
        {"$set": {"equipe.$.pv" : perso["pv"]}}
    )

"""
On récupère le nom et l'effet de l'objet
Selon le type d'objet:
    - Potion / Elexir -> on soigne le perso avec heal()
    - Epée -> bonus d'attaque avec bonus_atk()
    - Bouclier -> bonus de défense avec bonus_def()
    etc...
    - Rien -> on affiche que la boîte est vide
"""
def apply_effect(item, perso):
    nom = item["nom"].lower()
    effet = item["effets"]

    if "potion" in nom or "elexir" in nom:
        heal(perso, effet)
    elif "épée" in nom:
        bonus_atk(perso, effet)
    elif "bouclier" in nom:
        bonus_def(perso, effet)
    elif "anneau" in nom or "amulette" in nom:
        bonus_mixte(perso, effet)
    elif "parchemin" in nom or  "bombe" in nom:
        bonus_atk(perso, effet)
    elif "maudite" in nom or "piégé" in nom:
        malus_pv(perso, effet)
    elif "trèfle" in nom:
        bonus_chance(perso, effet)
    elif nom == "rien":
        print("La boite est vide...")


"""
heal -> ajoute des PV
bonus_atk -> augmente les dégâts d'attaque
bonus_def -> augmente la défense du personnage
bonus_mixte -> augmente les PV + l'attaque à moitié
malus_pv -> retire des PV au personnage
bonus_chance -> augmente PV, +20 ATK, +20 DEF
"""
def heal(perso, effet):
    perso["pv"] += effet
    print(f"{perso['nom']} récupère {effet}")

def bonus_atk(perso, effet):
    perso["atk"] += effet
    print(f"{perso['nom']} gagne {effet} ATK")

def bonus_def(perso, effet):
    perso["def"] += effet
    print(f"{perso['nom']} gagne {effet} DEF")

def bonus_mixte(perso, effet):
    perso["pv"] += effet
    perso["atk"] += effet // 2
    print(f"{perso['nom']} gagne {effet} PV et {effet//2} ATK")

def malus_pv(perso, effet):
    perso["pv"] += effet
    print(f"Mauvais objet ! {perso['nom']} perd {-effet} PV")

def bonus_chance(perso, effet):
    perso["atk"] += 20
    perso["def"] += 20
    perso["pv"] += effet
    print("Chance incroyable ! Bonus massif !")