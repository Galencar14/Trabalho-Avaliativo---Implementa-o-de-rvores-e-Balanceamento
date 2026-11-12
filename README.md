# Implementação de Árvores e Balanceamento

Trabalho Avaliativo AV2 (Parte 1) — Teoria dos Grafos — CESUPA

## Integrantes

- André Felipe Ribeiro Fernandes
- Lucas Sousa Jatene
- Brenno Yasuhei Tsuchiya
- Gustavo Alencar Sabóia Lobato

## Apresentação

[Slides no Canva](https://www.canva.com/design/DAHZnt_s2YQ/8Kr_Ssmix_L-WSR88pZl6A/edit)

## Branches

| Branch | Conteúdo |
|---|---|
| `arvore-2-3-4` | Árvore 2-3-4 (não binária): inserção, exclusão, busca e plotagem |
| `rubro-negra` | Árvore Rubro-Negra: inserção, exclusão, busca, plotagem e modo interativo |
| `arvore-kd` | Árvore k-D: explicação detalhada com exemplo, implementação e figuras |

## Como executar

Requisitos: Python 3.9 ou mais novo e Git.

```bash
git clone https://github.com/Galencar14/Trabalho-Avaliativo---Implementa-o-de-rvores-e-Balanceamento.git
cd Trabalho-Avaliativo---Implementa-o-de-rvores-e-Balanceamento
git checkout <nome-da-branch>
pip install -r requirements.txt
python main.py
```

### Árvore 2-3-4

```bash
git checkout arvore-2-3-4
python main.py
python teste_aleatorio.py
```

Insere 21 chaves, faz buscas e exclusões e salva uma imagem de cada passo na pasta `imagens/`.

### Árvore Rubro-Negra

```bash
git checkout rubro-negra
python main.py          # modo interativo
python main.py --demo   # demonstração automática
python teste_aleatorio.py
```

O modo interativo abre uma janela com a árvore, que é redesenhada a cada comando:

| Comando | Ação |
|---|---|
| `i 10 20 30` | inserir um ou mais números |
| `r 20` | remover (uma unidade, se repetido) |
| `rt 20` | remover o nó inteiro |
| `b 15` | buscar (destaca o caminho percorrido) |
| `l` | listar em ordem e validar as propriedades |
| `p` | liga/desliga o passo a passo (mostra cada recoloração e rotação) |
| `e` | carregar o exemplo do estoque (28 produtos) |
| `x 21` | inserir 21 números aleatórios novos |
| `f` | salvar a imagem atual em `arvore.png` |
| `c` | limpar a árvore |
| `h` / `s` | ajuda / sair |

A demonstração (`--demo`) simula o controle de estoque de uma distribuidora de produtos regionais. Cada produto é uma chave da árvore, e um PNG de cada passo é salvo na pasta `passos/`.

### Árvore k-D

```bash
git checkout arvore-kd
python main.py
python teste_aleatorio.py
```

O README dessa branch explica a árvore k-D passo a passo com um exemplo de 6 pontos no plano. O `main.py` executa esse mesmo exemplo (construção, inserção, busca, vizinho mais próximo, busca por intervalo e remoção) e salva as figuras na pasta `imagens/`.

## Decisões do projeto

- **Linguagem:** Python, com matplotlib para a plotagem.
- **Implementação:** nós encadeados, feitos à mão, sem nenhuma biblioteca de árvores.
  - Rubro-Negra: cada nó aponta para o filho esquerdo, o filho direito e o pai, como numa lista duplamente encadeada, e um nó sentinela `NIL` preto representa as folhas.
  - 2-3-4: cada nó guarda de 1 a 3 chaves e de 2 a 4 filhos.
  - k-D: cada nó guarda um ponto e compara uma coordenada por nível (x, y, x, y...).
- **Elementos repetidos:**
  - **2-3-4:** não são permitidos. Uma chave repetida é ignorada na inserção.
  - **Rubro-Negra:** não se cria um nó novo. Cada nó tem um contador `quantidade`, que aumenta quando a chave é inserida de novo. Na remoção, o contador diminui, e o nó só sai da árvore (com rebalanceamento) quando chega a zero.
  - **k-D:** são permitidos. Um ponto repetido vai para a subárvore direita (regra "maior ou igual"), e a remoção tira uma cópia por vez.
- **Remoção de nó com dois filhos (Rubro-Negra):** o nó é substituído pelo sucessor em ordem, que é a menor chave da subárvore direita.

## Balanceamento

| Árvore | Inserção | Exclusão |
|---|---|---|
| Rubro-Negra | O nó novo entra vermelho. Se o pai também for vermelho: **caso 1** (tio vermelho) recolore pai, tio e avô, e o problema sobe; **caso 2** (tio preto, nó interno) rotaciona o pai e vira o caso 3; **caso 3** (tio preto, nó externo) recolore e rotaciona o avô. No fim, a raiz é pintada de preto. | Só há correção quando o nó removido era preto ("duplo preto"): **caso 1** (irmão vermelho) recolore e rotaciona o pai; **caso 2** (irmão preto com filhos pretos) pinta o irmão de vermelho, e o problema sobe; **caso 3** (sobrinho interno vermelho) rotaciona o irmão e vira o caso 4; **caso 4** (sobrinho externo vermelho) recolore e rotaciona o pai, encerrando. |
| 2-3-4 | Na descida, todo nó cheio (3 chaves) é dividido em dois e a chave do meio sobe para o pai. Se a raiz está cheia, ela é dividida e a árvore cresce um nível. | Na descida, todo filho com só 1 chave recebe uma chave emprestada de um irmão (rotação pelo pai) ou é fundido com um irmão. Se a raiz fica vazia, a árvore diminui um nível. |
| k-D | A construção pela mediana gera uma árvore balanceada. A inserção não rebalanceia. | Não rebalanceia: o nó removido é substituído pelo ponto de menor coordenada, no eixo dele, da subárvore direita. |

Nas árvores Rubro-Negra e 2-3-4 o balanceamento é garantido após cada operação: a altura fica sempre em O(log n). Na árvore k-D ele depende da ordem das inserções; o usual é reconstruir a árvore de tempos em tempos.
