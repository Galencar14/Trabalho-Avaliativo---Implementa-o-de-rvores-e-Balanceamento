"""Árvore k-D (k-dimensional) implementada do zero, sem bibliotecas de árvore.

Uma árvore k-D é uma árvore binária de busca para pontos com k coordenadas.
Em cada nível ela compara UMA coordenada só, alternando entre elas:
  nível 0 -> coordenada 0, nível 1 -> coordenada 1, nível 2 -> coordenada 0 de novo...

Regra de cada nó (o "eixo" do nó é a coordenada que ele compara):
  - subárvore esquerda: pontos com coordenada MENOR que a do nó naquele eixo;
  - subárvore direita:  pontos com coordenada MAIOR OU IGUAL.

Cada ponto carrega um valor (o dado que está naquela posição).

Elementos repetidos: são permitidos. Um ponto igual a outro (ou só com a mesma
coordenada no eixo) vai sempre para a direita, por causa do "maior ou igual".
"""

import math


class No:
    def __init__(self, ponto, valor, eixo):
        self.ponto = ponto      # tupla com as k coordenadas
        self.valor = valor      # dado associado ao ponto
        self.eixo = eixo        # coordenada comparada neste nó (0, 1, ...)
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

    def construir(self, itens):
        """Monta uma árvore balanceada a partir de uma lista de (ponto, valor).

        Em cada nível ordena os pontos pelo eixo da vez e escolhe a MEDIANA
        como nó: metade dos pontos vai para cada lado, então a altura fica
        em torno de log2(n).
        """
        itens = [(self._conferir(p), v) for p, v in itens]
        self.raiz = self._construir(itens, 0)
        self.tamanho = len(itens)

    def _construir(self, itens, profundidade):
        if not itens:
            return None
        eixo = profundidade % self.k            # alterna os eixos a cada nível
        itens.sort(key=lambda item: item[0][eixo])
        meio = len(itens) // 2
        # Se houver pontos empatados com a mediana neste eixo, recua até o
        # primeiro deles: assim todos os iguais ficam à direita, como manda a regra.
        while meio > 0 and itens[meio - 1][0][eixo] == itens[meio][0][eixo]:
            meio -= 1
        no = No(itens[meio][0], itens[meio][1], eixo)
        no.esq = self._construir(itens[:meio], profundidade + 1)
        no.dir = self._construir(itens[meio + 1:], profundidade + 1)
        return no

    def reconstruir(self):
        """Rebalanceia a árvore: junta todos os pontos e constrói de novo pela mediana."""
        self.construir([(no.ponto, no.valor) for no in self.em_ordem()])

    # --------------------------------------------------------------- inserção

    def inserir(self, ponto, valor=None):
        """Insere um ponto descendo a árvore, como numa árvore binária de busca.

        A diferença é que cada nível compara uma coordenada diferente.
        Não há rebalanceamento: muitas inserções podem deixar a árvore
        desequilibrada, e aí o remédio é chamar reconstruir().
        Devolve a lista de nós visitados até o lugar da inserção.
        """
        ponto = self._conferir(ponto)
        self.tamanho += 1
        if self.raiz is None:
            self.raiz = No(ponto, valor, 0)
            return []
        no, caminho = self.raiz, []
        while True:
            caminho.append(no)
            vai_para_esquerda = ponto[no.eixo] < no.ponto[no.eixo]
            filho = no.esq if vai_para_esquerda else no.dir
            if filho is None:
                novo = No(ponto, valor, (no.eixo + 1) % self.k)    # o filho compara o próximo eixo
                if vai_para_esquerda:
                    no.esq = novo
                else:
                    no.dir = novo
                return caminho
            no = filho

    # ------------------------------------------------------------------ busca

    def buscar(self, ponto, valor=None):
        """Busca exata. Devolve (nó ou None, lista de nós visitados).

        Com pontos repetidos, `valor` escolhe qual das cópias se quer: a busca
        segue para a direita (onde ficam os iguais) até achar a cópia certa.
        """
        ponto = self._conferir(ponto)
        no, caminho = self.raiz, []
        while no is not None:
            caminho.append(no)
            if no.ponto == ponto and (valor is None or no.valor is valor):
                return no, caminho
            # Mesma decisão da inserção: só olha a coordenada do eixo do nó.
            no = no.esq if ponto[no.eixo] < no.ponto[no.eixo] else no.dir
        return None, caminho

    def vizinho_mais_proximo(self, alvo):
        """Nó da árvore mais próximo do alvo.

        Devolve (nó, distância, nós visitados, nós onde houve poda).
        Os ramos podados não aparecem em "visitados": essa é a economia.
        """
        alvo = self._conferir(alvo)
        melhor = [None, math.inf]       # [nó, distância] encontrados até agora
        visitados, podas = [], []

        def visitar(no):
            if no is None:
                return
            visitados.append(no)
            d = distancia(no.ponto, alvo)
            if d < melhor[1]:
                melhor[0], melhor[1] = no, d
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
            elif longe is not None:
                podas.append(no)

        visitar(self.raiz)
        return melhor[0], melhor[1], visitados, podas

    def busca_por_intervalo(self, minimos, maximos):
        """Nós dentro da caixa [minimos, maximos] (bordas incluídas).

        Devolve (nós encontrados, nós visitados).
        """
        minimos, maximos = self._conferir(minimos), self._conferir(maximos)
        achados, visitados = [], []

        def visitar(no):
            if no is None:
                return
            visitados.append(no)
            if all(minimos[i] <= no.ponto[i] <= maximos[i] for i in range(self.k)):
                achados.append(no)
            # A esquerda só tem valores MENORES que o do nó neste eixo:
            # só vale a pena descer se a caixa começa antes dele.
            if minimos[no.eixo] < no.ponto[no.eixo]:
                visitar(no.esq)
            # A direita tem valores MAIORES OU IGUAIS: só desce se a caixa chega até lá.
            if maximos[no.eixo] >= no.ponto[no.eixo]:
                visitar(no.dir)

        visitar(self.raiz)
        return achados, visitados

    def busca_por_raio(self, centro, raio):
        """Nós a no máximo `raio` de distância do centro.

        Devolve (nós encontrados, nós visitados). A poda é a mesma do vizinho
        mais próximo: se a linha divisória está a mais de `raio` do centro,
        nada do outro lado pode estar dentro do círculo.
        """
        centro = self._conferir(centro)
        achados, visitados = [], []

        def visitar(no):
            if no is None:
                return
            visitados.append(no)
            if distancia(no.ponto, centro) <= raio:
                achados.append(no)
            diferenca = centro[no.eixo] - no.ponto[no.eixo]
            # A esquerda só interessa se o círculo passa para antes da linha...
            if diferenca - raio < 0:
                visitar(no.esq)
            # ...e a direita, se ele chega até a linha ou passa dela.
            if diferenca + raio >= 0:
                visitar(no.dir)

        visitar(self.raiz)
        return achados, visitados

    # ---------------------------------------------------------------- remoção

    def _minimo(self, no, eixo):
        """Nó com a menor coordenada `eixo` na subárvore de `no`."""
        if no is None:
            return None
        if no.eixo == eixo:
            # Este nó divide justamente pelo eixo procurado: o mínimo só pode
            # ser ele mesmo ou estar à esquerda (a direita é toda >= ele).
            candidatos = [no, self._minimo(no.esq, eixo)]
        else:
            # Este nó divide por outro eixo: o mínimo pode estar em qualquer lado.
            candidatos = [no, self._minimo(no.esq, eixo), self._minimo(no.dir, eixo)]
        return min((c for c in candidatos if c is not None), key=lambda c: c.ponto[eixo])

    def remover(self, ponto, valor=None):
        """Remove um ponto (uma cópia, se houver repetidos). Devolve o valor removido ou None.

        `valor` escolhe qual cópia remover quando há pontos repetidos.
        """
        alvo, _ = self.buscar(ponto, valor)
        if alvo is None:
            return None
        valor = alvo.valor
        self.raiz = self._remover(self.raiz, alvo)
        self.tamanho -= 1
        return valor

    def _remover(self, no, alvo):
        """Remove o nó `alvo` (comparado por identidade) da subárvore de `no`."""
        if no is not alvo:
            # Ainda não é o nó: continua descendo pelo mesmo critério da busca.
            if alvo.ponto[no.eixo] < no.ponto[no.eixo]:
                no.esq = self._remover(no.esq, alvo)
            else:
                no.dir = self._remover(no.dir, alvo)
            return no

        if no.dir is not None:
            # Tem subárvore direita: o substituto é o nó de MENOR coordenada
            # (no eixo deste nó) da direita. Tudo que sobra à direita continua
            # sendo >= ele, então a regra da árvore é mantida.
            substituto = self._minimo(no.dir, no.eixo)
            no.ponto, no.valor = substituto.ponto, substituto.valor
            no.dir = self._remover(no.dir, substituto)
        elif no.esq is not None:
            # Só tem subárvore esquerda: não dá para usar o "máximo da esquerda"
            # (pontos empatados quebrariam a regra). Em vez disso, pega o MÍNIMO
            # da esquerda e move a subárvore inteira para a direita.
            substituto = self._minimo(no.esq, no.eixo)
            no.ponto, no.valor = substituto.ponto, substituto.valor
            no.dir = self._remover(no.esq, substituto)
            no.esq = None
        else:
            # Folha: é só tirar.
            return None
        return no

    # -------------------------------------------------------------- consultas

    def altura(self):
        """Número de níveis da árvore (0 se estiver vazia)."""
        def rec(no):
            """Altura da subárvore de `no`."""
            return 0 if no is None else 1 + max(rec(no.esq), rec(no.dir))
        return rec(self.raiz)

    def em_ordem(self):
        """Lista com todos os nós (percurso em ordem)."""
        nos = []

        def rec(no):
            """Percurso em ordem: esquerda, o próprio nó, direita."""
            if no is not None:
                rec(no.esq)
                nos.append(no)
                rec(no.dir)
        rec(self.raiz)
        return nos

    def validar(self):
        """Confere a regra da árvore em todos os nós. Devolve (ok, mensagem)."""
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

        try:
            assert rec(self.raiz, 0, []) == self.tamanho, "tamanho não confere"
        except AssertionError as erro:
            return False, str(erro)
        return True, "todo nó respeita os cortes dos ancestrais"
