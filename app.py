import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import re

#  Configuração da Página
st.set_page_config(layout="wide", page_title="Painel de Recrutamento e Seleção")

# ---------------------------------------------------------------------------
# **1. Funções Utilitárias de Carregamento**
# ---------------------------------------------------------------------------

@st.cache_resource
def carregar_arquivo_modelo(caminho):
    try:
        return joblib.load(caminho)
    except FileNotFoundError:
        st.error(f"Modelo não encontrado em '{caminho}'. Verifique o caminho.")
    except Exception as e:
        st.error(f"Erro ao carregar o modelo: {e}")
    return None


@st.cache_data
def carregar_dataframe(caminho_dados, arquivo_nome):
    path_completo = os.path.join(caminho_dados, arquivo_nome)
    try:
        df = pd.read_csv(path_completo)

        if "id_vaga" in df.columns:
            df["id_vaga"] = df["id_vaga"].astype(str)
        if "id_candidato" in df.columns:
            df["id_candidato"] = df["id_candidato"].astype(str)

        return df
    except FileNotFoundError:
        st.error(f"Erro: '{arquivo_nome}' não localizado em {path_completo}.")
    except Exception as e:
        st.error(f"Erro ao carregar '{arquivo_nome}': {e}")

    return pd.DataFrame()


@st.cache_data
def carregar_artefato(arquivo_artefato_path):
    try:
        return joblib.load(arquivo_artefato_path)
    except FileNotFoundError:
        st.error(f"Erro: '{arquivo_artefato_path}' ausente.")
    except Exception as e:
        st.error(f"Erro carregando artefato: {e}")
    return None


# ---------------------------------------------------------------------------
# **2. Caminhos e Configurações**
# ---------------------------------------------------------------------------
DIRETORIO_DADOS = 'data/'
DIRETORIO_ARTEFATOS = 'artifacts/'


# ---------------------------------------------------------------------------
# **3. Função Principal**
# ---------------------------------------------------------------------------
def iniciar_painel():
    # Configuração inicial e carregamentos
    st.title("Sistema de Recrutamento Inteligente")

    # Carregar modelos e dados
    modelo_carregado = carregar_arquivo_modelo(os.path.join(DIRETORIO_ARTEFATOS, 'modelo_recrutamento_rf.joblib'))
    colunas_treinamento = carregar_artefato(os.path.join(DIRETORIO_ARTEFATOS, 'colunas_modelo.joblib'))
    artefatos_engenharia = carregar_artefato(os.path.join(DIRETORIO_ARTEFATOS, 'artefatos_engenharia.joblib'))
    vagas_df = carregar_dataframe(DIRETORIO_DADOS, 'vagas_processadas.csv')
    candidatos_df = carregar_dataframe(DIRETORIO_DADOS, 'candidatos_processados.csv')

    # Verificação de elementos obrigatórios
    if not all([modelo_carregado, colunas_treinamento, artefatos_engenharia, not vagas_df.empty, not candidatos_df.empty]):
        st.error("Não foi possível carregar todos os elementos essenciais para o sistema.")
        st.stop()

    # Configurações do painel
    categorias = vagas_df['categoria_vaga'].unique() if 'categoria_vaga' in vagas_df.columns else []
    modalidades = vagas_df['modalidade_trabalho'].unique() if 'modalidade_trabalho' in vagas_df.columns else []
    niveis_prof = vagas_df['nivel_profissional_vaga'].unique() if 'nivel_profissional_vaga' in vagas_df.columns else []

    # Apresentação e Filtros
    st.header("Banco de Vagas Disponíveis")
    filtro_categorias = st.sidebar.multiselect("Categorias de Vagas:", categories=categorias)
    filtro_modalidades = st.sidebar.multiselect("Tipos de Trabalho:", options=modalidades)
    filtro_niveis = st.sidebar.multiselect("Níveis Profissionais:", options=niveis_prof)

    # Aplicação de Filtros
    vagas_filtradas = vagas_df.copy()
    if filtro_categorias:
        vagas_filtradas = vagas_filtradas[vagas_filtradas['categoria_vaga'].isin(filtro_categorias)]
    if filtro_modalidades:
        vagas_filtradas = vagas_filtradas[vagas_filtradas['modalidade_trabalho'].isin(filtro_modalidades)]
    if filtro_niveis:
        vagas_filtradas = vagas_filtradas[vagas_filtradas['nivel_profissional_vaga'].isin(filtro_niveis)]

    # Exibe Vagas Disponíveis
    st.dataframe(vagas_filtradas[['id_vaga', 'titulo_vaga', 'cliente', 'modalidade_trabalho', 'categoria_vaga']],
                 height=300, use_container_width=True)

    # Seleção de Vagas
    opcoes_vagas = vagas_filtradas['id_vaga'].unique()
    vaga_selecionada = st.selectbox("Selecione uma Vaga:", options=opcoes_vagas)

    # Calcular Match para Candidatos
    if vaga_selecionada:

        st.subheader(f"Resultados para a Vaga ID {vaga_selecionada}")
        # Aplica lógica de compatibilidade (exemplo parcial usado aqui)
        candidatos_filtrados = candidatos_df.head(10)  # Essa parte pode ter análise mais calibrada
        st.dataframe(candidatos_filtrados[['id_candidato', 'nome', 'nivel_profissional']], height=300)

    st.sidebar.markdown("---")


# ---------------------------------------------------------------------------
# **4. Inicializador**
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    iniciar_painel()
