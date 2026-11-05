VERMELHO, PRETO = "V", "P"


class No:
    def __init__(self, chave, valor=None, cor=VERMELHO, nil=None):
        self.chave = chave
        self.valor = valor
        self.quantidade = 1
        self.cor = cor
        self.esq = nil
        self.dir = nil
        self.pai = nil


class ArvoreRubroNegra:
    def __init__(self):
        self.NIL = No(None, cor=PRETO)
        self.raiz = self.NIL
        self.tamanho = 0
        self.log = []
        self.ao_mudar = None

    def _registrar(self, msg):
        self.log.append(msg)
        if self.ao_mudar:
            self.ao_mudar(msg)

    def buscar(self, chave):
        x, passos = self.raiz, []
        while x is not self.NIL:
            passos.append(x.chave)
            if chave == x.chave:
                return x, passos
            x = x.esq if chave < x.chave else x.dir
        return None, passos

    def _rot_esq(self, x):
        y = x.dir
        x.dir = y.esq
        if y.esq is not self.NIL:
            y.esq.pai = x
        y.pai = x.pai
        if x.pai is self.NIL:
            self.raiz = y
        elif x is x.pai.esq:
            x.pai.esq = y
        else:
            x.pai.dir = y
        y.esq = x
        x.pai = y
        self._registrar(f"Rotação à esquerda em {x.chave}")

    def _rot_dir(self, x):
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

    def inserir(self, chave, valor=None):
        y, x = self.NIL, self.raiz
        while x is not self.NIL:
            y = x
            if chave == x.chave:
                x.quantidade += 1
                self._registrar(f"Chave {chave} repetida: quantidade de {x.chave} passou para {x.quantidade} (sem novo nó)")
                return x
            x = x.esq if chave < x.chave else x.dir
        z = No(chave, valor, VERMELHO, self.NIL)
        z.pai = y
        if y is self.NIL:
            self.raiz = z
        elif chave < y.chave:
            y.esq = z
        else:
            y.dir = z
        self.tamanho += 1
        self._registrar(f"Inserido {chave} (vermelho)")
        self._corrigir_insercao(z)
        return z

    def _corrigir_insercao(self, z):
        while z.pai.cor == VERMELHO:
            avo = z.pai.pai
            if z.pai is avo.esq:
                tio = avo.dir
                if tio.cor == VERMELHO:
                    z.pai.cor = tio.cor = PRETO
                    avo.cor = VERMELHO
                    self._registrar(f"Caso 1: tio {tio.chave} vermelho -> recolorir pai, tio e avô {avo.chave}")
                    z = avo
                else:
                    if z is z.pai.dir:
                        self._registrar(f"Caso 2: {z.chave} é filho interno -> rotação no pai")
                        z = z.pai
                        self._rot_esq(z)
                    self._registrar(f"Caso 3: {z.chave} é filho externo -> recolorir e rotacionar o avô")
                    z.pai.cor = PRETO
                    avo.cor = VERMELHO
                    self._rot_dir(avo)
            else:
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
        if self.raiz.cor == VERMELHO:
            self.raiz.cor = PRETO
            self._registrar(f"Raiz {self.raiz.chave} pintada de preto")

    def _transplantar(self, u, v):
        if u.pai is self.NIL:
            self.raiz = v
        elif u is u.pai.esq:
            u.pai.esq = v
        else:
            u.pai.dir = v
        v.pai = u.pai

    def _minimo(self, x):
        while x.esq is not self.NIL:
            x = x.esq
        return x

    def remover(self, chave, todas=False):
        z, _ = self.buscar(chave)
        if z is None:
            self._registrar(f"Chave {chave} não encontrada")
            return False
        if z.quantidade > 1 and not todas:
            z.quantidade -= 1
            self._registrar(f"Chave {chave} repetida: quantidade caiu para {z.quantidade} (nó mantido)")
            return True
        y, cor_original = z, z.cor
        if z.esq is self.NIL:
            x = z.dir
            self._transplantar(z, z.dir)
        elif z.dir is self.NIL:
            x = z.esq
            self._transplantar(z, z.esq)
        else:
            y = self._minimo(z.dir)
            self._registrar(f"{chave} tem dois filhos -> substituído pelo sucessor {y.chave}")
            cor_original = y.cor
            x = y.dir
            if y.pai is z:
                x.pai = y
            else:
                self._transplantar(y, y.dir)
                y.dir = z.dir
                y.dir.pai = y
            self._transplantar(z, y)
            y.esq = z.esq
            y.esq.pai = y
            y.cor = z.cor
        self.tamanho -= 1
        self._registrar(f"Removido {chave}")
        if cor_original == PRETO:
            self._registrar("Nó removido era preto -> corrigir 'duplo preto'")
            self._corrigir_remocao(x)
        return True

    def _corrigir_remocao(self, x):
        while x is not self.raiz and x.cor == PRETO:
            if x is x.pai.esq:
                w = x.pai.dir
                if w.cor == VERMELHO:
                    self._registrar(f"Caso 1: irmão {w.chave} vermelho -> recolorir e rotacionar o pai")
                    w.cor = PRETO
                    x.pai.cor = VERMELHO
                    self._rot_esq(x.pai)
                    w = x.pai.dir
                if w.esq.cor == PRETO and w.dir.cor == PRETO:
                    self._registrar(f"Caso 2: irmão {w.chave} preto com filhos pretos -> irmão vira vermelho, sobe o problema")
                    w.cor = VERMELHO
                    x = x.pai
                else:
                    if w.dir.cor == PRETO:
                        self._registrar(f"Caso 3: sobrinho interno vermelho -> rotacionar irmão {w.chave}")
                        w.esq.cor = PRETO
                        w.cor = VERMELHO
                        self._rot_dir(w)
                        w = x.pai.dir
                    self._registrar(f"Caso 4: sobrinho externo vermelho -> recolorir e rotacionar o pai {x.pai.chave}")
                    w.cor = x.pai.cor
                    x.pai.cor = PRETO
                    w.dir.cor = PRETO
                    self._rot_esq(x.pai)
                    x = self.raiz
            else:
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

    def em_ordem(self):
        res, pilha, x = [], [], self.raiz
        while pilha or x is not self.NIL:
            while x is not self.NIL:
                pilha.append(x)
                x = x.esq
            x = pilha.pop()
            res.append(x)
            x = x.dir
        return res

    def altura(self, x=None):
        x = self.raiz if x is None else x
        if x is self.NIL:
            return 0
        return 1 + max(self.altura(x.esq), self.altura(x.dir))

    def validar(self):
        if self.raiz.cor != PRETO:
            return False, "raiz não é preta"

        def verificar(x):
            if x is self.NIL:
                return 1
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
