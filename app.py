import streamlit as st
import pandas as pd

st.set_page_config(page_title="Controle de Pátio", layout="wide", page_icon="🚗")

# --- INICIALIZAÇÃO DE DADOS (SIMULAÇÃO / MEMÓRIA) ---
if "veiculos" not in st.session_state:
    # Dados de exemplo iniciais
    st.session_state["veiculos"] = pd.DataFrame([
        {"chassi": "CHS001", "modelo": "EX5", "cor": "Branco", "ala": "EX5 - Branco", "posicao_fila": 1},
        {"chassi": "CHS002", "modelo": "EX5", "cor": "Branco", "ala": "EX5 - Branco", "posicao_fila": 2},
        {"chassi": "CHS003", "modelo": "EX5", "cor": "Branco", "ala": "EX5 - Branco", "posicao_fila": 3}, # Frente
        {"chassi": "CHS004", "modelo": "EX2", "cor": "Branco", "ala": "EX2 - Branco", "posicao_fila": 1},
        {"chassi": "CHS005", "modelo": "EX2", "cor": "Branco", "ala": "EX2 - Branco", "posicao_fila": 2}, # Frente
        {"chassi": "CHS006", "modelo": "EX5", "cor": "Preto",  "ala": "EX5 - Preto",  "posicao_fila": 1},
    ])

df = st.session_state["veiculos"]

st.title("🚗 Sistema de Gestão e Controle de Pátio")

# --- BARRA LATERAL: ENTRADA / SAÍDA DE VEÍCULOS ---
st.sidebar.header("⚙️ Operações")

aba_op, aba_cad = st.sidebar.tabs(["Retirar / Mover", "Cadastrar Novo"])

with aba_cad:
    st.subheader("Entrada de Veículo")
    novo_chassi = st.text_input("Chassi").upper().strip()
    novo_modelo = st.text_input("Modelo (ex: EX5)").upper().strip()
    nova_cor = st.text_input("Cor (ex: BRANCO)").capitalize().strip()
    
    if st.button("➕ Adicionar ao Pátio", use_container_width=True):
        if novo_chassi and novo_modelo and nova_cor:
            if novo_chassi in df['chassi'].values:
                st.error("Este chassi já está no pátio!")
            else:
                ala_nome = f"{novo_modelo} - {nova_cor}"
                # Posição na fila: coloca no final da fila (frente)
                carros_na_ala = df[df['ala'] == ala_nome]
                nova_posicao = carros_na_ala['posicao_fila'].max() + 1 if not carros_na_ala.empty else 1
                
                novo_veiculo = {
                    "chassi": novo_chassi,
                    "modelo": novo_modelo,
                    "cor": nova_cor,
                    "ala": ala_nome,
                    "posicao_fila": nova_posicao
                }
                st.session_state["veiculos"] = pd.concat([df, pd.DataFrame([novo_veiculo])], ignore_index=True)
                st.success(f"Veículo {novo_chassi} adicionado à ala {ala_nome}!")
                st.rerun()
        else:
            st.warning("Preencha todos os campos.")

with aba_op:
    st.subheader("Dar Saída do Veículo")
    chassi_saida = st.selectbox("Selecione o Chassi para remover:", [""] + list(df["chassi"].unique()))
    if st.button("🔴 Confirmar Saída", use_container_width=True):
        if chassi_saida:
            # Reorganizar posições na mesma ala
            veiculo_remover = df[df['chassi'] == chassi_saida].iloc[0]
            ala_remover = veiculo_remover['ala']
            pos_remover = veiculo_remover['posicao_fila']
            
            # Remove o carro
            df_novo = df[df['chassi'] != chassi_saida].copy()
            # Ajusta quem estava atrás dele
            df_novo.loc[(df_novo['ala'] == ala_remover) & (df_novo['posicao_fila'] > pos_remover), 'posicao_fila'] -= 1
            
            st.session_state["veiculos"] = df_novo
            st.success(f"Veículo {chassi_saida} removido com sucesso!")
            st.rerun()

# --- TELA PRINCIPAL (ABAS) ---
tab_visual, tab_manobra, tab_lista = st.tabs(["🗺️ Mapa Visual das Alas", "🔑 Assistente de Retirada (Chaves)", "📋 Lista Geral de Veículos"])

# 1. VISÃO VISUAL DO PÁTIO
with tab_visual:
    st.header("Disposição das Alas e Filas")
    st.info("📌 **Legenda**: Os carros estão dispostos em fileiras. O carro da **direita (maior número)** é o primeiro da fila (está na frente e pode sair livremente). Os da esquerda estão bloqueados.")
    
    alas_existentes = sorted(df["ala"].unique())
    
    if not alas_existentes:
        st.warning("O pátio está vazio no momento.")
    
    for ala in alas_existentes:
        st.subheader(f"🏷️ Ala: {ala}")
        carros_ala = df[df["ala"] == ala].sort_values("posicao_fila")
        
        cols = st.columns(max(len(carros_ala), 1))
        for idx, (_, carro) in enumerate(carros_ala.iterrows()):
            e_o_ultimo = (idx == len(carros_ala) - 1)
            status_cor = "#28a745" if e_o_ultimo else "#dc3545" # Verde se livre, vermelho se bloqueado
            
            with cols[idx]:
                st.markdown(f"""
                <div style="
                    border: 2px solid {status_cor};
                    border-radius: 8px;
                    padding: 10px;
                    text-align: center;
                    background-color: #f8f9fa;
                    color: #333;
                    margin-bottom: 10px;
                ">
                    <span style="font-size: 12px; color: #666;">Posição #{carro['posicao_fila']}</span><br>
                    <strong style="font-size: 16px;">{carro['chassi']}</strong><br>
                    <span style="font-size: 12px; font-weight: bold; color: {status_cor};">
                        {'🟢 SAÍDA LIVRE' if e_o_ultimo else '🔴 BLOQUEADO'}
                    </span>
                </div>
                """, unsafe_allow_html=True)

# 2. CONSULTA DE MANOBRA (QUAL CHAVE PEGAR)
with tab_manobra:
    st.header("🔑 Calcular Chaves Necessárias para Retirada")
    st.write("Escolha o carro que deseja retirar para saber exatamente quais chaves você precisa pegar na guarita/sala de chaves.")
    
    chassi_alvo = st.selectbox("Qual carro você precisa retirar?", ["-- Selecione --"] + list(df["chassi"].unique()))
    
    if chassi_alvo != "-- Selecione --":
        carro_alvo = df[df["chassi"] == chassi_alvo].iloc[0]
        ala_alvo = carro_alvo["ala"]
        posicao_alvo = carro_alvo["posicao_fila"]
        
        # Carros na frente dele (posicao_fila maior que a dele na mesma ala)
        carros_na_frente = df[(df["ala"] == ala_alvo) & (df["posicao_fila"] > posicao_alvo)].sort_values("posicao_fila", ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Chassi Alvo", value=carro_alvo["chassi"])
            st.metric(label="Ala", value=ala_alvo)
            st.metric(label="Posição na Fileira", value=f"#{posicao_alvo}")
        
        with col2:
            if carros_na_frente.empty:
                st.balloons()
                st.success("✅ **Saída Direta!** Não há nenhum carro na frente deste. Você só precisa da chave dele:")
                st.markdown(f"### 🔑 Chave necessária: **{carro_alvo['chassi']}**")
            else:
                st.error(f"⚠️ **Atenção!** Existem {len(carros_na_frente)} carro(s) bloqueando a saída.")
                st.warning("📋 **Pegue as seguintes chaves ANTES de ir ao pátio (na ordem de manobra):**")
                
                chaves_lista = list(carros_na_frente["chassi"]) + [carro_alvo["chassi"]]
                
                for idx, chasi_m in enumerate(chaves_lista):
                    if chasi_m == carro_alvo["chassi"]:
                        st.markdown(f"**{idx+1}º (SEU CARRO):** 🔑 `Chassi: {chasi_m}`")
                    else:
                        st.markdown(f"**{idx+1}º (Mover primeiro):** 🔑 `Chassi: {chasi_m}`")

# 3. LISTA GERAL / TABELA
with tab_lista:
    st.header("📋 Todos os Veículos no Pátio")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_ala = st.multiselect("Filtrar por Ala", options=sorted(df["ala"].unique()))
    with col_f2:
        busca_chassi = st.text_input("Buscar por Chassi específico").upper()
    
    df_filtrado = df.copy()
    if filtro_ala:
        df_filtrado = df_filtrado[df_filtrado["ala"].isin(filtro_ala)]
    if busca_chassi:
        df_filtrado = df_filtrado[df_filtrado["chassi"].str.contains(busca_chassi)]
        
    st.dataframe(
        df_filtrado.sort_values(["ala", "posicao_fila"]),
        use_container_width=True,
        column_config={
            "chassi": "Chassi",
            "modelo": "Modelo",
            "cor": "Cor",
            "ala": "Ala",
            "posicao_fila": "Posição na Fileira"
        }
    )
