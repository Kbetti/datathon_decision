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
│   ├── raw/
│   │   ├── applicants_raw.json
│   │   ├── prospects_raw.json
│   │   └── vagas_raw.json
│   ├── candidatos.csv
│   └── vagas.csv
│
├── artifacts/
│   ├── artefatos_features.joblib
│   ├── colunas_training.joblib
│   ├── exemplo_tn_streamlit.csv
│   ├── exemplo_tp_streamlit.csv
│   └── modelo_recrutamento_rf.joblib
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

1. Certifique-se de ter o **Python 3.8+** instalado.
2. Clone este repositório em sua máquina local:
   ```bash
   git clone https://github.com/Kbetti/datathon_decision.git
   cd datathon_decision

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

4. **Saída**
O navegador será aberto automaticamente com o painel interativo, onde você poderá explorar:
Dados processados.
Detalhes das melhores predições e insights gerados.

## 📌 Desenvolvimento Futuro

Implementação de novos indicadores de compatibilidade.

Integração de funcionalidades híbridas no modelo.

