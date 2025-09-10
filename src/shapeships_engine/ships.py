class Ship:
    def __init__(self, player):
        self.player = player

class Defender(Ship):
    name = 'defender'
    cost = 2
    fungible = True

    def damage(self):
        return 0

    def healing(self):
        return 1

class Fighter(Ship):
    name = 'fighter'
    cost = 3
    fungible = True

    def damage(self):
        return 1

    def healing(self):
        return 0

ship_types = {ship.name: ship for ship in [Defender, Fighter]}
