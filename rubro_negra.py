"""Árvore Rubro-Negra implementada do zero.

Propriedades que a árvore mantém após cada operação:
  1. Todo nó é vermelho ou preto.
  2. A raiz é preta.
  3. Toda folha (NIL) é preta.
  4. Um nó vermelho não tem filho vermelho.
  5. Todo caminho de um nó até as folhas abaixo dele tem o mesmo número
     de nós pretos ("altura negra").
Essas regras garantem altura no máximo 2*log2(n+1), então busca, inserção
e remoção custam O(log n).
"""

# Cores representadas por letras (aparecem também na saída em texto).
VERMELHO, PRETO = "V", "P"


class No:
    """Nó da árvore: guarda a chave, o valor e os ponteiros para filhos e pai."""

    def __init__(self, chave, valor=None, cor=VERMELHO, nil=None):
        self.chave = chave          # código do produto (usado para ordenar)
        self.valor = valor          # nome do produto (opcional)
        self.quantidade = 1         # quantas unidades dessa chave existem
        self.cor = cor              # todo nó novo nasce vermelho
        self.esq = nil              # filho esquerdo (aponta para o NIL se não houver)
        self.dir = nil              # filho direito
        self.pai = nil              # pai (o NIL, se o nó for a raiz)


class ArvoreRubroNegra:
    def __init__(self):
        # Sentinela NIL: um único nó preto que faz o papel de todas as folhas
        # vazias. Assim nunca precisamos testar "is None" nas correções.
        self.NIL = No(None, cor=PRETO)
        self.raiz = self.NIL
        self.tamanho = 0            # número de nós (chaves distintas)
        self.log = []               # mensagens explicando cada passo
        self.ao_mudar = None        # função opcional chamada a cada mensagem

    def _registrar(self, msg):
        """Guarda a mensagem no log e avisa quem estiver ouvindo (ex.: a janela)."""
        self.log.append(msg)
        if self.ao_mudar:
            self.ao_mudar(msg)

    # ------------------------------------------------------------------ busca

    def buscar(self, chave):
        """Busca binária comum. Devolve (nó ou None, lista de chaves visitadas)."""
        x, passos = self.raiz, []
        while x is not self.NIL:
            passos.append(x.chave)
            if chave == x.chave:
                return x, passos
            # menor vai para a esquerda, maior para a direita
            x = x.esq if chave < x.chave else x.dir
        return None, passos

    # --------------------------------------------------------------- rotações
    #
    # Rotações reorganizam três ponteiros sem quebrar a ordem da árvore:
    #
    #      x                y              (rotação à esquerda em x)
    #     / \              / \
    #    a   y     ->     x   c
    #       / \          / \
    #      b   c        a   b

    def _rot_esq(self, x):
        y = x.dir
        x.dir = y.esq                   # a subárvore b passa a ser filha direita de x
        if y.esq is not self.NIL:
            y.esq.pai = x
        y.pai = x.pai                   # y assume o lugar de x junto ao pai
        if x.pai is self.NIL:
            self.raiz = y
        elif x is x.pai.esq:
            x.pai.esq = y
        else:
            x.pai.dir = y
        y.esq = x                       # x desce e vira filho esquerdo de y
        x.pai = y
        self._registrar(f"Rotação à esquerda em {x.chave}")

    def _rot_dir(self, x):
        """Espelho de _rot_esq: o filho esquerdo sobe e x desce para a direita."""
        y = x.esq
        x.esq = y.dir
        if y.dir is not self.NIL:
            y.dir.pai = x
        y.pai = x.pai
        if x.pai is self.NIL:
            self.raiz = y
        elif x is x.pai.dir:
            x.pai.dir = y
        else:
            x.pai.esq = y
        y.dir = x
        x.pai = y
        self._registrar(f"Rotação à direita em {x.chave}")

    # --------------------------------------------------------------- inserção

    def inserir(self, chave, valor=None):
        """Insere a chave. Se ela já existir, só aumenta a quantidade."""
        # 1) Desce a árvore como numa busca, lembrando o último nó visitado (y).
        y, x = self.NIL, self.raiz
        while x is not self.NIL:
            y = x
            if chave == x.chave:
                # Chave repetida: não cria nó, a forma da árvore não muda.
                x.quantidade += 1
                self._registrar(f"Chave {chave} repetida: quantidade de {x.chave} passou para {x.quantidade} (sem novo nó)")
                return x
            x = x.esq if chave < x.chave else x.dir

        # 2) Pendura o novo nó (vermelho) como filho de y.
        z = No(chave, valor, VERMELHO, self.NIL)
        z.pai = y
        if y is self.NIL:
            self.raiz = z               # árvore estava vazia
        elif chave < y.chave:
            y.esq = z
        else:
            y.dir = z
        self.tamanho += 1
        self._registrar(f"Inserido {chave} (vermelho)")

        # 3) Um nó vermelho pode ter caído embaixo de outro vermelho: corrigir.
        self._corrigir_insercao(z)
        return z

    def _corrigir_insercao(self, z):
        """Resolve o "vermelho com pai vermelho" subindo pela árvore."""
        while z.pai.cor == VERMELHO:
            avo = z.pai.pai             # existe, pois um pai vermelho nunca é a raiz
            if z.pai is avo.esq:
                # --- pai é filho ESQUERDO do avô ---
                tio = avo.dir
                if tio.cor == VERMELHO:
                    # Caso 1: só recolorir; o avô pode ter gerado novo conflito.
                    z.pai.cor = tio.cor = PRETO
                    avo.cor = VERMELHO
                    self._registrar(f"Caso 1: tio {tio.chave} vermelho -> recolorir pai, tio e avô {avo.chave}")
                    z = avo
                else:
                    if z is z.pai.dir:
                        # Caso 2: z forma um "joelho" com pai e avô; uma rotação
                        # no pai deixa tudo numa linha reta (vira o caso 3).
                        self._registrar(f"Caso 2: {z.chave} é filho interno -> rotação no pai")
                        z = z.pai
                        self._rot_esq(z)
                    # Caso 3: linha reta; pai vira preto, avô vermelho e
                    # rotaciona o avô. Isso encerra o laço.
                    self._registrar(f"Caso 3: {z.chave} é filho externo -> recolorir e rotacionar o avô")
                    z.pai.cor = PRETO
                    avo.cor = VERMELHO
                    self._rot_dir(avo)
            else:
                # --- espelho: pai é filho DIREITO do avô ---
                tio = avo.esq
                if tio.cor == VERMELHO:
                    z.pai.cor = tio.cor = PRETO
                    avo.cor = VERMELHO
                    self._registrar(f"Caso 1: tio {tio.chave} vermelho -> recolorir pai, tio e avô {avo.chave}")
                    z = avo
                else:
                    if z is z.pai.esq:
                        self._registrar(f"Caso 2: {z.chave} é filho interno -> rotação no pai")
                        z = z.pai
                        self._rot_dir(z)
                    self._registrar(f"Caso 3: {z.chave} é filho externo -> recolorir e rotacionar o avô")
                    z.pai.cor = PRETO
                    avo.cor = VERMELHO
                    self._rot_esq(avo)
        # Propriedade 2: a raiz sempre termina preta.
        if self.raiz.cor == VERMELHO:
            self.raiz.cor = PRETO
            self._registrar(f"Raiz {self.raiz.chave} pintada de preto")

    # ---------------------------------------------------------------- remoção

    def _transplantar(self, u, v):
        """Coloca a subárvore v no lugar de u (u sai da árvore)."""
        if u.pai is self.NIL:
            self.raiz = v
        elif u is u.pai.esq:
            u.pai.esq = v
        else:
            u.pai.dir = v
        v.pai = u.pai                   # funciona mesmo se v for o NIL

    def _minimo(self, x):
        """Menor chave da subárvore de x: é só ir sempre para a esquerda."""
        while x.esq is not self.NIL:
            x = x.esq
        return x

    def minimo(self):
        """Nó de menor chave da árvore inteira, ou None se ela estiver vazia."""
        if self.raiz is self.NIL:
            return None
        return self._minimo(self.raiz)

    def remover(self, chave, todas=False):
        """Remove uma unidade da chave; com todas=True remove o nó inteiro.

        Devolve True se a chave existia, False caso contrário.
        """
        z, _ = self.buscar(chave)
        if z is None:
            self._registrar(f"Chave {chave} não encontrada")
            return False
        if z.quantidade > 1 and not todas:
            # Ainda há unidades: só diminui a contagem, o nó fica.
            z.quantidade -= 1
            self._registrar(f"Chave {chave} repetida: quantidade caiu para {z.quantidade} (nó mantido)")
            return True

        # y = nó que de fato sai da sua posição; x = quem ocupa o lugar dele.
        # Guardamos a cor original de y: se era preta, a altura negra mudou.
        y, cor_original = z, z.cor
        if z.esq is self.NIL:
            # Sem filho esquerdo: o filho direito sobe.
            x = z.dir
            self._transplantar(z, z.dir)
        elif z.dir is self.NIL:
            # Sem filho direito: o filho esquerdo sobe.
            x = z.esq
            self._transplantar(z, z.esq)
        else:
            # Dois filhos: o sucessor (menor da subárvore direita) toma o lugar de z.
            y = self._minimo(z.dir)
            self._registrar(f"{chave} tem dois filhos -> substituído pelo sucessor {y.chave}")
            cor_original = y.cor
            x = y.dir                   # o sucessor não tem filho esquerdo
            if y.pai is z:
                x.pai = y               # necessário quando x é o NIL
            else:
                # Tira o sucessor de onde está e entrega a ele a subárvore direita de z.
                self._transplantar(y, y.dir)
                y.dir = z.dir
                y.dir.pai = y
            # O sucessor ocupa a posição de z, herdando o filho esquerdo e a cor.
            self._transplantar(z, y)
            y.esq = z.esq
            y.esq.pai = y
            y.cor = z.cor
        self.tamanho -= 1
        self._registrar(f"Removido {chave}")

        # Remover um nó vermelho não muda nenhuma altura negra. Já um preto
        # deixa um "preto a menos" no caminho de x, que precisa ser corrigido.
        if cor_original == PRETO:
            self._registrar("Nó removido era preto -> corrigir 'duplo preto'")
            self._corrigir_remocao(x)
        return True

    def _corrigir_remocao(self, x):
        """Resolve o "duplo preto" em x olhando para o irmão w."""
        # Se x for vermelho, basta pintá-lo de preto (feito no final).
        while x is not self.raiz and x.cor == PRETO:
            if x is x.pai.esq:
                # --- x é filho ESQUERDO ---
                w = x.pai.dir
                if w.cor == VERMELHO:
                    # Caso 1: irmão vermelho. Rotação no pai deixa x com um
                    # irmão preto, caindo nos casos 2, 3 ou 4.
                    self._registrar(f"Caso 1: irmão {w.chave} vermelho -> recolorir e rotacionar o pai")
                    w.cor = PRETO
                    x.pai.cor = VERMELHO
                    self._rot_esq(x.pai)
                    w = x.pai.dir
                if w.esq.cor == PRETO and w.dir.cor == PRETO:
                    # Caso 2: irmão e sobrinhos pretos. Tira um preto do irmão
                    # (fica vermelho) e o problema sobe para o pai.
                    self._registrar(f"Caso 2: irmão {w.chave} preto com filhos pretos -> irmão vira vermelho, sobe o problema")
                    w.cor = VERMELHO
                    x = x.pai
                else:
                    if w.dir.cor == PRETO:
                        # Caso 3: só o sobrinho interno (esquerdo) é vermelho.
                        # Rotação no irmão transforma no caso 4.
                        self._registrar(f"Caso 3: sobrinho interno vermelho -> rotacionar irmão {w.chave}")
                        w.esq.cor = PRETO
                        w.cor = VERMELHO
                        self._rot_dir(w)
                        w = x.pai.dir
                    # Caso 4: sobrinho externo vermelho. Recolorir + rotação no
                    # pai devolve o preto que faltava. Termina o laço.
                    self._registrar(f"Caso 4: sobrinho externo vermelho -> recolorir e rotacionar o pai {x.pai.chave}")
                    w.cor = x.pai.cor
                    x.pai.cor = PRETO
                    w.dir.cor = PRETO
                    self._rot_esq(x.pai)
                    x = self.raiz
            else:
                # --- espelho: x é filho DIREITO ---
                w = x.pai.esq
                if w.cor == VERMELHO:
                    self._registrar(f"Caso 1: irmão {w.chave} vermelho -> recolorir e rotacionar o pai")
                    w.cor = PRETO
                    x.pai.cor = VERMELHO
                    self._rot_dir(x.pai)
                    w = x.pai.esq
                if w.dir.cor == PRETO and w.esq.cor == PRETO:
                    self._registrar(f"Caso 2: irmão {w.chave} preto com filhos pretos -> irmão vira vermelho, sobe o problema")
                    w.cor = VERMELHO
                    x = x.pai
                else:
                    if w.esq.cor == PRETO:
                        self._registrar(f"Caso 3: sobrinho interno vermelho -> rotacionar irmão {w.chave}")
                        w.dir.cor = PRETO
                        w.cor = VERMELHO
                        self._rot_esq(w)
                        w = x.pai.esq
                    self._registrar(f"Caso 4: sobrinho externo vermelho -> recolorir e rotacionar o pai {x.pai.chave}")
                    w.cor = x.pai.cor
                    x.pai.cor = PRETO
                    w.esq.cor = PRETO
                    self._rot_dir(x.pai)
                    x = self.raiz
        x.cor = PRETO

    # -------------------------------------------------------------- consultas

    def em_ordem(self):
        """Percurso em ordem (crescente) sem recursão, usando uma pilha."""
        res, pilha, x = [], [], self.raiz
        while pilha or x is not self.NIL:
            # Desce o máximo possível para a esquerda, empilhando o caminho.
            while x is not self.NIL:
                pilha.append(x)
                x = x.esq
            # Visita o nó do topo e passa para a subárvore direita dele.
            x = pilha.pop()
            res.append(x)
            x = x.dir
        return res

    def altura(self, x=None):
        """Altura em número de nós (árvore vazia = 0)."""
        x = self.raiz if x is None else x
        if x is self.NIL:
            return 0
        return 1 + max(self.altura(x.esq), self.altura(x.dir))

    def validar(self):
        """Confere as propriedades rubro-negras. Devolve (ok, mensagem)."""
        if self.raiz.cor != PRETO:
            return False, "raiz não é preta"

        def verificar(x):
            # Devolve a altura negra de x, ou lança erro se achar violação.
            if x is self.NIL:
                return 1                # folhas NIL contam como um nó preto
            if x.cor == VERMELHO and (x.esq.cor == VERMELHO or x.dir.cor == VERMELHO):
                raise ValueError(f"vermelho {x.chave} com filho vermelho")
            e, d = verificar(x.esq), verificar(x.dir)
            if e != d:
                raise ValueError(f"altura negra diferente em {x.chave}")
            return e + (x.cor == PRETO)

        try:
            return True, f"altura negra = {verificar(self.raiz)}"
        except ValueError as erro:
            return False, str(erro)
