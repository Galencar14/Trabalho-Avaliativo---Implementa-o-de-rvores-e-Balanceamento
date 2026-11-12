"""A janela do programa: tela inicial, painel de botões, vista da árvore e registro.

Tudo é feito com o matplotlib (botões e campo de texto incluídos), que é a
única dependência do projeto. A janela não sabe nada de árvores: ela repassa
os cliques e as teclas para o módulo aberto (um Controle).

Na vista:
  arrastar com o mouse   gira o modelo 3D
  rolagem                aproxima e afasta
  clique num nó          seleciona
  Delete                 remove o nó selecionado
  B (ou botão Buscar)    busca o nó selecionado, sem precisar digitar
  seta para a direita    próximo passo da demonstração

Desempenho: redesenhar a janela inteira custa caro (o painel de texto, os
botões...). Por isso só a parte que mudou é redesenhada e copiada para a tela
("blit"): ao girar, apenas o modelo 3D; depois de uma operação, apenas a
vista, o cabeçalho, o registro e os botões cujo texto muda.
"""

import time

import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from mpl_toolkits.mplot3d import proj3d

from controle import Aviso
from desenho import AMARELO, CIANO, FUNDO, LINHA, PAINEL, SUAVE, TEXTO, fundo_estrelado

AREA = (0.004, 0.215, 0.718, 0.715)     # região da vista: esquerda, base, largura, altura
COR_BOTAO, COR_BOTAO_ATIVO = "#1b2b55", "#2f4a8f"
LARANJA = "#ff9f1c"


def _sem_marcas(eixo, cor_da_borda=None):
    """Tira as marcações de um eixo, mas mantém o fundo (ao contrário de axis("off"))."""
    eixo.set_xticks([])
    eixo.set_yticks([])
    for lado in eixo.spines.values():
        lado.set_visible(cor_da_borda is not None)
        if cor_da_borda:
            lado.set_color(cor_da_borda)


class Campo:
    """Campo de entrada de texto.

    O campo de texto pronto do matplotlib (TextBox) redesenha a janela inteira
    a cada tecla, o que dá um atraso visível ao digitar. Este redesenha só o
    próprio retângulo.
    """

    def __init__(self, app, retangulo):
        self.app = app
        self.text = ""                  # o que foi digitado
        self.ativo = False              # True enquanto o campo está com o foco do teclado
        self.eixo = app.fig.add_axes(retangulo, facecolor="#0a1228", zorder=5)
        _sem_marcas(self.eixo, LINHA)
        self.artista = self.eixo.text(0.03, 0.5, "", va="center", fontsize=10, color=TEXTO,
                                      family="monospace", transform=self.eixo.transAxes)
        self._mostrar()

    def _mostrar(self):
        if self.ativo:
            self.artista.set_text(self.text + "|")      # a barra faz o papel de cursor
            self.artista.set_color(TEXTO)
        else:
            self.artista.set_text(self.text or "clique aqui para digitar")
            self.artista.set_color(TEXTO if self.text else SUAVE)
        for lado in self.eixo.spines.values():
            lado.set_color(CIANO if self.ativo else LINHA)

    def focar(self, ativo):
        """Dá ou tira o foco do teclado; a borda azul e a barra de cursor mostram que o campo está ativo."""
        if ativo != self.ativo:
            self.ativo = ativo
            self._mostrar()
            self.app.copiar([self.eixo])

    def tecla(self, tecla):
        """Trata uma tecla. Devolve True se foi Enter (o usuário terminou de digitar)."""
        if tecla == "enter":
            return True
        if tecla == "backspace":
            self.text = self.text[:-1]
        elif tecla == "escape":
            self.ativo = False
        elif tecla is not None and len(tecla) == 1 and len(self.text) < 40:
            self.text += tecla          # letras, números, espaço e pontuação chegam como um caractere
        self._mostrar()
        self.app.copiar([self.eixo])
        return False


class App:
    def __init__(self, modulos):
        self.modulos = modulos          # lista de classes de Controle, na ordem do menu
        # Desliga os atalhos de teclado do matplotlib ("s" salva, "l" muda a
        # escala...) para não dispararem enquanto o usuário digita.
        for chave in list(plt.rcParams):
            if chave.startswith("keymap."):
                plt.rcParams[chave] = []
        self.fig = plt.figure(figsize=(15, 8.4), facecolor=FUNDO)
        try:
            self.fig.canvas.manager.set_window_title("Observatório — Árvores e Balanceamento")
        except AttributeError:
            pass                        # sem janela de verdade (execução de teste)

        self.controle = None            # módulo aberto (None = tela inicial)
        self.widgets = []               # botões e campo de texto da tela atual
        self.eixos = []                 # eixos da vista em uso no desenho atual
        self._reserva = {}              # todos os eixos da vista já criados nesta tela
        self.eixo_3d = None
        self.pontos = []                # pontos clicáveis devolvidos pelo último desenho
        self.linhas = []                # registro das operações
        self.vista_3d = True
        self.animar = False
        self.pausa_do_quadro = 0.9      # segundos por quadro quando a animação está ligada
        self.elevacao, self.azimute, self.zoom = 22, -58, 1.0
        self.roteiro, self.passo = None, 0
        self._pressionado = None        # onde o botão do mouse foi apertado
        self._giro = None               # (x, y, elevação, azimute) no início de um arrasto no modelo 3D
        self._girando = False
        self._tela_completa = False     # True depois que a tela atual foi desenhada inteira uma vez

        canvas = self.fig.canvas
        canvas.mpl_connect("key_press_event", self._ao_teclar)
        canvas.mpl_connect("button_press_event", self._ao_pressionar)
        canvas.mpl_connect("motion_notify_event", self._ao_mover)
        canvas.mpl_connect("button_release_event", self._ao_soltar)
        canvas.mpl_connect("scroll_event", self._ao_rolar)
        canvas.mpl_connect("draw_event", self._ao_desenhar_tudo)
        self.tela_inicial()

    @property
    def visao(self):
        """Câmera da vista 3D: (elevação, azimute, zoom)."""
        return self.elevacao, self.azimute, self.zoom

    # ------------------------------------------------------------------ telas

    def _limpar_tela(self):
        for widget in self.widgets:
            widget.disconnect_events()
        self._desligar_eixos_3d()
        self._reserva = {}              # eixos da vista, guardados para reaproveitar
        self.fig.clf()
        self.widgets, self.eixos, self.eixo_3d, self.pontos = [], [], None, []
        self.entrada, self._botao_realcado = None, None
        self._tela_completa = False     # tela nova: o próximo desenho tem que ser completo

    def _botao(self, retangulo, texto, acao, fonte=8.5):
        eixo = self.fig.add_axes(retangulo, zorder=5)
        # As duas cores iguais desligam o realce do próprio matplotlib, que redesenha a
        # janela inteira toda vez que o mouse entra ou sai de um botão. O realce é feito
        # em _realcar_botao, redesenhando só o botão.
        botao = Button(eixo, texto, color=COR_BOTAO, hovercolor=COR_BOTAO)
        botao.label.set_color(TEXTO)
        botao.label.set_fontsize(fonte)
        for lado in eixo.spines.values():
            lado.set_color(LINHA)
        botao.on_clicked(lambda evento: acao())
        self.widgets.append(botao)
        return botao

    def tela_inicial(self):
        """Monta o menu principal: o título sobre o céu estrelado e um botão para cada módulo."""
        self._limpar_tela()
        self.controle = None
        ceu = self.fig.add_axes([0, 0, 1, 1])
        fundo_estrelado(ceu, 11, 700)
        ceu.axis("off")
        self.fig.text(0.5, 0.86, "OBSERVATÓRIO", ha="center", fontsize=44, fontweight="bold", color=TEXTO)
        self.fig.text(0.5, 0.80, "Árvores e Balanceamento", ha="center", fontsize=17, color=AMARELO)
        self.fig.text(0.5, 0.755, "Trabalho AV2 — Teoria dos Grafos — CESUPA", ha="center", fontsize=10, color=SUAVE)
        y = 0.60
        for i, modulo in enumerate(self.modulos):
            self._botao([0.31, y, 0.38, 0.095], f"{i + 1}.  {modulo.nome}\n{modulo.nome_da_arvore}",
                        lambda m=modulo: self.abrir(m), fonte=12)
            y -= 0.118
        self._botao([0.44, y + 0.035, 0.12, 0.05], "Sair", lambda: plt.close(self.fig), fonte=10)
        self.fig.text(0.5, 0.035, "Cada árvore é implementada do zero, com nós encadeados, sem bibliotecas de árvores.",
                      ha="center", fontsize=9, color=SUAVE)
        self.fig.canvas.draw_idle()

    def abrir(self, classe):
        """Monta a tela de um módulo: vista à esquerda, painel à direita, registro embaixo."""
        self._limpar_tela()
        self.linhas, self.roteiro, self.passo = [], None, 0
        self.controle = classe(self)
        c = self.controle

        painel = self.fig.add_axes([0.726, 0, 0.274, 1], facecolor=PAINEL, zorder=1)
        _sem_marcas(painel)
        x0, largura = 0.738, 0.25
        self.fig.text(x0, 0.955, c.nome, fontsize=14, fontweight="bold", color=AMARELO)
        self.fig.text(x0, 0.925, c.nome_da_arvore, fontsize=10, color=CIANO)
        self.fig.text(x0, 0.900, c.descricao, fontsize=8, color=TEXTO, va="top", linespacing=1.4)

        # Campo de entrada: o que for digitado aqui vale para Inserir, Buscar e os botões do módulo.
        self.fig.text(x0, 0.541, f"Entrada (ex.: {c.dica})", fontsize=8, color=SUAVE)
        self.entrada = Campo(self, [x0, 0.491, largura, 0.042])

        # Botões, em linhas de um ou dois.
        linhas = [[("Inserir", lambda: c.inserir(self.entrada.text)),
                   ("Buscar", self.buscar)],
                  [("Remover selecionado (Delete)", c.remover_selecionado)]]
        extras = [(rotulo, lambda m=metodo: getattr(c, m)(self.entrada.text)) for rotulo, metodo in c.extras]
        linhas += [extras[i:i + 2] for i in range(0, len(extras), 2)]
        linhas.append([("Carregar exemplo", c.carregar_exemplo), ("Limpar tudo", self._limpar_arvore)])
        y, altura, vao = 0.436, 0.042, 0.008
        for linha in linhas:
            fatia = (largura - vao * (len(linha) - 1)) / len(linha)
            for i, (rotulo, acao) in enumerate(linha):
                self._botao([x0 + i * (fatia + vao), y, fatia, altura], rotulo, lambda a=acao: self._agir(a))
            y -= altura + vao
        self.botao_passo = self._botao([x0, y, largura, altura], "", self.proximo_passo)
        y -= altura + vao
        metade = (largura - vao) / 2
        self._botao([x0, y, metade, altura], "Reiniciar demonstração", self.reiniciar_demonstracao)
        self.botao_vista = self._botao([x0 + metade + vao, y, metade, altura], "", self.alternar_vista)
        y -= altura + vao
        self.botao_animar = self._botao([x0, y, metade, altura], "", self.alternar_animacao)
        self._botao([x0 + metade + vao, y, metade, altura], "Menu principal", self.tela_inicial)
        self.fig.text(x0, 0.012, "Arrastar: girar   |   Rolagem: zoom   |   Clique: selecionar\n"
                                 "Com um nó selecionado:  B = buscar   |   Delete = remover",
                      fontsize=7.5, color=SUAVE, linespacing=1.5)

        # Fundo da vista e cabeçalho ficam em eixos próprios, com fundo opaco:
        # redesenhá-los apaga o que havia antes, sem precisar refazer a janela toda.
        self.eixo_fundo = self.fig.add_axes(list(AREA), facecolor=FUNDO, zorder=-1)
        _sem_marcas(self.eixo_fundo)
        self.eixo_cabecalho = self.fig.add_axes([AREA[0], 0.932, AREA[2], 0.066], facecolor=FUNDO)
        _sem_marcas(self.eixo_cabecalho)
        self.texto_titulo = self.eixo_cabecalho.text(0.5, 0.62, "", ha="center", va="center", fontsize=12,
                                                     fontweight="bold", color=TEXTO)
        self.texto_resumo = self.eixo_cabecalho.text(0.5, 0.18, "", ha="center", va="center", fontsize=8.5,
                                                     color=SUAVE)
        self.eixo_registro = self.fig.add_axes([0.004, 0.006, 0.718, 0.2], facecolor="#081126")
        self.registrar([f"{c.nome} — digite um valor e use os botões, ou siga a demonstração guiada."])
        self.redesenhar()

    # -------------------------------------------------------------- desenho

    def eixo(self, retangulo, tres_d=False):
        """Cria um eixo dentro da vista. `retangulo` é relativo à vista (0 a 1)."""
        # Os eixos são REAPROVEITADOS de um desenho para o outro. Criar um eixo 3D
        # novo a cada operação deixava os tratadores de mouse dos antigos ligados
        # à janela, e eles se acumulavam até travar tudo.
        chave = (tuple(retangulo), tres_d)
        eixo = self._reserva.get(chave)
        if eixo is None:
            esquerda, base, largura, altura = retangulo
            absoluto = [AREA[0] + esquerda * AREA[2], AREA[1] + base * AREA[3],
                        largura * AREA[2], altura * AREA[3]]
            eixo = self.fig.add_axes(absoluto, projection="3d" if tres_d else None)
            self._reserva[chave] = eixo
        else:
            eixo.clear()
            eixo.set_visible(True)
        self.eixos.append(eixo)
        if tres_d:
            self.eixo_3d = eixo
            eixo.disable_mouse_rotation()   # o giro é feito aqui (_ao_mover), redesenhando só o modelo
        return eixo

    def _desligar_eixos_3d(self):
        """Tira da janela os tratadores de mouse que os eixos 3D registraram ao serem criados."""
        registro = self.fig.canvas.callbacks
        eixos = [eixo for (_, tres_d), eixo in self._reserva.items() if tres_d]
        for funcoes in list(registro.callbacks.values()):
            for cid, referencia in list(funcoes.items()):
                funcao = referencia()
                if any(getattr(funcao, "__self__", None) is eixo for eixo in eixos):
                    registro.disconnect(cid)

    def redesenhar(self):
        """Refaz a vista a partir do estado atual da árvore e atualiza cabeçalho, registro e botões."""
        if self.controle is None:
            return
        if self.eixo_3d is not None:
            # Guarda o ângulo em que o usuário deixou a câmera.
            self.elevacao, self.azimute = self.eixo_3d.elev, self.eixo_3d.azim
        for eixo in self.eixos:
            eixo.set_visible(False)     # fica guardado na reserva para o próximo desenho
        self.eixos, self.eixo_3d = [], None
        c = self.controle
        self.pontos = c.desenhar(self.vista_3d and c.tem_3d)
        self.texto_titulo.set_text(c.titulo)
        self.texto_resumo.set_text(c.resumo())

        if self.roteiro is None:
            self.botao_passo.label.set_text("Demonstração guiada: iniciar  (→)")
        elif self.passo >= len(self.roteiro):
            self.botao_passo.label.set_text("Demonstração concluída")
        else:
            self.botao_passo.label.set_text(f"Próximo passo  ({self.passo}/{len(self.roteiro)})  (→)")
        self.botao_vista.label.set_text("Vista: 3D" if self.vista_3d else "Vista: 2D")
        if not c.tem_3d:
            self.botao_vista.label.set_text("Vista: 2D (única)")
        self.botao_animar.label.set_text(("Animar passos: sim" if self.animar else "Animar passos: não")
                                         if c.animavel else "Animação: não se aplica")

        # Registro: as últimas linhas, com cor conforme o tipo.
        eixo = self.eixo_registro
        eixo.clear()
        _sem_marcas(eixo, LINHA)
        for i, linha in enumerate(self.linhas[-9:]):
            cor = (AMARELO if linha.startswith(">") else LARANJA if linha.startswith("!")
                   else CIANO if linha.startswith(("---", "===")) else TEXTO)
            eixo.text(0.008, 0.93 - i * 0.105, linha[:150], color=cor, fontsize=8, family="monospace",
                      va="top", transform=eixo.transAxes)
        self._pintar()

    def _ao_desenhar_tudo(self, evento):
        """Chamado pelo matplotlib depois de cada desenho completo da janela."""
        self._tela_completa = True

    def _pode_copiar(self):
        """Dá para redesenhar só um pedaço? Só depois de um desenho completo, e se a janela suportar."""
        return self._tela_completa and getattr(self.fig.canvas, "supports_blit", False)

    def _pintar(self):
        """Redesenha só o que muda depois de uma operação e copia para a tela."""
        if not self._pode_copiar():
            self.fig.canvas.draw_idle()         # desenho completo (tela nova ou janela sem "blit")
            return
        self.copiar([self.eixo_fundo, *self.eixos, self.eixo_cabecalho, self.eixo_registro,
                     self.botao_passo.ax, self.botao_vista.ax, self.botao_animar.ax])

    def copiar(self, partes):
        """Redesenha só os eixos pedidos e copia o resultado para a tela."""
        if not self._pode_copiar():
            self.fig.canvas.draw_idle()
            return
        for parte in partes:
            self.fig.draw_artist(parte)
        self.fig.canvas.blit(self.fig.bbox)

    def _realcar_botao(self, evento):
        """Realça o botão sob o cursor (borda e texto), redesenhando só o botão que mudou."""
        sob_o_cursor = next((b for b in self.widgets if evento.inaxes is b.ax), None)
        if sob_o_cursor is self._botao_realcado:
            return
        mudaram = []
        for botao, borda, texto in ((self._botao_realcado, LINHA, TEXTO), (sob_o_cursor, AMARELO, AMARELO)):
            if botao is not None:
                for lado in botao.ax.spines.values():
                    lado.set_color(borda)
                botao.label.set_color(texto)
                mudaram.append(botao.ax)
        self._botao_realcado = sob_o_cursor
        self.copiar(mudaram)

    def _pintar_3d(self):
        """Redesenha apenas o modelo 3D: é o que roda a cada movimento do mouse."""
        if not self._pode_copiar():
            self.fig.canvas.draw_idle()
            return
        self.fig.draw_artist(self.eixo_3d)
        self.fig.canvas.blit(self.eixo_3d.bbox)

    def mostrar_quadro(self):
        """Desenha agora (no meio de uma operação) e espera um pouco: usado pela animação."""
        self.redesenhar()
        if not self._pode_copiar():
            self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        time.sleep(self.pausa_do_quadro)

    def registrar(self, linhas):
        for linha in linhas:
            print(linha)                # o terminal guarda o histórico completo
        self.linhas.extend(linhas)

    # ---------------------------------------------------------------- ações

    def _agir(self, acao):
        """Executa uma ação do módulo; um Aviso vira mensagem em vez de derrubar o programa."""
        try:
            acao()
        except Aviso as aviso:
            self.registrar([f"! {aviso}"])
        self.redesenhar()

    def buscar(self):
        """Busca o nó selecionado com o clique; se não há nenhum, busca o que foi digitado."""
        c = self.controle
        c.buscar(c.texto_do_selecionado() if c.selecionado is not None else self.entrada.text)

    def _limpar_arvore(self):
        """Botão Limpar tudo: apaga a árvore inteira e cancela a demonstração em andamento."""
        self.controle.limpar()
        self.roteiro, self.passo = None, 0
        self.registrar(["> Tudo apagado: árvore vazia"])

    def proximo_passo(self):
        """Executa o próximo passo da demonstração guiada (o primeiro clique começa do zero)."""
        if self.controle is None:
            return
        if self.roteiro is None:
            self.controle.limpar()
            self.roteiro, self.passo = self.controle.roteiro(), 0
            self.registrar(["=== Demonstração guiada ==="])
        if self.passo >= len(self.roteiro):
            self.registrar(["=== Fim da demonstração ==="])
            self.redesenhar()
            return
        fase, acao = self.roteiro[self.passo]
        if self.passo == 0 or fase != self.roteiro[self.passo - 1][0]:
            self.registrar([f"--- {fase} ---"])
        self.passo += 1
        self._agir(acao)

    def reiniciar_demonstracao(self):
        """Volta a árvore ao vazio para a demonstração guiada começar de novo."""
        if self.controle is None:
            return
        self.controle.limpar()
        self.roteiro, self.passo = None, 0
        self.registrar(["=== Demonstração reiniciada ==="])
        self.redesenhar()

    def alternar_vista(self):
        """Botão Vista: troca entre o modelo 3D e o desenho 2D da mesma árvore."""
        if self.controle is None or not self.controle.tem_3d:
            return
        self.vista_3d = not self.vista_3d
        self.controle.ao_trocar_vista()
        self.redesenhar()

    def alternar_animacao(self):
        """Botão Animar passos: liga ou desliga a exibição de cada rotação ou divisão em separado."""
        if self.controle is None or not self.controle.animavel:
            return
        self.animar = not self.animar
        self.redesenhar()

    # -------------------------------------------------------------- eventos

    def _ao_teclar(self, evento):
        if self.controle is None:
            return
        if self.entrada.ativo:
            # Enquanto se digita no campo, as teclas são texto; Enter insere.
            if self.entrada.tecla(evento.key):
                self._agir(lambda: self.controle.inserir(self.entrada.text))
            return
        if evento.key == "delete":
            self._agir(self.controle.remover_selecionado)
        elif evento.key == "b" and self.controle.selecionado is not None:
            self._agir(self.buscar)
        elif evento.key == "right":
            self.proximo_passo()
        elif evento.key == "escape":
            self.controle.selecionado = None
            self.redesenhar()

    def _ao_pressionar(self, evento):
        self._pressionado = (evento.x, evento.y)
        if self.entrada is not None:
            # Clicar no campo dá o foco do teclado a ele; clicar fora tira.
            self.entrada.focar(evento.inaxes is self.entrada.eixo)
        if self.eixo_3d is not None and evento.inaxes is self.eixo_3d and evento.button == 1:
            # Pode ser o começo de um giro: guarda a câmera de partida.
            self._giro = (evento.x, evento.y, self.eixo_3d.elev, self.eixo_3d.azim)
            self._girando = False

    def _ao_mover(self, evento):
        """Com o botão apertado sobre o modelo 3D, o movimento do mouse gira a câmera."""
        eixo = self.eixo_3d
        if eixo is not None:
            # O eixo 3D do matplotlib pede um redesenho COMPLETO da janela a cada
            # movimento do mouse enquanto acha que um botão está apertado, mesmo com
            # o giro dele desligado. Era isso que travava. Este tratador roda antes
            # do dele, então basta dizer que não há botão apertado.
            eixo.button_pressed = None
        if self._giro is None or eixo is None:
            self._realcar_botao(evento)
            return
        x0, y0, elevacao, azimute = self._giro
        dx, dy = evento.x - x0, evento.y - y0
        if not self._girando:
            if dx * dx + dy * dy <= 25:
                return                  # ainda pode ser só um clique
            self._girando = True
            for rotulo in eixo.rotulos:
                rotulo.set_visible(False)       # sem os textos o giro fica bem mais leve
        # Atravessar o modelo de um lado ao outro com o mouse equivale a meia volta.
        eixo.view_init(elev=max(-89, min(89, elevacao - dy / eixo.bbox.height * 180)),
                       azim=azimute - dx / eixo.bbox.width * 180)
        self._pintar_3d()

    def _ao_soltar(self, evento):
        """Fim de um giro, ou clique (sem arrastar), que seleciona o nó mais próximo do cursor."""
        pressionado, self._pressionado = self._pressionado, None
        girou, self._giro, self._girando = self._girando, None, False
        if girou and self.eixo_3d is not None:
            for rotulo in self.eixo_3d.rotulos:
                rotulo.set_visible(True)
            self.elevacao, self.azimute = self.eixo_3d.elev, self.eixo_3d.azim
            self._pintar_3d()
            return
        if self.controle is None or pressionado is None or evento.button != 1:
            return
        dx, dy = evento.x - pressionado[0], evento.y - pressionado[1]
        if dx * dx + dy * dy > 25:
            return                      # arrasto fora do modelo: não é um clique
        escolhido = self.no_em(evento.x, evento.y)
        if escolhido is None:
            return
        self.controle.selecionado = escolhido
        self.controle.titulo = f"Selecionado: {escolhido} — Buscar (ou B) mostra o caminho, Delete remove"
        self.redesenhar()

    def na_tela(self, eixo, posicao):
        """Converte a posição de um nó (2D ou 3D) em pixels da janela."""
        if len(posicao) == 3:
            x, y, _ = proj3d.proj_transform(*posicao, eixo.get_proj())
            return eixo.transData.transform((x, y))
        return eixo.transData.transform(posicao)

    def no_em(self, x, y, alcance=24):
        """Identificador do nó desenhado mais perto do pixel (x, y), ou None se não há nenhum perto."""
        melhor, menor = None, alcance * alcance
        for identificador, eixo, posicao in self.pontos:
            px, py = self.na_tela(eixo, posicao)
            d = (px - x) ** 2 + (py - y) ** 2
            if d < menor:
                melhor, menor = identificador, d
        return melhor

    def _ao_rolar(self, evento):
        """Zoom: muda só os limites do modelo 3D, sem refazer o desenho."""
        eixo = self.eixo_3d
        if self.controle is None or eixo is None or evento.inaxes is not eixo:
            return
        self.zoom = min(3.0, max(0.6, self.zoom * (1.12 if evento.button == "up" else 1 / 1.12)))
        alcance = eixo.limite / self.zoom
        eixo.set_xlim(-alcance, alcance)
        eixo.set_ylim(-alcance, alcance)
        eixo.set_zlim(-alcance, alcance)
        self._pintar_3d()

    def executar(self):
        """Abre a janela e fica atendendo aos eventos até ela ser fechada."""
        plt.show()
