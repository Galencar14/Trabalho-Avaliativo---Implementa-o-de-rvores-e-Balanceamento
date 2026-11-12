"""Módulo 1 — Agenda do telescópio (Árvore Rubro-Negra).

A chave é o horário da observação. A agenda precisa de duas coisas ao mesmo
tempo: aceitar pedidos em qualquer ordem e entregar sempre o MAIS CEDO. Na
rubro-negra as duas custam O(log n), porque a árvore se rebalanceia a cada
inserção e a cada remoção.

Elementos repetidos: dois pedidos no mesmo horário NÃO criam dois nós. O nó
daquele horário ganha um contador (quantidade) e os alvos formam uma fila.
"""

from controle import Animado, Aviso, Controle
from dados import OBSERVACOES
from desenho import rubro_negra_2d, rubro_negra_3d
from rubro_negra import ArvoreRubroNegra

INICIO_DA_NOITE = 18 * 60       # a noite de observação vai das 18:00 às 06:00


class Horario(int):
    """Minutos desde as 18:00. Ordena como número, mas aparece escrito como HH:MM.

    Por ser um int, a árvore compara horários sem saber que são horários.
    """

    def __str__(self):
        """Escreve o horário como HH:MM: é o que aparece nos nós e no registro."""
        total = (INICIO_DA_NOITE + int(self)) % (24 * 60)
        return f"{total // 60:02d}:{total % 60:02d}"

    __repr__ = __str__

    @classmethod
    def ler(cls, texto):
        """Converte "23:40" em Horario. Lança Aviso se não for um horário da noite."""
        try:
            horas, minutos = (int(parte) for parte in texto.split(":"))
            if not (0 <= horas < 24 and 0 <= minutos < 60):
                raise ValueError
            desde_o_inicio = (horas * 60 + minutos - INICIO_DA_NOITE) % (24 * 60)
            if desde_o_inicio >= 12 * 60:
                raise ValueError        # entre 06:00 e 18:00 é dia: o telescópio não observa
        except ValueError:
            raise Aviso(f'Horário inválido: "{texto}". Use HH:MM, entre 18:00 e 05:59') from None
        return cls(desde_o_inicio)


class Agenda(Animado, Controle):
    nome = "Agenda do telescópio"
    nome_da_arvore = "Árvore Rubro-Negra"
    dica = "23:40 Marte"
    animavel = True
    extras = (("Executar a mais cedo", "executar_proxima"),)
    descricao = """Pedidos de observação da noite, ordenados
pelo horário. O telescópio sempre executa o
mais cedo (o menor nó da árvore).

USO REAL: os temporizadores do kernel Linux
(hrtimers) ficam numa árvore rubro-negra
ordenada pelo horário de disparo. É o mesmo
mecanismo desta agenda.

REPETIDOS: dois pedidos no mesmo horário não
criam outro nó; somam no contador (×2, ×3).

NÓS: vermelho = vermelho; escuro com contorno
claro = preto.
BALANCEAMENTO: recolorações e rotações, a
cada inserção e a cada remoção."""

    def nova(self):
        self.arvore = ArvoreRubroNegra()
        self.arvore.ao_mudar = self.quadro      # permite animar cada rotação

    def _publicar(self, cabecalho, destaques=()):
        """Publica a operação junto com tudo que a árvore registrou ao executá-la."""
        mensagens = list(self.arvore.log)
        self.arvore.log.clear()
        self.publicar(cabecalho, mensagens, destaques)

    # --- operações ---

    def pedir(self, horario, alvo):
        """Novo pedido de observação: inserção na árvore."""
        no = self.arvore.inserir(horario, [alvo])
        if no.quantidade > 1:
            no.valor.append(alvo)       # horário já ocupado: o alvo entra na fila do nó
        self._publicar(f"> Pedido das {horario}: {alvo}", (horario,))

    def inserir(self, texto):
        """Botão Inserir: lê 'HH:MM alvo' do campo de entrada e registra o pedido."""
        partes = texto.split()
        if not partes:
            raise Aviso("Digite o horário e o alvo, por exemplo: 23:40 Marte")
        self.pedir(Horario.ler(partes[0]), " ".join(partes[1:]) or "alvo sem nome")

    def buscar(self, texto):
        """Botão Buscar: procura o horário e publica o caminho percorrido, que vira o traçado amarelo."""
        if not texto.strip():
            raise Aviso("Digite o horário a buscar, por exemplo: 23:40")
        horario = Horario.ler(texto.split()[0])
        no, caminho = self.arvore.buscar(horario)
        resultado = f"encontrado: {', '.join(no.valor)}" if no else "horário livre"
        self.publicar(f"> Busca por {horario}: {resultado}",
                      [f"Caminho: {' -> '.join(map(str, caminho)) or '(árvore vazia)'}",
                       f"Comparações: {len(caminho)}"], tuple(caminho), tuple(caminho))

    def executar_proxima(self, texto=""):
        """O telescópio executa a observação mais cedo: remoção do menor nó."""
        no = self.arvore.minimo()
        if no is None:
            raise Aviso("A agenda está vazia: não há observação a executar")
        horario, alvo = no.chave, no.valor[0]
        if no.quantidade > 1:
            no.valor.pop(0)             # ainda há fila: só o primeiro alvo sai
        self.arvore.remover(horario)
        self._publicar(f"> Executada a mais cedo: {horario} — {alvo}")

    def cancelar(self, horario):
        """Cancela todos os pedidos de um horário: remove o nó inteiro."""
        if not self.arvore.remover(horario, todas=True):
            self.arvore.log.clear()
            raise Aviso(f"Não há pedido às {horario}")
        self._publicar(f"> Removido o nó das {horario}")

    def remover_selecionado(self):
        """Tecla Delete: remove o nó em que o usuário clicou."""
        if self.selecionado is None:
            raise Aviso("Clique em um nó para selecioná-lo antes de remover")
        self.cancelar(self.selecionado)

    def carregar_exemplo(self):
        """Recomeça a agenda já com os pedidos de exemplo, sem mostrar o passo a passo."""
        self.limpar()
        for hora, alvo in OBSERVACOES:
            self.arvore.inserir(Horario.ler(hora), [alvo])
        self.arvore.log.clear()
        self.publicar(f"> Exemplo carregado: {len(OBSERVACOES)} pedidos de observação")

    # --- exibição ---

    def resumo(self):
        """Linha de estado da árvore: tamanho, altura e se as propriedades rubro-negras continuam valendo."""
        ok, info = self.arvore.validar()
        return (f"Nós: {self.arvore.tamanho}   |   altura: {self.arvore.altura()}   |   "
                f"propriedades rubro-negras: {'OK' if ok else 'VIOLADAS'} ({info})")

    def desenhar(self, tres_d):
        """Desenha a árvore na vista 3D ou na 2D e devolve os pontos clicáveis."""
        if tres_d:
            eixo = self.app.eixo((0, 0, 1, 1), True)
            return rubro_negra_3d(eixo, self.arvore, self.app.visao, self.destaques, self.selecionado,
                                  self.caminho)
        eixo = self.app.eixo((0.01, 0.02, 0.98, 0.94))
        return rubro_negra_2d(eixo, self.arvore, self.destaques, self.selecionado, caminho=self.caminho)

    def roteiro(self):
        h = Horario.ler
        passos = []
        fase = f"1. Os {len(OBSERVACOES)} pedidos chegam fora de ordem (inserção + balanceamento)"
        for hora, alvo in OBSERVACOES:
            passos.append((fase, lambda hora=hora, alvo=alvo: self.pedir(h(hora), alvo)))
        fase = "2. Horário repetido: não cria nó, soma no contador"
        for alvo in ("Rigel", "Betelgeuse"):
            passos.append((fase, lambda alvo=alvo: self.pedir(h("23:00"), alvo)))
        fase = "3. Busca"
        for hora in ("01:30", "02:10"):
            passos.append((fase, lambda hora=hora: self.buscar(hora)))
        fase = "4. O telescópio executa as mais cedo (remoção + balanceamento)"
        passos += [(fase, self.executar_proxima)] * 6
        # Escolhidos para completar, junto com a fase 4, os 4 casos de remoção.
        fase = "5. Cancelamentos no meio da noite (remoção de nós internos)"
        for hora in ("00:30", "23:00", "01:30"):
            passos.append((fase, lambda hora=hora: self.cancelar(h(hora))))
        return passos
