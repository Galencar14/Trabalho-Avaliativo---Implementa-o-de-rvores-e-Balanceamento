"""Módulo 4 — Comparação dos métodos de balanceamento.

As MESMAS chaves entram, na mesma ordem, na Rubro-Negra e na 2-3-4, que são
desenhadas lado a lado. A demonstração usa ordem crescente de propósito: é o
pior caso para uma árvore binária de busca comum, que viraria uma "lista" com
altura igual ao número de chaves.
"""

from arvore234 import Arvore234
from controle import Aviso, Controle
from desenho import arvore234_2d, rubro_negra_2d
from rubro_negra import ArvoreRubroNegra

CHAVES = list(range(10, 220, 10))       # 10, 20, ..., 210: 21 chaves em ordem crescente


def ler_chave(texto):
    """Converte o texto digitado num inteiro. Lança Aviso se não for um número."""
    partes = texto.split()
    if not partes or not partes[0].lstrip("-").isdigit():
        raise Aviso("Digite um número inteiro, por exemplo: 55")
    return int(partes[0])


class Comparacao(Controle):
    nome = "Comparar os balanceamentos"
    nome_da_arvore = "Rubro-Negra e 2-3-4 lado a lado"
    dica = "55"
    tem_3d = False
    descricao = """As mesmas chaves entram nas duas árvores.
Numa árvore binária comum, 21 chaves em ordem
crescente dariam altura 21 (uma lista).

RUBRO-NEGRA: equilibra com cores e rotações.
Altura no máximo 2·log2(n + 1).
2-3-4: equilibra dividindo e fundindo nós.
Todas as folhas no mesmo nível.
k-D: não se equilibra sozinha; é reconstruída
pela mediana.

LIGAÇÃO: toda rubro-negra corresponde a uma
2-3-4. Um nó preto com seus filhos vermelhos
equivale a um nó da 2-3-4 (1, 2 ou 3 chaves).
Recolorir (caso 1) é o mesmo que DIVIDIR um
nó cheio.

REPETIDOS: aqui, recusados nas duas, para as
árvores terem sempre as mesmas chaves."""

    def nova(self):
        """Cria as duas árvores vazias."""
        self.rubro_negra = ArvoreRubroNegra()
        self.arvore234 = Arvore234()

    def _mensagens(self):
        """Junta o que cada árvore registrou, identificando de qual veio."""
        linhas = ["Rubro-Negra: " + m for m in self.rubro_negra.log] + ["2-3-4: " + m for m in self.arvore234.log]
        self.rubro_negra.log.clear()
        self.arvore234.log.clear()
        return linhas

    def adicionar(self, chave):
        """Insere a mesma chave nas duas árvores."""
        if self.arvore234.buscar(chave)[0]:
            raise Aviso(f"{chave} já está nas duas árvores")
        self.rubro_negra.inserir(chave)
        self.arvore234.inserir(chave)
        self.publicar(f"> Inserir {chave} nas duas árvores", self._mensagens(), (chave,))

    def inserir(self, texto):
        """Botão Inserir: lê um número do campo de entrada."""
        self.adicionar(ler_chave(texto))

    def buscar(self, texto):
        chave = ler_chave(texto)
        no, caminho = self.rubro_negra.buscar(chave)
        _, _, nos = self.arvore234.buscar(chave)
        self.publicar(f"> Busca por {chave}: {'encontrada' if no else 'não encontrada'}",
                      [f"Rubro-Negra: {len(caminho)} nós visitados", f"2-3-4: {len(nos)} nós visitados"],
                      tuple(caminho) + tuple(c for n in nos for c in n.chaves),
                      (tuple(caminho), tuple(nos)))       # um traçado para cada árvore

    def remover(self, chave):
        """Remove a mesma chave das duas árvores."""
        if not self.rubro_negra.remover(chave, todas=True):
            self.rubro_negra.log.clear()
            raise Aviso(f"{chave} não está nas árvores")
        self.arvore234.excluir(chave)
        self.publicar(f"> Remover {chave} das duas árvores", self._mensagens())

    def remover_selecionado(self):
        """Tecla Delete: remove, das duas árvores, a chave clicada em qualquer uma delas."""
        if self.selecionado is None:
            raise Aviso("Clique em uma chave, em qualquer das árvores, antes de remover")
        self.remover(self.selecionado)

    def carregar_exemplo(self):
        """Recomeça com as 21 chaves em ordem crescente já inseridas nas duas árvores."""
        self.limpar()
        for chave in CHAVES:
            self.rubro_negra.inserir(chave)
            self.arvore234.inserir(chave)
        self._mensagens()
        self.publicar(f"> Exemplo carregado: chaves de {CHAVES[0]} a {CHAVES[-1]}, em ordem crescente")

    def resumo(self):
        """Alturas das duas árvores, comparadas com a de uma árvore binária comum no pior caso."""
        return (f"Chaves: {self.rubro_negra.tamanho}   |   altura da Rubro-Negra: {self.rubro_negra.altura()}   |   "
                f"altura da 2-3-4: {self.arvore234.altura()}   |   "
                f"árvore binária comum, no pior caso: {self.rubro_negra.tamanho}")

    def desenhar(self, tres_d):
        """Desenha a Rubro-Negra à esquerda e a 2-3-4 à direita; devolve os pontos clicáveis das duas."""
        esquerda = self.app.eixo((0.005, 0.02, 0.49, 0.9))
        direita = self.app.eixo((0.505, 0.02, 0.49, 0.9))
        tracado_rn, tracado_234 = self.caminho or ((), ())
        pontos = rubro_negra_2d(esquerda, self.rubro_negra, self.destaques, self.selecionado,
                                f"Rubro-Negra — altura {self.rubro_negra.altura()}", tracado_rn)
        return pontos + arvore234_2d(direita, self.arvore234, self.destaques, self.selecionado,
                                     f"2-3-4 — altura {self.arvore234.altura()}", tracado_234)

    def roteiro(self):
        """Demonstração: as 21 inserções em ordem crescente e depois 4 remoções."""
        fase = "1. Inserções em ordem crescente, lado a lado"
        passos = [(fase, lambda c=chave: self.adicionar(c)) for chave in CHAVES]
        fase = "2. Remoções lado a lado"
        passos += [(fase, lambda c=chave: self.remover(c)) for chave in (10, 40, 80, 120)]
        return passos
