"""Módulo 2 — Catálogo de estrelas (Árvore 2-3-4).

A chave é o número da estrela no catálogo e o valor é o registro dela. É um
índice: dado o número, achar o registro.

Elementos repetidos: NÃO são permitidos. O número de catálogo identifica uma
única estrela, como uma chave primária de banco de dados. Tentar cadastrar um
número que já existe é recusado.
"""

from arvore234 import Arvore234
from controle import Animado, Aviso, Controle
from dados import ESTRELAS, EXTRAS, TRES_MARIAS, Estrela
from desenho import arvore234_2d, arvore234_3d


def ler_numero(texto):
    """Separa o texto digitado em (número de catálogo, nome). Lança Aviso se não começar por um inteiro."""
    partes = texto.split()
    if not partes or not partes[0].isdigit():
        raise Aviso("Digite o número de catálogo (inteiro), por exemplo: 1713 Rigel")
    return int(partes[0]), " ".join(partes[1:])


class Catalogo(Animado, Controle):
    nome = "Catálogo de estrelas"
    nome_da_arvore = "Árvore 2-3-4"
    dica = "1713 Rigel"
    animavel = True
    descricao = """Índice das estrelas pelo número no Bright
Star Catalogue (HR): dado o número, achar
o registro.

USO REAL: bancos de dados e sistemas de
arquivos guardam índices em B-Trees, e a
2-3-4 é uma B-Tree de ordem 4. O catálogo
do SDSS fica num banco com índices B-Tree;
o formato HDF5 também usa B-Trees.

REPETIDOS: número repetido é recusado, como
uma chave primária.

NÓS: cada nó guarda de 1 a 3 chaves e tem
de 2 a 4 filhos.
BALANCEAMENTO: divide o nó cheio ao inserir;
empresta ou funde ao remover. Todas as
folhas ficam no mesmo nível."""

    def nova(self):
        self.arvore = Arvore234()
        self.arvore.ao_mudar = self.quadro      # permite animar cada divisão e fusão

    def _publicar(self, cabecalho, destaques=()):
        """Publica a operação junto com tudo que a árvore registrou ao executá-la."""
        mensagens = list(self.arvore.log)
        self.arvore.log.clear()
        self.publicar(cabecalho, mensagens, destaques)

    # --- operações ---

    def cadastrar(self, estrela):
        """Insere a estrela no índice pelo número. Número repetido é recusado pela própria árvore."""
        aceito = self.arvore.inserir(estrela.numero, estrela)
        resultado = "" if aceito else " — RECUSADO (número já existe)"
        self._publicar(f"> Cadastrar HR {estrela.numero} ({estrela.nome}){resultado}", (estrela.numero,))

    def inserir(self, texto):
        """Botão Inserir: lê 'número nome' do campo de entrada e cadastra a estrela."""
        numero, nome = ler_numero(texto)
        self.cadastrar(Estrela(numero, nome or "sem nome", "-", 0.0, 0.0, 2.0))

    def buscar(self, texto):
        numero, _ = ler_numero(texto)
        achou, estrela, caminho = self.arvore.buscar(numero)
        resultado = f"encontrada: {estrela.nome} ({estrela.constelacao})" if achou else "não cadastrada"
        # Destaca todas as chaves dos nós por onde a busca passou.
        visitadas = tuple(chave for no in caminho for chave in no.chaves)
        self.publicar(f"> Busca por HR {numero}: {resultado}",
                      [f"Caminho: {' -> '.join(map(str, caminho))}", f"Nós visitados: {len(caminho)}"],
                      visitadas, tuple(caminho))

    def remover(self, numero):
        """Remove a estrela de número dado: exclusão na árvore, com empréstimo ou fusão se for preciso."""
        if not self.arvore.excluir(numero):
            self.arvore.log.clear()
            raise Aviso(f"HR {numero} não está no catálogo")
        self._publicar(f"> Remover HR {numero}")

    def remover_selecionado(self):
        """Tecla Delete: remove a chave em que o usuário clicou."""
        if self.selecionado is None:
            raise Aviso("Clique em uma chave para selecioná-la antes de remover")
        self.remover(self.selecionado)

    def carregar_exemplo(self):
        """Recomeça o catálogo já com todas as estrelas de exemplo."""
        self.limpar()
        estrelas = ESTRELAS + TRES_MARIAS + EXTRAS
        for estrela in estrelas:
            self.arvore.inserir(estrela.numero, estrela)
        self.arvore.log.clear()
        self.publicar(f"> Exemplo carregado: {len(estrelas)} estrelas")

    # --- exibição ---

    def resumo(self):
        """Linha de estado da árvore: número de chaves, altura e se as regras da 2-3-4 continuam valendo."""
        ok, info = self.arvore.validar()
        return (f"Chaves: {self.arvore.tamanho}   |   altura: {self.arvore.altura()}   |   "
                f"regras da 2-3-4: {'OK' if ok else 'VIOLADAS'} ({info})")

    def desenhar(self, tres_d):
        """Desenha a árvore na vista 3D ou na 2D e devolve os pontos clicáveis."""
        if tres_d:
            eixo = self.app.eixo((0, 0, 1, 1), True)
            return arvore234_3d(eixo, self.arvore, self.app.visao, self.destaques, self.selecionado,
                                self.caminho)
        eixo = self.app.eixo((0.01, 0.02, 0.98, 0.94))
        return arvore234_2d(eixo, self.arvore, self.destaques, self.selecionado, caminho=self.caminho)

    def roteiro(self):
        passos = []
        estrelas = ESTRELAS[:21]
        fase = f"1. Cadastro de {len(estrelas)} estrelas (nó cheio é dividido na descida)"
        for estrela in estrelas:
            passos.append((fase, lambda e=estrela: self.cadastrar(e)))
        passos.append(("2. Número repetido: recusado", lambda: self.cadastrar(ESTRELAS[0])))
        fase = "3. Busca"
        for numero in ("7001", "9999"):
            passos.append((fase, lambda n=numero: self.buscar(n)))
        # Escolhidas para passar por todos os casos de exclusão: folha, empréstimo
        # de irmão, fusão, chave em nó interno (antecessora/sucessora) e raiz que encolhe.
        fase = "4. Remoções (empréstimo ou fusão antes de descer)"
        for numero in (5340, 6134, 2943, 2618, 5056, 4853, 4730, 2491, 2990):
            passos.append((fase, lambda n=numero: self.remover(n)))
        return passos
