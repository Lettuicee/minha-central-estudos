import streamlit as st
from supabase import create_client

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

if "materias" not in st.session_state:
    st.session_state.materias = []
    
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

pagina = st.sidebar.radio(
    "🌹 Minha Central",
    [
        "🏠 Início",
        "📚 Matérias",
        "⏱️ Estudar",
        "📊 Estatísticas",
        "🔗 Meus lugares"
    ]
)

st.markdown(
    '<div class="titulo">🌹 Minha Central de Estudos</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">um pequeno lugar para organizar tudo o que estou aprendendo</div>',
    unsafe_allow_html=True
)


if pagina == "🏠 Início":

    st.markdown("""
    <div class="card">
        <h3>🌹 Bem-vinda</h3>
        <p>
        Esse é o seu espaço pessoal de estudos.
        Aqui você vai organizar matérias, estudar,
        acompanhar seu progresso e, futuramente,
        conversar com sua própria IA.
        </p>
    </div>
    """, unsafe_allow_html=True)


elif pagina == "📚 Matérias":

    st.header("📚 Minhas matérias")

    with st.form("form_materia"):

        nome = st.text_input("Nome da matéria")

        semestre = st.selectbox(
            "Semestre",
            [
                "1º semestre",
                "2º semestre",
                "3º semestre",
                "4º semestre",
                "5º semestre",
                "6º semestre",
                "7º semestre",
                "8º semestre"
            ]
        )

        professor = st.text_input("Professor(a)")

        enviar = st.form_submit_button(
            "🌹 Cadastrar matéria"
        )

        if enviar:

            if nome:

                supabase.table("materias").insert({
                    "nome": nome,
                    "semestre": semestre,
                    "professor": professor
                }).execute()

                st.success(
                    f"'{nome}' foi salva permanentemente! 🌷"
                )

                st.rerun()

            else:

                st.warning(
                    "Digite o nome da matéria primeiro."
                )

    st.divider()

    st.subheader("📚 Disciplinas cadastradas")

    resposta = supabase.table(
        "materias"
    ).select("*").execute()

    materias = resposta.data

    if materias:

        for materia in materias:

            st.markdown(
                f"""
                <div class="card">

                <h3>📚 {materia["nome"]}</h3>

                <p>
                🎓 {materia["semestre"]}
                </p>

                <p>
                👩‍🏫 {materia["professor"] or "Professor não informado"}
                </p>

                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.info(
            "Você ainda não cadastrou nenhuma matéria."
        )


elif pagina == "⏱️ Estudar":

    st.header("⏱️ Sessão de estudo")

    st.info("Nosso cronômetro vai ficar aqui. 🕯️")


elif pagina == "📊 Estatísticas":

    st.header("📊 Meu progresso")

    st.info("Seus gráficos e estatísticas aparecerão aqui. 📈")


elif pagina == "🔗 Meus lugares":

    st.header("🔗 Meus lugares")

    st.info("Aqui vamos colocar seus links para Notion, OneNote, Word, Drive etc. 🌷")
