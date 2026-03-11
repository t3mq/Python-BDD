from db_init import collection_player, collection_personnages, collection_items
from colorama import Fore, Style

import sys
import tty
import termios
import os
import random

characters = list(collection_personnages.find())
personnages = characters
selection = 0

def choice(min, max, message):
    while True:
        try:
            nombre = int(input(message))
            if min <= nombre <= max:
                return nombre
            else:
                print(f"Veuillez entrer un nombre entre {min} et {max}.")
        except ValueError:
            print("Entrée invalide. Veuillez entrer un nombre.")

def select_player(player):
    equipe = []
    disponibles = [dict(p) for p in personnages]
    for slot in range(3):
        selection = 0
        while True:
            os.system("clear")
            equipe_str = ", ".join(p['nom'] for p in equipe) if equipe else ""
            print(f"Équipe : {equipe_str}")
            print(f"\nChoisis ton personnage {slot + 1}/3")
            for i, p in enumerate(disponibles):
                stats = f"{p['nom']} | ATK : {p['atk']}  DEF: {p['def']}  PV: {p['pv']}"
                if i == selection:
                    print(Fore.GREEN + "> " + stats + Style.RESET_ALL)
                else:
                    print(Style.RESET_ALL + "  " + stats)
            key = get_key()

            if key == "\x1b[A":   # flèche du haut
                selection = (selection - 1) % len(disponibles)
            elif key == "\x1b[B": # flèche du bas
                selection = (selection + 1) % len(disponibles)
            elif key == "\r":     # entrée
                p = disponibles.pop(selection)
                equipe.append(p)
                equipe_str = ", ".join(e['nom'] for e in equipe)
                print("---")
                print(f"\nÉquipe : {equipe_str}")
                break

    # Sauvegarder l'équipe en DB
    collection_player.update_one(
        {"nom": player},
        {"$set": {"equipe": [{"_id": p["_id"], "nom": p["nom"], "pv": p["pv"], "atk": p["atk"], "def": p["def"]} for p in equipe]}}
    )
    return equipe

def leaderboard():
    os.system("clear")
    print("Tableau des scores :\n")
    players = list(collection_player.find().sort("score", -1).limit(3))
    if not players:
        print("Aucun score enregistré pour le moment.")
        return
    colors = [Fore.YELLOW, "\033[38;5;208m", Fore.RED]
    for i, player in enumerate(players):
        color = colors[i] if i < len(colors) else Style.RESET_ALL
        print(f"{color}{i + 1}. {player['nom']} - Score : {player['score']} vagues survécues{Style.RESET_ALL}")


def save_player():
    while True:
        player = input("Veuillez saisir un pseudo : ")
        if 3 <= len(player) <= 20:
            collection_player.insert_one({"nom": player, "score": 0})
            print(f"Bienvenue, {player} ! Votre nom a été enregistré.")
            return player
        else:
            print("Le pseudo doit contenir entre 3-20 caractères.")

def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)

        if ch1 == "\x1b": # début séquence flèche
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch1 + ch2 + ch3
        return ch1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def open_box(items):
    items = list(collection_items.find())
    r = random.random()
    total = 0

    for item in items:
        total += item["drop"]
        if r <= total:
            return item
        
    return None