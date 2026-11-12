"""Árvore 2-3-4 (B-Tree de ordem 4) implementada do zero, sem bibliotecas de árvore.

Regras da árvore 2-3-4:
  - Cada nó tem 1, 2 ou 3 chaves (ou seja, 2, 3 ou 4 filhos).
  - Todas as folhas ficam no mesmo nível (a árvore é sempre balanceada).

Cada chave carrega um valor (o registro que ela identifica), como num índice
de banco de dados: a chave serve para achar, o valor é o dado.

Elementos repetidos: NÃO são permitidos. Inserir uma chave que já existe é
recusado, como uma chave primária de banco de dados.
"""

MAX_CHAVES = 3                  # nó cheio (nó-4): precisa ser dividido antes de receber mais uma
MIN_CHAVES = 1                  # mínimo de chaves de um nó que não é a raiz


class No:
    def __init__(self, folha=True):
        self.chaves = []        # de 1 a 3 chaves, sempre em ordem crescente
        self.valores = []       # valores[i] é o registro da chave chaves[i]
        self.filhos = []        # vazio na folha; senão, len(chaves) + 1 filhos
        self.folha = folha
        # filhos[i] guarda as chaves menores que chaves[i];
        # o último filho guarda as maiores que a última chave.

    def __str__(self):
        """Nó escrito como [chave | chave | chave], usado nas mensagens do registro."""
        return "[" + " | ".join(str(c) for c in self.chaves) + "]"


class Arvore234:
    def __init__(self):
        self.raiz = No(folha=True)
        self.tamanho = 0        # número de chaves
        self.log = []           # mensagens explicando cada passo
        self.ao_mudar = None    # função opcional chamada a cada mensagem

    def _registrar(self, msg):
        """Guarda a mensagem no log e avisa quem estiver ouvindo (a janela, para animar)."""
        self.log.append(msg)
        if self.ao_mudar:
            self.ao_mudar(msg)

    @staticmethod
    def _posicao(no, chave):
        """Índice da primeira chave do nó que não é menor que a procurada."""
        i = 0
        while i < len(no.chaves) and chave > no.chaves[i]:
            i += 1
        return i

    # ------------------------------------------------------------------ busca

    def buscar(self, chave):
        """Devolve (encontrou?, valor, caminho), onde caminho é a lista de nós visitados."""
        no, caminho = self.raiz, []
        while True:
            caminho.append(no)
            i = self._posicao(no, chave)
            if i < len(no.chaves) and chave == no.chaves[i]:
                return True, no.valores[i], caminho
            if no.folha:
                return False, None, caminho     # chegou ao fim sem achar
            no = no.filhos[i]                   # desce pelo filho entre chaves[i-1] e chaves[i]

    # --------------------------------------------------------------- inserção

    def _dividir_filho(self, pai, i):
        """Divide o filho cheio pai.filhos[i] em dois; a chave do meio sobe para o pai.

            pai: [.. P ..]                 pai: [.. P | b ..]
                    |               ->            /     \\
              [a | b | c]                       [a]     [c]
        """
        cheio = pai.filhos[i]
        self._registrar(f"Nó cheio {cheio} dividido: {cheio.chaves[1]} sobe para o pai")
        novo = No(folha=cheio.folha)

        meio_chave, meio_valor = cheio.chaves[1], cheio.valores[1]
        # A maior chave vai para o nó novo; a menor fica no antigo.
        novo.chaves, novo.valores = [cheio.chaves[2]], [cheio.valores[2]]
        cheio.chaves, cheio.valores = [cheio.chaves[0]], [cheio.valores[0]]

        if not cheio.folha:
            # Os 4 filhos são repartidos: 2 para cada metade.
            novo.filhos = cheio.filhos[2:]
            cheio.filhos = cheio.filhos[:2]

        pai.chaves.insert(i, meio_chave)        # a chave do meio sobe
        pai.valores.insert(i, meio_valor)
        pai.filhos.insert(i + 1, novo)          # o nó novo fica logo à direita do antigo

    def inserir(self, chave, valor=None):
        """Insere a chave. Devolve False (e não faz nada) se ela já existir."""
        if self.buscar(chave)[0]:
            self._registrar(f"Chave {chave} já existe: inserção recusada")
            return False

        # Raiz cheia: cria uma raiz nova acima dela e divide a antiga.
        # É o único momento em que a árvore cresce em altura.
        if len(self.raiz.chaves) == MAX_CHAVES:
            self._registrar("Raiz cheia: a árvore cresce um nível para cima")
            nova_raiz = No(folha=False)
            nova_raiz.filhos.append(self.raiz)
            self._dividir_filho(nova_raiz, 0)
            self.raiz = nova_raiz

        # Desce até uma folha, dividindo ANTES de entrar todo nó cheio do
        # caminho. Assim o pai nunca está cheio quando recebe a chave que sobe,
        # e a inserção é resolvida numa única descida.
        no = self.raiz
        while not no.folha:
            i = self._posicao(no, chave)
            if len(no.filhos[i].chaves) == MAX_CHAVES:
                self._dividir_filho(no, i)
                # A chave que subiu ficou em no.chaves[i]: decide em qual das
                # duas metades a chave nova deve entrar.
                if chave > no.chaves[i]:
                    i += 1
            no = no.filhos[i]

        # Na folha (que com certeza tem espaço), insere na posição ordenada.
        i = self._posicao(no, chave)
        no.chaves.insert(i, chave)
        no.valores.insert(i, valor)
        self.tamanho += 1
        self._registrar(f"Inserido {chave} na folha {no}")
        return True

    # --------------------------------------------------------------- exclusão

    def excluir(self, chave):
        """Remove a chave. Devolve False se ela não existir."""
        if not self.buscar(chave)[0]:
            self._registrar(f"Chave {chave} não encontrada")
            return False
        self._excluir(self.raiz, chave)
        self.tamanho -= 1

        # Se a raiz ficou sem chaves (após uma fusão), seu único filho vira a
        # raiz. É o único momento em que a árvore diminui de altura.
        if len(self.raiz.chaves) == 0 and not self.raiz.folha:
            self.raiz = self.raiz.filhos[0]
            self._registrar("Raiz ficou vazia: a árvore diminui um nível")
        return True

    def _excluir(self, no, chave):
        """Remove a chave da subárvore de `no`.

        Garantia: ao entrar aqui, `no` tem pelo menos 2 chaves (ou é a raiz),
        então sempre dá para tirar uma chave dele sem violar o mínimo.
        """
        i = self._posicao(no, chave)

        if i < len(no.chaves) and no.chaves[i] == chave:
            # ---- A chave está neste nó ----
            if no.folha:
                # Caso 1: folha, só remove.
                no.chaves.pop(i)
                no.valores.pop(i)
                self._registrar(f"Removido {chave} da folha")
            elif len(no.filhos[i].chaves) > MIN_CHAVES:
                # Caso 2a: o filho à esquerda tem chave sobrando. Troca pela
                # antecessora (maior chave da esquerda) e remove ela lá embaixo.
                ant_chave, ant_valor = self._maior(no.filhos[i])
                self._registrar(f"{chave} está em nó interno: substituída pela antecessora {ant_chave}")
                no.chaves[i], no.valores[i] = ant_chave, ant_valor
                self._excluir(no.filhos[i], ant_chave)
            elif len(no.filhos[i + 1].chaves) > MIN_CHAVES:
                # Caso 2b: idem com o filho à direita e a sucessora.
                suc_chave, suc_valor = self._menor(no.filhos[i + 1])
                self._registrar(f"{chave} está em nó interno: substituída pela sucessora {suc_chave}")
                no.chaves[i], no.valores[i] = suc_chave, suc_valor
                self._excluir(no.filhos[i + 1], suc_chave)
            else:
                # Caso 2c: os dois filhos têm só 1 chave. Funde os dois com a
                # chave no meio (ela desce) e continua a remoção no nó fundido.
                self._registrar(f"{chave} está em nó interno e os dois filhos vizinhos têm só 1 chave")
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
        """(chave, valor) da maior chave da subárvore: sempre pelo último filho."""
        while not no.folha:
            no = no.filhos[-1]
        return no.chaves[-1], no.valores[-1]

    def _menor(self, no):
        """(chave, valor) da menor chave da subárvore: sempre pelo primeiro filho."""
        while not no.folha:
            no = no.filhos[0]
        return no.chaves[0], no.valores[0]

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
        self._registrar(f"Nó {filho} tem só 1 chave: empresta do irmão esquerdo {irmao} "
                        f"({pai.chaves[i - 1]} desce do pai, {irmao.chaves[-1]} sobe)")
        filho.chaves.insert(0, pai.chaves[i - 1])
        filho.valores.insert(0, pai.valores[i - 1])
        pai.chaves[i - 1] = irmao.chaves.pop()
        pai.valores[i - 1] = irmao.valores.pop()
        if not irmao.folha:
            # O último filho do irmão acompanha a chave que mudou de lado.
            filho.filhos.insert(0, irmao.filhos.pop())

    def _emprestar_direita(self, pai, i):
        """Rotação: a chave do pai desce para o filho e a menor do irmão direito sobe."""
        filho, irmao = pai.filhos[i], pai.filhos[i + 1]
        self._registrar(f"Nó {filho} tem só 1 chave: empresta do irmão direito {irmao} "
                        f"({pai.chaves[i]} desce do pai, {irmao.chaves[0]} sobe)")
        filho.chaves.append(pai.chaves[i])
        filho.valores.append(pai.valores[i])
        pai.chaves[i] = irmao.chaves.pop(0)
        pai.valores[i] = irmao.valores.pop(0)
        if not irmao.folha:
            filho.filhos.append(irmao.filhos.pop(0))

    def _fundir(self, pai, i):
        """Junta filhos[i], a chave pai.chaves[i] e filhos[i + 1] num nó só (com 3 chaves)."""
        esq, dir_ = pai.filhos[i], pai.filhos[i + 1]
        self._registrar(f"Fusão: {esq} + {pai.chaves[i]} (desce do pai) + {dir_}")
        esq.chaves.append(pai.chaves.pop(i))        # a chave do pai desce
        esq.valores.append(pai.valores.pop(i))
        esq.chaves.extend(dir_.chaves)
        esq.valores.extend(dir_.valores)
        esq.filhos.extend(dir_.filhos)
        pai.filhos.pop(i + 1)                       # o nó da direita deixa de existir

    # -------------------------------------------------------------- consultas

    def altura(self):
        """Número de níveis. Basta descer por um lado: todas as folhas estão no mesmo nível."""
        if not self.raiz.chaves:
            return 0
        h, no = 1, self.raiz
        while not no.folha:
            no = no.filhos[0]
            h += 1
        return h

    def em_ordem(self):
        """Lista de (chave, valor) em ordem crescente de chave."""
        resultado = []

        def rec(no):
            # Intercala: filho 0, chave 0, filho 1, chave 1, ..., último filho.
            for i in range(len(no.chaves)):
                if not no.folha:
                    rec(no.filhos[i])
                resultado.append((no.chaves[i], no.valores[i]))
            if not no.folha:
                rec(no.filhos[-1])
        rec(self.raiz)
        return resultado

    def validar(self):
        """Confere as regras da árvore 2-3-4. Devolve (ok, mensagem)."""
        niveis_folhas = set()

        def rec(no, nivel, eh_raiz):
            """Confere um nó e desce para os filhos, anotando em que nível cada folha está."""
            assert no.chaves == sorted(no.chaves), "chaves fora de ordem"
            assert len(no.chaves) == len(no.valores), "chaves e valores desalinhados"
            assert len(no.chaves) <= MAX_CHAVES, "nó com mais de 3 chaves"
            if not eh_raiz:
                assert len(no.chaves) >= MIN_CHAVES, "nó sem chaves"
            if no.folha:
                niveis_folhas.add(nivel)
            else:
                assert len(no.filhos) == len(no.chaves) + 1, "filhos != chaves + 1"
                for f in no.filhos:
                    rec(f, nivel + 1, False)

        try:
            rec(self.raiz, 0, True)
            assert len(niveis_folhas) == 1, "folhas em níveis diferentes"
            # A ordem entre nós diferentes aparece no percurso em ordem.
            chaves = [c for c, _ in self.em_ordem()]
            assert chaves == sorted(chaves), "percurso em ordem não está crescente"
            assert len(chaves) == self.tamanho, "tamanho não confere"
        except AssertionError as erro:
            return False, str(erro)
        return True, f"todas as folhas no nível {self.altura()}"

    def texto(self):
        """Árvore em texto, um nó por linha, recuado pelo nível."""
        linhas = []

        def rec(no, nivel):
            """Acrescenta a linha deste nó e, mais recuadas, as dos filhos."""
            linhas.append("    " * nivel + str(no))
            for f in no.filhos:
                rec(f, nivel + 1)

        if not self.raiz.chaves:
            return "(árvore vazia)"
        rec(self.raiz, 0)
        return "\n".join(linhas)
