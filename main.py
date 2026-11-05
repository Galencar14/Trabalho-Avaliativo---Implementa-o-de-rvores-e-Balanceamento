"""Demonstração da Árvore 2-3-4: inserção (21 chaves), busca e exclusão."""

import os
from arvore234 import Arvore234

PASTA = "imagens"
os.makedirs(PASTA, exist_ok=True)

arvore = Arvore234()

# 21 chaves diferentes + o 7 repetido no final (de propósito, para mostrar que repetidos são ignorados)
chaves = [10, 20, 30, 40, 50, 60, 70, 80, 90, 15, 25, 35, 45, 55, 65, 75, 85, 5, 95, 100, 7, 7]

print("=== INSERÇÃO ===")
passo = 0
for c in chaves:
    inserido = arvore.inserir(c)
    if not inserido:
        print(f"Chave {c} repetida -> ignorada")
        continue
    passo += 1
    arvore.validar()
    print(f"Inseriu {c}")
    arvore.plotar(f"Inserção {passo}: chave {c}", f"{PASTA}/insercao_{passo:02d}_{c}.png")

print("\nÁrvore final após as inserções:")
arvore.imprimir()
print("Total de chaves:", len(arvore.todas_chaves()))
print("Altura:", arvore.altura())
print("Em ordem:", arvore.todas_chaves())
arvore.plotar("Árvore após 21 inserções", f"{PASTA}/arvore_completa.png")

print("\n=== BUSCA ===")
for c in [45, 100, 999]:
    print(f"Buscar {c}:", "encontrado" if arvore.buscar(c) else "não encontrado")

print("\n=== EXCLUSÃO ===")
for c in [60, 10, 90, 5, 999]:
    if arvore.excluir(c):
        arvore.validar()
        print(f"Excluiu {c}")
        arvore.plotar(f"Exclusão da chave {c}", f"{PASTA}/exclusao_{c}.png")
    else:
        print(f"Chave {c} não existe -> nada a excluir")

print("\nÁrvore final após as exclusões:")
arvore.imprimir()
print("Em ordem:", arvore.todas_chaves())
