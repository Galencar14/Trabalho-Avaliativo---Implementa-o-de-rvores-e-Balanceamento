import os
import sys

from rubro_negra import ArvoreRubroNegra

PASTA = "passos"

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
    def __init__(self, salvar_imagens=True):
        self.arvore = ArvoreRubroNegra()
        self.salvar = salvar_imagens
        self.passo = 0
        if self.salvar:
            os.makedirs(PASTA, exist_ok=True)

    def _foto(self, titulo, destaque=None):
        if not self.salvar or self.arvore.raiz is self.arvore.NIL:
            return
        self.passo += 1
        arquivo = os.path.join(PASTA, f"{self.passo:03d}.png")
        from plotagem import desenhar
        desenhar(self.arvore, f"Passo {self.passo}: {titulo}", arquivo, destaque)

    def _executar(self, titulo, operacao, destaque=None):
        inicio = len(self.arvore.log)
        resultado = operacao()
        for msg in self.arvore.log[inicio:]:
            print("   ", msg)
        self._foto(titulo, destaque)
        return resultado

    def entrada(self, codigo, nome=None):
        print(f"\n> Inserir {codigo}" + (f" ({nome})" if nome else ""))
        self._executar(f"inserir {codigo}", lambda: self.arvore.inserir(codigo, nome), codigo)

    def saida(self, codigo, todas=False):
        print(f"\n> Remover {codigo}" + (" (nó inteiro)" if todas else ""))
        self._executar(f"remover {codigo}", lambda: self.arvore.remover(codigo, todas))

    def consultar(self, codigo):
        no, caminho = self.arvore.buscar(codigo)
        print(f"\n> Busca por {codigo}: caminho {' -> '.join(map(str, caminho)) or '(vazio)'}")
        if no:
            print(f"    Encontrado{': ' + no.valor if no.valor else ''} | quantidade: {no.quantidade} | comparações: {len(caminho)}")
        else:
            print("    Produto não cadastrado")
        return no

    def relatorio(self):
        print(f"\nProdutos distintos (nós): {self.arvore.tamanho} | altura: {self.arvore.altura()}")
        for no in self.arvore.em_ordem():
            print(f"    {no.chave:>4}  {no.valor or '-':<24} qtd {no.quantidade}")
        ok, info = self.arvore.validar()
        print(f"Propriedades rubro-negras: {'OK' if ok else 'VIOLADAS'} ({info})")


def demonstracao():
    e = Estoque()
    for codigo, nome in PRODUTOS:
        e.entrada(codigo, nome)
    e.entrada(40)
    e.entrada(40)
    e.relatorio()
    e.consultar(42)
    e.consultar(99)
    e.saida(40)
    for codigo in (22, 33, 65, 35, 72, 42):
        e.saida(codigo)
    e.relatorio()
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
    from plotagem import Janela, texto

    janela = Janela()
    e = Estoque(salvar_imagens=False)
    passo_a_passo = [False]

    def a_cada_passo(msg):
        if passo_a_passo[0] and msg.startswith(("Rotação", "Caso", "Inserido", "Removido", "Raiz")):
            janela.mostrar(e.arvore, msg, pausa=1.5)

    e.arvore.ao_mudar = a_cada_passo
    janela.mostrar(e.arvore, "Árvore Rubro-Negra")
    print(AJUDA)
    while True:
        partes = input("\n>> ").split()
        if not partes:
            continue
        cmd, args = partes[0].lower(), partes[1:]
        try:
            nums = [int(a) for a in args]
        except ValueError:
            print("Use apenas números inteiros")
            continue
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
            no = e.consultar(nums[0])
            _, caminho = e.arvore.buscar(nums[0])
            titulo = f"Busca por {nums[0]}: {'encontrado' if no else 'não encontrado'}"
            destaques = caminho
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
            import random
            livres = [n for n in range(1, 1000) if e.arvore.buscar(n)[0] is None]
            novos = random.sample(livres, nums[0] if nums else 21)
            for n in novos:
                e.entrada(n)
            titulo = f"Inseridos {len(novos)} aleatórios"
        elif cmd == "f":
            janela.salvar("arvore.png")
            print("Salvo em arvore.png")
            continue
        elif cmd == "c":
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
        print(texto(e.arvore))
        ok, info = e.arvore.validar()
        print(f"Nós: {e.arvore.tamanho} | altura: {e.arvore.altura()} | {'válida' if ok else 'INVÁLIDA'} ({info})")
        janela.mostrar(e.arvore, titulo, destaques)


if __name__ == "__main__":
    if "--demo" in sys.argv:
        import matplotlib
        matplotlib.use("Agg")
        demonstracao()
    else:
        interativo()
