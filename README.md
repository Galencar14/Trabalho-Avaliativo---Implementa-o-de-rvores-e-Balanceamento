# Árvore 2-3-4 em Python

Trabalho Avaliativo AV2 (Parte 1) — Teoria dos Grafos — CESUPA

Implementação de uma árvore 2-3-4 (não binária) feita do zero, sem bibliotecas de árvores.

## O que tem

| Arquivo | Conteúdo |
|---|---|
| `arvore234.py` | A árvore: inserção, exclusão, busca, validação e plotagem |
| `main.py` | Demonstração com 21 chaves, buscas e exclusões |
| `teste_aleatorio.py` | 300 rodadas aleatórias de inserção e exclusão, validando a árvore após cada operação |
| `imagens/` | Figuras geradas a cada operação da demonstração |

## Regras da árvore

- Cada nó tem de 1 a 3 chaves (2 a 4 filhos).
- Todas as folhas ficam no mesmo nível.
- **Elementos repetidos:** não são permitidos. Uma chave repetida é ignorada na inserção.

## Como funciona o balanceamento

- **Inserção:** ao descer, todo nó cheio (3 chaves) é dividido em dois e a chave do meio sobe para o pai.
- **Exclusão:** antes de descer, se o filho tem só 1 chave, ele pega emprestado de um irmão ou funde com ele.
- Se a raiz enche, a árvore cresce pela raiz. Se a raiz esvazia, a árvore diminui.

Como a árvore só cresce e diminui pela raiz, todas as folhas continuam sempre no mesmo nível.

## Como executar

Requisitos: Python 3.9 ou mais novo.

```bash
git clone https://github.com/Galencar14/Trabalho-Avaliativo---Implementa-o-de-rvores-e-Balanceamento.git
cd Trabalho-Avaliativo---Implementa-o-de-rvores-e-Balanceamento
git checkout arvore-2-3-4
pip install -r requirements.txt
python main.py              # demonstração; as imagens aparecem na pasta imagens/
python teste_aleatorio.py   # teste de corretude
```

## Integrantes

- André Felipe Ribeiro Fernandes
- Lucas Sousa Jatene
- Brenno Yasuhei Tsuchiya
- Gustavo Alencar Sabóia Lobato
