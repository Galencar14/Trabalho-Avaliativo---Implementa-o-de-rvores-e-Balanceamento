"""Árvore k-D (k-dimensional) implementada do zero, sem bibliotecas de árvore.

Uma árvore k-D é uma árvore binária de busca para pontos com k coordenadas.
Em cada nível ela compara UMA coordenada só, alternando entre elas:
  nível 0 -> coordenada 0 (x), nível 1 -> coordenada 1 (y), nível 2 -> x de novo...

Regra de cada nó (o "eixo" do nó é a coordenada que ele compara):
  - subárvore esquerda: pontos com coordenada MENOR que a do nó naquele eixo;
  - subárvore direita:  pontos com coordenada MAIOR OU IGUAL.

Elementos repetidos: são permitidos. Um ponto igual a outro (ou só com a mesma
coordenada no eixo) vai sempre para a direita, por causa do "maior ou igual".
"""

import math


class No:
    def __init__(self, ponto, eixo):
        self.ponto = ponto      # tupla com as k coordenadas
        self.eixo = eixo        # coordenada comparada neste nó (0 = x, 1 = y, ...)
        self.esq = None         # pontos menores neste eixo
        self.dir = None         # pontos maiores ou iguais neste eixo


def distancia(a, b):
    """Distância euclidiana entre dois pontos."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


class ArvoreKD:
    def __init__(self, k=2):
        self.k = k              # número de dimensões
        self.raiz = None
        self.tamanho = 0

    def _conferir(self, ponto):
        """Garante que o ponto é uma tupla com exatamente k coordenadas."""
        ponto = tuple(ponto)
        if len(ponto) != self.k:
            raise ValueError(f"o ponto {ponto} deveria ter {self.k} coordenadas")
        return ponto

    # ------------------------------------------------------------- construção

    def construir(self, pontos):
        """Monta uma árvore balanceada a partir de uma lista de pontos.

        Em cada nível ordena os pontos pelo eixo da vez e escolhe a MEDIANA
        como nó: metade dos pontos vai para cada lado, então a altura fica
        em torno de log2(n).
        """
        pontos = [self._conferir(p) for p in pontos]
        self.raiz = self._construir(pontos, 0)
        self.tamanho = len(pontos)

    def _construir(self, pontos, profundidade):
        if not pontos:
            return None
        eixo = profundidade % self.k            # alterna x, y, x, y...
        pontos.sort(key=lambda p: p[eixo])
        meio = len(pontos) // 2
        # Se houver pontos empatados com a mediana neste eixo, recua até o
        # primeiro deles: assim todos os iguais ficam à direita, como manda a regra.
        while meio > 0 and pontos[meio - 1][eixo] == pontos[meio][eixo]:
            meio -= 1
        no = No(pontos[meio], eixo)
        no.esq = self._construir(pontos[:meio], profundidade + 1)
        no.dir = self._construir(pontos[meio + 1:], profundidade + 1)
        return no

    # --------------------------------------------------------------- inserção

    def inserir(self, ponto):
        """Insere um ponto descendo a árvore, como numa árvore binária de busca.

        A diferença é que cada nível compara uma coordenada diferente.
        Não há rebalanceamento: muitas inserções em ordem podem deixar a
        árvore desequilibrada (ver README).
        """
        ponto = self._conferir(ponto)
        self.tamanho += 1
        if self.raiz is None:
            self.raiz = No(ponto, 0)
            return
        no = self.raiz
        while True:
            vai_para_esquerda = ponto[no.eixo] < no.ponto[no.eixo]
            filho = no.esq if vai_para_esquerda else no.dir
            if filho is None:
                novo = No(ponto, (no.eixo + 1) % self.k)   # o filho compara o próximo eixo
                if vai_para_esquerda:
                    no.esq = novo
                else:
                    no.dir = novo
                return
            no = filho

    # ------------------------------------------------------------------ busca

    def buscar(self, ponto):
        """Busca exata. Devolve (encontrou?, lista de pontos visitados)."""
        ponto = self._conferir(ponto)
        no, caminho = self.raiz, []
        while no is not None:
            caminho.append(no.ponto)
            if no.ponto == ponto:
                return True, caminho
            # Mesma decisão da inserção: só olha a coordenada do eixo do nó.
            no = no.esq if ponto[no.eixo] < no.ponto[no.eixo] else no.dir
        return False, caminho

    def vizinho_mais_proximo(self, alvo):
        """Ponto da árvore mais próximo do alvo.

        Devolve (ponto, distância, lista de pontos visitados).
        A lista mostra a economia: os ramos podados não aparecem nela.
        """
        alvo = self._conferir(alvo)
        melhor = [None, math.inf]       # [ponto, distância] encontrados até agora
        visitados = []

        def visitar(no):
            if no is None:
                return
            visitados.append(no.ponto)
            d = distancia(no.ponto, alvo)
            if d < melhor[1]:
                melhor[0], melhor[1] = no.ponto, d
            # Distância (com sinal) do alvo até a linha divisória deste nó.
            diferenca = alvo[no.eixo] - no.ponto[no.eixo]
            perto, longe = (no.esq, no.dir) if diferenca < 0 else (no.dir, no.esq)
            # 1) Primeiro o lado onde o alvo está: é o mais promissor.
            visitar(perto)
            # 2) O outro lado só pode ter algo melhor se a linha divisória
            #    estiver mais perto do alvo que o melhor ponto já achado.
            #    Caso contrário, o ramo inteiro é descartado (poda).
            if abs(diferenca) < melhor[1]:
                visitar(longe)

        visitar(self.raiz)
        return melhor[0], melhor[1], visitados

    def busca_por_intervalo(self, minimos, maximos):
        """Todos os pontos dentro da caixa [minimos, maximos] (bordas incluídas)."""
        minimos, maximos = self._conferir(minimos), self._conferir(maximos)
        achados = []

        def visitar(no):
            if no is None:
                return
            if all(minimos[i] <= no.ponto[i] <= maximos[i] for i in range(self.k)):
                achados.append(no.ponto)
            # A esquerda só tem valores MENORES que o do nó neste eixo:
            # só vale a pena descer se a caixa começa antes dele.
            if minimos[no.eixo] < no.ponto[no.eixo]:
                visitar(no.esq)
            # A direita tem valores MAIORES OU IGUAIS: só desce se a caixa chega até lá.
            if maximos[no.eixo] >= no.ponto[no.eixo]:
                visitar(no.dir)

        visitar(self.raiz)
        return achados

    # ---------------------------------------------------------------- remoção

    def _minimo(self, no, eixo):
        """Ponto com a menor coordenada `eixo` na subárvore de `no`."""
        if no is None:
            return None
        if no.eixo == eixo:
            # Este nó divide justamente pelo eixo procurado: o mínimo só pode
            # ser ele mesmo ou estar à esquerda (a direita é toda >= ele).
            candidatos = [no.ponto, self._minimo(no.esq, eixo)]
        else:
            # Este nó divide por outro eixo: o mínimo pode estar em qualquer lado.
            candidatos = [no.ponto, self._minimo(no.esq, eixo), self._minimo(no.dir, eixo)]
        return min((p for p in candidatos if p is not None), key=lambda p: p[eixo])

    def remover(self, ponto):
        """Remove um ponto. Devolve True se ele existia."""
        ponto = self._conferir(ponto)
        if not self.buscar(ponto)[0]:
            return False
        self.raiz = self._remover(self.raiz, ponto)
        self.tamanho -= 1
        return True

    def _remover(self, no, ponto):
        if no.ponto != ponto:
            # Ainda não é o nó: continua descendo pelo mesmo critério da busca.
            if ponto[no.eixo] < no.ponto[no.eixo]:
                no.esq = self._remover(no.esq, ponto)
            else:
                no.dir = self._remover(no.dir, ponto)
            return no

        if no.dir is not None:
            # Tem subárvore direita: o substituto é o ponto de MENOR coordenada
            # (no eixo deste nó) da direita. Tudo que sobra à direita continua
            # sendo >= ele, então a regra da árvore é mantida.
            substituto = self._minimo(no.dir, no.eixo)
            no.ponto = substituto
            no.dir = self._remover(no.dir, substituto)
        elif no.esq is not None:
            # Só tem subárvore esquerda: não dá para usar o "máximo da esquerda"
            # (pontos empatados quebrariam a regra). Em vez disso, pega o MÍNIMO
            # da esquerda e move a subárvore inteira para a direita.
            substituto = self._minimo(no.esq, no.eixo)
            no.ponto = substituto
            no.dir = self._remover(no.esq, substituto)
            no.esq = None
        else:
            # Folha: é só tirar.
            return None
        return no

    # -------------------------------------------------------------- consultas

    def altura(self):
        def rec(no):
            return 0 if no is None else 1 + max(rec(no.esq), rec(no.dir))
        return rec(self.raiz)

    def todos_pontos(self):
        """Lista com todos os pontos (percurso em ordem)."""
        pontos = []

        def rec(no):
            if no is not None:
                rec(no.esq)
                pontos.append(no.ponto)
                rec(no.dir)
        rec(self.raiz)
        return pontos

    def validar(self):
        """Confere a regra da árvore em todos os nós. Lança AssertionError se falhar."""
        def rec(no, profundidade, limites):
            # limites = lista de (eixo, valor, lado) herdada dos ancestrais
            if no is None:
                return 0
            assert no.eixo == profundidade % self.k, f"eixo errado em {no.ponto}"
            for eixo, valor, lado in limites:
                if lado == "esq":
                    assert no.ponto[eixo] < valor, f"{no.ponto} deveria estar à direita"
                else:
                    assert no.ponto[eixo] >= valor, f"{no.ponto} deveria estar à esquerda"
            valor = no.ponto[no.eixo]
            return (1 + rec(no.esq, profundidade + 1, limites + [(no.eixo, valor, "esq")])
                      + rec(no.dir, profundidade + 1, limites + [(no.eixo, valor, "dir")]))

        assert rec(self.raiz, 0, []) == self.tamanho, "tamanho não confere"
        return True

    def texto(self):
        """Árvore em texto: cada linha mostra o ponto e o eixo que o nó compara."""
        nomes = "xyzwvu"
        linhas = []

        def rec(no, prefixo, rotulo):
            if no is None:
                return
            eixo = nomes[no.eixo] if no.eixo < len(nomes) else f"e{no.eixo}"
            linhas.append(f"{prefixo}{rotulo}{no.ponto}  [divide por {eixo}]")
            rec(no.esq, prefixo + "    ", "esq: ")
            rec(no.dir, prefixo + "    ", "dir: ")

        rec(self.raiz, "", "")
        return "\n".join(linhas) if linhas else "(árvore vazia)"
