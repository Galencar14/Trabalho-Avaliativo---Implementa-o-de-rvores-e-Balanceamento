# Árvore 2-3-4 em Python

Implementação de uma árvore 2-3-4 (não binária) feita do zero, sem bibliotecas de árvores.
Trabalho AV2 (Parte 1) - Teoria de Grafos - CESUPA.

## O que tem

- `arvore234.py`: a árvore (inserção, exclusão, busca, validação e plotagem)
- `main.py`: demonstração com 21 chaves, busca e exclusões
- `imagens/`: figuras geradas a cada operação

## Regras da árvore

- Cada nó tem de 1 a 3 chaves (2 a 4 filhos).
- Todas as folhas ficam no mesmo nível.
- **Elementos repetidos:** não são permitidos. Uma chave repetida é ignorada na inserção.

## Como funciona o balanceamento

- **Inserção:** ao descer, todo nó cheio (3 chaves) é dividido em dois e a chave do meio sobe para o pai.
- **Exclusão:** antes de descer, se o filho tem só 1 chave, ele pega emprestado de um irmão ou funde com ele.
- Se a raiz enche, a árvore cresce pela raiz. Se a raiz esvazia, a árvore diminui.

## Como executar

Precisa do Python 3.8 ou mais novo.

```
pip install -r requirements.txt
python main.py
```

As imagens aparecem na pasta `imagens/`.

## Integrantes

(preencher com os nomes da equipe)
