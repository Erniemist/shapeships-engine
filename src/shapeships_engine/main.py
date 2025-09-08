import random
from dataclasses import dataclass
from enum import Enum, StrEnum, auto
from functools import reduce


class Species(StrEnum):
    HUMAN = 'Human'
    XENITE = 'Xenite'
    CENTAUR = 'Centaur'
    ANCIENT = 'Ancient'


@dataclass(frozen=True)
class Player:
    species: Species
    hp: int
    lines: int
    ships: dict

    @classmethod
    def new_player(cls, species):
        if species not in Species.__members__.values():
            raise ValueError(f"'{species} is not a valid species")
        return cls(species, 25, 0, {})

    def copy(self, species=None, hp=None, lines=None, ships=None):
        return Player(
            self.species if species is None else species,
            self.hp if hp is None else hp,
            self.lines if lines is None else lines,
            self.ships if ships is None else ships,
        )

    def start_turn(self, die_roll):
        return self.copy(lines=self.lines + die_roll)

    def battle(self, other):
        return self.copy(hp=self.hp - 5)

    def requests(self, phase):
        return []

class Phase(Enum):
    START_TURN = auto()
    BATTLE = auto()

    def next_phase(self):
        return {
            self.START_TURN: Phase.BATTLE,
            self.BATTLE: Phase.START_TURN,
        }[self]


@dataclass(frozen=True)
class Game:
    phase: Phase
    players: list[Player]

    @classmethod
    def start_game(cls, player_species):
        return cls(Phase.START_TURN, [Player.new_player(species) for species in player_species])

    def copy(self, phase=None, players=None):
        return Game(
            self.phase if phase is None else phase,
            self.players if players is None else players,
        )

    def next(self):
        all_requests = [player.requests(self.phase) for player in self.players]
        if any(len(requests) > 0 for requests in all_requests):
            return self, all_requests
        return self.resolve_phase().next_phase(), []

    def resolve_phase(self):
        match self.phase:
            case Phase.START_TURN:
                return self.start_turn()
            case Phase.BATTLE:
                return self.battle()

    def next_phase(self):
        return self.copy(phase=self.phase.next_phase())

    def start_turn(self):
        die_roll = random.randint(1, 6)
        return self.copy(players=[player.start_turn(die_roll) for player in self.players])

    def battle(self):
        return self.copy(players=[
            reduce(
                lambda x, y: x.battle(y),
                [other for other in self.players if player is not other],
                player
            ) for player in self.players
        ])
