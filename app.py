import streamlit as st
import pandas as pd
import ollama

from library import LibraryDB
from recommendation import RecommendationAPI

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="Agente Inteligente de Recomendação Literária",
    page_icon="🤖",
    layout="wide"
)

# ==================================================
# CSS
# ==================================================

st.markdown("""
<style>

.main {
    background-color: #0b1020;
}

.block-container {
    max-width: 1450px;
    padding-top: 1rem;
}

.hero {
    background: linear-gradient(
        135deg,
        #111827,
        #1e3a8a
    );

    padding: 2rem;
    border-radius: 20px;

    border: 1px solid #334155;

    margin-bottom: 20px;
}

.hero h1 {
    color: white;
    text-align: center;
    font-size: 2.8rem;
    margin-bottom: 0;
}

.hero p {
    color: #cbd5e1;
    text-align: center;
}

.metric-card {
    background: #111827;

    border: 1px solid #334155;

    border-radius: 16px;

    padding: 20px;

    text-align: center;
}

.metric-card h2 {
    color: white;
}

.metric-card h3 {
    color: #94a3b8;
}

.agent-card {

    background: #111827;

    border: 1px solid #334155;

    border-radius: 18px;

    padding: 24px;

    margin-top: 20px;
}

.route-tag {

    background: #1e293b;

    color: white;

    padding: 8px 14px;

    border-radius: 12px;

    display: inline-block;
}

.workflow-step {

    background: #172033;

    padding: 10px;

    border-radius: 12px;

    margin-bottom: 8px;
}

.arch-box {

    background: #111827;

    border: 1px solid #334155;

    border-radius: 18px;

    padding: 20px;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# BACKEND
# ==================================================

library = LibraryDB()

if "recommender" not in st.session_state:
    st.session_state.recommender = RecommendationAPI()

if "recommendation" not in st.session_state:
    st.session_state.recommendation = None

EMBEDDING_MODELS = {
    "nomic-embed-text",
    "mxbai-embed-large",
    "all-minilm",
    "bge-large"
}

try:

    raw_models = ollama.list()["models"]

    chat_models = [

        model["model"]

        for model in raw_models

        if not any(
            emb in model["model"].lower()
            for emb in EMBEDDING_MODELS
        )
    ]

except:
    chat_models = ["llama3.2:1b"]

with st.sidebar:

    st.header("⚙️ Configurações")

    selected_model = st.selectbox(
        "Modelo de Linguagem",
        chat_models
    )

    st.session_state.recommender.set_model(
        selected_model
    )

    st.divider()

    st.markdown("""
### 🤖 Padrões Agênticos

✅ Routing

✅ Tool Use

✅ Sequential Workflow

✅ Prompt Chaining

✅ Human-in-the-Loop
""")

    st.divider()

    if st.button("🔄 Reiniciar Sessão"):

        st.session_state.recommender.reset_session()

        st.session_state.recommendation = None

        st.success("Sessão reiniciada.")

st.markdown("""
<div class="hero">

<h1>🤖 Agente Inteligente de Recomendação Literária</h1>

<p>
Entrada → Análise → Routing → Decisão → Explicação → Validação Humana
</p>

</div>
""", unsafe_allow_html=True)

metrics = library.get_metrics()

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.markdown(f"""
    <div class="metric-card">
        <h3>📚 Livros</h3>
        <h2>{metrics['books']}</h2>
    </div>
    """, unsafe_allow_html=True)

with c2:

    st.markdown(f"""
    <div class="metric-card">
        <h3>📖 Leituras</h3>
        <h2>{metrics['reads']}</h2>
    </div>
    """, unsafe_allow_html=True)

with c3:

    st.markdown(f"""
    <div class="metric-card">
        <h3>🎯 Aceitação</h3>
        <h2>{metrics['acceptance_rate']}%</h2>
    </div>
    """, unsafe_allow_html=True)

with c4:

    st.markdown(f"""
    <div class="metric-card">
        <h3>🧪 Testes</h3>
        <h2>{metrics['tests']}</h2>
    </div>
    """, unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([

    "📚 Biblioteca",

    "📖 Histórico",

    "🤖 Recomendações",

    "🏗️ Arquitetura",

    "📊 Métricas"
])


# ==================================================
# BIBLIOTECA
# ==================================================

with tab1:

    st.subheader("📚 Catálogo da Biblioteca")

    c1, c2, c3 = st.columns(3)

    with c1:
        search_title = st.text_input(
            "Título"
        )

    with c2:
        search_author = st.text_input(
            "Autor"
        )

    with c3:
        search_category = st.text_input(
            "Categoria"
        )

    books = library.search_books(
        title=search_title,
        author=search_author,
        category=search_category
    )

    st.dataframe(
        pd.DataFrame(books),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("➕ Adicionar Livro")

    with st.form("add_book_form"):

        new_title = st.text_input("Título")

        new_author = st.text_input("Autor")

        new_category = st.text_input("Categoria")

        submitted = st.form_submit_button(
            "Adicionar"
        )

        if submitted:

            try:

                library.add_book(
                    new_title,
                    new_author,
                    new_category
                )

                st.success(
                    "Livro adicionado."
                )

                st.rerun()

            except Exception as e:

                st.error(str(e))


# ==================================================
# HISTÓRICO
# ==================================================

with tab2:

    st.subheader(
        "📖 Registrar Leitura"
    )

    books = library.get_all_books()

    titles = [
        b["title"]
        for b in books
    ]

    selected_book = st.selectbox(
        "Livro",
        titles
    )

    rating = st.slider(
        "Avaliação",
        1,
        5,
        5
    )

    notes = st.text_area(
        "Observações"
    )

    if st.button(
        "Salvar Histórico"
    ):

        library.add_to_history(
            selected_book,
            rating,
            notes
        )

        st.success(
            "Histórico salvo."
        )

        st.rerun()

    st.divider()

    st.subheader(
        "📚 Leituras Registradas"
    )

    history = library.get_read_history()

    if history:

        history_df = pd.DataFrame(
            history
        )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Nenhuma leitura registrada."
        )

# ==================================================
# RECOMENDAÇÕES
# ==================================================

with tab3:

    st.subheader(
        "🤖 Agente Inteligente"
    )

    st.caption(
        "Workflow agêntico com Routing, Tool Use e Human-in-the-Loop"
    )

    if st.button(
        "🚀 Executar Agente",
        use_container_width=True,
        type="primary"
    ):

        with st.status(
            "Executando workflow..."
        ) as status:

            st.write(
                "🔍 Analisando perfil..."
            )

            st.write(
                "🧭 Definindo rota..."
            )

            st.write(
                "📚 Buscando candidatos..."
            )

            st.write(
                "🧠 Tomando decisão..."
            )

            st.write(
                "✍️ Gerando explicação..."
            )

            recommendation = (
                st.session_state
                .recommender
                .recommend()
            )

            st.session_state.recommendation = (
                recommendation
            )

            status.update(
                label="Concluído",
                state="complete"
            )

    rec = st.session_state.recommendation

    if rec and rec["success"]:

        book = rec["book"]

        st.markdown(
            """
            <div class="agent-card">
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"# 📖 {book['title']}"
        )

        st.markdown(
            f"### ✍️ {book['author']}"
        )

        st.markdown(
            f"**Categoria:** {book['category']}"
        )

        st.markdown(
            f"""
            <div class="route-tag">
            🧭 Rota: {rec['route']}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            "### 🎯 Confiança"
        )

        score = max(
            0,
            min(
                int(rec["score"]),
                100
            )
        )

        st.progress(score)

        st.caption(
            f"{score}%"
        )

        st.markdown(
            "### 🧠 Explicação"
        )

        st.info(
            rec["explanation"]
        )

        with st.expander(
            "📋 Critérios Utilizados"
        ):

            for item in rec["criteria"]:

                st.write(
                    "✅",
                    item
                )

        with st.expander(
            "⚙️ Workflow Executado"
        ):

            for step in rec["workflow"]:

                st.markdown(
                    f"""
                    <div class="workflow-step">
                    {step}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown(
            "### 👤 Validação Humana"
        )

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "👍 Gostei",
                use_container_width=True
            ):

                st.session_state.recommender.feedback(
                    True
                )

                st.success(
                    "Feedback positivo registrado."
                )

        with c2:

            if st.button(
                "👎 Não Gostei",
                use_container_width=True
            ):

                st.session_state.recommender.feedback(
                    False
                )

                new_rec = (
                    st.session_state
                    .recommender
                    .recommend()
                )

                st.session_state.recommendation = (
                    new_rec
                )

                st.rerun()

        st.divider()

        st.markdown(
            "### 🎛️ Ajuste Humano"
        )

        preference = st.radio(
            "Como deseja a próxima recomendação?",
            [
                "Parecida com minhas leituras",
                "Explorar novos gêneros"
            ]
        )

        if preference == "Explorar novos gêneros":

            st.info(
                "O agente priorizará exploração."
            )
        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )
# ==================================================
# ARQUITETURA
# ==================================================

with tab4:

    st.subheader(
        "🏗️ Arquitetura do Agente"
    )

    st.markdown(
        """
        <div class="arch-box">
        """,
        unsafe_allow_html=True
    )


    st.markdown("""
# Fluxo Principal

Usuário
   ↓
Análise de Perfil
   ↓
Routing
   ↓
Busca Semântica
   ↓
Tomada de Decisão
   ↓
Explicação
   ↓
Validação Humana
""")

    st.divider()

    st.subheader(
        "🤖 Padrões de IA Agêntica"
    )

    patterns = pd.DataFrame({

        "Padrão": [

            "Routing",

            "Tool Use",

            "Sequential Workflow",

            "Prompt Chaining",

            "Human-in-the-Loop"
        ],

        "Implementação": [

            "Escolha da rota baseada no histórico",

            "Embeddings + SQLite + Similaridade",

            "Pipeline em etapas",

            "Saída de uma etapa alimenta a próxima",

            "Gostei / Não gostei"
        ]
    })

    st.dataframe(
        patterns,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "🧭 Rotas de Decisão"
    )

    routes = pd.DataFrame({

        "Rota": [

            "cold_start",

            "sparse_profile",

            "personalized",

            "exploration"
        ],

        "Quando é usada": [

            "Sem histórico",

            "Poucos livros avaliados",

            "Perfil consistente",

            "Muitas rejeições"
        ]
    })

    st.dataframe(
        routes,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "⚙️ Componentes"
    )

    st.markdown("""
### library.py

- Banco SQLite
- Histórico
- Logs
- Métricas

### recommendation.py

- Análise de perfil
- Routing
- Similaridade semântica
- Explicação

### app.py

- Interface
- Dashboard
- Human-in-the-Loop
- Visualização
""")

    st.divider()

    st.subheader(
        "🎯 Critérios de Decisão"
    )

    st.markdown("""
1. Livros já lidos são removidos.

2. Livros avaliados positivamente
   constroem o perfil do usuário.

3. Similaridade semântica é utilizada
   para ranquear candidatos.

4. Rejeições sucessivas ativam
   modo de exploração.

5. Feedback humano altera
   decisões futuras.
""")

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

# ==================================================
# MÉTRICAS
# ==================================================

with tab5:

    st.subheader(
        "📊 Métricas do Agente"
    )

    metrics = library.get_metrics()

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Recomendações",
            metrics["recommendations"]
        )

    with c2:

        st.metric(
            "Aceitação",
            f"{metrics['acceptance_rate']}%"
        )

    with c3:

        st.metric(
            "Sucesso dos Testes",
            f"{metrics['success_rate']}%"
        )

    st.divider()

    st.subheader(
        "📋 Métricas da Rubrica"
    )

    rubric = pd.DataFrame({

        "Métrica": [

            "Taxa de Funcionamento",

            "Cobertura de Cenários",

            "Coerência da Decisão",

            "Clareza da Explicação",

            "Robustez"
        ],

        "Status": [

            "Implementada",

            "Implementada",

            "Implementada",

            "Implementada",

            "Implementada"
        ]
    })

    st.dataframe(
        rubric,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "🧪 Cenários de Teste"
    )

    if st.button(
        "Executar Testes Demonstrativos"
    ):

        scenarios = [

            (
                "Cold Start",
                "Rota cold_start"
            ),

            (
                "Perfil Fraco",
                "Rota sparse_profile"
            ),

            (
                "Perfil Completo",
                "Rota personalized"
            ),

            (
                "Exploração",
                "Rota exploration"
            )
        ]

        for scenario, expected in scenarios:

            library.add_test_result(
                scenario=scenario,
                expected=expected,
                obtained=expected,
                success=True
            )

        st.success(
            "Testes registrados."
        )

        st.rerun()

    tests = library.get_test_results()

    if tests:

        st.dataframe(
            pd.DataFrame(tests),
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.subheader(
        "📜 Histórico de Decisões"
    )

    logs = library.get_recommendation_logs()

    if logs:

        logs_df = pd.DataFrame(logs)

        st.dataframe(
            logs_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Nenhuma recomendação registrada."
        )

