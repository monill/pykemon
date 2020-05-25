from pygame.locals import Rect

import config
import game


class Item:
    # que está parado
    def __init__(self, sprite, position, type, facing=(0, 1), toggle=0):
        self.sprite = sprite  # O sprite associado a este item
        self.position = position  # Um retângulo usado para manter a posição x, y (no canto superior esquerdo) do objeto
        self.facing = facing  # O vetor de direção do item
        self.sliding = 0  # The number of pixels away from rest an item is when moving
        self.toggle = toggle  # O primeiro ou o segundo andarilho estão sendo usados agora?
        self.type = type  # Os tipos de itens especialmente manipulados são "pedregulho", "pessoa", "jogador", "bloco", "garota", "garoto"
        self.properties = {}  # Dictionary para armazenar pares de nome/valor de informações sobre o item. As propriedades usadas atualmente são "path"
        self.path = []  # Lista de caminhos de movimento com x, y alternados. Exemplo: [2, -1,0,2] passará por baixo 2, esquerda 1, direita 2.
        self.step = 0  # que índice da lista de caminhos em que o item está trabalhando atualmente
        self.gone = 0  # número de etapas já executadas em direção ao caminho [etapa]

    """Mova o item um bloco na direção desejada fornecida por um vetor de direção (2-tuplas).
        return true se o item puder se mover nessa direção. Ele retornará false se for executado em um obstáculo imóvel,
        obstáculo móvel ou se o item já estiver se movendo para algum lugar."""

    def move(self, direction):
        # Quando movido, um item assume imediatamente suas novas coordenadas para que os cálculos de colisão sejam
        # sempre atualizado. No entanto, ele também obtém um deslocamento de exibição tile_width para que não pareça
        # ter se movido. O deslocamento é reduzido lentamente (4 pixels por quadro) até que o item esteja na posição.
        # Durante esse período, outro item pode mover-se para o local antigo, mas como todos os itens se movem na
        # mesma velocidade, seus gráficos não podem se sobrepor.

        if direction == (0, 0):  # Não pode deixar de ficar parado
            return True

        if self.sliding == 0:
            self.facing = direction
            self.toggle = not self.toggle  # Utilize o outro andarilho

            new_x, new_y = self.position.left = direction[0], self.position.top + direction[1]
            hit = Rect(new_x, new_y, 1, 1).collidelist([i.position for i in game.game.tmxhandler.items])

            # O item estará dentro de outro item se ele assumir new_x e new_y?
            if hit > -1:
                game.game.tmxhandler.items[hit].bump_notify(self.type, self.facing)
                # Saiba que está sendo esbarrado
                return False
            # O item estará dentro de uma área de bloqueio (fora dos limites, cercas, prédios, etc.) se assumir o new_x e o new_y?
            elif not game.game.map_edges.collidepoint(new_x, new_y - 1) or Rect(new_x, new_y, 1, 1).collidelist(
                    game.game.tmxhandler.blocking) > -1:
                return False
            else:
                # Olhando claro, comece a mudança.
                self.position.move_ip(direction[0], direction[1])
                self.sliding = config.tiles_size
                return True

    def go(self):
        # Se o item não estiver fazendo nada nesta etapa, prossiga imediatamente para a próxima instrução de caminho ou contorne.
        # Você pode fazer isso se o caminho desejado voltar a dobrar (como "Cima 5, Esquerda 0, Desce 5" suba e desça)
        if self.path[self.step] == 0:
            self.step = (self.step + 1) % len(self.path)

        # Pegue o sinal da instrução atual
        unit = (self.path[self.step] > 0) * 2 - 1
        # Obtenha o vetor com esse sinal, com a direção dependendo da etapa ser ímpar ou par
        unit_v = (0, unit) if self.step % 2 else (unit, 0)

        if self.move(unit_v):
            self.gone += unit

            # Se o item concluiu sua instrução atual, vá para a próxima etapa ou siga em frente.
            if self.gone == self.path[self.step]:
                self.step = (self.step + 1) % len(self.path)
                self.gone = 0

    def bump_notify(self, type, facing):
        # Mova uma pedra para a frente, mas somente se estiver sendo empurrada diretamente por uma pessoa ou jogador
        # Isso significa não empurrar longas pilhas de pedras
        if self.type == 'boulder' and (type == 'player' or type == 'person'):
            self.move(facing)
