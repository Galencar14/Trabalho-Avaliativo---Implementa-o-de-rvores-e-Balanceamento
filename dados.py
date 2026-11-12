"""Dados de exemplo do observatório.

As estrelas são reais. O número é o do Bright Star Catalogue (HR). As
coordenadas (ascensão reta e declinação, em graus) estão arredondadas para uma
casa decimal e a magnitude (brilho) é aproximada: servem para a demonstração,
não para apontar um telescópio.
"""

import math


class Estrela:
    """Registro de uma estrela. É o "valor" guardado nas árvores do catálogo e do mapa."""

    def __init__(self, numero, nome, constelacao, ra, dec, magnitude):
        self.numero = numero            # número no catálogo HR (chave do catálogo)
        self.nome = nome
        self.constelacao = constelacao
        self.ra = ra                    # ascensão reta, em graus (0 a 360)
        self.dec = dec                  # declinação, em graus (-90 a 90)
        self.magnitude = magnitude      # quanto MENOR, mais brilhante

    def __str__(self):
        """O nome é o que aparece nos rótulos e nas mensagens."""
        return self.nome

    def plano(self):
        """Posição no mapa plano: (ascensão reta, declinação)."""
        return (self.ra, self.dec)

    def esfera(self):
        """Posição na esfera celeste: ponto (x, y, z) de raio 1.

        É assim que os programas reais guardam posições no céu: em 3
        coordenadas, a distância em linha reta entre dois pontos cresce junto
        com o ângulo entre eles, então "mais próximo" continua valendo.
        """
        ra, dec = math.radians(self.ra), math.radians(self.dec)
        return (math.cos(dec) * math.cos(ra), math.cos(dec) * math.sin(ra), math.sin(dec))


def _estrelas(linhas):
    """Transforma cada linha (tupla) da tabela num objeto Estrela."""
    return [Estrela(*linha) for linha in linhas]


# (número HR, nome, constelação, ascensão reta, declinação, magnitude)
ESTRELAS = _estrelas([
    (2491, "Sirius", "Cão Maior", 101.3, -16.7, -1.5),
    (2326, "Canopus", "Carina", 96.0, -52.7, -0.7),
    (5340, "Arcturus", "Boieiro", 213.9, 19.2, -0.1),
    (7001, "Vega", "Lira", 279.2, 38.8, 0.0),
    (1708, "Capella", "Cocheiro", 79.2, 46.0, 0.1),
    (1713, "Rigel", "Órion", 78.6, -8.2, 0.1),
    (2943, "Procyon", "Cão Menor", 114.8, 5.2, 0.3),
    (2061, "Betelgeuse", "Órion", 88.8, 7.4, 0.4),
    (472, "Achernar", "Erídano", 24.4, -57.2, 0.5),
    (5267, "Hadar", "Centauro", 210.9, -60.4, 0.6),
    (7557, "Altair", "Águia", 297.7, 8.9, 0.8),
    (4730, "Acrux", "Cruzeiro do Sul", 186.6, -63.1, 0.8),
    (1457, "Aldebaran", "Touro", 69.0, 16.5, 0.9),
    (6134, "Antares", "Escorpião", 247.4, -26.4, 1.0),
    (5056, "Spica", "Virgem", 201.3, -11.2, 1.0),
    (2990, "Pollux", "Gêmeos", 116.3, 28.0, 1.1),
    (8728, "Fomalhaut", "Peixe Austral", 344.4, -29.6, 1.2),
    (7924, "Deneb", "Cisne", 310.4, 45.3, 1.3),
    (4853, "Mimosa", "Cruzeiro do Sul", 191.9, -59.7, 1.3),
    (3982, "Regulus", "Leão", 152.1, 12.0, 1.4),
    (2618, "Adhara", "Cão Maior", 104.7, -29.0, 1.5),
    (2891, "Castor", "Gêmeos", 113.6, 31.9, 1.6),
    (4763, "Gacrux", "Cruzeiro do Sul", 187.8, -57.1, 1.6),
    (6527, "Shaula", "Escorpião", 263.4, -37.1, 1.6),
])

# Estrelas que entram depois, durante as demonstrações.
TRES_MARIAS = _estrelas([
    (1852, "Mintaka", "Órion", 83.0, -0.3, 2.2),
    (1903, "Alnilam", "Órion", 84.1, -1.2, 1.7),
    (1948, "Alnitak", "Órion", 85.2, -1.9, 1.8),
])
EXTRAS = _estrelas([
    (1790, "Bellatrix", "Órion", 81.3, 6.3, 1.6),
    (2004, "Saiph", "Órion", 86.9, -9.7, 2.1),
    (1791, "Elnath", "Touro", 81.6, 28.6, 1.7),
    (424, "Polaris", "Ursa Menor", 37.9, 89.3, 2.0),
    (5459, "Rigil Kentaurus", "Centauro", 219.9, -60.8, -0.3),
])

# Pares de estrelas ligados por uma linha no mapa (só desenho, não fazem parte das árvores).
CONSTELACOES = [
    ("Betelgeuse", "Bellatrix"), ("Betelgeuse", "Alnitak"), ("Bellatrix", "Mintaka"),
    ("Mintaka", "Alnilam"), ("Alnilam", "Alnitak"), ("Alnitak", "Saiph"),
    ("Mintaka", "Rigel"), ("Saiph", "Rigel"),               # Órion
    ("Acrux", "Gacrux"), ("Hadar", "Rigil Kentaurus"),      # Cruzeiro do Sul e os "guardas"
    ("Castor", "Pollux"), ("Sirius", "Adhara"), ("Antares", "Shaula"),
]

# Pedidos de observação da noite, na ordem em que chegam (fora de ordem de horário).
# (horário, alvo)
OBSERVACOES = [
    ("23:00", "Nebulosa de Órion (M42)"),
    ("20:00", "Júpiter"),
    ("02:00", "Ômega Centauri"),
    ("19:20", "Lua"),
    ("21:00", "Plêiades (M45)"),
    ("00:30", "Eta Carinae"),
    ("03:00", "Nebulosa da Lagoa (M8)"),
    ("19:00", "Saturno"),
    ("19:40", "Galáxia de Andrômeda (M31)"),
    ("20:30", "47 Tucanae"),
    ("21:40", "Pequena Nuvem de Magalhães"),
    ("00:00", "Grande Nuvem de Magalhães"),
    ("01:00", "Caixa de Joias (NGC 4755)"),
    ("02:30", "Centaurus A"),
    ("03:40", "Nebulosa Trífida (M20)"),
    ("04:20", "Nebulosa da Águia (M16)"),
    ("21:20", "Galáxia do Escultor (NGC 253)"),
    ("22:00", "Nebulosa do Caranguejo (M1)"),
    ("22:30", "Nebulosa da Tarântula"),
    ("23:20", "Marte"),
    ("23:40", "Galáxia do Sombreiro (M104)"),
    ("01:30", "Galáxia Cata-vento do Sul (M83)"),
]
