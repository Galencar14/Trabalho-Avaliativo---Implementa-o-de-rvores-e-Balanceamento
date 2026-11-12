"""Observatório — Árvores e Balanceamento.

Abre a janela do programa. A tela inicial é o menu: escolha uma árvore, e o
botão "Menu principal" de cada módulo volta para cá.

Uso: python main.py
"""

from agenda import Agenda
from catalogo import Catalogo
from comparacao import Comparacao
from janela import App
from mapa import Mapa

if __name__ == "__main__":
    # A ordem da lista é a ordem dos botões no menu. Cada item é um módulo:
    # uma classe que liga os botões da janela às operações de uma árvore.
    App([Agenda, Catalogo, Mapa, Comparacao]).executar()
