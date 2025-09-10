import random
from dataclasses import dataclass
from typing import Self

from shapeships_engine.Phase import Phase
from shapeships_engine.Player import Player, ProposalError


@dataclass(frozen=True)
class Game:
    phase: Phase
    players: list[Player]

    @classmethod
    def start_game(cls, player_species) -> Self:
        game = cls(Phase.BUILD, [
            Player.new_player(species) for species in player_species
        ]).resolve_phase().generate_requests()
        return game, [player.request for player in game.players]

    def to_dict(self):
        return {
            'phase': self.phase.name,
            'players': [player.to_dict() for player in self.players]
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            phase=Phase.__members__[data['phase']],
            players=[Player.from_dict(player_data) for player_data in data['players']],
        )

    def copy(self, phase=None, players=None) -> Self:
        return Game(
            self.phase if phase is None else phase,
            self.players if players is None else players,
        )

    def next(self) -> tuple[Self, list]:
        requests = [player.request for player in self.players]
        if any(request != {} for request in requests):
            return self, requests
        game = self.next_phase().resolve_phase().generate_requests()
        return game, [player.request for player in game.players]

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
        player_hps = [player.hp for player in self.players]
        for i, player in enumerate(self.players):
            for j, other in enumerate(self.players):
                healing, damage = player.battle(other)
                if i == j:
                    player_hps[j] += healing
                else:
                    player_hps[j] -= damage

        player_hps = [min(hp, 35) for hp in player_hps]

        return self.copy(
            phase=self.phase if all(hp > 0 for hp in player_hps) else Phase.GAME_OVER,
            players=[
                player.copy(hp=hp)
                for hp, player in zip(player_hps, self.players)
            ])
