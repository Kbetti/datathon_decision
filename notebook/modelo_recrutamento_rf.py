# Importação de bibliotecas essenciais
import json
import pandas as pd
import os
import gdown 

# Configuração inicial e parâmetros externos
drive_file_ids = {
    "vagas": "1NNzV_w90OlbONFq6oeO4T5xV5lTb4TuM",
    "candidatos": "1TQoEwhpYOwxjjZYmKVgAtEbN57kI2Slc",
    "prospectos": "1QIlM6G2bdWkYbWKp9The5bEL4Kr-hxfR"
}
project_paths = {
    "dados_originais": "dados/raw/",
    "dados_processados": "dados/processed/",
    "artefatos": "resultados/"
}

# Função para criar diretórios se necessário
def criar_diretorios(paths):
    for caminho in paths.values():
        os.makedirs(caminho, exist_ok=True)

# Função para baixar arquivos do Google Drive
def baixar_arquivo_google_drive(file_id, output_path):
    try:
        gdown.download(id=file_id, output=output_path, quiet=False, fuzzy=True)
        print(f"Download concluído: {output_path}")
    except Exception as e:
        print(f"Erro ao baixar arquivo (ID: {file_id}): {e}")

# Função para processar dados de um arquivo JSON
def processar_arquivo_json(caminho_arquivo, colunas_desejadas):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            dados_json = json.load(arquivo)
    except Exception as e:
        print(f"Erro ao carregar JSON {caminho_arquivo}: {e}")
        return pd.DataFrame()

    registros = []
    if isinstance(dados_json, dict):
        # Extrair informações e reorganizar
        for chave, detalhes in dados_json.items():
            linha = {"identificador": chave}
            if isinstance(detalhes, dict):
                detalhes_basicos = detalhes.get("informacoes_basicas", {})
                perfil = detalhes.get("perfil_vaga", {})
                linha.update(detalhes_basicos if isinstance(detalhes_basicos, dict) else {})
                linha.update(perfil if isinstance(perfil, dict) else {})
            registros.append(linha)
    else:
        print(f"AVISO: Estrutura inesperada no JSON {caminho_arquivo}.")

    df_dados = pd.DataFrame(registros)

    # Criar DataFrame com as colunas desejadas
    df_final = df_dados.reindex(columns=colunas_desejadas, fill_value=None)
    return df_final

# Execução principal do código
if __name__ == "__main__":
    # Criar diretórios necessários
    criar_diretorios(project_paths)

    # Caminhos dos arquivos a serem manipulados
    json_vagas_path = os.path.join(project_paths["dados_originais"], "vagas.json")

    # Baixar arquivo de vagas do Google Drive
    baixar_arquivo_google_drive(drive_file_ids["vagas"], json_vagas_path)

    # Processar os dados de vagas
    colunas_vagas = [
        "identificador", "titulo", "contratacao", "sap_cargo", "cliente",
        "divisao_empresa", "estado", "municipio", "nivel_profissional",
        "formacao", "ingles", "espanhol", "area", "atividades",
        "competencias", "observacoes"
    ]
    vagas_processado = processar_arquivo_json(json_vagas_path, colunas_vagas)

    # Exibir informações básicas do DataFrame resultante
    if not vagas_processado.empty:
        print(f"\nDados de Vagas Processados (Amostra):\n{vagas_processado.sample(5)}")
        vagas_processado.to_csv(os.path.join(project_paths["dados_processados"], "vagas_processado.csv"), index=False)
        print("\nDados de vagas processados e salvos com sucesso.")

# Função para pré-limpeza de campos textuais
def pre_limpar_campos_textuais(df, colunas_textuais, valor_faltante="Indefinido"):
    for coluna in colunas_textuais:
        if coluna in df.columns:
            df[coluna] = df[coluna].fillna(valor_faltante).astype(str)
        else:
            df[coluna] = valor_faltante
    return df

# Função para extração da modalidade de trabalho (Híbrido, Remoto, Presencial)
def classificar_modalidade(texto):
    texto = str(texto).lower()
    if "remoto" in texto:
        return "Remoto" if "híbrido" not in texto else "Híbrido"
    if "híbrido" in texto:
        return "Híbrido"
    if "presencial" in texto or "no escritório" in texto:
        return "Presencial"
    return "Não especificado"

# Função para mapear níveis de idioma
def mapear_nivel_idioma(valor, mapeamento):
    return mapeamento.get(str(valor).lower(), 0)

# Função para limpeza de áreas de atuação
def limpar_area(area):
    return str(area).replace("-", "").strip()

# Função para extração de tecnologias
def marcar_tecnologias(df, tecnologias, campo_texto, sufixo="tecnologia_"):
    for tecnologia in tecnologias:
        nome_coluna = sufixo + tecnologia.replace(" ", "_").replace(".", "").replace("+", "plus").lower()
        padrao = rf"\b{re.escape(tecnologia)}\b"
        df[nome_coluna] = df[campo_texto].apply(lambda x: 1 if re.search(padrao, str(x), re.IGNORECASE) else 0)
    return df

# Função para categorizar vagas com base no título
def categorizar_titulo(titulo):
    titulo_lower = str(titulo).lower()
    categorias = {
        "Consultoria SAP": ["consultor sap", "consultora sap", "especialista sap"],
        "Arquitetura SAP": ["arquitetura sap", "architect sap"],
        "Desenvolvimento": ["developer", "desenvolvedor", "programador", "abap", "frontend", "backend", "fullstack"],
        "Dados e BI": ["dados", "bi", "cientista de dados", "engenheiro de dados"],
        "Infraestrutura e Cloud": ["infraestrutura", "devops", "cloud", "aws", "azure", "google cloud"],
        "Gestão de Projetos": ["gerente de projetos", "scrum master", "agile coach"],
        "QA e Testes": ["qa", "testes", "quality assurance"],
        "Design e UX": ["design", "ux", "ui", "product designer"],
        "Analistas": ["analista", "analyst", "especialista"],
        "Liderança Técnica": ["arquiteto de sistemas", "líder técnico", "tech lead"]
    }
    for categoria, palavras_chave in categorias.items():
        if any(chave in titulo_lower for chave in palavras_chave):
            return categoria
    return "Outros/Não especificado"

# Processar o DataFrame ajustando a pré-limpeza e extrações
if not vagas_processado.empty:
    # 1. Pré-limpeza textual
    colunas_textuais = ["titulo", "atividades", "competencias", "observacoes", "area", "sap_cargo", "ingles", "espanhol", "cliente", "divisao_empresa"]
    vagas_processado = pre_limpar_campos_textuais(vagas_processado, colunas_textuais)

    # 2. Extração da modalidade de trabalho
    vagas_processado["modalidade"] = vagas_processado["observacoes"].apply(classificar_modalidade)

    # 3. Flag de vagas específicas (e.g., SAP)
    vagas_processado["vaga_flag_sap"] = vagas_processado["sap_cargo"].apply(lambda x: 1 if str(x).strip().lower() == "sim" else 0)

    # 4. Codificação ordinal de idiomas
    nivel_idioma_mapeado = {"não informado": 0, "nenhum": 0, "básico": 1, "intermediário": 2, "avançado": 3, "fluente": 4, "nativo": 5}
    vagas_processado["nivel_ingles"] = vagas_processado["ingles"].apply(lambda x: mapear_nivel_idioma(x, nivel_idioma_mapeado))
    vagas_processado["nivel_espanhol"] = vagas_processado["espanhol"].apply(lambda x: mapear_nivel_idioma(x, nivel_idioma_mapeado))

    # 5. Limpeza de áreas de atuação
    vagas_processado["area_limpa"] = vagas_processado["area"].apply(limpar_area)

    # 6. Criação de texto combinado para NLP
    colunas_texto_combinado = ["titulo", "atividades", "competencias"]
    vagas_processado["descricao_unificada"] = vagas_processado[colunas_texto_combinado].apply(lambda x: " ".join(x), axis=1).str.lower()

    # 7. Extração de tecnologias
    tecnologias_chave = ['python', 'java', 'aws', 'azure', 'devops', 'abap', 'sap']
    vagas_processado = marcar_tecnologias(vagas_processado, tecnologias_chave, "descricao_unificada")

    # 8. Generalização de títulos para categorias
    vagas_processado["categoria"] = vagas_processado["titulo"].apply(categorizar_titulo)

    # 9. Renomear colunas que requerem ajustes
    vagas_processado.rename(columns={"nivel_profissional": "nivel_profissional_cargo"}, inplace=True)

    # Output e informações do DataFrame processado
    print("\n--- Informações do DataFrame Processado ---")
    vagas_processado.info(verbose=False)

    # Exportar resultado final para CSV
    caminho_csv_final = os.path.join(project_paths["dados_processados"], "vagas_final.csv")
    vagas_processado.to_csv(caminho_csv_final, index=False)
    print(f"\nDados processados salvos em: {caminho_csv_final}")
else:
    print("Nenhum dado foi processado, o DataFrame está vazio.")

# Função modular para download de dados e carregamento de JSON
def carregar_dados_json(file_id, path_arquivo):
    try:
        print(f"Baixando arquivo de ID: {file_id} para {path_arquivo}...")
        gdown.download(id=file_id, output=path_arquivo, quiet=False, fuzzy=True)
        with open(path_arquivo, 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)
    except Exception as e:
        print(f"Erro ao baixar ou carregar JSON de ID {file_id}: {e}")
        return {}

# Função para transformar candidatos JSON em DataFrame
def preparar_dados_candidatos(dados_json):
    registros = []
    if isinstance(dados_json, dict):
        for candidato_id, detalhes in dados_json.items():
            registro = {"identificador_candidato": candidato_id}

            if isinstance(detalhes, dict):
                registro.update(detalhes.get("infos_basicas", {}))
                registro.update(detalhes.get("informacoes_pessoais", {}))
                registro.update(detalhes.get("informacoes_profissionais", {}))
                registro.update(detalhes.get("formacao_e_idiomas", {}))
                
                # Concatenar descrições e títulos de experiências profissionais
                experiencias = detalhes.get("experiencia_profissional", [])
                if isinstance(experiencias, list):
                    descricao_completa = " ".join(
                        exp.get("descricao_atividades", "") for exp in experiencias if "descricao_atividades" in exp
                    )
                    titulos_concatenados = " ".join(
                        exp.get("titulo_cargo", "") for exp in experiencias if "titulo_cargo" in exp
                    )
                    registro["experiencias_descricao"] = descricao_completa.strip()
                    registro["experiencias_titulos"] = titulos_concatenados.strip()
            registros.append(registro)
    else:
        print("A estrutura do JSON de candidatos é inválida ou incompatível.")
    
    return pd.DataFrame(registros)

# Função para realizar pré-limpeza de campos textuais
def limpar_campos_textuais_candidatos(df, colunas_limpeza, valores_vazios=None):
    if valores_vazios is None:
        valores_vazios = ["", "na", "null", "nan", "não informado", "undefined", "[]", "{}"]
    for coluna in colunas_limpeza:
        if coluna in df.columns:
            # Limpeza e substituição de valores vazios
            df[coluna] = df[coluna].fillna("Indefinido").str.strip()
            df[coluna] = df[coluna].replace(valores_vazios, "Indefinido", regex=True).str.lower()
        else:
            df[coluna] = "Indefinido"
    return df

# Função para combinar múltiplos campos em um único texto
def criar_campo_texto_unificado(df, colunas_unificar, coluna_final):
    print(f"Gerando campo '{coluna_final}' de texto unificado para candidatos...")
    if not df.empty:
        df[coluna_final] = df[colunas_unificar].apply(
            lambda x: " ".join(str(valor).strip() for valor in x if str(valor).lower() != "não informado"),
            axis=1
        ).str.lower().str.strip()
    return df

# Função para engenharia de features (categorias e mapeamentos básicos)
def engenharia_features_candidatos(df):
    # Categorizar profissionais
    def categorizar_profissional(titulo):
        titulo = str(titulo).lower()
        categorias = {
            "Consultoria SAP": ["consultor sap", "especialista sap"],
            "Desenvolvimento": ["developer", "engenheiro", "programador", "dev"],
            "Dados e BI": ["cientista de dados", "bi", "engenheiro de dados"],
            "Infraestrutura": ["infraestrutura", "devops", "cloud"],
            "Outros": ["gerente", "supervisor", "gestor"]
        }
        for categoria, palavras in categorias.items():
            if any(palavra in titulo for palavra in palavras):
                return categoria
        return "Não especificado"
    
    if "titulo_profissional" in df.columns:
        df["categoria_profissional"] = df["titulo_profissional"].apply(categorizar_profissional)
    else:
        df["categoria_profissional"] = "Não especificado"
    
    # Padronizar nível acadêmico
    df["nivel_academico_limpo"] = df.get("nivel_academico", "Não especificado").apply(padronizar_nivel_academico_candidato)
    
    # Padronizar nível profissional
    df["nivel_profissional_limpo"] = df.get("nivel_profissional", "Não especificado").apply(padronizar_nivel_profissional_candidato)

    return df

# Função para extrair habilidades/tecnologias de um campo textual
def extrair_habilidades(df, col_texto, habilidades_techs, sufixo="skill_"):
    if col_texto in df.columns and not df.empty:
        for habilidade in habilidades_techs:
            nome_col_habilidade = f"{sufixo}{habilidade.replace(' ', '_').lower()}"
            df[nome_col_habilidade] = df[col_texto].apply(
                lambda x: 1 if isinstance(x, str) and re.search(rf"\b{re.escape(habilidade)}\b", x, re.IGNORECASE) else 0
            )
    return df

# Execução principal
if __name__ == "__main__":
    print("\n--- Processamento de Dados de Candidatos ---")
    
    # Caminho e ID do arquivo de candidatos
    caminho_arquivo_candidatos = os.path.join(project_paths["dados_originais"], "candidatos.json")
    dados_json_candidatos = carregar_dados_json(drive_file_ids["candidatos"], caminho_arquivo_candidatos)

    # Transformação JSON em DataFrame
    candidatos_df = preparar_dados_candidatos(dados_json_candidatos)

    # Seleção e limpeza de campos importantes
    colunas_textuais = [
        "nome", "email", "local", "titulo_profissional", "nivel_academico", "nivel_profissional",
        "experiencias_descricao", "experiencias_titulos"
    ]
    candidatos_df = limpar_campos_textuais_candidatos(candidatos_df, colunas_textuais)

    # Combinar campos textuais para NLP
    colunas_unificar = ["experiencias_descricao", "experiencias_titulos", "titulo_profissional"]
    candidatos_df = criar_campo_texto_unificado(candidatos_df, colunas_unificar, "descricao_completa")

    # Engenharia de features
    candidatos_df = engenharia_features_candidatos(candidatos_df)

    # Extração de habilidades/tecnologias
    habilidades_chave = ['python', 'java', 'sap', 'sql', 'aws', 'excel', 'jira']
    candidatos_df = extrair_habilidades(candidatos_df, "descricao_completa", habilidades_chave)

    # Exportar DataFrame processado
    caminho_csv_final_candidatos = os.path.join(project_paths["dados_processados"], "candidatos_final.csv")
    candidatos_df.to_csv(caminho_csv_final_candidatos, index=False)
    print(f"\nProcessamento de candidatos concluído. Arquivo salvo em: {caminho_csv_final_candidatos}")

# Função para carregar e processar dados de prospecções
def preparar_dados_prospeccoes(dados_json):
    registros = []
    if isinstance(dados_json, dict):
        for origem_id, detalhes_origem in dados_json.items():
            # Extrair informações principais de origem
            titulo_origem = detalhes_origem.get("titulo", "Não disponível")
            modalidade_origem = detalhes_origem.get("modalidade", "Não disponível")
            candidatos_origem = detalhes_origem.get("prospects", [])

            if isinstance(candidatos_origem, list):
                for candidato in candidatos_origem:
                    if isinstance(candidato, dict):
                        registro = {
                            "origem_id_prospec": origem_id,
                            "origem_titulo_prospec": titulo_origem,
                            "origem_modalidade_prospec": modalidade_origem,
                            "candidato_nome": candidato.get("nome", "Não disponível"),
                            "candidato_codigo": candidato.get("codigo", "Não disponível"),
                            "candidato_status": candidato.get("situacao_candidado", "Não disponível"),
                            "data_candidatura": candidato.get("data_candidatura", "Não disponível"),
                            "ultima_atualizacao": candidato.get("ultima_atualizacao", "Não disponível"),
                            "comentarios": candidato.get("comentario", "Não disponível"),
                            "recrutador": candidato.get("recrutador", "Não disponível")
                        }
                        registros.append(registro)
    else:
        print("Estrutura de dados de prospecções incompatível ou vazia.")
    return pd.DataFrame(registros)

# Função para limpar e pré-processar dados de prospecções
def limpar_prospeccoes(df, colunas_textuais, colunas_data):
    # Limpeza de campos textuais
    padrões_vazios = ["", "na", "nulo", "null", "não disponível", "undefined", "[]", "{}", "<NA>", "nan"]
    for coluna in colunas_textuais:
        if coluna in df.columns:
            df[coluna] = df[coluna].fillna("Indefinido").astype(str).str.strip().str.lower()
            df[coluna] = df[coluna].replace(padrões_vazios, "Indefinido", regex=True)
        else:
            df[coluna] = "Indefinido"
    
    # Conversão de datas
    for coluna_data in colunas_data:
        if coluna_data in df.columns:
            nova_coluna = f"{coluna_data}_dt"
            df[nova_coluna] = pd.to_datetime(df[coluna_data], format='%d-%m-%Y', errors='coerce')
        else:
            df[f"{coluna_data}_dt"] = pd.NaT
    print("Pré-processamento de prospecções concluído.")
    return df

# Função para engenharia de features de prospecções
def engenharia_features_prospeccoes(df):
    # Calcular duração do processo
    if "ultima_atualizacao_dt" in df.columns and "data_candidatura_dt" in df.columns:
        df["duracao_processo_dias"] = (
            df["ultima_atualizacao_dt"] - df["data_candidatura_dt"]
        ).dt.days.apply(lambda x: x if pd.notna(x) and x >= 0 else np.nan)

    # Padronizar modalidade da vaga
    def padronizar_modalidade(modalidade):
        modalidade = str(modalidade).lower()
        if re.search(r"remoto|home office", modalidade):
            return "Remoto"
        if re.search(r"h[íi]brido", modalidade):
            return "Híbrido"
        if re.search(r"presencial", modalidade):
            return "Presencial"
        return "Não especificado"
    
    if "origem_modalidade_prospec" in df.columns:
        df["modalidade_padronizada_prospec"] = df["origem_modalidade_prospec"].apply(padronizar_modalidade)

    # Mapear situações dos candidatos
    mapping_situacao = {
        "prospect": "Em Avaliação",
        "aprovado": "Finalizado - Contratado",
        "contratado": "Finalizado - Contratado",
        "reprovado": "Finalizado - Rejeitado",
        "desistiu": "Desistiu",
        "pausado": "Standby"
    }

    def agrupar_situacao(texto):
        texto = str(texto).lower()
        return mapping_situacao.get(texto, "Outros/Desconhecido")
    
    if "candidato_status" in df.columns:
        df["situacao_resumida_prospec"] = df["candidato_status"].apply(agrupar_situacao)
    
    # Análise de valor monetário em comentários
    if "comentarios" in df.columns:
        df["tem_referencia_financeira"] = df["comentarios"].apply(
            lambda x: 1 if isinstance(x, str) and re.search(r"salário|remuneração|r\$|pretensão", x, re.IGNORECASE) else 0
        )
    return df

# Execução principal para dados de prospecções
if __name__ == "__main__":
    print("\n--- Processamento de Dados de Prospecções ---")

    # Caminho e ID do arquivo de prospecções
    caminho_arquivo_prospec = os.path.join(project_paths["dados_originais"], "prospec.json")
    dados_json_prospec = carregar_dados_json(drive_file_ids["prospectos"], caminho_arquivo_prospec)

    # Transformar JSON em DataFrame
    prospec_df = preparar_dados_prospeccoes(dados_json_prospec)

    # Pré-processamento de dados
    colunas_textuais_prospec = [
        "origem_titulo_prospec", "origem_modalidade_prospec", "candidato_nome",
        "candidato_status", "comentarios", "recrutador"
    ]
    colunas_data_prospec = ["data_candidatura", "ultima_atualizacao"]
    prospec_df = limpar_prospeccoes(prospec_df, colunas_textuais_prospec, colunas_data_prospec)

    # Engenharia de features
    prospec_df = engenharia_features_prospeccoes(prospec_df)

    # Exportar dados processados
    caminho_csv_final_prospec = os.path.join(project_paths["dados_processados"], "prospeccoes_final.csv")
    prospec_df.to_csv(caminho_csv_final_prospec, index=False)
    print(f"\nProcessamento de prospecções concluído. Arquivo salvo em: {caminho_csv_final_prospec}")

# Função para realizar merges entre múltiplos DataFrames (vagas, candidatos e prospecções)
def realizar_merge_dataframes(df_prospec, df_vagas, df_candidatos):
    if df_prospec.empty:
        print("Erro: O DataFrame de prospecções está vazio. Merge não será realizado.")
        return pd.DataFrame()

    # Merge com vagas
    if df_vagas.empty:
        print("Aviso: O DataFrame de vagas está vazio. Será realizado o merge apenas com candidatos.")
        df_vagas = pd.DataFrame(columns=['identificacao_vaga'])  # Criação de um DataFrame vazio para evitar erros.

    df_merge_temp = pd.merge(
        df_prospec,
        df_vagas,
        left_on='id_vaga_origem',
        right_on='identificacao_vaga',
        how='left',
        suffixes=('_prospec', '_vagas')
    )
    print(f"Número de linhas após merge com vagas: {len(df_merge_temp)}")

    # Merge com candidatos
    if df_candidatos.empty:
        print("Aviso: O DataFrame de candidatos está vazio. Merge será completado sem informações dos candidatos.")
        df_candidatos = pd.DataFrame(columns=['identificacao_candidato'])
    
    df_final = pd.merge(
        df_merge_temp,
        df_candidatos,
        left_on='id_candidato_origem',
        right_on='identificacao_candidato',
        how='left',
        suffixes=('_vagas', '_candidatos')
    )
    print(f"Número de linhas após merge com candidatos: {len(df_final)}")

    # Limpar duplicações de colunas criadas pelo merge
    if 'identificacao_candidato' in df_final.columns and 'id_candidato_origem' in df_final.columns:
        df_final.drop(columns=['identificacao_candidato'], inplace=True)
    if 'identificacao_vaga' in df_final.columns and 'id_vaga_origem' in df_final.columns:
        df_final.drop(columns=['identificacao_vaga'], inplace=True)

    return df_final


# Função para preparar os dados finais para modelos preditivos
def preparar_dados_para_modelagem(df_merged, colunas_checagem, situacoes_alvo):
    if df_merged.empty:
        print("Erro: O DataFrame combinado está vazio. Preparação final não será realizada.")
        return pd.DataFrame()

    print(f"Linhas antes da remoção de nulos para merges incompletos: {len(df_merged)}")
    
    # Limpeza de linhas sem informações cruciais
    df_limpo = df_merged.copy()
    df_limpo.dropna(subset=colunas_checagem, inplace=True)
    print(f"Linhas após remoção de nulos: {len(df_limpo)}")

    # Criar a variável alvo 'foi_contratado'
    situacoes_sucessos, situacoes_rejeitadas = situacoes_alvo
    if 'situacao_candidato' in df_limpo.columns:
        df_limpo['foi_contratado_temp'] = -1
        df_limpo.loc[df_limpo['situacao_candidato'].str.lower().isin(situacoes_sucessos), 'foi_contratado_temp'] = 1
        df_limpo.loc[df_limpo['situacao_candidato'].str.lower().isin(situacoes_rejeitadas), 'foi_contratado_temp'] = 0
        df_final_modelagem = df_limpo[df_limpo['foi_contratado_temp'] != -1].copy()
        df_final_modelagem.rename(columns={'foi_contratado_temp': 'foi_contratado'}, inplace=True)
        print(f"Variável de saída 'foi_contratado' adicionada. Total de linhas restantes: {len(df_final_modelagem)}")
        return df_final_modelagem
    else:
        print("Coluna 'situacao_candidato' ausente. Não foi possível criar a variável alvo.")
        return df_limpo.copy()


# Execução Principal
if __name__ == "__main__":
    print("\n--- Merge e Preparação dos DataFrames Processados ---")
    
    # Validação preliminar
    df_prospeccoes = df_prospects_processado if 'df_prospects_processado' in globals() else pd.DataFrame()
    df_vagas = df_vagas_processado if 'df_vagas_processado' in globals() else pd.DataFrame()
    df_candidatos = df_candidatos_processado if 'df_candidatos_processado' in globals() else pd.DataFrame()

    # Realizar merges
    df_master_final = realizar_merge_dataframes(df_prospeccoes, df_vagas, df_candidatos)

    # Preparação para modelagem
    colunas_chave_checagem = ['titulo_vaga_prospec', 'candidato_nome']
    situacoes_sucesso_contratado = [
        'contratado pela decision', 'contratado como hunting', 'aprovado', 'proposta aceita'
    ]
    situacoes_sem_sucesso = [
        'não aprovado pelo cliente', 'não aprovado pelo rh', 'não aprovado pelo requisitante', 'reprovado',
        'desistiu', 'desistiu da contratação', 'sem interesse nesta vaga'
    ]
    variavel_alvo_situacoes = (situacoes_sucesso_contratado, situacoes_sem_sucesso)

    df_final_modelagem = preparar_dados_para_modelagem(
        df_master_final,
        colunas_chave_checagem,
        variavel_alvo_situacoes
    )

    # Verificar dados finais de modelagem
    if not df_final_modelagem.empty:
        print("\n--- Informações do DataFrame para Modelagem (df_final_modelagem) ---")
        df_final_modelagem.info(verbose=True, show_counts=True, max_cols=200)
        print("\n--- Distribuição da variável 'foi_contratado' ---")
        print(df_final_modelagem['foi_contratado'].value_counts(normalize=True))
        print("\n--- Amostra do DataFrame Final para Modelagem ---")
        print(df_final_modelagem.head(5).to_string())


# Função para recalcular variáveis exploratórias
def recalcular_features_eda(df):
    if df.empty:
        print("DataFrame está vazio. Não foi possível realizar a EDA.")
        return df

    print("\n--- Recalculando Variáveis Exploratórias (EDA) ---")

    def calcular_compatibilidade(col_cand, col_vaga):
        return (col_cand >= col_vaga).astype(int)

    # Nível de inglês
    col_nivel_ingles_cand = obter_nome_coluna_eda(df, 'nivel_ingles_ordinal', ['_candidato', ''])
    col_nivel_ingles_vaga = obter_nome_coluna_eda(df, 'nivel_ingles_ordinal', ['_vaga', '_vaga_merged', ''])
    if col_nivel_ingles_cand and col_nivel_ingles_vaga:
        df['compat_ingles'] = calcular_compatibilidade(
            df[col_nivel_ingles_cand].fillna(0).astype(int),
            df[col_nivel_ingles_vaga].fillna(0).astype(int)
        )
    else:
        df['compat_ingles'] = 0

    # Nível de espanhol
    col_nivel_espanhol_cand = obter_nome_coluna_eda(df, 'nivel_espanhol_ordinal', ['_candidato', ''])
    col_nivel_espanhol_vaga = obter_nome_coluna_eda(df, 'nivel_espanhol_ordinal', ['_vaga', '_vaga_merged', ''])
    if col_nivel_espanhol_cand and col_nivel_espanhol_vaga:
        df['compat_espanhol'] = calcular_compatibilidade(
            df[col_nivel_espanhol_cand].fillna(0).astype(int),
            df[col_nivel_espanhol_vaga].fillna(0).astype(int)
        )
    else:
        df['compat_espanhol'] = 0

    # Total de tecnologias da vaga
    tech_cols_vaga = [col for col in df.columns if col.startswith('tech_') and '_candidato' not in col]
    if tech_cols_vaga:
        df['total_techs_vaga'] = df[tech_cols_vaga].sum(axis=1)
    else:
        df['total_techs_vaga'] = 0

    # Cálculo de "skills_match_count" e "skills_faltantes"
    skill_cols_cand = [col for col in df.columns if col.startswith('skill_')]

    if tech_cols_vaga and skill_cols_cand:
        df['skills_match_count'] = 0
        for tech_col in tech_cols_vaga:
            skill_col_match = tech_col.replace('tech_', 'skill_')
            if skill_col_match in skill_cols_cand:
                df['skills_match_count'] += df[tech_col] * df[skill_col_match]
        df['skills_faltantes_vaga'] = (df['total_techs_vaga'] - df['skills_match_count']).clip(lower=0)
    else:
        df['skills_match_count'] = 0
        df['skills_faltantes_vaga'] = df['total_techs_vaga']

    print("Cálculo de novas features de EDA concluído.")
    return df

# Função para preparar conjunto de features finais
def preparar_features_modelagem(df, categoricas_vaga, categoricas_cand, target_col):
    if df.empty or target_col not in df.columns:
        print("Erro: DataFrame vazio ou variável-alvo ausente. Não é possível preparar as features.")
        return pd.DataFrame(), pd.Series(dtype='int')

    print("\n--- Preparação das Features para Modelagem ---")
    # Seleção de features categóricas e numéricas
    features_num = [col for col in df.columns if df[col].dtype in ['int64', 'float64'] and col != target_col]
    features_cat_vaga = [col for col in categoricas_vaga if col in df.columns]
    features_cat_cand = [col for col in categoricas_cand if col in df.columns]

    # Aplicação de One-Hot Encoding
    df_encoded = pd.get_dummies(df, columns=features_cat_vaga + features_cat_cand, drop_first=True)
    
    # Remoção da variável-alvo entre as features
    X = df_encoded.drop(columns=[target_col])
    y = df_encoded[target_col]

    return X, y

# Função para treinar e avaliar modelos baseline com uma abordagem alternativa
def treinar_avaliar_modelos_baseline(X_train, X_test, y_train, y_test):
    if X_train.empty or y_train.empty:
        print("Erro: Conjuntos de treino e teste estão vazios.")
        return None

    print("\n--- Treinamento e Avaliação: Modelos Baseline ---")

    resultados = {}
    
    # LightGBM (Gradient Boosting)
    from lightgbm import LGBMClassifier

    modelo_lgbm = LGBMClassifier(
        n_estimators=200,
        max_depth=7,
        learning_rate=0.05,
        random_state=42,
        class_weight='balanced'
    )
    modelo_lgbm.fit(X_train, y_train)

    y_pred_lgbm = modelo_lgbm.predict(X_test)
    y_pred_proba_lgbm = modelo_lgbm.predict_proba(X_test)[:, 1]

    resultados['lightgbm'] = {
        'acuracia': accuracy_score(y_test, y_pred_lgbm),
        'roc_auc': roc_auc_score(y_test, y_pred_proba_lgbm) if len(np.unique(y_test)) > 1 else 0.5,
        'relatorio_classificacao': classification_report(y_test, y_pred_lgbm, zero_division=0, target_names=['Não Contratado', 'Contratado']),
        'importancia_features': pd.Series(modelo_lgbm.feature_importances_, index=X_train.columns).sort_values(ascending=False)
    }

    print("\nResultados Baseline (com LGBM):")
    for modelo in resultados:
        print(f"\nModelo: {modelo.upper()}")
        print(f"Acurácia: {resultados[modelo]['acuracia']:.4f}")
        print(f"ROC-AUC: {resultados[modelo]['roc_auc']:.4f}")

    return resultados

# Lógica para treinamento e avaliação do modelo atualizado
if not df_modelagem.empty:
    # Recalcular features exploratórias
    df_modelagem = recalcular_features_eda(df_modelagem)

    # Prepara as features
    features_categoricas_vaga = ['modalidade_trabalho', 'categoria_vaga']
    features_categoricas_cand = ['categoria_profissional', 'nivel_academico_padronizado']
    X, y = preparar_features_modelagem(df_modelagem, features_categoricas_vaga, features_categoricas_cand, 'foi_contratado')

    # Dividir em conjuntos de treino (70%) e teste (30%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

    # Treina e avalia modelos baseline com LightGBM
    resultados_baseline = treinar_avaliar_modelos_baseline(X_train, X_test, y_train, y_test)

    # Exibir resultados e importância de features do LightGBM
    if 'lightgbm' in resultados_baseline:
        importancias_lgbm = resultados_baseline['lightgbm']['importancia_features']
        print("\nTop 10 Features Mais Importantes - LightGBM:")
        print(importancias_lgbm.head(10))


# Função para salvar modelos e artefatos em formato joblib
def salvar_artefato_joblib(objeto, caminho, descricao="Artefato"):
    try:
        joblib.dump(objeto, caminho)
        print(f"{descricao} salvo em '{caminho}'")
    except Exception as e:
        print(f"Erro ao salvar {descricao}: {e}")


# Função para salvar artefatos necessários para o Streamlit
def salvar_artefatos_para_streamlit(df_vagas, df_candidatos, df_tp, df_tn, modelo, colunas, artefatos):
    print("\n--- Iniciando Salvamento de Artefatos para Streamlit ---")

    # Salvando dados processados
    salvar_dataframe_para_csv(df_vagas, os.path.join(path_data_processed, 'vagas_processadas.csv'), "Dados de Vagas Processadas")
    salvar_dataframe_para_csv(df_candidatos, os.path.join(path_data_processed, 'candidatos_processados.csv'), "Dados de Candidatos Processados")

    # Salvando modelo otimizado
    salvar_artefato_joblib(modelo, os.path.join(path_artifacts, 'modelo_recrutamento_rf.joblib'), "Modelo Random Forest Otimizado")

    # Salvando colunas do modelo
    if colunas:
        salvar_artefato_joblib(colunas, os.path.join(path_artifacts, 'colunas_modelo.joblib'), "Lista de Colunas do Modelo")

    # Salvando artefatos auxiliares para engenharia de features no Streamlit
    salvar_artefato_joblib(artefatos, os.path.join(path_artifacts, 'artefatos_engenharia.joblib'), "Artefatos de Engenharia de Features")

    # Salvando exemplos (TP e TN) para uso no Streamlit
    salvar_dataframe_para_csv(df_tp, os.path.join(path_artifacts, 'exemplo_tp_streamlit.csv'), "Exemplo de Verdadeiro Positivo (TP)")
    salvar_dataframe_para_csv(df_tn, os.path.join(path_artifacts, 'exemplo_tn_streamlit.csv'), "Exemplo de Verdadeiro Negativo (TN)")

    print("\n--- Salvamento de Artefatos Concluído ---")
    print(f"Verifique os diretórios '{path_data_processed}' e '{path_artifacts}' para os arquivos gerados.")


# Execução Principal para Salvamento
if __name__ == "__main__":
    # Validar as entradas necessárias
    df_vagas_para_salvar = df_vagas_processado if 'df_vagas_processado' in globals() else pd.DataFrame()
    df_candidatos_para_salvar = df_candidatos_processado if 'df_candidatos_processado' in globals() else pd.DataFrame()
    modelo_otimizado_para_salvar = best_rf_clf_otimizado if 'best_rf_clf_otimizado' in locals() else None
    colunas_para_salvar = X.columns.tolist() if 'X' in globals() and not X.empty else X_train.columns.tolist() if 'X_train' in globals() and not X_train.empty else []
    
    artefatos_para_streamlit = {
        'mapa_nivel_idioma': mapa_nivel_idioma,
        'mapa_nivel_academico_candidato': mapa_nivel_academico_candidato,
        'mapa_nivel_profissional_candidato': mapa_nivel_profissional_candidato,
        'tecnologias_lista_vagas': tecnologias_lista_vagas,
        'tecnologias_lista_candidatos': tecnologias_lista_candidatos
    }

    exemplo_tp_para_salvar = exemplo_tp_df if 'exemplo_tp_df' in globals() and exemplo_tp_df is not None else pd.DataFrame()
    exemplo_tn_para_salvar = exemplo_tn_df if 'exemplo_tn_df' in globals() and exemplo_tn_df is not None else pd.DataFrame()

    # Chamar função para salvar artefatos
    salvar_artefatos_para_streamlit(
        df_vagas=df_vagas_para_salvar,
        df_candidatos=df_candidatos_para_salvar,
        df_tp=exemplo_tp_para_salvar,
        df_tn=exemplo_tn_para_salvar,
        modelo=modelo_otimizado_para_salvar,
        colunas=colunas_para_salvar,
        artefatos=artefatos_para_streamlit
    )

