tiles_visible_x = 13
tiles_visible_y = 11

# Isso inclui mais para evitar constantes mágicas do que para fornecer uma maneira
# para definir tamanhos personalizados. Isso deve sempre corresponder às dimensões fornecidas no
# map file (que são os valores reais dos conjuntos de peças usadas). O motivo
# nós não podemos simplesmente usar esses valores é que a exibição precisa ser inicializada
# para o tamanho correto antes de analisarmos o XML porque o analisador usa
# image processing chama os conjuntos de mosaicos vinculados para criar a lista de mosaicos.
tiles_size = 32

# Defina isso no arquivo de mapa que você deseja carregar. Arquivos de mapa válidos incluídos no
# the demo são "map.tmx" e "map2.tmx"
map = "maps/map2.tmx"
