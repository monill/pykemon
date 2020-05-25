import pygame as pg
from pygame.locals import Rect


class Tileset:
    """Um conjunto de peças é uma imagem raster grande dividida em retângulos que podem ser colocados na tela para
    criar mosaicos personalizados mundos de jogos sem ter que ser um artista capaz de trabalhar com novos
    gráficos.Esta classe corta cada bloco do dado arquivo de conjunto de peças e o torna disponível em uma lista 2 D(
    mesmas posições da imagem do conjunto de peças) de superfícies a serem referenciadas como necessário.Os ladrilhos
    são usados para decoração e não podem ser interagidos.
    """

    def __init__(self, tile_width, tile_height):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.tiles = []  # Uma lista simples contendo cada quadrado de tile_size recortado no conjunto de peças

    def add_set(self, file, transp):
        image = pg.image.load(file)
        if not image:
            print("Não foi possível encontrar o arquivo do tileset" + file)

        image.set_alpha(None)
        image.set_colorkey(transp)
        image.convert()

        # Popular tiles do arquivo do tileset
        for row in range(image.get_height() / self.tile_height):
            for column in range(image.get_width() / self.tile_width):
                self.tiles.append(image.subsurface(
                    Rect(column * self.tile_width, row * self.tile_height, self.tile_width, self.tile_height)))
