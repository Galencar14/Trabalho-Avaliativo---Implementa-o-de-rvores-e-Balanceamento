"""Controle de estoque usando a Árvore Rubro-Negra.

Uso:
  python main.py --demo   demonstração automática, salva uma imagem por passo em ./passos/
  python main.py          modo interativo com janela gráfica
"""

import os
import random
import sys

from rubro_negra import ArvoreRubroNegra

PASTA = "passos"            # onde a demonstração salva as imagens
MAX_CODIGO = 999            # o comando "x" sorteia códigos de 1 até este valor

# (código, nome) dos produtos usados no exemplo.
PRODUTOS = [
    (68, "Bacuri polpa"), (35, "Pirarucu seco 1kg"), (65, "Taperebá polpa"), (55, "Muruci polpa"),
    (75, "Pupunha 1kg"), (45, "Camarão seco 500g"), (42, "Tambaqui 1kg"), (52, "Uxi polpa"),
    (38, "Dourada 1kg"), (50, "Açaí 1L"), (25, "Maniçoba 1kg"), (30, "Farinha d'água 1kg"),
    (70, "Tucupi 1L"), (40, "Castanha-do-pará 500g"), (10, "Tapioca 1kg"), (20, "Jambu (maço)"),
    (33, "Filhote 1kg"), (5, "Goma de tapioca"), (48, "Mapará 1kg"), (60, "Cupuaçu polpa"),
    (80, "Bacaba 1L"), (28, "Chicória (maço)"), (15, "Tacacá (kit)"), (62, "Murumuru"),
    (72, "Biribá"), (58, "Buriti polpa"), (22, "Pimenta-de-cheiro"), (85, "Piquiá"),
]


class Estoque:
    """Camada de estoque sobre a árvore: imprime cada passo e opcionalmente salva imagens."""

    def __init__(self, salvar_imagens=True):
        self.arvore = ArvoreRubroNegra()
        self.salvar = salvar_imagens
        self.passo = 0                  # numeração das imagens (001.png, 002.png...)
        if self.salvar:
            os.makedirs(PASTA, exist_ok=True)

    def _foto(self, titulo, destaque=None):
        """Salva a árvore atual como imagem (só no modo demonstração)."""
        if not self.salvar or self.arvore.raiz is self.arvore.NIL:
            return
        self.passo += 1
        arquivo = os.path.join(PASTA, f"{self.passo:03d}.png")
        # Import aqui dentro para o matplotlib só carregar quando for usado.
        from plotagem import desenhar
        desenhar(self.arvore, f"Passo {self.passo}: {titulo}", arquivo, destaque)

    def _executar(self, titulo, operacao, destaque=None):
        """Roda uma operação da árvore, imprime as mensagens que ela gerou e tira a foto."""
        resultado = operacao()
        for msg in self.arvore.log:
            print("   ", msg)
        # Esvazia o log para ele não crescer sem limite em sessões longas.
        self.arvore.log.clear()
        self._foto(titulo, destaque)
        return resultado

    def entrada(self, codigo, nome=None):
        """Entrada de uma unidade no estoque (inserção na árvore)."""
        print(f"\n> Inserir {codigo}" + (f" ({nome})" if nome else ""))
        self._executar(f"inserir {codigo}", lambda: self.arvore.inserir(codigo, nome), codigo)

    def saida(self, codigo, todas=False):
        """Saída do estoque: uma unidade, ou o produto inteiro se todas=True."""
        print(f"\n> Remover {codigo}" + (" (nó inteiro)" if todas else ""))
        self._executar(f"remover {codigo}", lambda: self.arvore.remover(codigo, todas))

    def consultar(self, codigo):
        """Busca um produto e mostra o caminho percorrido. Devolve (nó ou None, caminho)."""
        no, caminho = self.arvore.buscar(codigo)
        print(f"\n> Busca por {codigo}: caminho {' -> '.join(map(str, caminho)) or '(vazio)'}")
        if no:
            # O número de comparações é o tamanho do caminho: no máximo ~2*log2(n).
            print(f"    Encontrado{': ' + no.valor if no.valor else ''} | quantidade: {no.quantidade} | comparações: {len(caminho)}")
        else:
            print("    Produto não cadastrado")
        return no, caminho

    def relatorio(self):
        """Lista os produtos em ordem de código e confere as propriedades da árvore."""
        print(f"\nProdutos distintos (nós): {self.arvore.tamanho} | altura: {self.arvore.altura()}")
        for no in self.arvore.em_ordem():
            print(f"    {no.chave:>4}  {no.valor or '-':<24} qtd {no.quantidade}")
        ok, info = self.arvore.validar()
        print(f"Propriedades rubro-negras: {'OK' if ok else 'VIOLADAS'} ({info})")


def demonstracao():
    """Roteiro fixo que passa por todos os casos de balanceamento."""
    e = Estoque()
    # 28 inserções
    for codigo, nome in PRODUTOS:
        e.entrada(codigo, nome)
    # 2 repetições: o 40 passa a ter quantidade 3, sem novos nós
    e.entrada(40)
    e.entrada(40)
    e.relatorio()
    # Uma busca que encontra e outra que não encontra
    e.consultar(42)
    e.consultar(99)
    # O 40 só perde uma unidade (fica com 2); os outros 6 saem da árvore
    e.saida(40)
    for codigo in (22, 33, 65, 35, 72, 42):
        e.saida(codigo)
    e.relatorio()               # 28 - 6 = 22 nós
    print(f"\nImagens salvas em ./{PASTA}/")


AJUDA = """Comandos:
  i 10 20 30   inserir um ou mais números
  r 20         remover (uma unidade, se repetido)
  rt 20        remover o nó inteiro
  b 15         buscar (destaca o caminho)
  l            listar em ordem e validar propriedades
  p            liga/desliga modo passo a passo (mostra cada rotação)
  e            carregar os 28 produtos do exemplo
  x 25         inserir 25 números aleatórios
  f            salvar a imagem atual (arvore.png)
  c            limpar a árvore
  h            ajuda
  s            sair"""


def interativo():
    """Lê comandos do terminal e redesenha a janela após cada um."""
    from plotagem import Janela, texto

    janela = Janela()
    e = Estoque(salvar_imagens=False)
    passo_a_passo = [False]     # lista para poder ser alterada dentro de a_cada_passo

    def a_cada_passo(msg):
        # No modo passo a passo, redesenha a janela a cada inserção, remoção,
        # caso de balanceamento ou rotação, com pausa para dar tempo de ver.
        if passo_a_passo[0] and msg.startswith(("Rotação", "Caso", "Inserido", "Removido", "Raiz")):
            janela.mostrar(e.arvore, msg, pausa=1.5)

    e.arvore.ao_mudar = a_cada_passo
    janela.mostrar(e.arvore, "Árvore Rubro-Negra")
    print(AJUDA)
    while True:
        # Ctrl+C ou Ctrl+D (fim da entrada) encerram sem mostrar erro.
        try:
            partes = input("\n>> ").split()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not partes:
            continue
        cmd, args = partes[0].lower(), partes[1:]
        try:
            nums = [int(a) for a in args]
        except ValueError:
            print("Use apenas números inteiros")
            continue

        # Título e nós destacados na janela depois do comando.
        titulo, destaques = "Árvore Rubro-Negra", ()
        if cmd == "i" and nums:
            for n in nums:
                e.entrada(n)
            titulo, destaques = f"Após inserir {' '.join(args)}", nums
        elif cmd in ("r", "rt") and nums:
            for n in nums:
                e.saida(n, cmd == "rt")
            titulo = f"Após remover {' '.join(args)}"
        elif cmd == "b" and nums:
            no, caminho = e.consultar(nums[0])
            titulo = f"Busca por {nums[0]}: {'encontrado' if no else 'não encontrado'}"
            destaques = caminho         # destaca todos os nós visitados na busca
        elif cmd == "l":
            e.relatorio()
        elif cmd == "p":
            passo_a_passo[0] = not passo_a_passo[0]
            print("Passo a passo", "ligado" if passo_a_passo[0] else "desligado")
            continue
        elif cmd == "e":
            for codigo, nome in PRODUTOS:
                e.entrada(codigo, nome)
            titulo = "Exemplo carregado"
        elif cmd == "x":
            quantos = nums[0] if nums else 21
            if quantos <= 0:
                print("Informe uma quantidade maior que zero")
                continue
            # Só sorteia códigos que ainda não estão na árvore.
            livres = [n for n in range(1, MAX_CODIGO + 1) if e.arvore.buscar(n)[0] is None]
            if not livres:
                print(f"Todos os códigos de 1 a {MAX_CODIGO} já estão na árvore")
                continue
            if quantos > len(livres):
                print(f"Só há {len(livres)} códigos livres; inserindo todos eles")
                quantos = len(livres)
            novos = random.sample(livres, quantos)
            for n in novos:
                e.entrada(n)
            titulo = f"Inseridos {len(novos)} aleatórios"
        elif cmd == "f":
            janela.salvar("arvore.png")
            print("Salvo em arvore.png")
            continue
        elif cmd == "c":
            # Nova árvore vazia; a_cada_passo usa "e", então já enxerga a nova.
            e = Estoque(salvar_imagens=False)
            e.arvore.ao_mudar = a_cada_passo
        elif cmd == "h":
            print(AJUDA)
            continue
        elif cmd == "s":
            break
        else:
            print("Comando inválido (h = ajuda)")
            continue

        # Depois de qualquer comando que mexe na árvore: texto, resumo e janela.
        print(texto(e.arvore))
        ok, info = e.arvore.validar()
        print(f"Nós: {e.arvore.tamanho} | altura: {e.arvore.altura()} | {'válida' if ok else 'INVÁLIDA'} ({info})")
        janela.mostrar(e.arvore, titulo, destaques)


if __name__ == "__main__":
    if "--demo" in sys.argv:
        # Backend "Agg" desenha direto em arquivo, sem abrir janela.
        # Precisa vir antes do primeiro import de matplotlib.pyplot.
        import matplotlib
        matplotlib.use("Agg")
        demonstracao()
    else:
        interativo()
