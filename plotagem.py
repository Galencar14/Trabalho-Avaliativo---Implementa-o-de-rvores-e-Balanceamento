import matplotlib.pyplot as plt

from rubro_negra import VERMELHO


def _posicoes(arvore):
    pos, contador = {}, [0]

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
    ax.clear()
    ax.axis("off")
    ax.set_title(titulo, fontsize=11)
    pos = _posicoes(arvore)
    if not pos:
        ax.text(0.5, 0.5, "(árvore vazia)", ha="center", va="center", transform=ax.transAxes)
        return
    for no, (x, y) in pos.items():
        for filho in (no.esq, no.dir):
            if filho in pos:
                fx, fy = pos[filho]
                ax.plot([x, fx], [y, fy], color="gray", lw=1.2, zorder=1)
    for no, (x, y) in pos.items():
        cor = "#d62828" if no.cor == VERMELHO else "#1a1a1a"
        borda = "#ffb703" if no.chave in destaques else cor
        ax.scatter(x, y, s=700, c=cor, edgecolors=borda, linewidths=3, zorder=2)
        rotulo = str(no.chave) if no.quantidade == 1 else f"{no.chave}\n×{no.quantidade}"
        ax.text(x, y, rotulo, color="white", ha="center", va="center", fontsize=8, fontweight="bold", zorder=3)
    ax.margins(0.08)


def desenhar(arvore, titulo, arquivo, destaque=None):
    largura = max(6, arvore.tamanho * 0.55)
    altura = max(3, arvore.altura() * 1.1)
    fig, ax = plt.subplots(figsize=(largura, altura))
    _plotar(ax, arvore, titulo, (destaque,))
    fig.tight_layout()
    fig.savefig(arquivo, dpi=110)
    plt.close(fig)


class Janela:
    def __init__(self):
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(13, 6))
        self.fig.canvas.manager.set_window_title("Árvore Rubro-Negra")

    def mostrar(self, arvore, titulo, destaques=(), pausa=0.05):
        _plotar(self.ax, arvore, titulo, destaques)
        self.fig.tight_layout()
        self.fig.canvas.draw_idle()
        plt.pause(pausa)

    def salvar(self, arquivo):
        self.fig.savefig(arquivo, dpi=110)


def texto(arvore):
    linhas = []

    def visitar(x, prefixo, eh_dir):
        if x is arvore.NIL:
            return
        visitar(x.dir, prefixo + ("    " if eh_dir else "│   "), True)
        marca = "┌── " if eh_dir else "└── "
        qtd = f" x{x.quantidade}" if x.quantidade > 1 else ""
        linhas.append(f"{prefixo}{marca}{x.chave}({x.cor}){qtd}")
        visitar(x.esq, prefixo + ("│   " if eh_dir else "    "), False)

    if arvore.raiz is arvore.NIL:
        return "(árvore vazia)"
    visitar(arvore.raiz.dir, "", True)
    qtd = f" x{arvore.raiz.quantidade}" if arvore.raiz.quantidade > 1 else ""
    linhas.append(f"{arvore.raiz.chave}({arvore.raiz.cor}){qtd}")
    visitar(arvore.raiz.esq, "", False)
    return "\n".join(linhas)
