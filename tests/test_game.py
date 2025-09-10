import random

from shapeships_engine.Game import Game
from shapeships_engine.Phase import Phase
from shapeships_engine.Player import Species

def test_start_game():
    random.seed(0)
    game = Game.start_game([Species.HUMAN, Species.XENITE])
    players = game.players
    assert len(players) == 2
    assert players[0].species == Species.HUMAN
    assert players[1].species == Species.XENITE
    for player in players:
        assert player.hp == 25
        assert player.lines == 4
        assert player.ships == {}

def test_start_turn():
    random.seed(0)
    game = Game.start_game([Species.HUMAN, Species.HUMAN])
    assert game.phase == Phase.BUILD
    game, requests = game.next()
    assert game.phase == Phase.BUILD
    for player in game.players:
        assert player.lines == 4
    assert requests == [
        {'type': 'build', 'options': [{}, {'defender': 1}, {'defender': 2}]},
        {'type': 'build', 'options': [{}, {'defender': 1}, {'defender': 2}]},
    ]
    game, success = game.submit(0, {'type': 'build', 'option': {'defender': 1}})
    assert success is True
    game, success = game.submit(1, {'type': 'build', 'option': {'defender': 2}})
    assert success is True
    assert game.players[0].ships['defender'] == 1
    assert game.players[1].ships['defender'] == 2
    game, requests = game.next()
    assert game.phase == Phase.BATTLE
    assert requests == []

def test_build_failures():
    random.seed(0)
    game = Game.start_game([Species.HUMAN, Species.HUMAN])
    assert game.phase == Phase.BUILD
    game, requests = game.next()
    assert game.phase == Phase.BUILD
    for player in game.players:
        assert player.lines == 4
    assert requests == [
        {'type': 'build', 'options': [{}, {'defender': 1}, {'defender': 2}]},
        {'type': 'build', 'options': [{}, {'defender': 1}, {'defender': 2}]},
    ]
    game, success = game.submit(-5, {'type': 'build', 'option': {'defender': 1}})
    assert success is False
    game, success = game.submit(0, {'type': 'something_else', 'option': {'defender': 1}})
    assert success is False
    game, success = game.submit(0, {'type': 'build', 'option': {'defender': 1000}})
    assert success is False
    game, success = game.submit(0, {'type': 'build', 'option': {'defender': 1}})
    assert success is True

def test_battle():
    random.seed(0)
    game = Game.start_game([Species.HUMAN, Species.HUMAN])
    game, requests = game.next()
    for player in game.players:
        assert player.hp == 25
    game, success = game.submit(0, {'type': 'build', 'option': requests[0]['options'][1]})
    game, success = game.submit(1, {'type': 'build', 'option': requests[1]['options'][2]})
    game, requests = game.next()
    assert requests == []
    assert game.players[0].hp == 26
    assert game.players[1].hp == 27
