import random
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum, StrEnum, auto
from functools import reduce
from typing import Self


class Species(StrEnum):
    HUMAN = 'Human'
    XENITE = 'Xenite'
    CENTAUR = 'Centaur'
    ANCIENT = 'Ancient'


class ProposalError(Exception):
    pass


@dataclass(frozen=True)
class Player:
    species: Species
    hp: int
    lines: int
    ships: dict
    request: dict
    ship_costs = {'defender': 2}

    @classmethod
    def new_player(cls, species) -> Self:
        if species not in Species.__members__.values():
            raise ValueError(f"'{species} is not a valid species")
        return cls(species, 25, 0, {}, {})

    def copy(self, species=None, hp=None, lines=None, ships=None, request=None) -> Self:
        return Player(
            self.species if species is None else species,
            self.hp if hp is None else hp,
            self.lines if lines is None else lines,
            self.ships if ships is None else ships,
            self.request if request is None else request,
        )

    def start_turn(self, die_roll) -> Self:
        return self.copy(lines=self.lines + die_roll)

    def battle(self, other) -> Self:
        return self.copy(hp=self.hp - 5)

    def generate_requests(self, phase) -> Self:
        if phase == Phase.BUILD:
            return self.copy(request=self.generate_possible_builds())
        return self.copy(request={})

    def generate_possible_builds(self) -> dict:
        proposals = [{'ships': {}, 'lines': self.lines, 'seen': False}]
        while any(not proposal['seen'] for proposal in proposals):
            for proposal in proposals:
                if proposal['seen']:
                    continue
                proposal['seen'] = True
                for name, line_cost in Player.ship_costs.items():
                    if proposal['lines'] >= line_cost:
                        new_proposal = {
                            'ships': deepcopy(proposal['ships']),
                            'lines': proposal['lines'] - line_cost,
                            'seen': False,
                        }
                        if name in proposal['ships'].keys():
                            new_proposal['ships'][name] += 1
                        else:
                            new_proposal['ships'][name] = 1
                        proposals.append(new_proposal)
        return {'type': 'build', 'options': [proposal['ships'] for proposal in proposals]}

    def clear_request(self):
        return self.copy(request={})

    def submit(self, proposal):
        try:
            if proposal['type'] != self.request['type']:
                raise ProposalError()
            if  proposal['option'] not in self.request['options']:
                raise ProposalError()
        except KeyError:
            raise ProposalError()
        if proposal['type'] == 'build':
            return self.build(proposal['option'])
        raise ProposalError()

    def build(self, ships) -> Self:
        remaining_lines = self.lines
        for ship, quantity in ships.items():
            remaining_lines -= quantity * Player.ship_costs[ship]
            if remaining_lines < 0:
                raise ProposalError()

        return self.copy(lines=remaining_lines, ships={
            ship: self.ships.get(ship, 0) + ships.get(ship, 0)
            for ship in set(self.ships.keys()).union(set(ships.keys()))
        })


class Phase(Enum):
    BUILD = auto()
    BATTLE = auto()

    def next_phase(self) -> Self:
        return {
            self.BUILD: Phase.BATTLE,
            self.BATTLE: Phase.BUILD,
        }[self]


@dataclass(frozen=True)
class Game:
    phase: Phase
    players: list[Player]

    @classmethod
    def start_game(cls, player_species) -> Self:
        return cls(Phase.BUILD, [
            Player.new_player(species) for species in player_species
        ]).resolve_phase().generate_requests()

    def copy(self, phase=None, players=None) -> Self:
        return Game(
            self.phase if phase is None else phase,
            self.players if players is None else players,
        )

    def next(self) -> tuple[Self, list]:
        requests = [player.request for player in self.players]
        if any(request != {} for request in requests):
            return self, requests
        return self.next_phase().resolve_phase().generate_requests(), []

    def generate_requests(self):
        return self.copy(players=[player.generate_requests(self.phase) for player in self.players])

    def submit(self, player_id, proposal):
        if player_id >= len(self.players) or player_id < 0:
            return self, False
        try:
            return self.copy(players=[
                player.submit(proposal).clear_request() if i == player_id else player
                for i, player in enumerate(self.players)
            ]), True
        except ProposalError:
            return self, False

    def resolve_phase(self) -> Self:
        match self.phase:
            case Phase.BUILD:
                return self.start_turn()
            case Phase.BATTLE:
                return self.battle()
            case _:
                return self

    def next_phase(self) -> Self:
        return self.copy(phase=self.phase.next_phase())

    def start_turn(self) -> Self:
        die_roll = random.randint(1, 6)
        return self.copy(players=[player.start_turn(die_roll) for player in self.players])

    def battle(self) -> Self:
        return self.copy(players=[
            reduce(
                lambda x, y: x.battle(y),
                [other for other in self.players if player is not other],
                player
            ) for player in self.players
        ])
