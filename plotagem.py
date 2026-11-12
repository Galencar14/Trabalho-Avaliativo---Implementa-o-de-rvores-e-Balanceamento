"""Desenho da árvore: imagens com matplotlib e versão em texto para o terminal."""

import matplotlib.pyplot as plt

from rubro_negra import VERMELHO


def _posicoes(arvore):
    """Calcula (x, y) de cada nó.

    x = posição do nó no percurso em ordem (0, 1, 2...), assim os nós nunca se
    sobrepõem na horizontal; y = -profundidade, para a raiz ficar no topo.
    """
    pos, contador = {}, [0]     # lista para o contador poder ser alterado dentro de visitar

    def visitar(x, nivel):
        if x is arvore.NIL:
            return
        visitar(x.esq, nivel + 1)
        pos[x] = (contador[0], -nivel)
        contador[0] += 1
        visitar(x.dir, nivel + 1)

    visitar(arvore.raiz, 0)
    return pos


def _plotar(ax, arvore, titulo, destaques=()):
    """Desenha a árvore no eixo ax. Nós cujas chaves estão em destaques ganham borda amarela."""
    ax.clear()
    ax.axis("off")
    ax.set_title(titulo, fontsize=11)
    pos = _posicoes(arvore)
    if not pos:
        ax.text(0.5, 0.5, "(árvore vazia)", ha="center", va="center", transform=ax.transAxes)
        return
    # Primeiro as arestas (ficam por baixo, zorder=1)...
    for no, (x, y) in pos.items():
        for filho in (no.esq, no.dir):
            if filho in pos:            # o NIL não tem posição, então é ignorado
                fx, fy = pos[filho]
                ax.plot([x, fx], [y, fy], color="gray", lw=1.2, zorder=1)
    # ...depois os círculos e os rótulos por cima.
    for no, (x, y) in pos.items():
        cor = "#d62828" if no.cor == VERMELHO else "#1a1a1a"
        borda = "#ffb703" if no.chave in destaques else cor
        ax.scatter(x, y, s=700, c=cor, edgecolors=borda, linewidths=3, zorder=2)
        # Chaves repetidas mostram a quantidade embaixo (ex.: "40\n×3").
        rotulo = str(no.chave) if no.quantidade == 1 else f"{no.chave}\n×{no.quantidade}"
        ax.text(x, y, rotulo, color="white", ha="center", va="center", fontsize=8, fontweight="bold", zorder=3)
    ax.margins(0.08)


def desenhar(arvore, titulo, arquivo, destaque=None):
    """Salva a árvore em um arquivo PNG (usado na demonstração)."""
    # A figura cresce com o número de nós e com a altura da árvore.
    largura = max(6, arvore.tamanho * 0.55)
    altura = max(3, arvore.altura() * 1.1)
    fig, ax = plt.subplots(figsize=(largura, altura))
    _plotar(ax, arvore, titulo, (destaque,))
    fig.tight_layout()
    fig.savefig(arquivo, dpi=110)
    plt.close(fig)                      # libera a memória da figura


class Janela:
    """Janela do matplotlib que é redesenhada a cada comando do modo interativo."""

    def __init__(self):
        plt.ion()                       # modo interativo: a janela não trava o input()
        self.fig, self.ax = plt.subplots(figsize=(13, 6))
        self.fig.canvas.manager.set_window_title("Árvore Rubro-Negra")

    def mostrar(self, arvore, titulo, destaques=(), pausa=0.05):
        """Redesenha a árvore e espera `pausa` segundos para a janela atualizar."""
        _plotar(self.ax, arvore, titulo, destaques)
        self.fig.tight_layout()
        self.fig.canvas.draw_idle()
        plt.pause(pausa)

    def salvar(self, arquivo):
        self.fig.savefig(arquivo, dpi=110)


def texto(arvore):
    """Árvore em texto, deitada: direita em cima, esquerda embaixo, raiz à esquerda.

    Cada linha mostra chave(cor) e, se repetida, a quantidade (ex.: 40(P) x3).
    """
    linhas = []

    def visitar(x, prefixo, eh_dir):
        if x is arvore.NIL:
            return
        # A barra vertical "│" só continua do lado onde ainda vai haver irmão.
        visitar(x.dir, prefixo + ("    " if eh_dir else "│   "), True)
        marca = "┌── " if eh_dir else "└── "
        qtd = f" x{x.quantidade}" if x.quantidade > 1 else ""
        linhas.append(f"{prefixo}{marca}{x.chave}({x.cor}){qtd}")
        visitar(x.esq, prefixo + ("│   " if eh_dir else "    "), False)

    if arvore.raiz is arvore.NIL:
        return "(árvore vazia)"
    # A raiz é impressa sem prefixo, entre a subárvore direita e a esquerda.
    visitar(arvore.raiz.dir, "", True)
    qtd = f" x{arvore.raiz.quantidade}" if arvore.raiz.quantidade > 1 else ""
    linhas.append(f"{arvore.raiz.chave}({arvore.raiz.cor}){qtd}")
    visitar(arvore.raiz.esq, "", False)
    return "\n".join(linhas)
