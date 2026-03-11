from utils import save_player, select_player, open_box
from db_init import collection_monstres, collection_player, collection_items
from colorama import Fore, Style
import random
import time

def start_game():
    player = save_player()
    equipe = select_player(player)
    start(player, equipe)

def start(player, squad):
    monsters = list(collection_monstres.find())
    vague = 1
    ennemis(squad, vague, player, monsters)

def ennemis(squad, vague, player, monsters):
    while True: 
        print(f"\nVAGUE {vague}")

        if vague < 5:
            monstres_dispo = [m for m in monsters if m["pv"] <= 80]
        else: 
            monstres_dispo = monsters

        ennemis = random.sample(monstres_dispo, min(3, len(monstres_dispo)))
        
        for ennemi in ennemis:
            print(f"\n Un {ennemi['nom']} apparaît ! (PV : {ennemi['pv']})")
            time.sleep(1)

            ennemi_vaincu = False
            while not ennemi_vaincu:
                squad_life = [p for p in squad if p['pv'] > 0]

                if not squad_life:
                    print(Fore.RED + f"\n Votre équipe a été vaincu à la vague {vague} !" + Style.RESET_ALL)
                    collection_player.update_one({"nom": player}, {"$set" : {"score": vague}})
                    print(Fore.YELLOW + f"Score enregistré : {vague} vagues survécues." + Style.RESET_ALL)
                    return

                combattant = squad_life[0]
                print(f"{combattant['nom']} part au combat!")
                time.sleep(0.5)

                resultat = combat(combattant, ennemi, player)
                if resultat == "defaite":
                    combattant['pv'] = 0
                    print(Fore.RED + f"{combattant['nom']} a été vaincu par {ennemi['nom']}" + Style.RESET_ALL)
                    items = list(collection_items.find())
                    item = open_box(items)
                    if item:
                        print(Fore.YELLOW + "Le monstre as obtenu :", item['nom'] + Style.RESET_ALL)
                        apply_effect(item, ennemi)
                else:
                    print(Fore.GREEN + f"{combattant['nom']} a vaincu {ennemi['nom']}" + Style.RESET_ALL)
                    items = list(collection_items.find())
                    item = open_box(items)
                    if item:
                        print(Fore.YELLOW + "Tu as obtenu :", item['nom'] + Style.RESET_ALL)
                        apply_effect(item, combattant)
                    ennemi_vaincu = True
                time.sleep(1)

        vague += 1

def combat(perso, monters, player):
    pv_perso = perso['pv']
    pv_monters = monters['pv']

    while pv_perso > 0 and pv_monters > 0:
        degats_perso = max(0, perso['atk'] - monters['def'])
        pv_monters -= degats_perso
        print(f"{perso['nom']} inflige {degats_perso} dégâts ! (PV monstre : {max(0, pv_monters)})")
        time.sleep(0.4)

        if pv_monters <= 0:
            perso['pv'] = pv_perso
            monters['pv'] = 0
            save_pv(player, perso)
            return "victoire"
        
        degats_monster = max(0, monters['atk'] - perso['def'])
        pv_perso -= degats_monster
        print(f"{monters['nom']} inflige {degats_monster} dégâts ! (PV {perso['nom']} : {max(0, pv_perso)})")
        time.sleep(0.4)

    perso['pv'] = max(0, pv_perso)
    monters['pv'] = max(0, pv_monters)
    save_pv(player, perso)
    return "victoire" if pv_perso > 0 else "defaite"

def save_pv(player, perso):
    collection_player.update_one(
        {"nom": player, "equipe._id": perso['_id']},
        {"$set": {"equipe.$.pv" : perso['pv']}}
    )

def apply_effect(item, perso):
    nom = item["nom"].lower()
    effet = item["effets"]

    if "potion" in nom or "elexir" in nom:
        perso["pv"] += effet
        print(f"--- {perso['nom']} récupère {effet} PV ! (PV : {perso['pv']}) ---")
    elif "épée" in nom:
        perso["atk"] += effet
        print(f"--- {perso['nom']} gagne {effet} ATK supplémentaire (ATK : {perso['atk']}) ---")
    elif "bouclier" in nom:
        perso["def"] += effet
        print(f"--- {perso['nom']} gagne {effet} DEF supplémentaire (DEF : {perso['def']}) ---")
    elif "anneau" in nom or "amulette" in nom:
        perso["pv"] += effet
        perso["atk"] += effet // 2
        print(f"--- {perso['nom']} gagne {effet} PV et {effet // 2} ATK ! ---")
    elif "parchemin" in nom or "bombe" in nom:
        perso["atk"] += effet
        print(f"--- L'objet inflige {effet} dégâts bonus au prochain combat ---")
    elif "maudite" in nom.lower() or "piégé" in nom.lower():
        perso["pv"] += effet
        print(f"Mauvais objet ! {perso['nom']} perd {-effet} PV")

    elif "trèfle" in nom.lower():
        perso["atk"] += 20
        perso["def"] += 20
        perso["pv"] += effet
        print("Chance incroyable ! Bonus massif !")

    elif nom == "Rien":
        print("La boîte est vide...")
    else:
        print("Objet étrange... rien ne se passe")