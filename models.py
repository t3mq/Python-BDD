def list_characters(characters):
    for i, character in enumerate(characters, 1):
        print(f"{i}. {character['nom']} | ATK: {character['atk']} | DEF: {character['def']} | PV: {character['pv']}")
    return [character['nom'] for character in characters]