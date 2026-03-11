from utils import leaderboard, get_key
from game import start_game
from db_init import init_db
from colorama import Fore, Style

import os

# /!\ Poser la question comment ça marche réellement car j'ai pas trop compris cette partie
MENU_ITEMS = [
    ("Lancer le jeu",                 start_game),
    ("Afficher le tableau des scores", leaderboard),
    ("Quitter",                        exit),
]

def main():
    selection = 0
    while True:
        os.system("clear")
        print('''
         =*===
       $$- - $$$
       $ <    D$$
       $ -   $$$
 ,     $$$$  |
///; ,---' _ |----.
 \ )(           /  )
 | \/ \.   '  _.|  \              $
 |  \ /(   /    /\_ \          $$$$$
  \ /  (       / /  )         $$$ $$$
       (  ,   /_/ ,`_,-----.,$$  $$$
       |   <----|  \---##     \   $$
       /         \\\           |    $
      '   '                    |
      |                 \      /
      /  \_|    /______,/     /
     /   / |   /    |   |    /
    (   /--|  /.     \  (\  (_
     `----,( ( _\     \ / / ,/
           | /        /,_/,/
          _|/        / / (
         / (        ^-/, |
        /, |          ^-    
        ^-

''')
        
        for i, (label, _) in enumerate(MENU_ITEMS):
            if i == selection:
                print(Fore.GREEN + "> " + label + Style.RESET_ALL)
            else:
                print("  " + label)
        key = get_key()

        if key == "\x1b[A":   # flèche du haut
            selection = (selection - 1) % len(MENU_ITEMS)
        elif key == "\x1b[B": # flèche du bas
            selection = (selection + 1) % len(MENU_ITEMS)
        elif key == "\r":     # entrée
            MENU_ITEMS[selection][1]()
            input("\nAppuyez sur Entrée pour revenir au menu...")

if __name__ == "__main__":
    init_db()
    main()
