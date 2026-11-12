"""Demonstração da Árvore k-D (2 dimensões) com o exemplo explicado no README.

Uso: python main.py   (imprime cada passo e salva as figuras em ./imagens/)
"""

import os

from arvore_kd import ArvoreKD
from plotagem import desenhar

PASTA = "imagens"
os.makedirs(PASTA, exist_ok=True)

# Os 6 pontos do exemplo do README.
PONTOS = [(2, 3), (5, 4), (9, 6), (4, 7), (8, 1), (7, 2)]


def mostrar(arvore):
    print(arvore.texto())
    arvore.validar()
    print(f"Pontos: {arvore.tamanho} | altura: {arvore.altura()}")


arvore = ArvoreKD(k=2)

print("=== 1. CONSTRUÇÃO (pela mediana) ===")
arvore.construir(PONTOS)
mostrar(arvore)
desenhar(arvore, "1. Árvore construída com os 6 pontos", f"{PASTA}/1_construcao.png")

print("\n=== 2. INSERÇÃO ===")
for ponto in [(3, 6), (6, 8)]:
    arvore.inserir(ponto)
    _, caminho = arvore.buscar(ponto)
    print(f"Inseriu {ponto}: caminho {' -> '.join(map(str, caminho))}")
mostrar(arvore)
desenhar(arvore, "2. Após inserir (3, 6) e (6, 8)", f"{PASTA}/2_insercao.png", visitados=[(3, 6), (6, 8)])

print("\n=== 3. BUSCA EXATA ===")
for ponto in [(8, 1), (6, 6)]:
    achou, caminho = arvore.buscar(ponto)
    print(f"Buscar {ponto}: {'encontrado' if achou else 'não encontrado'} | caminho {' -> '.join(map(str, caminho))}")
achou, caminho = arvore.buscar((8, 1))
desenhar(arvore, "3. Busca por (8, 1): nós visitados em amarelo", f"{PASTA}/3_busca.png", visitados=caminho)

print("\n=== 4. VIZINHO MAIS PRÓXIMO ===")
alvo = (9, 2)
vizinho, dist, visitados = arvore.vizinho_mais_proximo(alvo)
print(f"Alvo {alvo}: mais próximo é {vizinho}, distância {dist:.3f}")
print(f"Nós visitados: {len(visitados)} de {arvore.tamanho} -> {visitados}")
desenhar(arvore, f"4. Vizinho mais próximo de {alvo}: {vizinho}", f"{PASTA}/4_vizinho.png",
         alvo=alvo, destaque=vizinho, visitados=visitados)

print("\n=== 5. BUSCA POR INTERVALO ===")
caixa = ((3, 3), (8, 7))
achados = arvore.busca_por_intervalo(*caixa)
print(f"Pontos com x em [3, 8] e y em [3, 7]: {sorted(achados)}")
desenhar(arvore, "5. Busca por intervalo: x em [3, 8], y em [3, 7]", f"{PASTA}/5_intervalo.png",
         caixa=caixa, visitados=achados)

print("\n=== 6. REMOÇÃO ===")
for ponto in [(7, 2), (1, 1)]:
    if arvore.remover(ponto):
        print(f"Removeu {ponto}")
    else:
        print(f"{ponto} não existe -> nada a remover")
mostrar(arvore)
desenhar(arvore, "6. Após remover a raiz (7, 2)", f"{PASTA}/6_remocao.png")

print(f"\nImagens salvas em ./{PASTA}/")
