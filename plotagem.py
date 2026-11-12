"""Desenho da árvore k-D de 2 dimensões: o plano dividido e a árvore lado a lado."""

import matplotlib
matplotlib.use("Agg")           # desenha direto em arquivo, sem abrir janela
import matplotlib.pyplot as plt

COR_X = "#d62828"               # nós/linhas que dividem por x (linha vertical)
COR_Y = "#1d4e89"               # nós/linhas que dividem por y (linha horizontal)


def _plano(ax, arvore, limites, alvo, destaque, caixa):
    """Lado esquerdo: os pontos no plano e a linha divisória de cada nó."""
    xmin, xmax, ymin, ymax = limites

    def rec(no, x0, x1, y0, y1):
        # (x0, x1, y0, y1) é a região do plano que pertence a este nó.
        if no is None:
            return
        x, y = no.ponto
        if no.eixo == 0:
            # Divide por x: linha vertical, só dentro da região do nó.
            ax.plot([x, x], [y0, y1], color=COR_X, lw=1.5, zorder=1)
            rec(no.esq, x0, x, y0, y1)
            rec(no.dir, x, x1, y0, y1)
        else:
            # Divide por y: linha horizontal.
            ax.plot([x0, x1], [y, y], color=COR_Y, lw=1.5, zorder=1)
            rec(no.esq, x0, x1, y0, y)
            rec(no.dir, x0, x1, y, y1)
        ax.scatter(x, y, s=45, color="black", zorder=3)
        ax.annotate(f"({x}, {y})", (x, y), textcoords="offset points", xytext=(6, 6), fontsize=8)

    rec(arvore.raiz, xmin, xmax, ymin, ymax)

    if caixa:
        # Retângulo da busca por intervalo.
        (ax0, ay0), (ax1, ay1) = caixa
        ax.add_patch(plt.Rectangle((ax0, ay0), ax1 - ax0, ay1 - ay0,
                                   facecolor="#ffb703", alpha=0.25, edgecolor="#fb8500", lw=2, zorder=0))
    if alvo:
        ax.scatter(*alvo, s=110, marker="*", color="#2a9d8f", zorder=4)
        ax.annotate(f"alvo {alvo}", alvo, textcoords="offset points", xytext=(6, -14), fontsize=8, color="#2a9d8f")
        if destaque:
            # Liga o alvo ao vizinho mais próximo encontrado.
            ax.plot([alvo[0], destaque[0]], [alvo[1], destaque[1]], "--", color="#2a9d8f", zorder=2)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Divisão do plano", fontsize=10)


def _arvore(ax, arvore, destaques):
    """Lado direito: a árvore. Vermelho = divide por x, azul = divide por y."""
    pos, contador = {}, [0]

    def posicionar(no, nivel):
        # x = ordem no percurso em ordem (evita sobreposição), y = -nível
        if no is None:
            return
        posicionar(no.esq, nivel + 1)
        pos[no] = (contador[0], -nivel)
        contador[0] += 1
        posicionar(no.dir, nivel + 1)

    posicionar(arvore.raiz, 0)
    ax.axis("off")
    ax.set_title("Árvore (vermelho: divide por x | azul: divide por y)", fontsize=10)
    for no, (x, y) in pos.items():
        for filho in (no.esq, no.dir):
            if filho is not None:
                fx, fy = pos[filho]
                ax.plot([x, fx], [y, fy], color="gray", lw=1.2, zorder=1)
    for no, (x, y) in pos.items():
        cor = COR_X if no.eixo == 0 else COR_Y
        borda = "#ffb703" if no.ponto in destaques else cor
        ax.scatter(x, y, s=1500, c=cor, edgecolors=borda, linewidths=3.5, zorder=2)
        ax.text(x, y, f"{no.ponto[0]}, {no.ponto[1]}", color="white", ha="center", va="center",
                fontsize=8, fontweight="bold", zorder=3)
    ax.margins(0.15)


def desenhar(arvore, titulo, arquivo, limites=(0, 10, 0, 10), alvo=None, destaque=None, visitados=(), caixa=None):
    """Salva um PNG com o plano e a árvore.

    alvo/destaque: ponto consultado e o vizinho encontrado (opcionais);
    visitados: nós que ganham borda amarela na árvore;
    caixa: ((xmin, ymin), (xmax, ymax)) da busca por intervalo.
    """
    if arvore.k != 2:
        raise ValueError("só é possível desenhar árvores de 2 dimensões")
    fig, (ax_plano, ax_arvore) = plt.subplots(1, 2, figsize=(13, 5.5))
    if arvore.raiz is not None:
        _plano(ax_plano, arvore, limites, alvo, destaque, caixa)
        _arvore(ax_arvore, arvore, set(visitados))
    fig.suptitle(titulo, fontsize=12)
    fig.tight_layout()
    fig.savefig(arquivo, dpi=110)
    plt.close(fig)
