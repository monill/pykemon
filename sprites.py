import pygame as pg
from pygame.locals import Rect


class Sprite:

    def __init__(self, file, tile_width, tile_height, transp):
        image = pg.image.load(file)
        if not image:
            print("Não foi possível encontrar o arquivo do tileset" + file)

        # Desative canais alfa para que o antigo mecanismo de cores de transparência com chave funcione
        image.set_alpha(None)
        image.set_colorkey(transp)

        # Um dicionário de listas, indexadas pela direção oposta, cada uma das quais contém os 3 quadros
        # associated with that direction. Os quadros são retirados do arquivo de folha de sprite fornecido.
        # As folhas
        # Sprite devem ter 12 larguras de lado a lado. Os mosaicos congruentes com x (mod 3) são:
        # x = 0: o item parado
        # x = 1: O primeiro andarilho
        # x = 2: O segundo andarilho
        self.facing = {}

        # South
        self.facing[(0, 1)] = []
        self.facing[(0, 1)].append(pg.Surface.subsurface(Rect(0 * tile_width, 0, tile_width, tile_height)))
        self.facing[(0, 1)].append(pg.Surface.subsurface(Rect(1 * tile_width, 0, tile_width, tile_height)))
        self.facing[(0, 1)].append(pg.Surface.subsurface(Rect(2 * tile_width, 0, tile_width, tile_height)))

        # North
        self.facing[(0, -1)] = []
        self.facing[(0, -1)].append(pg.Surface.subsurface(Rect(3 * tile_width, 0, tile_width, tile_height)))
        self.facing[(0, -1)].append(pg.Surface.subsurface(Rect(4 * tile_width, 0, tile_width, tile_height)))
        self.facing[(0, -1)].append(pg.Surface.subsurface(Rect(5 * tile_width, 0, tile_width, tile_height)))

        # East
        self.facing[(1, 0)] = []
        self.facing[(1, 0)].append(pg.Surface.subsurface(Rect(6 * tile_width, 0, tile_width, tile_height)))
        self.facing[(1, 0)].append(pg.Surface.subsurface(Rect(7 * tile_width, 0, tile_width, tile_height)))
        self.facing[(1, 0)].append(pg.Surface.subsurface(Rect(8 * tile_width, 0, tile_width, tile_height)))

        # West
        self.facing[(-1, 0)] = []
        self.facing[(-1, 0)].append(pg.Surface.subsurface(Rect(9 * tile_width, 0, tile_width, tile_height)))
        self.facing[(-1, 0)].append(pg.Surface.subsurface(Rect(10 * tile_width, 0, tile_width, tile_height)))
        self.facing[(-1, 0)].append(pg.Surface.subsurface(Rect(11 * tile_width, 0, tile_width, tile_height)))

        self.facing[(0, 0)] = self.facing[(0, 1)]
