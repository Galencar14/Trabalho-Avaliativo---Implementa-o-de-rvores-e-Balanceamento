"""Teste de corretude da Árvore 2-3-4: compara a árvore com um conjunto (set) comum.

Em cada rodada faz 300 inserções e exclusões aleatórias e, após cada uma,
confere as regras da árvore, o percurso em ordem e a busca.
"""

import random

from arvore234 import Arvore234

SEMENTE = 2024              # semente fixa: se algo falhar, a falha se repete igual
random.seed(SEMENTE)

for rodada in range(300):
    arvore, ref = Arvore234(), set()    # ref = resposta esperada
    for passo in range(300):
        k = random.randint(0, 120)      # faixa pequena para gerar muitas repetições
        if random.random() < 0.55:
            # Inserir: só deve devolver True se a chave ainda não existia.
            assert arvore.inserir(k) == (k not in ref)
            ref.add(k)
        else:
            # Excluir: só deve devolver True se a chave existia.
            assert arvore.excluir(k) == (k in ref)
            ref.discard(k)
        arvore.validar()
        assert arvore.todas_chaves() == sorted(ref), f"rodada {rodada}, passo {passo}"
        assert arvore.buscar(k) == (k in ref)
print(f"300 rodadas aleatórias OK (semente {SEMENTE})")
