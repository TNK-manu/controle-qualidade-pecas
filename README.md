# Sistema de Controle de Qualidade de Peças

## Aluno
Emmanoel Shiroshi Tanaka  
RA: 237221  

---

## Descrição

Este projeto consiste no desenvolvimento de um sistema em Python para simulação de um processo de automação industrial voltado ao controle de qualidade de peças.

O sistema realiza a análise automática das peças com base em critérios pré-definidos, armazena as peças aprovadas em caixas com capacidade limitada e gera relatórios para acompanhamento do processo.

---

## Objetivo

O objetivo do sistema é demonstrar a aplicação de conceitos de lógica de programação em um cenário prático, incluindo:

- Estruturas condicionais
- Estruturas de repetição
- Organização modular do código
- Manipulação de banco de dados
- Simulação de processos automatizados

---

## Funcionalidades

- Cadastro manual de peças  
- Geração automática de peças (simulação de produção em lote)  
- Avaliação automática de qualidade  
- Armazenamento de peças aprovadas em caixas com limite de 10 unidades  
- Listagem de peças (todas, aprovadas ou reprovadas)  
- Remoção de peças com confirmação  
- Restrição de exclusão para peças em caixas já fechadas  
- Listagem de caixas fechadas  
- Exibição da caixa aberta atual  
- Geração de relatório final  
- Limpeza completa do banco de dados (reinício de lote)  
- Interface em terminal com uso de cores (Colorama)  

---

## Regras de Negócio

Uma peça será considerada **aprovada** quando atender simultaneamente aos seguintes critérios:

- Peso entre 95g e 105g  
- Cor azul ou verde  
- Comprimento entre 10cm e 20cm  

Caso contrário, será considerada **reprovada**, sendo registrados os motivos da reprovação.

---

## Estrutura do Sistema

O sistema foi desenvolvido utilizando funções para garantir organização e modularização do código:

- cadastrar_peca()  
- avaliar_peca()  
- armazenar_em_caixa()  
- listar_pecas()  
- remover_peca()  
- listar_caixas()  
- mostrar_caixa_aberta_atual()  
- gerar_relatorio()  
- limpar_banco_dados()  
- menu()  

---

## Tecnologias Utilizadas

- Python 3  
- SQLite (banco de dados local)  
- Colorama (interface no terminal)  

---

## Como Executar o Projeto

1. Instalar a biblioteca necessária:

```bash
pip install colorama
