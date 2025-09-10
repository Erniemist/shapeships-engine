from copy import deepcopy
from dataclasses import dataclass
from enum import StrEnum
from typing import Self

from shapeships_engine.Phase import Phase
from shapeships_engine.ships import ship_types


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

    @classmethod
    def new_player(cls, species) -> Self:
        if species not in Species.__members__.values():
            raise ValueError(f"'{species} is not a valid species")
        return cls(species, 25, 0, {}, {})

    def to_dict(self):
        return {
            'species': self.species.name,
            'hp': self.hp,
            'lines': self.lines,
            'ships': self.ships,
            'request': self.request,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            species=Species.__members__[data['species']],
            hp=data['hp'],
            lines=data['lines'],
            ships=data['ships'],
            request=data['request'],
        )

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
        total_healing, total_damage = 0, 0
        for ship, quantity in self.ships.items():
            healing, damage = self.get_ship_group_numbers(ship, quantity)
            total_healing += healing
            total_damage += damage
        return total_healing, total_damage

    def get_ship_group_numbers(self, ship, quantity):
        ship = ship_types[ship]
        if ship.fungible:
            healing = ship(self).healing() * quantity
            damage = ship(self).damage() * quantity
        else:
            healing = 0
            damage = 0
            for datum in quantity:
                ship = ship(self, datum)
                healing += ship.healing()
                damage += ship.damage()
        return healing, damage

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
                for name, ship_type in ship_types.items():
                    if proposal['lines'] >= ship_type.cost:
                        new_proposal = {
                            'ships': deepcopy(proposal['ships']),
                            'lines': proposal['lines'] - ship_type.cost,
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
            remaining_lines -= quantity * ship_types[ship].cost
            if remaining_lines < 0:
                raise ProposalError()

        return self.copy(lines=remaining_lines, ships={
            ship: self.ships.get(ship, 0) + ships.get(ship, 0)
            for ship in set(self.ships.keys()).union(set(ships.keys()))
        })
