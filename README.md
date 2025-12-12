# Análise de Grafos na Informática Forense

<p align="center">
  <img src="https://img.shields.io/badge/language-Python-blue?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/status-Completed-success?style=for-the-badge">
  <img src="https://img.shields.io/badge/course-Algorithms-orange?style=for-the-badge">
</p>

<p align="center">
  <a href="#-artigo-relacionado">Artigo Relacionado</a> •
  <a href="#-visão-geral-da-implementação">Visão Geral</a> •
  <a href="#-pré-requisitos">Pré-requisitos</a> •
  <a href="#-bibliotecas-necessárias">Bibliotecas</a> •
  <a href="#-como-executar">Como Executar</a> •
  <a href="#-estrutura-de-diretórios-importantes">Estrutura de Diretórios</a> •
  <a href="#-autor">Autor</a>
</p>

Este repositório contém a implementação dos algoritmos e scripts utilizados no artigo sobre aplicação de Teoria dos Grafos em investigações forenses digitais, utilizando o *dataset* de e-mails da Enron.

## 📄 Artigo Relacionado

A documentação completa da metodologia, fundamentação teórica e discussão dos resultados encontra-se no artigo associado a este projeto.

> [**Clique aqui para acessar o Artigo Completo**](LINK_DO_SEU_ARTIGO_AQUI)

---

## 💻 Visão Geral da Implementação

O projeto está estruturado em módulos Python que realizam desde o tratamento dos dados brutos até a análise de métricas complexas de redes.

* **Pré-processamento:** Limpeza e normalização do *dataset* Enron (extração de `From`, `To`, `Date`).
* **Análise Estática:** Cálculo de centralidades (Betweenness, PageRank, Closeness) e detecção de comunidades (Louvain).
* **Análise de Disrupção:** Simulação de ataques à rede para testar a resiliência da estrutura criminal/corporativa.
* **Visualização Interativa:** Geração de subgrafos dinâmicos em HTML focados nos atores mais relevantes da rede.

## 🛠️ Pré-requisitos

Para executar os scripts, é necessário ter o **Python 3.x** instalado. As dependências do projeto podem ser instaladas via `pip`.

### Bibliotecas Necessárias

Crie um ambiente virtual ou instale diretamente as bibliotecas listadas abaixo:

```bash
pip install pandas networkx matplotlib python-louvain pyvis
```

> **Nota:** A biblioteca de detecção de comunidades é a `python-louvain` (importada como `community`).

## 🚀 Como Executar

Siga a ordem de execução abaixo para garantir que os dados sejam gerados corretamente para as etapas subsequentes.

### 1. Clonar o Repositório

```bash
git clone https://github.com/ViniciusRO22/analise-de-grafos-na-informatica-forense.git
cd analise-de-grafos-na-informatica-forense
```

### 2. Pré-processamento dos Dados

Este script lê o arquivo bruto `EnronEmails.csv` e gera o arquivo tratado `EnronEmailsTratados.csv`.

```bash
python src/DataTreatment/PreProcessamento.py
```

Saídas geradas em: `dataSets/Outputs/`

### 3. Análise Estática de Redes

Gera os rankings de centralidade (CSV) e o mapeamento de comunidades (JSON).

```bash
python src/Analysis/AnaliseEstatica.py
```

Saídas geradas em: `dataSets/Outputs/`

### 4. Simulação de Disrupção

Executa a simulação de remoção de nós (ataques) e gera o gráfico comparativo de estratégias.

```bash
python src/Analysis/AnaliseDisrupcao.py
```

Saídas geradas em: `dataSets/Outputs/` como um gráfico

### 5. Visualização de Subgrafos 
Gera arquivos HTML interativos focados na vizinhança dos atores mais centrais (identificados nas métricas de Betweenness, PageRank e Closeness).

```bash
python src/Analysis/PlotSubGrafo.py
```

Saídas geradas: em `dataSets/Outputs/`  como arquivos `.html`
Exemplo: `subgrafo_interativo_jeff.skilling@enron.com.html`

### 6. Validação Estrutural 

Gera um arquivo de texto detalhando predecessores e sucessores de cada nó para conferência manual.

```bash
python src/Analysis/VisualizadorGrafo.py
```

Saídas geradas: em `dataSets/Outputs/`  como arquivos `.txt`


---

## 📂 Estrutura de Diretórios Importantes

- `src/Analysis/`: Scripts de cálculo de métricas, simulação e visualização (PlotSubGrafo.py).  
- `src/DataTreatment/`: Scripts de limpeza de dados.  
- `dataSets/Inputs/`: Local para o dataset bruto (`EnronEmails.csv`).  
- `dataSets/Outputs/`: Local onde os resultados (CSVs, JSONs, Gráficos, TXTs e HTMLs interativos) são salvos.

---

## 👨‍💻 Author

<div align="center">
  <a href="https://github.com/ViniciusRO22">
   <img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/ViniciusRO22?v=4" width="100px;" alt=""/>
   <br />
   <sub><b>ViniciusRO22</b></sub>
  </a>
  <br />
  <a href="https://github.com/ViniciusRO22" title="Rocketseat">🚀</a>
  <p>Made by <b>Vinicius</b>. Get in touch!</p>
  
  <a href="https://www.linkedin.com/in/vinícius-ramalho-de-oliveira-4464b8327" target="_blank">
    <img src="https://img.shields.io/badge/-LinkedIn-%230077B5?style=for-the-badge&logo=linkedin&logoColor=white" target="_blank">
  </a> 
  <a href="mailto:ramalhooliveiravini@gmail.com" target="_blank">
    <img src="https://img.shields.io/badge/-Gmail-%23D14836?style=for-the-badge&logo=gmail&logoColor=white" target="_blank">
  </a>
</div>
