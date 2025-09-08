import uuid
import random


def start_game(player_species):
    return {
        'id': uuid.UUID(int=random.getrandbits(128), version=4).hex,
        'players': [
            {
                'hp': 25,
                'lines': 0,
                'species': species,
                'ships': {},
            } for species in player_species
        ],
    }
