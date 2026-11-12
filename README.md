# Árvore Rubro-Negra — Controle de Estoque

Implementação de uma Árvore Rubro-Negra (Red-Black) do zero em Python, sem bibliotecas de árvore, aplicada ao controle de estoque de uma distribuidora de produtos regionais. Cada produto é identificado por um **código numérico** (chave da árvore).

## Estrutura

| Arquivo | Conteúdo |
|---|---|
| `rubro_negra.py` | Nó (`esq`, `dir`, `pai`, `cor`, `quantidade`) e a árvore: inserção + balanceamento, remoção + balanceamento, busca, percurso em ordem, validação das propriedades |
| `plotagem.py` | Desenho da árvore com matplotlib (nós vermelhos/pretos, nó afetado com borda amarela) |
| `main.py` | Aplicação de estoque: demonstração automática e menu interativo |
| `teste_aleatorio.py` | 300 rodadas aleatórias (semente fixa) de inserção, remoção de uma unidade e remoção do nó inteiro, validando as 5 propriedades e as quantidades após cada operação |

## Implementação

- **Nós encadeados** ao estilo de lista duplamente encadeada: cada nó aponta para os filhos e para o pai.
- **Sentinela NIL**: um único nó preto compartilhado representa todas as folhas nulas, o que simplifica as correções.
- Única estrutura auxiliar: uma lista Python usada como pilha no percurso em ordem iterativo.

## Elementos repetidos

A árvore **não cria nós duplicados**. Cada nó tem um campo `quantidade`:

- **Inserir** uma chave que já existe → `quantidade += 1` (entrada de mais uma unidade no estoque). A árvore não muda de forma, então não há balanceamento.
- **Remover** uma chave com `quantidade > 1` → `quantidade -= 1`, e o nó continua na árvore.
- **Remover** com `quantidade == 1` (ou com a opção "saída total") → o nó é removido de fato e a árvore é rebalanceada.

## Remoção de nó com dois filhos

O nó é substituído pelo **sucessor em ordem** (menor chave da subárvore direita).

## Como executar

Requisitos: Python 3.9+.

```bash
git clone https://github.com/Galencar14/Trabalho-Avaliativo---Implementa-o-de-rvores-e-Balanceamento.git
cd Trabalho-Avaliativo---Implementa-o-de-rvores-e-Balanceamento
git checkout rubro-negra
pip install -r requirements.txt
```

Demonstração completa (28 inserções, 2 repetições, 2 buscas, 7 remoções, terminando com 22 nós):

```bash
python main.py --demo
```

Cada passo é registrado no terminal (casos de balanceamento, recolorações e rotações) e salvo como imagem em `passos/001.png`, `passos/002.png`, ...

Modo interativo (abre uma janela com a árvore, atualizada a cada comando):

```bash
python main.py
```

| Comando | Ação |
|---|---|
| `i 10 20 30` | inserir um ou mais números |
| `r 20` | remover (uma unidade, se repetido) |
| `rt 20` | remover o nó inteiro |
| `b 15` | buscar (destaca o caminho percorrido) |
| `l` | listar em ordem e validar as propriedades |
| `p` | liga/desliga o passo a passo (mostra cada recoloração/rotação) |
| `e` | carregar o exemplo do estoque (28 produtos) |
| `x 25` | inserir 25 números aleatórios novos |
| `f` | salvar a imagem atual em `arvore.png` |
| `c` | limpar a árvore |
| `h` / `s` | ajuda / sair |

Após cada comando o terminal também mostra a árvore em texto, o número de nós, a altura e se as propriedades continuam válidas.

Teste de corretude:

```bash
python teste_aleatorio.py
```

## Casos de balanceamento cobertos na demonstração

**Inserção** (o novo nó entra vermelho):
1. Tio vermelho → recolorir pai, tio e avô; o problema sobe para o avô.
2. Tio preto, nó é filho interno → rotação no pai (vira o caso 3).
3. Tio preto, nó é filho externo → recolorir e rotacionar o avô.

**Remoção** (só corrige quando o nó removido era preto, gerando um "duplo preto"):
1. Irmão vermelho → recolorir e rotacionar o pai (vira caso 2, 3 ou 4).
2. Irmão preto com dois filhos pretos → irmão vira vermelho; o problema sobe.
3. Irmão preto, sobrinho interno vermelho → rotacionar o irmão (vira o caso 4).
4. Irmão preto, sobrinho externo vermelho → recolorir e rotacionar o pai. Fim.
