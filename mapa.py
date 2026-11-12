"""Módulo 3 — Mapa do céu (Árvore k-D).

Cada estrela é um ponto. A árvore responde perguntas de posição: qual estrela
está mais perto de um ponto, e quais estão a até certa distância dele.

O módulo mantém DUAS árvores k-D com as mesmas estrelas, uma para cada vista:
  - vista 2D: k = 2, com os pontos (ascensão reta, declinação) num mapa plano.
    É a melhor para entender a ideia: cada nó traça uma linha no mapa.
  - vista 3D: k = 3, com os pontos (x, y, z) na esfera celeste. É como os
    programas reais fazem, porque o céu é uma esfera e não um plano.
Toda inserção e remoção é aplicada nas duas. O código da árvore é o mesmo;
só muda o número de coordenadas (o "k").

Elementos repetidos: são permitidos. Duas estrelas podem ter a mesma
coordenada (uma estrela dupla); a segunda vai para a subárvore direita.
"""

import math

from arvore_kd import ArvoreKD
from controle import Aviso, Controle
from dados import ESTRELAS, EXTRAS, TRES_MARIAS, Estrela
from desenho import kd_arvore_2d, kd_esfera, kd_plano


def ler_numeros(texto, quantidade, exemplo):
    """Lê os primeiros `quantidade` números do texto; o resto é devolvido como nome."""
    partes = texto.split()
    try:
        numeros = [float(parte.replace(",", ".")) for parte in partes[:quantidade]]
        if len(numeros) < quantidade:
            raise ValueError
    except ValueError:
        raise Aviso(f"Digite {quantidade} números, por exemplo: {exemplo}") from None
    ra, dec = numeros[0], numeros[1]
    if not (0 <= ra <= 360 and -90 <= dec <= 90):
        raise Aviso("Coordenada fora do céu: ascensão reta de 0 a 360 e declinação de -90 a 90")
    return numeros, " ".join(partes[quantidade:])


def nomes(nos):
    """Nomes das estrelas de uma lista de nós, separados por vírgula (para as mensagens)."""
    return ", ".join(str(no.valor) for no in nos) or "(nenhuma)"


class Mapa(Controle):
    nome = "Mapa do céu"
    nome_da_arvore = "Árvore k-D"
    dica = "81.3 6.3 Bellatrix"
    extras = (("Mais próxima  (ra dec)", "mais_proxima"), ("No raio  (ra dec graus)", "no_raio"),
              ("Rebalancear", "rebalancear"))
    descricao = """Estrelas como pontos: ascensão reta e
declinação, em graus. A árvore compara uma
coordenada por nível, em rodízio.

USO REAL: quando o telescópio detecta um
objeto, é preciso achar a estrela catalogada
mais próxima. A biblioteca Astropy faz esse
cruzamento de catálogos com uma árvore k-D.

REPETIDOS: permitidos. Duas estrelas na mesma
coordenada (estrela dupla): a segunda vai
para a direita.

VISTAS: 2D = mapa plano, k = 2 (cada nó traça
um corte). 3D = esfera celeste, k = 3.
BALANCEAMENTO: não é automático. A árvore
nasce equilibrada pela mediana e precisa ser
reconstruída (botão Rebalancear)."""

    def nova(self):
        self.plana = ArvoreKD(k=2)      # pontos (ascensão reta, declinação)
        self.esfera = ArvoreKD(k=3)     # pontos (x, y, z) na esfera de raio 1
        self.consulta = {}              # última consulta, para destacar no desenho

    def limpar(self):
        """Além do que todo módulo limpa, esquece a última consulta."""
        super().limpar()
        self.consulta = {}

    def ao_trocar_vista(self):
        # Os nós visitados numa consulta dependem da árvore: não valem na outra vista.
        self.consulta = {}
        self.titulo = "Vista 3D: esfera celeste (k = 3)" if self.app.vista_3d else "Vista 2D: mapa plano (k = 2)"

    def texto_do_selecionado(self):
        # No mapa a busca é pela coordenada da estrela, não pelo nome.
        return f"{self.selecionado.ra} {self.selecionado.dec}"

    def _atual(self):
        """Árvore da vista que está na tela."""
        return self.esfera if self.app.vista_3d else self.plana

    def _ponto(self, ra, dec):
        """Converte (ascensão reta, declinação) no ponto da árvore da vista atual."""
        estrela = Estrela(0, "", "", ra, dec, 0)
        return estrela.esfera() if self.app.vista_3d else estrela.plano()

    def _publicar(self, cabecalho, mensagens=(), **consulta):
        """Publica a operação e guarda o que destacar no desenho: alvo, nós visitados, traçado..."""
        self.publicar(cabecalho, mensagens)
        self.consulta = consulta

    # --- operações ---

    def construir(self, estrelas):
        """Monta as duas árvores pela mediana: já nascem balanceadas."""
        self.plana.construir([(e.plano(), e) for e in estrelas])
        self.esfera.construir([(e.esfera(), e) for e in estrelas])
        self._publicar(f"> Construção pela mediana com {len(estrelas)} estrelas",
                       [f"Altura da árvore: {self._atual().altura()} (o mínimo possível para {len(estrelas)} nós "
                        f"é {math.ceil(math.log2(len(estrelas) + 1))})"])

    def adicionar(self, estrela):
        """Insere a estrela nas duas árvores e mostra por onde ela desceu na árvore da vista atual."""
        caminho_plano = self.plana.inserir(estrela.plano(), estrela)
        caminho_esfera = self.esfera.inserir(estrela.esfera(), estrela)
        caminho = caminho_esfera if self.app.vista_3d else caminho_plano
        self._publicar(f"> Inserir {estrela.nome} em ({estrela.ra}, {estrela.dec})",
                       [f"Desceu por: {nomes(caminho)}", "Sem rebalanceamento: entrou como folha"],
                       visitados={no.valor for no in caminho}, escolhidos={estrela})

    def inserir(self, texto):
        """Botão Inserir: lê 'ascensão_reta declinação nome' do campo de entrada."""
        (ra, dec), nome = ler_numeros(texto, 2, self.dica)
        self.adicionar(Estrela(0, nome or "sem nome", "-", ra, dec, 1.5))

    def buscar(self, texto):
        """Botão Buscar: busca exata pela coordenada, na árvore da vista atual. O caminho vira o traçado."""
        (ra, dec), _ = ler_numeros(texto, 2, "81.3 6.3")
        no, caminho = self._atual().buscar(self._ponto(ra, dec))
        resultado = f"encontrada {no.valor}" if no else "não há estrela nessa coordenada"
        self._publicar(f"> Busca exata por ({ra}, {dec}): {resultado}",
                       [f"Caminho: {nomes(caminho)}", f"Nós visitados: {len(caminho)}"],
                       visitados={n.valor for n in caminho}, escolhidos={no.valor} if no else set(),
                       caminho=[n.valor for n in caminho])

    def mais_proxima(self, texto):
        (ra, dec), _ = ler_numeros(texto, 2, "100 -20")
        arvore = self._atual()
        vizinho, distancia, visitados, podas = arvore.vizinho_mais_proximo(self._ponto(ra, dec))
        if vizinho is None:
            raise Aviso("O mapa está vazio")
        if self.app.vista_3d:
            # Na esfera a árvore mede a corda (linha reta); convertemos para o ângulo.
            distancia = math.degrees(2 * math.asin(min(1.0, distancia / 2)))
        self._publicar(f"> Mais próxima de ({ra}, {dec}): {vizinho.valor}, a {distancia:.1f} graus",
                       [f"Nós visitados: {len(visitados)} de {arvore.tamanho} ({nomes(visitados)})",
                        f"Podas: em {len(podas)} nós o outro lado do corte foi descartado sem ser visitado"],
                       alvo=(ra, dec), vizinho=vizinho.valor, visitados={n.valor for n in visitados},
                       escolhidos={vizinho.valor})

    def no_raio(self, texto):
        (ra, dec, graus), _ = ler_numeros(texto, 3, "84 -1 12")
        if graus <= 0:
            raise Aviso("O raio deve ser maior que zero")
        arvore = self._atual()
        # Na esfera, um ângulo vira o comprimento da corda correspondente.
        raio = 2 * math.sin(math.radians(min(graus, 180)) / 2) if self.app.vista_3d else graus
        achados, visitados = arvore.busca_por_raio(self._ponto(ra, dec), raio)
        self._publicar(f"> Estrelas a até {graus:g} graus de ({ra}, {dec}): {len(achados)}",
                       [f"Encontradas: {nomes(achados)}", f"Nós visitados: {len(visitados)} de {arvore.tamanho}"],
                       alvo=(ra, dec), raio=graus, visitados={n.valor for n in visitados},
                       escolhidos={n.valor for n in achados})

    def remover(self, estrela):
        era_raiz = self._atual().raiz is not None and self._atual().raiz.valor is estrela
        # `estrela` como segundo argumento garante que as duas árvores removem a mesma cópia.
        self.plana.remover(estrela.plano(), estrela)
        self.esfera.remover(estrela.esfera(), estrela)
        mensagens = ["Substituto: o menor ponto da subárvore direita, no eixo do nó removido"]
        if era_raiz and self._atual().raiz is not None:
            mensagens.append(f"Era a raiz. Nova raiz: {self._atual().raiz.valor}")
        self._publicar(f"> Remover {estrela.nome}", mensagens)

    def remover_selecionado(self):
        """Tecla Delete: remove a estrela em que o usuário clicou."""
        if self.selecionado is None:
            raise Aviso("Clique em uma estrela para selecioná-la antes de remover")
        self.remover(self.selecionado)

    def remover_raiz(self):
        """Passo da demonstração: remove a raiz, o caso que mais reorganiza a árvore."""
        if self._atual().raiz is None:
            raise Aviso("O mapa está vazio")
        self.remover(self._atual().raiz.valor)

    def rebalancear(self, texto=""):
        """Botão Rebalancear: reconstrói as duas árvores pela mediana e mostra a altura antes e depois."""
        antes = self._atual().altura()
        self.plana.reconstruir()
        self.esfera.reconstruir()
        self._publicar("> Rebalancear: árvore reconstruída pela mediana",
                       [f"Altura: {antes} -> {self._atual().altura()}"])

    def carregar_exemplo(self):
        """Recomeça o mapa com todas as estrelas de exemplo, já construído pela mediana."""
        self.limpar()
        self.construir(ESTRELAS + TRES_MARIAS + EXTRAS)

    # --- exibição ---

    def resumo(self):
        """Linha de estado: número de estrelas, altura de cada uma das duas árvores e validação."""
        ok2, _ = self.plana.validar()
        ok3, _ = self.esfera.validar()
        return (f"Estrelas: {self.plana.tamanho}   |   altura da árvore k = 2: {self.plana.altura()}   |   "
                f"altura da árvore k = 3: {self.esfera.altura()}   |   regra da k-D: "
                f"{'OK' if ok2 and ok3 else 'VIOLADA'}")

    def desenhar(self, tres_d):
        arvore = self.esfera if tres_d else self.plana
        c = self.consulta
        # A consulta guarda estrelas; o desenho precisa dos nós da árvore da vista.
        nos = arvore.em_ordem()
        visitados = [no for no in nos if no.valor in c.get("visitados", ())]
        escolhidos = [no for no in nos if no.valor in c.get("escolhidos", ())]
        vizinho = next((no for no in nos if no.valor is c.get("vizinho")), None)
        # Traçado da busca exata: as estrelas visitadas, em ordem, viram os nós desta árvore.
        por_estrela = {id(no.valor): no for no in nos}
        caminho = [por_estrela[id(e)] for e in c.get("caminho", ()) if id(e) in por_estrela]
        alvo = c.get("alvo")
        if tres_d:
            eixo = self.app.eixo((0, 0, 0.6, 1), True)
            ponto = Estrela(0, "", "", alvo[0], alvo[1], 0).esfera() if alvo else None
            pontos = kd_esfera(eixo, arvore, self.app.visao, ponto, vizinho, visitados, escolhidos,
                               self.selecionado, caminho)
        else:
            eixo = self.app.eixo((0.07, 0.11, 0.5, 0.8))
            pontos = kd_plano(eixo, arvore, alvo, vizinho, escolhidos, self.selecionado, c.get("raio"), caminho)
        diagrama = self.app.eixo((0.6, 0.04, 0.4, 0.9))
        return pontos + kd_arvore_2d(diagrama, arvore, visitados, escolhidos, self.selecionado, caminho)

    def roteiro(self):
        passos = [(f"1. Construção pela mediana com {len(ESTRELAS)} estrelas", lambda: self.construir(ESTRELAS))]
        fase = "2. Inserção das Três Marias: uma coordenada por nível"
        for estrela in TRES_MARIAS:
            passos.append((fase, lambda e=estrela: self.adicionar(e)))
        # Estrela dupla: duas estrelas na mesma coordenada.
        fase = "3. Coordenada repetida: permitida, vai para a direita"
        dupla = EXTRAS[4]
        companheira = Estrela(0, dupla.nome + " B", dupla.constelacao, dupla.ra, dupla.dec, 1.3)
        for estrela in (dupla, companheira):
            passos.append((fase, lambda e=estrela: self.adicionar(e)))
        fase = "4. Busca exata"
        for texto in ("247.4 -26.4", "150 0"):
            passos.append((fase, lambda t=texto: self.buscar(t)))
        fase = "5. Vizinho mais próximo: que estrela é o objeto detectado?"
        for texto in ("100 -20", "200 -55"):
            passos.append((fase, lambda t=texto: self.mais_proxima(t)))
        fase = "6. Busca por raio: as estrelas em volta do cinturão de Órion"
        for estrela in EXTRAS[:2]:      # Bellatrix e Saiph completam a constelação
            passos.append((fase, lambda e=estrela: self.adicionar(e)))
        passos.append((fase, lambda: self.no_raio("84 -1 12")))
        passos.append(("7. Remoção da raiz", self.remover_raiz))
        passos.append(("8. Balanceamento: reconstruir pela mediana", self.rebalancear))
        return passos
