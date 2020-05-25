from xml import sax

from pygame.locals import Rect

import item
import sprites
from tileset import Tileset


class TMXHandler(sax.ContentHandler):

    def __init__(self):
        super().__init__()

        self.column = 0
        self.line = 0
        self.tile_width = 0
        self.tile_height = 0
        self.columns = 0
        self.lines = 0
        self.layers = 0  # Quantas camada's foram processadas (conterão o número total de camadas quando o ContentHandler for concluído)
        self.properties = [{}]  # Lista de dicionários (um por camada) de pares nome / valor. Especificado pelas tags <property>
        self.tileset = None  # O objeto Tileset criado a partir de tags <tileset>
        self.image = []  # Uma lista de camadas, cada uma contendo uma lista 2D de referências a células Tileset
        self.cur_row = []
        self.cur_layer = []
        self.blocking = []  # Lista de áreas de bloqueio nas quais os itens não podem entrar (pintados em terrenos intransitáveis)
        self.items = []  # Lista de todos os itens
        self.in_item = False  # se estou colocando propriedades em um item ou em uma camada

    def start_element(self, name, attributes):
        if name == 'map':
            self.columns = int(attributes.get('width', None))
            self.lines = int(attributes.get('height', None))
            self.tile_width = int(attributes.get('tilewidth', None))
            self.tile_height = int(attributes.get('tileheight', None))
        elif name == 'image':  # criar um tileset
            # É possível usar mais de um conjunto de peças, mas eles devem ter tamanhos e peças idênticos.
            # chaves de cores transparentes.
            source = attributes.get('source', None)
            transp = attributes.get('trans', None)

            if self.tileset is None:
                self.tileset = Tileset(self.tile_width, self.tile_height)

            self.tileset.add_set(source, ("0x" + str(transp)))
        elif name == 'property':  # armazena propriedades adicionais.
            # adicionar às propriedades do item ou da camada, dependendo da tag pai em que estamos
            if self.in_item:
                self.items[-1].properties[attributes.get('name', None)] = attributes.get('value', None)
            else:
                self.properties[self.layers][attributes.get('name', None)] = attributes.get('value', None)
        elif name == 'layer':  # começando a contagem
            self.line = 0
            self.column = 0
            self.layers += 1
            self.properties.append({})
            self.in_item = False
        elif name == 'tile':  # obter informações de cada bloco e colocar no mapa
            # ID do arquivo para fazer referência ao conjunto de blocos
            gid = int(attributes.get('gid', None)) - 1

            if gid < 0:
                gid = 0

            self.cur_row.append(self.tileset.tiles[gid])
            self.column += 1

            if self.column >= self.columns:
                self.line += 1
                self.column = 0
                self.cur_layer.append(self.cur_row)
                self.cur_row = []

            if self.line >= self.lines:
                self.image.append(self.cur_layer)
                self.cur_layer = []
        elif name == 'object':
            # áreas de objetos podem ser pintadas em azulejo ou especificadas manualmente, como no mapa de amostra
            self.in_item = True

            x = int(attributes.get('x', None)) / self.tile_width
            y = int(attributes.get('y', None)) / self.tile_height

            if attributes.get('type', None) == 'block':  # impede que itens entrem em quadrados contidos
                width = int(attributes.get('width', None)) / self.tile_width
                height = int(attributes.get('height', None)) / self.tile_height

                self.blocking.append(Rect(x, y, width, height))

            if attributes.get('type', None) == 'boulder':  # empurrável
                self.items.append(
                    item.Item(sprites.Sprite('sprites/rock.png', 32, 64, (0, 198, 198)), Rect(x, y, 1, 1), 'boulder'))

            if attributes.get('type', None) == 'girl':
                self.items.append(
                    item.Item(sprites.Sprite('sprites/girl.png', 32, 64, (0, 198, 198)), Rect(x, y, 1, 1), 'person'))

            if attributes.get('type', None) == 'boy':
                self.items.append(
                    item.Item(sprites.Sprite('sprites/boy.png', 32, 64, (0, 198, 198)), Rect(x, y, 1, 1), 'person'))
