import random

from shapeships_engine.main import *

def test_start_game():
    game = Game.start_game([Species.HUMAN, Species.XENITE])
    players = game.players
    assert len(players) == 2
    assert players[0].species == Species.HUMAN
    assert players[1].species == Species.XENITE
    for player in players:
        assert player.hp == 25
        assert player.lines == 0
        assert player.ships == {}

def test_start_turn():
    random.seed(0)
    game = Game.start_game([Species.HUMAN, Species.HUMAN])
    assert game.phase == Phase.START_TURN
    game, requests = game.next()
    assert requests == []
    for player in game.players:
        assert player.lines == 4

def test_battle():
    random.seed(0)
    game = Game.start_game([Species.HUMAN, Species.HUMAN])
    game, requests = game.next()
    for player in game.players:
        assert player.hp == 25
    game, requests = game.next()
    assert requests == []
    for player in game.players:
        assert player.hp == 20
