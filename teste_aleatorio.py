"""Teste de corretude da Árvore k-D: compara cada resposta com a força bruta.

Em cada rodada constrói uma árvore, faz inserções e remoções aleatórias e
confere que a regra da árvore continua válida e que busca, vizinho mais
próximo e busca por intervalo dão o mesmo resultado de percorrer a lista toda.
"""

import random

from arvore_kd import ArvoreKD, distancia

SEMENTE = 2024              # semente fixa: se algo falhar, a falha se repete igual
random.seed(SEMENTE)


def ponto_aleatorio(k):
    # Faixa pequena de propósito, para gerar coordenadas e pontos repetidos.
    return tuple(random.randint(0, 12) for _ in range(k))


for rodada in range(200):
    k = random.choice([2, 2, 3])
    arvore = ArvoreKD(k)
    ref = [ponto_aleatorio(k) for _ in range(random.randint(0, 20))]    # resposta esperada
    arvore.construir(ref)
    arvore.validar()

    for passo in range(80):
        p = ponto_aleatorio(k)
        if random.random() < 0.6:
            arvore.inserir(p)
            ref.append(p)
        else:
            existia = p in ref
            assert arvore.remover(p) == existia
            if existia:
                ref.remove(p)           # tira só uma cópia, como a árvore
        arvore.validar()
        assert sorted(arvore.todos_pontos()) == sorted(ref)

        # Busca exata
        q = ponto_aleatorio(k)
        assert arvore.buscar(q)[0] == (q in ref)

        # Vizinho mais próximo: a distância tem que ser a menor possível
        vizinho, dist, _ = arvore.vizinho_mais_proximo(q)
        if ref:
            assert abs(dist - min(distancia(q, r) for r in ref)) < 1e-9
        else:
            assert vizinho is None

        # Busca por intervalo
        a, b = ponto_aleatorio(k), ponto_aleatorio(k)
        minimos = tuple(min(x, y) for x, y in zip(a, b))
        maximos = tuple(max(x, y) for x, y in zip(a, b))
        esperado = [r for r in ref if all(minimos[i] <= r[i] <= maximos[i] for i in range(k))]
        assert sorted(arvore.busca_por_intervalo(minimos, maximos)) == sorted(esperado)

print(f"200 rodadas aleatórias OK (semente {SEMENTE})")
