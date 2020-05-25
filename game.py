import sys
from xml import sax

import pygame as pg
from pygame.locals import *

import config
import item
import maps
import sprites

game = None


def terminate():
    pg.quit()
    sys.exit()


def run():
    global game
    game = Game()
    game.main()


class Game:

    def __init__(self):
        self.tmxhandler = maps.TMXHandler()
        self.map_edges = pg.Rect(0, 0, self.tmxhandler.columns, self.tmxhandler.lines)
        self.screen = pg.display.set_mode(
            (config.tiles_visible_x * config.tiles_size, config.tiles_visible_y * config.tiles_size - 16))

    """Esse bloco de código é usado duas vezes, na primeira vez para desenhar cada bloco de cada camada de plano de 
    fundo e depois (após o primeiro plano ter sido desenhado) para desenhar cada bloco de cada camada oclusiva. Em 
    vez de ter código duplicado, eu o coloco em uma definição de função local e deixo que muitas variáveis caiam. O 
    primeiro plano usa seu próprio código, porque lida com sprites de vários quadros, em vez de blocos estáticos, 
    e só precisa percorrer a lista de itens. """

    def main(self):

        global player

        # Estes assumem valores de 0, -1 ou 1, dependendo se os blocos estão deslizando nesse momento
        # direção. Isso é diferente de se mover, pois leva em consideração a janela que se fecha pelas bordas.
        x_tile_sliding, y_tile_sliding = 0, 0

        # Tudo funciona mesmo com um número par de linhas/colunas visíveis. O jogador simplesmente não está
        # centralizado na superfície da tela.
        mid_x, mid_y = (config.tiles_visible_x - 1) / 2, (config.tiles_visible_y - 1) / 2

        # Manuseio especial para objetos ativos no mundo do jogo. Todas as pessoas devem ter uma propriedade de caminho.
        for i in self.tmxhandler.items:
            # Construa o caminho da lista de propriedades analisadas para o mapa
            if i.type == 'person':
                i.path = [int(n) for n in i.properties['path'].split(',')]

        # Estes parâmetros de conjuntos de peças regulares são especificados nos arquivos mundiais XML, mas não há
        # arquivos XML para sprites
        # player para que eles tenham que ser codificados em algum lugar.
        player = item.Item(sprites.Sprite('sprites/boy.png', 32, 64, (0, 198, 198)), Rect(3, 3, 1, 1), 'player')

        # Adicione o player à lista de itens para que ele colide corretamente e seja pintado como parte do primeiro plano.
        self.tmxhandler.items.append(player)

        # Calcular quais blocos devem ficar visíveis ao redor do player. A visão fixa garante que a câmera não
        # go fora das fronteiras do mundo.
        viewport = Rect(player.position.left - mid_x, player.position.top - mid_y, config.tiles_visible_x,
                        config.tiles_visible_y)
        clamped = viewport.clamp(self.map_edges)

        # A posição do jogador determina quais peças serão sorteadas. Além disso, se o jogador ainda estiver
        # moving, a linha / coluna à direita uma unidade atrás dele também deve ser desenhada.
        for row in range(0 - (y_tile_sliding and player.facing[1] == 1),
                         config.tiles_visible_y + (y_tile_sliding and player.facing[1] == -1)):
            for column in range(0 - (x_tile_sliding and player.facing[0] == 1),
                                config.tiles_visible_x + (x_tile_sliding and player.facing[0] == -1)):
                # Blit a área apropriada de uma determinada camada da representação interna do
                # game world no buffer da superfície da tela.
                self.screen.blit(self.tmxhandler.image[layer][row + clamped.top][column + clamped.left], (
                    column * config.tiles_size + (x_tile_sliding * player.sliding * player.facing[0]),
                    row * config.tiles_size + (y_tile_sliding * player.sliding * player.facing[1]) - 16))

        pg.init()

        pg.display.set_caption("Pykemon - Demo")

        # Usamos a biblioteca sax para analisar mapas, caminhos e metadados de blocos dos arquivos XML do mundo do jogo.
        parser = sax.make_parser()
        parser.setContentHandler(self.tmxhandler)

        # moving representa a tecla de direção pressionada agora
        # Se você quiser saber se o jogador está se movendo, player.facing e player.sliding devem ser
        # usado em vez disso, porque a tecla de direção pode ser liberada ou alterada durante o movimento.
        moving = 0, 0
        player.facing = 0, 1

        # Mapas constantes do teclado para vetores de movimento
        moves = {
            K_UP: (0, -1),
            K_DOWN: (0, 1),
            K_LEFT: (-1, 0),
            K_RIGHT: (1, 0)
        }

        # O limitador de quadros está desativado no momento?
        turbo = 0

        # Há um único quadro para ficar parado. Ao deslizar, o item alterna entre a posição imóvel
        # frame e a estrutura de marcha atual (que é alternada a cada passo para que as pernas se alternem)
        animation_cutoffs = (config.tiles_size / 2)

        clock = pg.time.Clock()

        # Estamos gravando atualmente?
        recording = False
        frame = 0
        capture_run = 0

        # Loop principal do jogo
        while True:
            self.screen.fill(255, 0, 255)

            for event in pg.event.get():
                if event.type == QUIT:
                    terminate()

                if event.type == KEYDOWN:
                    if event.key in moves.keys():
                        moving = moves[event.key]

                    if event.key is K_SPACE:  # Segure espaço para desativar o limitador de quadros
                        turbo = True

                    if event.key is K_r:  # Segure r para gravar a saída da tela em muitos PNGs
                        recording = True
                elif event.type == KEYUP:
                    # Não queremos parar se o jogador pressionar e soltar uma tecla de movimento enquanto estiver
                    # movendo em uma direção diferente, para que a direção do movimento seja verificada na tecla
                    # pressionada
                    if event.key in moves.keys() and moves[event.key] == moving:
                        moving = 0, 0

                    if event.key is K_SPACE:  # Restaura o limitador de quadros quando o espaço é liberado
                        turbo = False

                    if event.key is K_r:
                        recording = False
                        capture_run += 1

            # Observe que o movimento do jogador está sendo tratado aqui e não abaixo com o restante dos itens.
            if player.sliding == 0 and moving != (0, 0):
                # Isso retornará falso se o jogador encontrar um obstáculo.
                if player.move(moving):
                    # Mover a janela de visualização com o player
                    viewport.move_ip(moving)
                    # Mova a janela de visualização de volta ao mundo do jogo, se ela acabou de sair.
                    clamped = viewport.clamp(self.map_edges)


                    # Estes cálculos determinam se o jogador deve se mover livremente perto das fronteiras ou deve
                    # ser fixado em o centro de um plano de fundo de rolagem quando distante das bordas. Observe que,
                    # por exemplo, o player pode estar perto do topo do mundo e capaz de se mover livremente na
                    # vertical, mas ainda assim estar fixo no direção horizontal.
                    x_tile_sliding, y_tile_sliding = 0, 0

                    if viewport.left == clamped.left and viewport.move(-1 * moving[0], 0).left == viewport.move(
                            -1 * moving[0], 0).clamp(self.map_edges).left:
                        x_tile_sliding = 1

                    if viewport.top == clamped.top and viewport.move(0, -1 * moving[1]).top == viewport.move(0, -1 *
                                                                                                                moving[
                                                                                                                    1]).clamp(
                            self.map_edges).top:
                        y_tile_sliding = 1

            # Manipula o movimento de todas as pessoas em todos os quadros, alterando a direção conforme necessário
            # para corresponder ao caminho no arquivo XML.
            for i in self.tmxhandler.items:
                if i.type == 'person':  # Observe que os pedregulhos nunca são chamados para go(), apenas bump_notify()
                    i.go()

            # Primeiro, precisamos escolher todas as camadas não marcadas como oclusivas e desenhá-las em ordem.
            # Isso cria o background em que itens se movem.
            occluding = []

            for layer in range(0, self.tmxhandler.layers):
                if 'occlude' in self.tmxhandler.properties[layer + 1]:  # + 1 porque 0 é o suporte do mapa
                    occluding.append(layer)
                else:
                    self.main()  # Muitas e muitas variáveis gratuitas passam por aqui

            # Agora, desenhe cada item (incluindo o player), dependendo de estar visível na janela de exibição da
            # câmera.
            for i in self.tmxhandler.items:
                # O deslizamento de um item é definido como tiles_size toda vez que ele se move e diminui em 4 pixels
                # por quadro até it atinge 0 e, nesse ponto, alcançou sua nova posição. Observe que o valor de
                # deslizamento do jogador não é changed até que a camada de oclusão tenha sido desenhada. Isso é
                # necessário porque se a viewport for alterada b Antes de os itens serem desenhados,
                # eles retrocederão 4 pixels no final do movimento deslizante.
                if i is not player and i.sliding > 0:
                    i.sliding -= 4

                # Verifique se o item está visível dentro de três blocos ao redor da janela de visualização e,
                # se estiver, desenhe-o. A visualização deve ser expandida por três peças devido ao pior caso:
                # enquanto um item está deslizando para a direita do jogador, o jogador Move-se para a esquerda. No
                # futuro, posso adicionar uma verificação que permita inflar apenas 2 peças e um inflável direcional
                # dependendo para que lado o jogador está se movendo.
                if clamped.inflate(3, 3).contains(i.position):
                    self.screen.blit(
                        i.sprite.facing[i.facing][0 if i.sliding < animation_cutoffs else 1 + i.toggle], (
                            (i.position.left - clamped.left) * config.tiles_size - (i.sliding * i.facing[0]),
                            (i.position.top - clamped.top - 1) * config.tiles_size - (
                                    i.sliding * i.facing[1]) + (
                                    y_tile_sliding * player.sliding * player.facing[1]) - 16))

            # Finalmente, desenhe cada camada de oclusão que foi ignorada anteriormente. Essa camada será desenhada
            # em cima dos itens.
            for layer in occluding:
                self.main()

            # E agora que as operações de desenho estão concluídas, atualize o valor deslizante do jogador.
            if player.sliding > 0:
                player.sliding -= 4

            # E agora que as operações de desenho estão concluídas, atualize o valor deslizante do jogador.
            pg.display.update()

            if not turbo:
                clock.tick(30)

            if recording:
                # Exporte a superfície da tela para um arquivo png para fazer vídeos. Isso pode consumir muito espaço
                # em disco se você gravar por mais than alguns segundos. A compactação PNG mata a taxa de quadros,
                # mas os tamanhos dos arquivos são muito mais gerenciáveis.
                pg.image.save(self.screen,
                              'capture/' + 'run' + str(capture_run).zfill(2) + '_f' + str(frame).zfill(5) + '.png')
                frame += 1
