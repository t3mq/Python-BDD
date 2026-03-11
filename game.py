from utils import save_player, select_player, open_box
from db_init import collection_items, collection_monstres, collection_player
from colorama import Fore, Style

import random
import time

def start_game():
    player = save_player()
    squad = select_player(player)
    start(player, squad)

def start(player, squad):
    monsters = list(collection_monstres.find())
    vague = 1
    fighter_index = 0

    while True:
        print(f"\n----VAGUE {vague}----")
        enemies = choisir_monstres(monsters, vague)

        for enemy in enemies:
            afficher_monstre(enemy)
            victoire, fighter_index = tour_combat(squad, enemy, player, fighter_index)
            if not victoire:
                fin_partie(player, vague)
                return

        vague += 1

def choisir_monstres(monsters, vague):
    if vague < 5:
        dispo = [m for m in monsters if m["pv"] <= 80]
    else:
        dispo = monsters

    return [dict(m) for m in random.sample(dispo, min(3, len(dispo)))]

def afficher_monstre(enemy):
    print(f"\nUn {enemy['nom']} apparaît ! (PV : {enemy['pv']})")
    time.sleep(1)

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


def fin_partie(player, vague):
    print(Fore.RED + f"\nVotre équipe a perdu à la vague {vague}" + Style.RESET_ALL)

    collection_player.update_one(
        {"nom": player},
        {"$set": {"score": vague}}
    )

    print(Fore.YELLOW + f"Score enregistré : {vague}" + Style.RESET_ALL)

def drop_item(perso):
    items = list(collection_items.find())
    item = open_box(items)

    if item:
        print(Fore.YELLOW + f"Objet obtenu : {item['nom']}" + Style.RESET_ALL)
        apply_effect(item, perso)

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