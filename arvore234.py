"""
Árvore 2-3-4 (B-Tree de grau mínimo 2) implementada do zero, sem bibliotecas de árvore.

Regras da árvore 2-3-4:
  - Cada nó tem 1, 2 ou 3 chaves (ou seja, 2, 3 ou 4 filhos).
  - Todas as folhas ficam no mesmo nível (a árvore é sempre balanceada).

Tratamento de elementos repetidos: NÃO são permitidos.
  Se tentar inserir uma chave que já existe, ela é ignorada.
"""

import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt


MAX_CHAVES = 3  
MIN_CHAVES = 1  

class No:
    def __init__(self, folha=True):
        self.chaves = []    
        self.filhos = []    
        self.folha = folha


class Arvore234:
    def __init__(self):
        self.raiz = No(folha=True)

    def buscar(self, chave):
        no = self.raiz
        while True:
            i = 0
            while i < len(no.chaves) and chave > no.chaves[i]:
                i += 1
            if i < len(no.chaves) and chave == no.chaves[i]:
                return True
            if no.folha:
                return False
            no = no.filhos[i]

    def _dividir_filho(self, pai, i):
        cheio = pai.filhos[i]
        novo = No(folha=cheio.folha)

        meio = cheio.chaves[1]
        novo.chaves = [cheio.chaves[2]]
        cheio.chaves = [cheio.chaves[0]]

        if not cheio.folha:
            novo.filhos = cheio.filhos[2:]
            cheio.filhos = cheio.filhos[:2]

        pai.chaves.insert(i, meio)
        pai.filhos.insert(i + 1, novo)

    def inserir(self, chave):
        if self.buscar(chave):
            return False  

        if len(self.raiz.chaves) == MAX_CHAVES:
            nova_raiz = No(folha=False)
            nova_raiz.filhos.append(self.raiz)
            self._dividir_filho(nova_raiz, 0)
            self.raiz = nova_raiz

        no = self.raiz
        while not no.folha:
            i = 0
            while i < len(no.chaves) and chave > no.chaves[i]:
                i += 1
            if len(no.filhos[i].chaves) == MAX_CHAVES:
                self._dividir_filho(no, i)
                if chave > no.chaves[i]:
                    i += 1
            no = no.filhos[i]

        i = 0
        while i < len(no.chaves) and chave > no.chaves[i]:
            i += 1
        no.chaves.insert(i, chave)
        return True

    def excluir(self, chave):
        if not self.buscar(chave):
            return False
        self._excluir(self.raiz, chave)
        
        if len(self.raiz.chaves) == 0 and not self.raiz.folha:
            self.raiz = self.raiz.filhos[0]
        return True

    def _excluir(self, no, chave):
        i = 0
        while i < len(no.chaves) and chave > no.chaves[i]:
            i += 1

        if i < len(no.chaves) and no.chaves[i] == chave:
            if no.folha:
                no.chaves.pop(i)  
            elif len(no.filhos[i].chaves) > MIN_CHAVES:
                pred = self._maior(no.filhos[i])
                no.chaves[i] = pred
                self._excluir(no.filhos[i], pred)
            elif len(no.filhos[i + 1].chaves) > MIN_CHAVES:
                suc = self._menor(no.filhos[i + 1])
                no.chaves[i] = suc
                self._excluir(no.filhos[i + 1], suc)
            else:
                self._fundir(no, i)
                self._excluir(no.filhos[i], chave)
        else:
            if no.folha:
                return
            era_ultimo = (i == len(no.chaves))
            if len(no.filhos[i].chaves) == MIN_CHAVES:
                self._garantir_chaves(no, i)
            if era_ultimo and i > len(no.chaves):
                self._excluir(no.filhos[i - 1], chave)
            else:
                self._excluir(no.filhos[i], chave)

    def _maior(self, no):
        while not no.folha:
            no = no.filhos[-1]
        return no.chaves[-1]

    def _menor(self, no):
        while not no.folha:
            no = no.filhos[0]
        return no.chaves[0]

    def _garantir_chaves(self, pai, i):
        if i > 0 and len(pai.filhos[i - 1].chaves) > MIN_CHAVES:
            self._emprestar_esquerda(pai, i)
        elif i < len(pai.chaves) and len(pai.filhos[i + 1].chaves) > MIN_CHAVES:
            self._emprestar_direita(pai, i)
        elif i < len(pai.chaves):
            self._fundir(pai, i)
        else:
            self._fundir(pai, i - 1)

    def _emprestar_esquerda(self, pai, i):
        filho, irmao = pai.filhos[i], pai.filhos[i - 1]
        filho.chaves.insert(0, pai.chaves[i - 1])
        pai.chaves[i - 1] = irmao.chaves.pop()
        if not irmao.folha:
            filho.filhos.insert(0, irmao.filhos.pop())

    def _emprestar_direita(self, pai, i):
        filho, irmao = pai.filhos[i], pai.filhos[i + 1]
        filho.chaves.append(pai.chaves[i])
        pai.chaves[i] = irmao.chaves.pop(0)
        if not irmao.folha:
            filho.filhos.append(irmao.filhos.pop(0))

    def _fundir(self, pai, i):
        esq, dir_ = pai.filhos[i], pai.filhos[i + 1]
        esq.chaves.append(pai.chaves.pop(i))
        esq.chaves.extend(dir_.chaves)
        esq.filhos.extend(dir_.filhos)
        pai.filhos.pop(i + 1)

    def imprimir(self):
        def rec(no, nivel):
            print("    " * nivel + str(no.chaves))
            for f in no.filhos:
                rec(f, nivel + 1)
        rec(self.raiz, 0)

    def altura(self):
        h, no = 1, self.raiz
        while not no.folha:
            no = no.filhos[0]
            h += 1
        return h

    def todas_chaves(self):
        resultado = []

        def rec(no):
            for i, c in enumerate(no.chaves):
                if not no.folha:
                    rec(no.filhos[i])
                resultado.append(c)
            if not no.folha:
                rec(no.filhos[-1])
        rec(self.raiz)
        return resultado

    def validar(self):
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
        return True

    def plotar(self, titulo="Árvore 2-3-4", arquivo="arvore.png"):
        posicoes = {}      
        proximo_x = [0]    

        def calcular(no, nivel):
            if no.folha:
                x = proximo_x[0]
                proximo_x[0] += len(no.chaves) + 1
            else:
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
        plt.close(fig)
