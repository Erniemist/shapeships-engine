from shapeships_engine.main import *
import random

def test_start_game():
    random.seed('shapeships')
    gamestate = start_game(['human', 'xenite'])
    assert gamestate['id'] == '92a75417713a4d19be0ec0c3169cd360'
    assert gamestate['players'] == [
        {
            'hp': 25,
            'lines': 0,
            'species': 'human',
            'ships': {},
        },
        {
            'hp': 25,
            'lines': 0,
            'species': 'xenite',
            'ships': {},
        },
    ]
