"""Teste de corretude das três árvores: cada uma é comparada com uma estrutura simples do Python.

Após CADA operação aleatória o teste confere as regras da árvore (validar)
e se o conteúdo é igual ao da estrutura de referência.

Uso: python teste_aleatorio.py
"""

import random

from arvore234 import Arvore234
from arvore_kd import ArvoreKD, distancia
from rubro_negra import ArvoreRubroNegra

SEMENTE = 2024              # semente fixa: se algo falhar, a falha se repete igual


def testar_rubro_negra(rodadas=300):
    for rodada in range(rodadas):
        arv, ref = ArvoreRubroNegra(), {}       # ref = {chave: quantidade}
        for passo in range(200):
            k = random.randint(0, 80)           # faixa pequena para gerar repetições
            sorteio = random.random()
            if sorteio < 0.6:
                arv.inserir(k)
                ref[k] = ref.get(k, 0) + 1
            elif sorteio < 0.9:
                # remover uma unidade
                assert arv.remover(k) == (k in ref)
                if k in ref:
                    ref[k] -= 1
                    if ref[k] == 0:
                        del ref[k]
            else:
                # remover o nó inteiro
                assert arv.remover(k, todas=True) == (k in ref)
                ref.pop(k, None)
            ok, info = arv.validar()
            assert ok, f"rodada {rodada}, passo {passo}: {info}"
            assert [(n.chave, n.quantidade) for n in arv.em_ordem()] == sorted(ref.items())
            assert arv.tamanho == len(ref)
            menor = arv.minimo()
            assert (menor.chave if menor else None) == (min(ref) if ref else None)
    print(f"Rubro-Negra: {rodadas} rodadas OK")


def testar_234(rodadas=300):
    for rodada in range(rodadas):
        arv, ref = Arvore234(), {}              # ref = {chave: valor}
        for passo in range(300):
            k = random.randint(0, 120)
            if random.random() < 0.55:
                # inserir: só aceita se a chave ainda não existe
                valor = f"registro {rodada}-{passo}"
                assert arv.inserir(k, valor) == (k not in ref)
                ref.setdefault(k, valor)
            else:
                assert arv.excluir(k) == (k in ref)
                ref.pop(k, None)
            ok, info = arv.validar()
            assert ok, f"rodada {rodada}, passo {passo}: {info}"
            # as chaves E os valores têm que acompanhar as divisões e fusões
            assert arv.em_ordem() == sorted(ref.items())
            achou, valor, _ = arv.buscar(k)
            assert achou == (k in ref) and valor == ref.get(k)
    print(f"2-3-4:       {rodadas} rodadas OK")


def testar_kd(rodadas=200):
    def ponto_aleatorio(k):
        """Ponto com k coordenadas inteiras numa faixa pequena, para gerar repetições."""
        return tuple(random.randint(0, 12) for _ in range(k))

    for rodada in range(rodadas):
        k = random.choice([2, 2, 3])
        arv = ArvoreKD(k)
        ref = [(ponto_aleatorio(k), f"v{i}") for i in range(random.randint(0, 20))]
        arv.construir(ref)

        for passo in range(80):
            p = ponto_aleatorio(k)
            sorteio = random.random()
            if sorteio < 0.55:
                valor = f"r{rodada}p{passo}"
                arv.inserir(p, valor)
                ref.append((p, valor))
            elif sorteio < 0.95:
                removido = arv.remover(p)
                existia = any(q == p for q, _ in ref)
                assert (removido is not None) == existia
                if existia:
                    ref.remove((p, removido))   # o par removido tem que existir
            else:
                arv.reconstruir()               # rebalanceamento não pode perder nada
            ok, info = arv.validar()
            assert ok, f"rodada {rodada}, passo {passo}: {info}"
            assert sorted((n.ponto, n.valor) for n in arv.em_ordem()) == sorted(ref)

            # busca exata
            q = ponto_aleatorio(k)
            assert (arv.buscar(q)[0] is not None) == any(r == q for r, _ in ref)

            # vizinho mais próximo: a distância tem que ser a menor possível
            vizinho, dist, _, _ = arv.vizinho_mais_proximo(q)
            if ref:
                assert abs(dist - min(distancia(q, r) for r, _ in ref)) < 1e-9
            else:
                assert vizinho is None

            # busca por intervalo
            a, b = ponto_aleatorio(k), ponto_aleatorio(k)
            minimos = tuple(min(x, y) for x, y in zip(a, b))
            maximos = tuple(max(x, y) for x, y in zip(a, b))
            esperado = [r for r in ref if all(minimos[i] <= r[0][i] <= maximos[i] for i in range(k))]
            achados, _ = arv.busca_por_intervalo(minimos, maximos)
            assert sorted((n.ponto, n.valor) for n in achados) == sorted(esperado)

            # busca por raio
            raio = random.uniform(0, 8)
            esperado = [r for r in ref if distancia(q, r[0]) <= raio]
            achados, _ = arv.busca_por_raio(q, raio)
            assert sorted((n.ponto, n.valor) for n in achados) == sorted(esperado)
    print(f"k-D:         {rodadas} rodadas OK")


if __name__ == "__main__":
    random.seed(SEMENTE)
    testar_rubro_negra()
    testar_234()
    testar_kd()
    print(f"Todas as árvores passaram (semente {SEMENTE})")
