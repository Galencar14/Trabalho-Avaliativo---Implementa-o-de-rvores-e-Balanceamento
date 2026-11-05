import random

from rubro_negra import ArvoreRubroNegra

for rodada in range(300):
    arv, ref = ArvoreRubroNegra(), {}
    for _ in range(200):
        k = random.randint(0, 80)
        if random.random() < 0.6:
            arv.inserir(k)
            ref[k] = ref.get(k, 0) + 1
        else:
            arv.remover(k)
            if k in ref:
                ref[k] -= 1
                if ref[k] == 0:
                    del ref[k]
        ok, info = arv.validar()
        assert ok, info
        assert [(n.chave, n.quantidade) for n in arv.em_ordem()] == sorted(ref.items())
print("300 rodadas aleatórias OK")
