"""Teste de corretude: compara a árvore com um dicionário comum.

Em cada rodada faz 200 operações aleatórias (inserir, remover uma unidade ou
remover o nó inteiro) e, após cada uma, confere que:
  - as propriedades rubro-negras continuam válidas;
  - o percurso em ordem tem exatamente as mesmas chaves e quantidades do dicionário.
"""

import random

from rubro_negra import ArvoreRubroNegra

SEMENTE = 2024              # semente fixa: se algo falhar, a falha se repete igual
random.seed(SEMENTE)

for rodada in range(300):
    arv, ref = ArvoreRubroNegra(), {}   # ref = resposta esperada {chave: quantidade}
    for passo in range(200):
        k = random.randint(0, 80)       # faixa pequena para gerar muitas repetições
        sorteio = random.random()
        if sorteio < 0.6:
            # 60%: inserir
            arv.inserir(k)
            ref[k] = ref.get(k, 0) + 1
        elif sorteio < 0.9:
            # 30%: remover uma unidade
            assert arv.remover(k) == (k in ref)
            if k in ref:
                ref[k] -= 1
                if ref[k] == 0:
                    del ref[k]
        else:
            # 10%: remover o nó inteiro, não importa a quantidade
            assert arv.remover(k, todas=True) == (k in ref)
            ref.pop(k, None)
        ok, info = arv.validar()
        assert ok, f"rodada {rodada}, passo {passo}: {info}"
        assert [(n.chave, n.quantidade) for n in arv.em_ordem()] == sorted(ref.items())
        assert arv.tamanho == len(ref)
print(f"300 rodadas aleatórias OK (semente {SEMENTE})")
