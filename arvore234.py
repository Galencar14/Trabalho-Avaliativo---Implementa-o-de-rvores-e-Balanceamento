"""
Árvore 2-3-4 (B-Tree de grau mínimo 2) implementada do zero, sem bibliotecas de árvore.

Regras da árvore 2-3-4:
  - Cada nó tem 1, 2 ou 3 chaves (ou seja, 2, 3 ou 4 filhos).
  - Todas as folhas ficam no mesmo nível (a árvore é sempre balanceada).

Tratamento de elementos repetidos: NÃO são permitidos.
  Se tentar inserir uma chave que já existe, ela é ignorada.
"""

import matplotlib
matplotlib.use("Agg")           # desenha direto em arquivo, sem abrir janela
import matplotlib.pyplot as plt


MAX_CHAVES = 3                  # nó cheio (nó-4): precisa ser dividido antes de receber mais uma
MIN_CHAVES = 1                  # mínimo de chaves de um nó que não é a raiz


class No:
    def __init__(self, folha=True):
        self.chaves = []        # de 1 a 3 chaves, sempre em ordem crescente
        self.filhos = []        # vazio na folha; senão, len(chaves) + 1 filhos
        self.folha = folha
        # filhos[i] guarda as chaves menores que chaves[i];
        # o último filho guarda as maiores que a última chave.


class Arvore234:
    def __init__(self):
        self.raiz = No(folha=True)

    # ------------------------------------------------------------------ busca

    def buscar(self, chave):
        """Devolve True se a chave está na árvore."""
        no = self.raiz
        while True:
            # Acha a primeira chave do nó que não é menor que a procurada.
            i = 0
            while i < len(no.chaves) and chave > no.chaves[i]:
                i += 1
            if i < len(no.chaves) and chave == no.chaves[i]:
                return True
            if no.folha:
                return False            # chegou ao fim sem achar
            no = no.filhos[i]           # desce pelo filho entre chaves[i-1] e chaves[i]

    # --------------------------------------------------------------- inserção

    def _dividir_filho(self, pai, i):
        """Divide o filho cheio pai.filhos[i] em dois; a chave do meio sobe para o pai.

            pai: [.. P ..]                 pai: [.. P  b ..]   (ou b antes de P)
                    |               ->            /    \\
              [a | b | c]                       [a]    [c]
        """
        cheio = pai.filhos[i]
        novo = No(folha=cheio.folha)

        meio = cheio.chaves[1]
        novo.chaves = [cheio.chaves[2]]     # a maior chave vai para o nó novo
        cheio.chaves = [cheio.chaves[0]]    # a menor fica no nó antigo

        if not cheio.folha:
            # Os 4 filhos são repartidos: 2 para cada metade.
            novo.filhos = cheio.filhos[2:]
            cheio.filhos = cheio.filhos[:2]

        pai.chaves.insert(i, meio)          # a chave do meio sobe
        pai.filhos.insert(i + 1, novo)      # o nó novo fica logo à direita do antigo

    def inserir(self, chave):
        """Insere a chave. Devolve False (e não faz nada) se ela já existir."""
        if self.buscar(chave):
            return False

        # Raiz cheia: cria uma raiz nova acima dela e divide a antiga.
        # É o único momento em que a árvore cresce em altura.
        if len(self.raiz.chaves) == MAX_CHAVES:
            nova_raiz = No(folha=False)
            nova_raiz.filhos.append(self.raiz)
            self._dividir_filho(nova_raiz, 0)
            self.raiz = nova_raiz

        # Desce até uma folha, dividindo ANTES de entrar todo nó cheio do
        # caminho. Assim o pai nunca está cheio quando recebe a chave que sobe,
        # e a inserção é resolvida numa única descida.
        no = self.raiz
        while not no.folha:
            i = 0
            while i < len(no.chaves) and chave > no.chaves[i]:
                i += 1
            if len(no.filhos[i].chaves) == MAX_CHAVES:
                self._dividir_filho(no, i)
                # A chave que subiu ficou em no.chaves[i]: decide em qual das
                # duas metades a chave nova deve entrar.
                if chave > no.chaves[i]:
                    i += 1
            no = no.filhos[i]

        # Na folha (que com certeza tem espaço), insere na posição ordenada.
        i = 0
        while i < len(no.chaves) and chave > no.chaves[i]:
            i += 1
        no.chaves.insert(i, chave)
        return True

    # --------------------------------------------------------------- exclusão

    def excluir(self, chave):
        """Remove a chave. Devolve False se ela não existir."""
        if not self.buscar(chave):
            return False
        self._excluir(self.raiz, chave)

        # Se a raiz ficou sem chaves (após uma fusão), seu único filho vira a
        # raiz. É o único momento em que a árvore diminui de altura.
        if len(self.raiz.chaves) == 0 and not self.raiz.folha:
            self.raiz = self.raiz.filhos[0]
        return True

    def _excluir(self, no, chave):
        """Remove a chave da subárvore de `no`.

        Garantia: ao entrar aqui, `no` tem pelo menos 2 chaves (ou é a raiz),
        então sempre dá para tirar uma chave dele sem violar o mínimo.
        """
        i = 0
        while i < len(no.chaves) and chave > no.chaves[i]:
            i += 1

        if i < len(no.chaves) and no.chaves[i] == chave:
            # ---- A chave está neste nó ----
            if no.folha:
                no.chaves.pop(i)                        # caso 1: folha, só remove
            elif len(no.filhos[i].chaves) > MIN_CHAVES:
                # Caso 2a: o filho à esquerda tem chave sobrando. Troca pela
                # antecessora (maior chave da esquerda) e remove ela lá embaixo.
                pred = self._maior(no.filhos[i])
                no.chaves[i] = pred
                self._excluir(no.filhos[i], pred)
            elif len(no.filhos[i + 1].chaves) > MIN_CHAVES:
                # Caso 2b: idem com o filho à direita e a sucessora.
                suc = self._menor(no.filhos[i + 1])
                no.chaves[i] = suc
                self._excluir(no.filhos[i + 1], suc)
            else:
                # Caso 2c: os dois filhos têm só 1 chave. Funde os dois com a
                # chave no meio (ela desce) e continua a remoção no nó fundido.
                self._fundir(no, i)
                self._excluir(no.filhos[i], chave)
        else:
            # ---- A chave está mais abaixo, no filho i ----
            if no.folha:
                return
            era_ultimo = (i == len(no.chaves))
            # Caso 3: antes de descer, garante que o filho tem pelo menos 2 chaves.
            if len(no.filhos[i].chaves) == MIN_CHAVES:
                self._garantir_chaves(no, i)
            # Se o filho era o último e foi fundido com o irmão da esquerda,
            # o nó fundido passou a ser o filho i - 1.
            if era_ultimo and i > len(no.chaves):
                self._excluir(no.filhos[i - 1], chave)
            else:
                self._excluir(no.filhos[i], chave)

    def _maior(self, no):
        """Maior chave da subárvore: sempre pelo último filho."""
        while not no.folha:
            no = no.filhos[-1]
        return no.chaves[-1]

    def _menor(self, no):
        """Menor chave da subárvore: sempre pelo primeiro filho."""
        while not no.folha:
            no = no.filhos[0]
        return no.chaves[0]

    def _garantir_chaves(self, pai, i):
        """Faz o filho i (que tem só 1 chave) ficar com pelo menos 2."""
        if i > 0 and len(pai.filhos[i - 1].chaves) > MIN_CHAVES:
            self._emprestar_esquerda(pai, i)        # irmão esquerdo tem sobrando
        elif i < len(pai.chaves) and len(pai.filhos[i + 1].chaves) > MIN_CHAVES:
            self._emprestar_direita(pai, i)         # irmão direito tem sobrando
        elif i < len(pai.chaves):
            self._fundir(pai, i)                    # funde com o irmão direito
        else:
            self._fundir(pai, i - 1)                # é o último: funde com o esquerdo

    def _emprestar_esquerda(self, pai, i):
        """Rotação: a chave do pai desce para o filho e a maior do irmão esquerdo sobe."""
        filho, irmao = pai.filhos[i], pai.filhos[i - 1]
        filho.chaves.insert(0, pai.chaves[i - 1])
        pai.chaves[i - 1] = irmao.chaves.pop()
        if not irmao.folha:
            # O último filho do irmão acompanha a chave que mudou de lado.
            filho.filhos.insert(0, irmao.filhos.pop())

    def _emprestar_direita(self, pai, i):
        """Rotação: a chave do pai desce para o filho e a menor do irmão direito sobe."""
        filho, irmao = pai.filhos[i], pai.filhos[i + 1]
        filho.chaves.append(pai.chaves[i])
        pai.chaves[i] = irmao.chaves.pop(0)
        if not irmao.folha:
            filho.filhos.append(irmao.filhos.pop(0))

    def _fundir(self, pai, i):
        """Junta filhos[i], a chave pai.chaves[i] e filhos[i + 1] num nó só (com 3 chaves)."""
        esq, dir_ = pai.filhos[i], pai.filhos[i + 1]
        esq.chaves.append(pai.chaves.pop(i))        # a chave do pai desce
        esq.chaves.extend(dir_.chaves)
        esq.filhos.extend(dir_.filhos)
        pai.filhos.pop(i + 1)                       # o nó da direita deixa de existir

    # -------------------------------------------------------------- consultas

    def imprimir(self):
        """Mostra a árvore no terminal, um nó por linha, recuado pelo nível."""
        def rec(no, nivel):
            print("    " * nivel + str(no.chaves))
            for f in no.filhos:
                rec(f, nivel + 1)
        rec(self.raiz, 0)

    def altura(self):
        """Número de níveis. Basta descer por um lado: todas as folhas estão no mesmo nível."""
        h, no = 1, self.raiz
        while not no.folha:
            no = no.filhos[0]
            h += 1
        return h

    def todas_chaves(self):
        """Lista de todas as chaves em ordem crescente (percurso em ordem)."""
        resultado = []

        def rec(no):
            # Intercala: filho 0, chave 0, filho 1, chave 1, ..., último filho.
            for i, c in enumerate(no.chaves):
                if not no.folha:
                    rec(no.filhos[i])
                resultado.append(c)
            if not no.folha:
                rec(no.filhos[-1])
        rec(self.raiz)
        return resultado

    def validar(self):
        """Confere as regras da árvore 2-3-4. Lança AssertionError se alguma falhar."""
        niveis_folhas = set()

        def rec(no, nivel, eh_raiz):
            assert no.chaves == sorted(no.chaves), "chaves fora de ordem"
            assert len(no.chaves) <= MAX_CHAVES, "nó com mais de 3 chaves"
            if not eh_raiz:
                assert len(no.chaves) >= MIN_CHAVES, "nó sem chaves"
            if no.folha:
                niveis_folhas.add(nivel)
            else:
                assert len(no.filhos) == len(no.chaves) + 1, "filhos != chaves + 1"
                for f in no.filhos:
                    rec(f, nivel + 1, False)
        rec(self.raiz, 0, True)
        assert len(niveis_folhas) == 1, "folhas em níveis diferentes"
        # A ordem entre nós diferentes aparece no percurso em ordem.
        chaves = self.todas_chaves()
        assert chaves == sorted(chaves), "percurso em ordem não está crescente"
        return True

    # --------------------------------------------------------------- plotagem

    def plotar(self, titulo="Árvore 2-3-4", arquivo="arvore.png"):
        """Salva um PNG da árvore: cada nó é uma caixa com as chaves separadas por |."""
        posicoes = {}           # id(nó) -> (x, y)
        proximo_x = [0]         # próxima posição livre para uma folha

        def calcular(no, nivel):
            if no.folha:
                # Folhas são colocadas lado a lado, com largura proporcional às chaves.
                x = proximo_x[0]
                proximo_x[0] += len(no.chaves) + 1
            else:
                # Nó interno fica centralizado sobre os filhos.
                xs = [calcular(f, nivel + 1) for f in no.filhos]
                x = sum(xs) / len(xs)
            posicoes[id(no)] = (x, -nivel)
            return x

        calcular(self.raiz, 0)

        fig, ax = plt.subplots(figsize=(max(8, proximo_x[0] * 0.55), 2 + self.altura() * 1.3))

        def desenhar(no):
            x, y = posicoes[id(no)]
            for f in no.filhos:
                fx, fy = posicoes[id(f)]
                ax.plot([x, fx], [y - 0.12, fy + 0.12], color="gray", zorder=1)
                desenhar(f)
            largura = 0.6 * len(no.chaves) + 0.3
            ax.add_patch(plt.Rectangle((x - largura / 2, y - 0.12), largura, 0.24,
                                       facecolor="#cfe8ff", edgecolor="black", zorder=2))
            ax.text(x, y, " | ".join(str(c) for c in no.chaves),
                    ha="center", va="center", fontsize=9, zorder=3)

        desenhar(self.raiz)
        ax.set_title(titulo)
        ax.set_xlim(-1, proximo_x[0])
        ax.set_ylim(-self.altura() + 0.5, 0.6)
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(arquivo, dpi=130)
        plt.close(fig)                  # libera a memória da figura
