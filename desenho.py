"""Desenho das árvores no tema de céu noturno, em 2D e em 3D.

Cada função recebe um eixo do matplotlib (ax) e uma árvore, desenha, e devolve
a lista de "pontos clicáveis": pares (identificador, posição). A janela usa
essa lista para descobrir em qual nó o usuário clicou.

Nas vistas 3D cada árvore vira uma constelação: os nós são estrelas e as
ligações são linhas. Só a forma de DESENHAR muda; a árvore é a mesma.
"""

import math
import random

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d.art3d import Line3DCollection

from dados import CONSTELACOES
from rubro_negra import VERMELHO

# Paleta do tema
FUNDO = "#050b1a"
PAINEL = "#0d1730"
TEXTO = "#e8eefc"
SUAVE = "#8795b8"
LINHA = "#6f7fa8"
AMARELO = "#ffd166"             # nós em destaque (inseridos, visitados na busca)
CIANO = "#4cc9f0"               # nó selecionado com o clique
VERDE = "#8ae234"               # resultado de uma consulta
ROSA = "#ff5d8f"                # alvo de uma consulta no mapa
VERMELHO_NO = "#ff4d5a"
PRETO_NO = "#0b0b0f"
DOURADO = "#ffe08a"
COR_EIXO = ("#ff6b6b", "#4dabf7", "#b197fc")    # k-D: cor do nó conforme o eixo que ele compara
NOME_EIXO = ("x", "y", "z")
CEU = (0, 360, -90, 90)         # limites do mapa plano


# ----------------------------------------------------------------- utilidades

def fundo_estrelado(ax, semente=1, quantidade=160):
    """Fundo escuro com estrelinhas, para os eixos 2D."""
    ax.set_facecolor(FUNDO)
    sorteio = random.Random(semente)
    xs = [sorteio.random() for _ in range(quantidade)]
    ys = [sorteio.random() for _ in range(quantidade)]
    tamanhos = [sorteio.choice((0.4, 0.8, 1.5, 3)) for _ in range(quantidade)]
    ax.scatter(xs, ys, s=tamanhos, color="white", alpha=0.45, transform=ax.transAxes, zorder=0)


def preparar_3d(ax, limite, elevacao, azimute, zoom):
    """Configura um eixo 3D: sem grade, fundo escuro, câmera e estrelas ao fundo."""
    ax.set_facecolor(FUNDO)
    ax.set_axis_off()
    ax.limite = limite              # guardado para a janela poder aplicar o zoom sem redesenhar
    ax.rotulos = []                 # textos dos nós: a janela os esconde enquanto o modelo gira
    alcance = limite / zoom
    ax.set_xlim(-alcance, alcance)
    ax.set_ylim(-alcance, alcance)
    ax.set_zlim(-alcance, alcance)
    ax.set_box_aspect((1, 1, 1), zoom=1.6)     # o matplotlib deixa muita margem em 3D: aproxima
    ax.view_init(elev=elevacao, azim=azimute)
    # Estrelas de fundo numa esfera em volta da cena: elas giram junto com o modelo.
    sorteio = random.Random(3)
    xs, ys, zs = [], [], []
    for _ in range(110):
        a, b = sorteio.uniform(0, 2 * math.pi), math.asin(sorteio.uniform(-1, 1))
        xs.append(1.15 * limite * math.cos(b) * math.cos(a))
        ys.append(1.15 * limite * math.cos(b) * math.sin(a))
        zs.append(1.15 * limite * math.sin(b))
    ax.scatter(xs, ys, zs, s=1.2, color="white", alpha=0.35, depthshade=False)


# Desenhar cada nó e cada linha como um objeto separado deixa o giro lento.
# As funções abaixo juntam tudo em poucos objetos: todas as linhas numa
# coleção, todas as estrelas num único scatter.

def _linhas_3d(ax, segmentos, cores=LINHA, largura=1.1, alpha=0.9, estilo="-"):
    """Desenha vários segmentos [(ponto, ponto), ...] como um objeto só."""
    if segmentos:
        ax.add_collection3d(Line3DCollection(segmentos, colors=cores, linewidths=largura,
                                             alpha=alpha, linestyles=estilo))


def _estrelas_3d(ax, posicoes, nucleos, contornos, tamanhos, halos, marcas=()):
    """Desenha todas as estrelas de uma vez: halo fraco por baixo e núcleo por cima.

    `marcas` é a lista de (posição, cor, tamanho) dos nós em destaque, que
    ganham um anel colorido em volta.
    """
    xs, ys, zs = zip(*posicoes)
    ax.scatter(xs, ys, zs, s=[t * 3.7 for t in tamanhos], c=halos, alpha=0.13, linewidths=0, depthshade=False)
    ax.scatter(xs, ys, zs, s=tamanhos, c=nucleos, edgecolors=contornos, linewidths=1.5, depthshade=False)
    for posicao, cor, tamanho in marcas:
        ax.scatter(*[[c] for c in posicao], s=tamanho, facecolors="none", edgecolors=cor,
                   linewidths=3.2, depthshade=False)


def _tracado_3d(ax, pontos):
    """Traçado da busca em 3D: linha grossa pelos nós visitados, na ordem, com um brilho por baixo."""
    if len(pontos) > 1:
        _linhas_3d(ax, [pontos], AMARELO, 9, 0.22)
        _linhas_3d(ax, [pontos], AMARELO, 3.6, 0.95)


def _tracado_2d(ax, pontos, zorder=1.5):
    """Traçado da busca em 2D: fica acima das arestas comuns e abaixo dos nós."""
    if len(pontos) > 1:
        xs, ys = zip(*pontos)
        ax.plot(xs, ys, color=AMARELO, lw=9, alpha=0.22, solid_capstyle="round", zorder=zorder)
        ax.plot(xs, ys, color=AMARELO, lw=3.6, alpha=0.95, solid_capstyle="round", zorder=zorder)


def _rotulo_3d(ax, posicao, texto, **estilo):
    rotulo = ax.text(*posicao, texto, **estilo)
    # Textos 3D não são cortados na borda do eixo por padrão: com zoom, os
    # nomes de nós fora do campo de visão apareceriam por cima do painel.
    rotulo.set_clip_on(True)
    rotulo.set_clip_box(ax.bbox)
    ax.rotulos.append(rotulo)


def _marca(identificador, selecionado, destaques):
    """Cor do anel de um nó: ciano se selecionado, amarelo se em destaque, None se normal."""
    if selecionado is not None and identificador == selecionado:
        return CIANO
    return AMARELO if identificador in destaques else None


def _vazia(ax, tres_d=False):
    """Escreve '(árvore vazia)' no meio do eixo."""
    if tres_d:
        ax.text2D(0.5, 0.5, "(árvore vazia)", ha="center", va="center", color=SUAVE, transform=ax.transAxes)
    else:
        ax.text(0.5, 0.5, "(árvore vazia)", ha="center", va="center", color=SUAVE, transform=ax.transAxes)


def _posicoes_2d(raiz, vazio):
    """Posição (x, y) de cada nó de uma árvore binária, para o desenho plano.

    x = ordem do nó no percurso em ordem (assim nunca há sobreposição);
    y = -profundidade. `vazio` é o que marca o fim de um ramo: NIL ou None.
    """
    pos, contador = {}, [0]

    def visitar(no, nivel):
        """Percurso em ordem: esquerda, numera o nó, direita."""
        if no is vazio:
            return
        visitar(no.esq, nivel + 1)
        pos[no] = (contador[0], -nivel)
        contador[0] += 1
        visitar(no.dir, nivel + 1)

    visitar(raiz, 0)
    return pos


def _posicoes_3d(raiz, vazio):
    """Posição (x, y, z) de cada nó de uma árvore binária, para o desenho 3D.

    A raiz fica no topo e cada nível desce um degrau em z. Os filhos se abrem
    para os lados no eixo x nos níveis pares e no eixo y nos ímpares, com a
    abertura caindo pela metade a cada vez que o mesmo eixo é usado. Por isso
    dois ramos nunca se cruzam e a árvore ocupa o espaço de verdade.
    """
    pos = {}

    def visitar(no, nivel, x, y):
        """Posiciona o nó e chama a si mesma para os dois filhos, um para cada lado."""
        if no is vazio:
            return
        pos[no] = (x, y, -1.25 * nivel)
        abertura = 4.6 / 2 ** (nivel // 2)
        if nivel % 2 == 0:
            visitar(no.esq, nivel + 1, x - abertura, y)
            visitar(no.dir, nivel + 1, x + abertura, y)
        else:
            visitar(no.esq, nivel + 1, x, y - abertura)
            visitar(no.dir, nivel + 1, x, y + abertura)

    visitar(raiz, 0, 0.0, 0.0)
    return pos


def _centralizar(pos):
    """Desloca as posições 3D para o centro da cena ficar na origem. Devolve o raio da cena."""
    if not pos:
        return 3.0
    centro = [(min(p[i] for p in pos.values()) + max(p[i] for p in pos.values())) / 2 for i in range(3)]
    for no, p in pos.items():
        pos[no] = tuple(p[i] - centro[i] for i in range(3))
    return max(3.0, max(max(abs(c) for c in p) for p in pos.values()) * 1.3)


def _borda(identificador, selecionado, destaques, normal):
    """Cor e espessura da borda de um nó: selecionado > em destaque > normal."""
    if selecionado is not None and identificador == selecionado:
        return CIANO, 3.5
    if identificador in destaques:
        return AMARELO, 3.0
    return normal, 1.5


# ---------------------------------------------------------------- Rubro-Negra

def _cores_rubro_negra(no):
    """(preenchimento, borda) de um nó. O nó preto tem contorno claro para aparecer no céu escuro."""
    return (VERMELHO_NO, VERMELHO_NO) if no.cor == VERMELHO else (PRETO_NO, "#cfd6ea")


def _rotulo_rubro_negra(no):
    # Chave repetida mostra o contador (ex.: "23:00 ×3").
    return str(no.chave) if no.quantidade == 1 else f"{no.chave}\n×{no.quantidade}"


def rubro_negra_2d(ax, arvore, destaques=(), selecionado=None, subtitulo=None, caminho=()):
    fundo_estrelado(ax)
    ax.axis("off")
    if subtitulo:
        ax.set_title(subtitulo, fontsize=10, color=TEXTO)
    pos = _posicoes_2d(arvore.raiz, arvore.NIL)
    if not pos:
        _vazia(ax)
        return []
    for no, (x, y) in pos.items():
        for filho in (no.esq, no.dir):
            if filho in pos:            # o NIL não tem posição, então é ignorado
                ax.plot([x, pos[filho][0]], [y, pos[filho][1]], color=LINHA, lw=1.2, zorder=1)
    # Traçado da busca: `caminho` traz as chaves visitadas, da raiz até o fim da busca.
    por_chave = {no.chave: p for no, p in pos.items()}
    _tracado_2d(ax, [por_chave[chave] for chave in caminho if chave in por_chave])
    tamanho = 950 if len(pos) <= 16 else 700
    for no, (x, y) in pos.items():
        cor, contorno = _cores_rubro_negra(no)
        borda, espessura = _borda(no.chave, selecionado, destaques, contorno)
        ax.scatter(x, y, s=tamanho, c=cor, edgecolors=borda, linewidths=espessura, zorder=2)
        ax.text(x, y, _rotulo_rubro_negra(no), color="white", ha="center", va="center",
                fontsize=6.3 if no.quantidade > 1 else 7.5, fontweight="bold", zorder=3)
    ax.margins(0.08)
    return [(no.chave, ax, p) for no, p in pos.items()]


def rubro_negra_3d(ax, arvore, visao, destaques=(), selecionado=None, caminho=()):
    pos = _posicoes_3d(arvore.raiz, arvore.NIL)
    preparar_3d(ax, _centralizar(pos), *visao)
    if not pos:
        _vazia(ax, True)
        return []
    _linhas_3d(ax, [(p, pos[filho]) for no, p in pos.items() for filho in (no.esq, no.dir) if filho in pos])
    por_chave = {no.chave: p for no, p in pos.items()}
    _tracado_3d(ax, [por_chave[chave] for chave in caminho if chave in por_chave])
    nucleos, contornos, halos, marcas = [], [], [], []
    for no, p in pos.items():
        cor, contorno = _cores_rubro_negra(no)
        nucleos.append(cor)
        contornos.append(contorno)
        halos.append(VERMELHO_NO if no.cor == VERMELHO else "#9fb3ff")
        anel = _marca(no.chave, selecionado, destaques)
        if anel:
            marcas.append((p, anel, 420))
        _rotulo_3d(ax, (p[0], p[1], p[2] - 0.42), _rotulo_rubro_negra(no).replace("\n", " "), color=TEXTO,
                   ha="center", va="top", fontsize=7, fontweight="bold")
    _estrelas_3d(ax, list(pos.values()), nucleos, contornos, [300] * len(pos), halos, marcas)
    return [(no.chave, ax, p) for no, p in pos.items()]


# ---------------------------------------------------------------------- 2-3-4

def arvore234_2d(ax, arvore, destaques=(), selecionado=None, subtitulo=None, caminho=()):
    """Cada nó é uma caixa com as chaves separadas por |."""
    fundo_estrelado(ax, 2)
    ax.axis("off")
    if subtitulo:
        ax.set_title(subtitulo, fontsize=10, color=TEXTO)
    if not arvore.raiz.chaves:
        _vazia(ax)
        return []

    # As posições são calculadas em "caracteres": a largura de cada caixa é o
    # tamanho do texto que vai dentro dela.
    def texto(no):
        return " | ".join(str(c) for c in no.chaves)

    pos, cursor = {}, [0]

    def calcular(no, nivel):
        if no.folha:
            largura = len(texto(no)) + 2
            x = cursor[0] + largura / 2
            cursor[0] += largura + 2            # espaço entre folhas vizinhas
        else:
            # Nó interno fica centralizado sobre os filhos.
            xs = [calcular(f, nivel + 1) for f in no.filhos]
            x = sum(xs) / len(xs)
        pos[id(no)] = (x, -nivel)
        return x

    calcular(arvore.raiz, 0)

    # Tamanho da fonte para o texto caber na caixa (fonte monoespaçada:
    # cada caractere tem largura de 0,6 x o tamanho da fonte).
    largura_pol = ax.get_position().width * ax.figure.get_figwidth()
    fonte_maxima = 11
    # Árvore pequena: o eixo fica mais largo que ela, para as caixas não esticarem.
    total = max(cursor[0], 105 * largura_pol / fonte_maxima)
    margem = (total - cursor[0]) / 2
    fonte = min(fonte_maxima, 105 * largura_pol / total)
    pontos = []

    def desenhar(no):
        x, y = pos[id(no)]
        for f in no.filhos:
            fx, fy = pos[id(f)]
            ax.plot([x, fx], [y - 0.16, fy + 0.16], color=LINHA, lw=1.2, zorder=1)
            desenhar(f)
        largura = len(texto(no)) + 2
        marcado = any(c in destaques for c in no.chaves)
        escolhido = selecionado in no.chaves
        ax.add_patch(plt.Rectangle((x - largura / 2, y - 0.16), largura, 0.32, facecolor="#16264d",
                                   edgecolor=CIANO if escolhido else AMARELO if marcado else DOURADO,
                                   lw=3 if (escolhido or marcado) else 1.3, zorder=2))
        # Cada chave é escrita separadamente para poder ter cor e clique próprios.
        inicio = x - len(texto(no)) / 2
        for i, chave in enumerate(no.chaves):
            centro = inicio + len(str(chave)) / 2
            cor = CIANO if chave == selecionado else AMARELO if chave in destaques else TEXTO
            ax.text(centro, y, str(chave), ha="center", va="center", fontsize=fonte, color=cor,
                    family="monospace", fontweight="bold", zorder=3)
            pontos.append((chave, ax, (centro, y)))
            inicio += len(str(chave))
            if i < len(no.chaves) - 1:
                # Separador " | " entre esta chave e a próxima.
                ax.text(inicio + 1.5, y, "|", ha="center", va="center", fontsize=fonte, color=SUAVE,
                        family="monospace", zorder=3)
                inicio += 3

    desenhar(arvore.raiz)
    # Traçado da busca: `caminho` traz os nós visitados, da raiz até o fim da busca.
    _tracado_2d(ax, [pos[id(no)] for no in caminho if id(no) in pos])
    ax.set_xlim(-1 - margem, cursor[0] + margem)
    ax.set_ylim(-max(arvore.altura(), 4) + 0.5, 0.5)    # reserva espaço para 4 níveis
    return pontos


def arvore234_3d(ax, arvore, visao, destaques=(), selecionado=None, caminho=()):
    """Cada nó é um aglomerado de 1 a 3 estrelas (uma por chave), com os filhos em círculo abaixo."""
    centros = {}

    def calcular(no, nivel, x, y, direcao):
        centros[id(no)] = (x, y, -1.7 * nivel)
        if no.folha:
            return
        quantidade = len(no.filhos)
        raio = 4.2 / 1.35 ** nivel      # cada nível fica um pouco mais perto do pai que o anterior
        leque = 2.4 / 1.5 ** (nivel - 1)    # abertura total do leque, em radianos
        for i, filho in enumerate(no.filhos):
            if nivel == 0:
                # Os filhos da raiz se espalham em volta dela, num círculo completo.
                angulo = direcao + 2 * math.pi * i / quantidade
            else:
                # Os demais se abrem em leque para FORA, na direção em que o pai
                # já estava indo: assim ramos vizinhos não se misturam.
                angulo = direcao + leque * (i / (quantidade - 1) - 0.5)
            calcular(filho, nivel + 1, x + raio * math.cos(angulo), y + raio * math.sin(angulo), angulo)

    if arvore.raiz.chaves:
        calcular(arvore.raiz, 0, 0.0, 0.0, 0.3)
    limite = _centralizar(centros)
    preparar_3d(ax, limite, *visao)
    if not centros:
        _vazia(ax, True)
        return []
    pontos, ligacoes, barras, marcas = [], [], [], []

    def percorrer(no):
        x, y, z = centros[id(no)]
        for filho in no.filhos:
            ligacoes.append(((x, y, z), centros[id(filho)]))
            percorrer(filho)
        # As chaves do nó ficam lado a lado, ligadas por um traço dourado.
        quantidade = len(no.chaves)
        xs = [x + 0.42 * (i - (quantidade - 1) / 2) for i in range(quantidade)]
        if quantidade > 1:
            barras.append(((xs[0], y, z), (xs[-1], y, z)))
        for chave, xc in zip(no.chaves, xs):
            pontos.append((chave, ax, (xc, y, z)))
            anel = _marca(chave, selecionado, destaques)
            if anel:
                marcas.append(((xc, y, z), anel, 300))
        _rotulo_3d(ax, (x, y, z - 0.42), " | ".join(str(c) for c in no.chaves), color=TEXTO, ha="center",
                   va="top", fontsize=7, fontweight="bold", family="monospace")

    percorrer(arvore.raiz)
    _linhas_3d(ax, ligacoes)
    _tracado_3d(ax, [centros[id(no)] for no in caminho if id(no) in centros])
    _linhas_3d(ax, barras, DOURADO, 2.2)
    quantidade = len(pontos)
    _estrelas_3d(ax, [p for _, _, p in pontos], ["#fff3c4"] * quantidade, [DOURADO] * quantidade,
                 [170] * quantidade, [DOURADO] * quantidade, marcas)
    return pontos


# ------------------------------------------------------------------------ k-D

def _tamanho_estrela(estrela):
    """Tamanho do ponto conforme o brilho (magnitude menor = estrela mais brilhante)."""
    return 85 * 10 ** (-0.2 * estrela.magnitude)


def _linhas_das_constelacoes(nos, posicao):
    """Pares de posições das constelações cujas duas estrelas estão na árvore."""
    por_nome = {no.valor.nome.rstrip(" AB"): no for no in nos}
    return [(posicao(por_nome[a]), posicao(por_nome[b])) for a, b in CONSTELACOES
            if a in por_nome and b in por_nome]


def kd_arvore_2d(ax, arvore, visitados=(), escolhidos=(), selecionado=None, caminho=()):
    """Diagrama da árvore k-D: a cor do nó indica qual coordenada ele compara."""
    fundo_estrelado(ax, 4, 90)
    ax.axis("off")
    eixos = "x, y, z" if arvore.k == 3 else "ascensão reta, declinação"
    ax.set_title(f"Árvore k-D (k = {arvore.k}: {eixos})", fontsize=9, color=TEXTO)
    pos = _posicoes_2d(arvore.raiz, None)
    if not pos:
        _vazia(ax)
        return []
    # Todas as arestas num objeto só e todos os nós num único scatter: bem mais rápido.
    ax.add_collection(LineCollection([(p, pos[filho]) for no, p in pos.items()
                                      for filho in (no.esq, no.dir) if filho is not None],
                                     colors=LINHA, linewidths=1.1, zorder=1))
    _tracado_2d(ax, [pos[no] for no in caminho if no in pos])
    # Com muitos nós, círculos e rótulos menores para não encostarem.
    tamanho, letras, fonte = (620, 6, 6.3) if len(pos) <= 20 else (330, 5, 5.2)
    cores, bordas, espessuras = [], [], []
    for no, (x, y) in pos.items():
        cor = COR_EIXO[no.eixo]
        if no.valor is selecionado:
            borda, espessura = CIANO, 3.5
        elif no in escolhidos:
            borda, espessura = VERDE, 3.2
        elif no in visitados:
            borda, espessura = AMARELO, 2.8
        else:
            borda, espessura = cor, 1.5
        cores.append(cor)
        bordas.append(borda)
        espessuras.append(espessura)
        ax.text(x, y, str(no.valor)[:letras], color="white", ha="center", va="center",
                fontsize=fonte, fontweight="bold", zorder=3)
    xs, ys = zip(*pos.values())
    ax.scatter(xs, ys, s=tamanho, c=cores, edgecolors=bordas, linewidths=espessuras, zorder=2)
    ax.margins(0.1)
    return [(no.valor, ax, p) for no, p in pos.items()]


def kd_plano(ax, arvore, alvo=None, vizinho=None, escolhidos=(), selecionado=None, raio=None, caminho=()):
    """Mapa plano do céu (k = 2): cada nó traça a linha que divide a sua região."""
    fundo_estrelado(ax, 5, 120)
    for lado in ax.spines.values():
        lado.set_color(LINHA)
    ax.tick_params(colors=SUAVE, labelsize=7)

    def cortes(no, x0, x1, y0, y1):
        # (x0, x1, y0, y1) é a região do mapa que pertence a este nó.
        if no is None:
            return
        x, y = no.ponto
        if no.eixo == 0:
            # Compara a ascensão reta: linha vertical, só dentro da região do nó.
            ax.plot([x, x], [y0, y1], color=COR_EIXO[0], lw=0.9, alpha=0.6, zorder=1)
            cortes(no.esq, x0, x, y0, y1)
            cortes(no.dir, x, x1, y0, y1)
        else:
            # Compara a declinação: linha horizontal.
            ax.plot([x0, x1], [y, y], color=COR_EIXO[1], lw=0.9, alpha=0.6, zorder=1)
            cortes(no.esq, x0, x1, y0, y)
            cortes(no.dir, x0, x1, y, y1)

    cortes(arvore.raiz, *CEU)
    nos = arvore.em_ordem()
    for (x0, y0), (x1, y1) in _linhas_das_constelacoes(nos, lambda no: no.ponto):
        ax.plot([x0, x1], [y0, y1], color="white", lw=0.8, alpha=0.5, ls=":", zorder=2)
    # No mapa, o traçado liga as estrelas na ordem em que a busca passou por elas.
    _tracado_2d(ax, [no.ponto for no in caminho], zorder=2.5)
    # Os rótulos alternam de posição para não ficarem uns sobre os outros.
    deslocamentos = [(5, 5), (5, -10), (-5, 5), (-5, -10)]
    for i, no in enumerate(nos):
        x, y = no.ponto
        cor = CIANO if no.valor is selecionado else VERDE if no in escolhidos else "white"
        ax.scatter(x, y, s=_tamanho_estrela(no.valor) * 0.8, color=cor, alpha=0.95, zorder=3)
        dx, dy = deslocamentos[i % 4]
        ax.annotate(str(no.valor), (x, y), textcoords="offset points", xytext=(dx, dy),
                    ha="left" if dx > 0 else "right", fontsize=6.3, color=cor if cor != "white" else SUAVE)
    if alvo:
        ax.scatter(*alvo, s=170, marker="*", color=ROSA, zorder=4)
        if raio:
            ax.add_patch(plt.Circle(alvo, raio, facecolor=ROSA, alpha=0.12, edgecolor=ROSA, lw=1.5, zorder=1))
        if vizinho is not None:
            ax.plot([alvo[0], vizinho.ponto[0]], [alvo[1], vizinho.ponto[1]], "--", color=ROSA, zorder=2)
    ax.set_xlim(CEU[0], CEU[1])
    ax.set_ylim(CEU[2], CEU[3])
    ax.set_xlabel("Ascensão reta (graus)", color=SUAVE, fontsize=8)
    ax.set_ylabel("Declinação (graus)", color=SUAVE, fontsize=8)
    ax.set_title("Mapa plano: cada nó traça um corte", fontsize=9, color=TEXTO)
    return [(no.valor, ax, no.ponto) for no in nos]


def kd_esfera(ax, arvore, visao, alvo=None, vizinho=None, visitados=(), escolhidos=(), selecionado=None,
              caminho=()):
    """Esfera celeste (k = 3): as estrelas ficam na superfície e a árvore liga pai e filho por dentro."""
    preparar_3d(ax, 1.25, *visao)
    # Grade da esfera: paralelos e meridianos bem fracos, com o equador mais forte.
    passo = [math.radians(g) for g in range(0, 361, 10)]
    grade = []
    for dec in (-60, -30, 0, 30, 60):
        d = math.radians(dec)
        circulo = [(math.cos(d) * math.cos(a), math.cos(d) * math.sin(a), math.sin(d)) for a in passo]
        if dec == 0:
            _linhas_3d(ax, [circulo], "#3a4a75", 1.1, 0.8)
        else:
            grade.append(circulo)
    for ra in range(0, 360, 45):
        a = math.radians(ra)
        grade.append([(math.cos(d) * math.cos(a), math.cos(d) * math.sin(a), math.sin(d))
                      for d in (math.radians(g) for g in range(-90, 91, 10))])
    _linhas_3d(ax, grade, "#3a4a75", 0.5, 0.8)
    nos = arvore.em_ordem()
    if not nos:
        _vazia(ax, True)
        return []

    # Arestas da árvore, cada uma na cor do eixo que o PAI compara.
    arestas, cores = [], []
    for no in nos:
        for filho in (no.esq, no.dir):
            if filho is not None:
                arestas.append((no.ponto, filho.ponto))
                cores.append(COR_EIXO[no.eixo])
    _linhas_3d(ax, arestas, cores, 1.0, 0.75)
    _tracado_3d(ax, [no.ponto for no in caminho])
    _linhas_3d(ax, _linhas_das_constelacoes(nos, lambda no: no.ponto), "white", 0.9, 0.6, ":")

    nucleos, marcas = [], []
    for no in nos:
        if no.valor is selecionado:
            cor, anel = "white", CIANO
        elif no in escolhidos:
            cor, anel = VERDE, VERDE
        elif no in visitados:
            cor, anel = "white", AMARELO
        else:
            cor, anel = "white", None
        nucleos.append(cor)
        if anel:
            marcas.append((no.ponto, anel, _tamanho_estrela(no.valor) + 90))
        _rotulo_3d(ax, tuple(c * 1.07 for c in no.ponto), str(no.valor), color=anel or TEXTO,
                   fontsize=6.3, ha="center")
    # A raiz ganha um anel dourado fino: é por ela que toda busca começa.
    ax.scatter(*[[c] for c in arvore.raiz.ponto], s=420, facecolors="none", edgecolors=DOURADO,
               linewidths=1.3, depthshade=False)
    _estrelas_3d(ax, [no.ponto for no in nos], nucleos, nucleos, [_tamanho_estrela(no.valor) for no in nos],
                 nucleos, marcas)
    if alvo is not None:
        ax.scatter(*[[c] for c in alvo], s=190, marker="*", color=ROSA, depthshade=False)
        if vizinho is not None:
            _linhas_3d(ax, [(alvo, vizinho.ponto)], ROSA, 1.6, 1.0, "--")
    return [(no.valor, ax, no.ponto) for no in nos]
