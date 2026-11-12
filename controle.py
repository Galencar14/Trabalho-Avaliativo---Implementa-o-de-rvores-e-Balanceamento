"""Base dos módulos do observatório.

Cada módulo (agenda, catálogo, mapa, comparação) é um "controle": ele guarda a
árvore, sabe traduzir o que o usuário digitou em operações dela e sabe
desenhá-la. A janela (janela.py) só conhece esta interface comum, então os
botões funcionam do mesmo jeito para as três árvores.
"""


class Aviso(Exception):
    """Mensagem para o usuário (entrada inválida, nada selecionado etc.). Não é um erro do programa."""


class Controle:
    nome = ""               # título do módulo
    nome_da_arvore = ""     # qual árvore ele usa
    descricao = ""          # texto do painel lateral (uso real e regra de repetidos)
    dica = ""               # exemplo do que digitar no campo de entrada
    tem_3d = True           # se o módulo tem vista 3D
    animavel = False        # se dá para mostrar cada rotação/divisão separadamente
    extras = ()             # botões próprios do módulo: ((rótulo, nome do método), ...)

    def __init__(self, app):
        """Guarda a janela (para registrar mensagens e criar eixos) e começa com a árvore vazia."""
        self.app = app
        self.limpar()

    def limpar(self):
        """Volta ao estado inicial: árvore vazia, nada selecionado."""
        self.nova()
        self.selecionado = None     # nó escolhido com o clique
        self.destaques = ()         # nós a destacar (inserido, visitados na busca...)
        self.caminho = ()           # traçado da última busca: por onde ela passou, em ordem
        self.titulo = self.nome

    def publicar(self, cabecalho, mensagens=(), destaques=(), caminho=()):
        """Registra uma operação: vai para o painel de registro e vira o título da vista.

        `caminho` é o traçado a desenhar sobre as arestas (usado pela busca).
        Qualquer outra operação apaga o traçado anterior.
        """
        self.app.registrar([cabecalho] + ["    " + m for m in mensagens])
        self.titulo = cabecalho.lstrip("> ")
        self.destaques = destaques
        self.caminho = caminho
        self.selecionado = None

    def texto_do_selecionado(self):
        """O nó selecionado escrito do jeito que `buscar` espera receber (como se fosse digitado)."""
        return str(self.selecionado)

    def ao_trocar_vista(self):
        """Chamado quando o usuário alterna entre 2D e 3D."""

    # --- o que cada módulo precisa definir ---

    def nova(self):
        """Cria a árvore vazia."""
        raise NotImplementedError

    def inserir(self, texto):
        """Botão Inserir: recebe o texto do campo de entrada."""
        raise NotImplementedError

    def buscar(self, texto):
        """Botão Buscar: recebe o texto digitado, ou o nó selecionado já convertido em texto."""
        raise NotImplementedError

    def remover_selecionado(self):
        """Tecla Delete: remove o nó guardado em self.selecionado."""
        raise NotImplementedError

    def carregar_exemplo(self):
        """Botão Carregar exemplo: recomeça com os dados de exemplo já na árvore."""
        raise NotImplementedError

    def resumo(self):
        """Uma linha com tamanho, altura e validação da árvore."""
        raise NotImplementedError

    def desenhar(self, tres_d):
        """Desenha a árvore na janela e devolve a lista de pontos clicáveis."""
        raise NotImplementedError

    def roteiro(self):
        """Passos da demonstração guiada: lista de (nome da fase, função)."""
        raise NotImplementedError


class Animado:
    """Mistura para os módulos que mostram cada rotação/divisão como um quadro separado.

    As árvores chamam `ao_mudar(msg)` a cada passo interno; com a animação
    ligada, a janela é redesenhada ali mesmo, com uma pequena pausa.
    """

    PASSOS_VISIVEIS = ("Rotação", "Caso", "Inserido", "Removido", "Raiz", "Nó cheio", "Fusão", "Nó [")

    def quadro(self, msg):
        """Recebe cada mensagem da árvore; com a animação ligada, mostra a árvore naquele instante."""
        if self.app.animar and msg.startswith(self.PASSOS_VISIVEIS):
            self.titulo = msg
            self.app.mostrar_quadro()
