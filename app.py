import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def gerar_pdf(produto, metodo, previsao, demandas):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer)

    estilos = getSampleStyleSheet()

    elementos = []

    elementos.append(Paragraph("<b>PREVISOR DE DEMANDA</b>", estilos["Title"]))

    elementos.append(Paragraph(f"Produto: {produto}", estilos["Normal"]))
    elementos.append(Paragraph(f"Método: {metodo}", estilos["Normal"]))
    elementos.append(Paragraph(f"Períodos analisados: {len(demandas)}", estilos["Normal"]))
    elementos.append(Paragraph(f"Previsão: {previsao:.2f} unidades", estilos["Normal"]))

    doc.build(elementos)

    buffer.seek(0)

    return buffer

# =====================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================

st.set_page_config(
    page_title="Previsor de Demanda",
    page_icon="📈",
    layout="centered"
)

st.title("📈 Previsor de Demanda")
st.write("Sistema para previsão de demanda utilizando diferentes métodos.")
st.caption("Desenvolvido para a disciplina de Administração da Produção - UECE")

st.divider()

# =====================================
# BARRA LATERAL
# =====================================

st.sidebar.header("⚙️ Configurações")
st.sidebar.caption(
    "Informe os dados para gerar a previsão de demanda."
)

produto = st.sidebar.text_input("Nome do Produto")

historico = st.sidebar.text_area(
    "Demandas Históricas",
    placeholder="Exemplo: 120,125,130,128,135"
)

semanas = st.sidebar.number_input(
    "Número de semanas para prever",
    min_value=1,
    max_value=12,
    value=4
)

metodo = st.sidebar.selectbox(
    "Método de previsão",
    [
        "Média Móvel",
        "Suavização Exponencial",
        "Regressão Linear"
    ]
)

st.sidebar.divider()

calcular = st.sidebar.button("📊 Calcular Previsão")

# =====================================
# PROCESSAMENTO
# =====================================

if not calcular:
    st.info(
        """
### 👋 Bem-vindo!

Preencha as informações na barra lateral e clique em **🚀 Calcular Previsão** para visualizar:

- 📊 Histórico das demandas
- 📈 Gráfico de evolução
- 📋 Indicadores
- 🔮 Resultado da previsão
- 💡 Interpretação automática
"""
    )
if calcular:
    # Validação do nome
    if produto.strip() == "":
        st.error("Informe o nome do produto.")
        st.stop()

    # Validação do histórico
    if historico.strip() == "":
        st.error("Informe as demandas históricas.")
        st.stop()

    # Conversão para números
    try:
        demandas = [float(valor.strip()) for valor in historico.split(",")]
        st.info(f"📋 Foram informados {len(demandas)} períodos históricos.")
    except:
        st.error("Digite apenas números separados por vírgula.")
        st.stop()

    # =====================================
    # DADOS INFORMADOS
    # =====================================

    st.subheader("Dados Validados")

    st.write(f"**Produto:** {produto}")
    st.write(f"**Semanas para previsão:** {semanas}")
    st.write(f"**Método escolhido:** {metodo}")

    st.success("Todos os dados foram validados com sucesso!")

    # =====================================
    # CÁLCULO DA PREVISÃO
    # =====================================

    if metodo == "Média Móvel":

        previsao = sum(demandas) / len(demandas)

    elif metodo == "Suavização Exponencial":

        alfa = 0.3
        previsao = demandas[0]

        for demanda in demandas[1:]:
            previsao = alfa * demanda + (1 - alfa) * previsao

    elif metodo == "Regressão Linear":

        x = np.arange(1, len(demandas) + 1)
        coeficientes = np.polyfit(x, demandas, 1)

        inclinacao = coeficientes[0]
        intercepto = coeficientes[1]

        proxima_semana = len(demandas) + 1
        previsao = inclinacao * proxima_semana + intercepto


    # =====================================
    # TABELA
    # =====================================

    tabela = pd.DataFrame({
        "Semana": range(1, len(demandas) + 1),
        "Demanda": demandas
    })
    st.write("### Histórico de Demandas")

    # Formata a coluna Demanda
    tabela["Demanda"] = tabela["Demanda"].map(lambda x: f"{x:.2f}")

    # Gera o HTML automaticamente
    html_tabela = tabela.to_html(index=False, classes="tabela-demanda")

    # CSS da tabela
    st.markdown("""
    <style>
.tabela-demanda{
    width:100%;
    border-collapse:collapse;
    border-radius:10px;
    overflow:hidden;
    font-size:16px;
}
    .tabela-demanda td{
    padding:14px;
    vertical-align:middle;
    text-align:center;
    border-bottom:1px solid #333;
    color:white;
    }

    .tabela-demanda thead tr{
        background:#2563EB;
        box-shadow:0 4px 10px rgba(0,0,0,0.25);
        border:1px solid #3b3b3b;
    }

    .tabela-demanda th{
        color:white;
        padding:14px;
        vertical-align:middle;
        text-align:center;
    }

    .tabela-demanda td{
        padding:14px;
        vertical-align:middle;
        text-align:center;
        border-bottom:1px solid #333;
    }

 .tabela-demanda tbody tr:nth-child(even){
    background:#262730;
}

.tabela-demanda tbody tr:nth-child(odd){
    background:#1f1f1f;
}

.tabela-demanda tbody tr:hover{
    background:#3b3b3b;
}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(html_tabela, unsafe_allow_html=True)
    # =====================================
    # GRÁFICO
    # =====================================

    # Dados da previsão
    tabela_previsao = pd.DataFrame({
        "Semana": [len(demandas) + 1],
        "Demanda": [previsao]
    })

    fig = px.line(
        tabela,
        x="Semana",
        y="Demanda",
        markers=True
    )

    fig.add_scatter(
        x=tabela_previsao["Semana"],
        y=tabela_previsao["Demanda"],
        mode="markers+text",
        name="Previsão",
        showlegend=False,
        marker=dict(
            size=10,
            color="gold",
            symbol="star"
        ),
        text=[f"{previsao:.2f}"],
        textposition="top right"
    )

    fig.update_layout(
        title={
            "text": "Histórico e previsão da demanda",
            "x": 0.5,
            "xanchor": "center"
        },
        xaxis_title="Semana",
        yaxis_title="Demanda"
    )

    fig.add_scatter(
        x=[tabela["Semana"].iloc[-1], tabela_previsao["Semana"].iloc[0]],
        y=[tabela["Demanda"].iloc[-1], tabela_previsao["Demanda"].iloc[0]],
        mode="lines",
        line=dict(
            dash="dash",
            color="red",
            width=1.5
        ),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # =====================================
    # INDICADORES
    # =====================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📈 Maior", f"{max(demandas):.0f}")

    with col2:
        st.metric("📉 Menor", f"{min(demandas):.0f}")

    with col3:
        st.metric("📊 Média", f"{sum(demandas)/len(demandas):.2f}")

    with col4:
        st.metric("📅 Períodos", len(demandas))

# =====================================
# COMPARAÇÃO DOS MÉTODOS
# =====================================

    # Média Móvel
    media_movel = sum(demandas) / len(demandas)

    # Suavização Exponencial
    alfa = 0.3
    suavizacao = demandas[0]

    for demanda in demandas[1:]:
        suavizacao = alfa * demanda + (1 - alfa) * suavizacao

    # Regressão Linear
    x = np.arange(1, len(demandas) + 1)
    coeficientes = np.polyfit(x, demandas, 1)

    inclinacao = coeficientes[0]
    intercepto = coeficientes[1]

    proxima_semana = len(demandas) + 1
    regressao = inclinacao * proxima_semana + intercepto

    st.divider()

    st.subheader("📊 Comparação dos Métodos")

    comparacao = pd.DataFrame({
    "Método": [
        "Média Móvel",
        "Suavização Exponencial",
        "Regressão Linear"
    ],
    "Previsão": [
        f"{media_movel:.2f}",
        f"{suavizacao:.2f}",
        f"{regressao:.2f}"
    ]
    })

    st.dataframe(
    comparacao,
    use_container_width=True,
    hide_index=True
    )

    st.info(
    """
### 📊 Análise Comparativa

**Média Móvel:** indicada para demandas mais estáveis, sem grandes oscilações.
É simples, rápida e bastante utilizada para previsões de curto prazo.


**Suavização Exponencial:** atribui maior peso aos dados mais recentes, sendo mais sensível às mudanças.
É recomendada quando a demanda sofre pequenas variações ao longo do tempo.


**Regressão Linear:** ideal quando existe uma tendência clara de crescimento ou queda na demanda.
O método identifica a direção dos dados e projeta o próximo período.
"""
)

    # =====================================
    # PREVISÃO
    # =====================================

    st.divider()

    st.subheader("Resultado da Previsão")

    

    variacao = demandas[-1] - demandas[0]

    if variacao > 0:
        tendencia = "crescimento"

    elif variacao < 0:
        tendencia = "queda"

    else:
        tendencia = "estabilidade"


    if metodo == "Média Móvel":

        conclusao = (
            f"A demanda apresentou um comportamento de **{tendencia}** ao longo dos períodos analisados. "
            "A Média Móvel é indicada quando as variações são moderadas e a demanda tende a permanecer estável."
            )

    elif metodo == "Suavização Exponencial":

        conclusao = (
            f"A demanda apresentou um comportamento de **{tendencia}**. "
            "Como este método prioriza os dados mais recentes, ele responde melhor às mudanças ocorridas na série histórica."
        )

    else:

        conclusao = (
            f"A demanda apresentou uma tendência de **{tendencia}**. "
            "A Regressão Linear identificou essa direção e projetou o próximo período com base na tendência observada."
        )

    st.success(conclusao)

    st.divider()

    st.subheader("📄 Relatório Gerencial")

    st.markdown(f"""

    **📦 Produto:** {produto}

    **📅 Períodos analisados:** {len(demandas)}

    **📈 Método utilizado:** {metodo}

    **📊 Demanda média:** {sum(demandas)/len(demandas):.2f} unidades

    **🔺 Maior demanda:** {max(demandas):.2f} unidades

    **🔻 Menor demanda:** {min(demandas):.2f} unidades

    **🔮 Previsão para o próximo período:** **{previsao:.2f} unidades**
    """)

    pdf = gerar_pdf(
        produto,
        metodo,
        previsao,
        demandas
    )

    st.download_button(
        label="📄 Baixar Relatório em PDF",
        data=pdf,
        file_name="Relatorio_Previsao_Demanda.pdf",
        mime="application/pdf"
    )
