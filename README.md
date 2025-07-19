# 📌 Pipeline de Recrutamento Otimizado

Bem-vindo ao repositório do **Pipeline de Recrutamento Otimizado**, uma solução robusta e modular para automatização de processos de recrutamento e seleção, integrando dados de vagas e candidatos com análises avançadas e aprendizado de máquina.

## 📝 Sobre o Projeto

Este projeto visa otimizar o processo de **ranqueamento e análise** de candidatos baseado em sua compatibilidade com vagas, a partir de dados estruturados e técnicas de aprendizado de máquina. 

Principais funcionalidades:
- **Automação** de coleta, limpeza e pré-processamento de dados.
- **Engenharia de Features** para avaliação detalhada dos candidatos em relação às vagas.
- **Modelagem Preditiva** utilizando **LightGBM** para propor rankings confiáveis.
- **Painel Interativo** com filtros avançados permitindo a análise dinâmica dos resultados.

---

## 📂 Estrutura do Repositório

```plaintext
├── data/
│   ├── raw/                  # Dados brutos originais (ex.: JSONs de vaga/candidato).
│   ├── processed/            # Dados limpos e organizados prontos para modelagem (CSV).
│
├── artifacts/
│   ├── modelos/              # Modelos treinados e serializados (`joblib`).
│   ├── artefatos/            # Colunas e artefatos de engenharia de features.
│
├── notebook/
│   ├── modelo_recrutamento_rf.py      # Código de pré-processamento.
│
├── README.md                 # Documentação principal (este arquivo).
├── requirements.txt          # Dependências do projeto.

```

## 🔧 Tecnologias Utilizadas
- **Linguagem:** Python `>=3.8`
- **Bibliotecas Essenciais:**
  - **Manipulação de Dados:** `pandas`, `numpy`
  - **Aprendizado de Máquina:** `lightgbm`, `scikit-learn`
  - **Deploy Interativo:** `streamlit`
  - **Serialização e Persistência:** `joblib`

---

## 🚀 Como Executar

### 1️⃣ Instalação

1. Certifique-se de ter o **Python 3.8+** instalado.
2. Clone este repositório em sua máquina local:
   ```bash
   git clone https://github.com/Kbetti/datathon_decision.git
   cd datathon_decision
``

### 2️⃣ Execução do Pipeline

#### Organização Inicial:
Certifique-se de que os dados originais necessários para o pipeline (no formato JSON) estejam no diretório `data/raw/`.

#### Etapas de Execução:

1. **Pré-processamento de Dados**  
   Este script realiza a limpeza, padronização e organização dos dados de vagas e candidatos para que fiquem prontos para a etapa de modelagem. 

2. **Treinamento do Modelo**
Treine o modelo preditivo utilizando o algoritmo LightGBM. Este script também persiste o modelo treinado e as colunas/features relevantes

3. **Execução do Painel Interativo**
Depois de realizar o pré-processamento e o treinamento, abra o painel interativo para explorar os resultados gerados

#### Características do Painel:
**Filtros Avançados:** Permite filtrar candidatos por modalidade, nível profissional, nível acadêmico, entre outros.
**Ranking de Candidatos:** Exposição visual dos candidatos classificados de acordo com a compatibilidade com as vagas.
**Exportação de Resultados:** Opção para exportar os rankings gerados em formatos personalizados.

## 🛠️ Pipeline Detalhado


### Etapas do Pipeline
1. **Extração e Pré-processamento**
   
Entrada:
Arquivos JSON contendo os dados brutos das vagas (vagas.json) e dos candidatos (candidatos.json).


Ações Realizadas:

Padronização de colunas, como:
nivel_academico
nivel_profissional
pcd (Pessoa com Deficiência)
Tratamento de duplicatas e valores ausentes nos dados.
Uso de expressões regulares para consolidar competências técnicas nas colunas _skills.

2. **Engenharia de Features**

   
Criação de Atributos:

Compatibilidade Linguística: Avalia se o candidato atende os requisitos de idiomas (e.g. inglês e espanhol) exigidos pela vaga.

Skills Match: Calcula o número total de _skills compatíveis entre o candidato e a vaga.

Análise de Gaps: Identifica as skills exigidas pela vaga que o candidato não possui.


3. **Modelagem**

   
Modelo Utilizado:

LightGBM, escolhido por sua performance e eficiência em conjuntos de dados relativamente grandes.

Configurações do Modelo:

Principais hiperparâmetros:
n_estimators=200
learning_rate=0.05
max_depth=7
Balanceamento das classes-alvo para lidar com desbalanceamento nos dados.
Persistência de Artefatos:

Modelo treinado, colunas-chave e artefatos de engenharia de features são salvos usando o Joblib.

4. **Avaliação e Visualização**

Accuracy (Acurácia): Medida da porcentagem de previsões corretas.
Resultado: 87.3%
ROC-AUC: Área sob a curva ROC, avalia a discriminação do modelo entre as classes.
Resultado: 94.1%
Precision (Precisão): Taxa de previsão positiva verdadeira.
Resultado: 86.5%
Outras Visualizações no Painel:

As métricas e resultados do treino/validação são exibidos diretamente no painel Streamlit para uma interação prática e personalizada.
