import streamlit as st

st.set_page_config(
    page_title="Minha Central de Estudos",
    page_icon="🌹",
    layout="wide"
)

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Inter:wght@300;400;500&display=swap');

.stApp {
    background: #171315;
    color: #f3e8dc;
}

h1, h2, h3 {
    font-family: 'Cormorant Garamond', serif !important;
}

p, div, span, button {
    font-family: 'Inter', sans-serif;
}

.titulo {
    font-family: 'Cormorant Garamond', serif;
    font-size: 58px;
    text-align: center;
    color: #ead7c3;
    margin-top: 60px;
}

.subtitulo {
    text-align: center;
    color: #b9a69a;
    font-size: 18px;
    margin-bottom: 50px;
}

.card {
    background: rgba(55, 39, 42, 0.75);
    border: 1px solid rgba(218, 191, 166, 0.2);
    border-radius: 18px;
    padding: 30px;
    margin: 10px;
}

.card h3 {
    color: #e5c9b0;
    font-size: 28px;
}

.card p {
    color: #c7b9b0;
}

</style>
""", unsafe_allow_html=True)


st.markdown(
    '<div class="titulo">🌹 Minha Central de Estudos</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">um pequeno lugar para organizar tudo o que estou aprendendo</div>',
    unsafe_allow_html=True
)


col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card">
        <h3>📚 Matérias</h3>
        <p>Organize suas disciplinas, conteúdos e materiais.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <h3>⏱️ Estudar</h3>
        <p>Registre seu tempo de estudo e acompanhe seu progresso.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
        <h3>📊 Estatísticas</h3>
        <p>Veja seu histórico diário, semanal e mensal.</p>
    </div>
    """, unsafe_allow_html=True)
