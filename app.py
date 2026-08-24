import streamlit as st
import time
from supabase import create_client
from datetime import datetime

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

if "cronometro_rodando" not in st.session_state:
    st.session_state.cronometro_rodando = False

if "cronometro_inicio" not in st.session_state:
    st.session_state.cronometro_inicio = None

if "cronometro_acumulado" not in st.session_state:
    st.session_state.cronometro_acumulado = 0

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

                try:
                    supabase.table("materias").insert({
                        "nome": nome,
                        "semestre": semestre,
                        "professor": professor
                    }).execute()

                    st.success(
                        f"'{nome}' foi salva permanentemente! 🌷"
                    )

                    st.rerun()

                except Exception as e:
                    st.error("Erro ao salvar a matéria:")
                    st.code(str(e))

            else:
                st.warning(
                    "Digite o nome da matéria primeiro."
                )

    st.divider()

    st.subheader("📚 Disciplinas cadastradas")

    try:
        resposta = supabase.table(
            "materias"
        ).select("*").execute()

        materias = resposta.data

    except Exception as e:
        st.error("Erro ao consultar o Supabase:")
        st.code(str(e))
        materias = []

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

    resposta = supabase.table("materias").select("*").execute()
    materias = resposta.data

    if not materias:

        st.warning("Cadastre pelo menos uma matéria primeiro. 📚")

    else:

        nomes_materias = [
            materia["nome"]
            for materia in materias
        ]

        materia_escolhida = st.selectbox(
            "📚 O que você vai estudar?",
            nomes_materias
        )

        if st.session_state.cronometro_rodando:

            run_every = 1

        else:

            run_every = None


        @st.fragment(run_every=run_every)
        def mostrar_cronometro():

            if st.session_state.cronometro_rodando:

                tempo_atual = (
                    st.session_state.cronometro_acumulado
                    + time.time()
                    - st.session_state.cronometro_inicio
                )

            else:

                tempo_atual = (
                    st.session_state.cronometro_acumulado
                )


            horas = int(tempo_atual // 3600)

            minutos = int(
                (tempo_atual % 3600) // 60
            )

            segundos = int(
                tempo_atual % 60
            )


            st.markdown(
                f"""
                <div style="
                    text-align: center;
                    font-size: 70px;
                    font-family: serif;
                    margin: 30px;
                ">
                    ⏱️ {horas:02d}:{minutos:02d}:{segundos:02d}
                </div>
                """,
                unsafe_allow_html=True
            )


            col1, col2, col3 = st.columns(3)


            with col1:

                if st.button(
                    "▶️ Começar",
                    use_container_width=True
                ):

                    if not st.session_state.cronometro_rodando:

                        st.session_state.cronometro_inicio = time.time()

                        st.session_state.cronometro_rodando = True

                        st.rerun()


            with col2:

                if st.button(
                    "⏸️ Pausar",
                    use_container_width=True
                ):

                    if st.session_state.cronometro_rodando:

                        st.session_state.cronometro_acumulado += (
                            time.time()
                            - st.session_state.cronometro_inicio
                        )

                        st.session_state.cronometro_rodando = False

                        st.session_state.cronometro_inicio = None

                        st.rerun()


            with col3:
    
                if st.button(
                    "■ Finalizar",
                    use_container_width=True
                ):
    
                    if st.session_state.cronometro_rodando:
    
                        tempo_total = (
                            st.session_state.cronometro_acumulado
                            + time.time()
                            - st.session_state.cronometro_inicio
                        )
    
                    else:
    
                        tempo_total = (
                            st.session_state.cronometro_acumulado
                        )
    
                    if tempo_total > 0:
    
                        materia_atual = next(
                            (
                                materia
                                for materia in materias
                                if materia["nome"] == materia_escolhida
                            ),
                            None
                        )
    
                        supabase.table("sessoes_estudo").insert({
                            "materia_id": (
                                materia_atual["id"]
                                if materia_atual
                                else None
                            ),
                            "materia_nome": materia_escolhida,
                            "duracao_segundos": int(tempo_total)
                        }).execute()
    
                        minutos = int(tempo_total // 60)
    
                        st.success(
                            f"🎉 Sessão salva! "
                            f"Você estudou {minutos} minutos "
                            f"de {materia_escolhida}."
                        )
    
                    st.session_state.cronometro_rodando = False
                    st.session_state.cronometro_inicio = None
                    st.session_state.cronometro_acumulado = 0
    
                    st.rerun()

        mostrar_cronometro()

        st.caption(
            f"Estudando: {materia_escolhida} 📚"
        )

    st.divider()

    st.subheader("📖 Histórico de estudos")

    try:

        resposta_historico = (
            supabase
            .table("sessoes_estudo")
            .select("*")
            .order("criado_em", desc=True)
            .execute()
        )

        historico = resposta_historico.data

    except Exception as e:

        st.error("Erro ao carregar o histórico:")
        st.code(str(e))

        historico = []


    if historico:

        for sessao in historico:

            segundos = sessao["duracao_segundos"]

            horas = int(segundos // 3600)

            minutos = int(
                (segundos % 3600) // 60
            )

            segundos_restantes = int(
                segundos % 60
            )


            if horas > 0:

                duracao = (
                    f"{horas}h "
                    f"{minutos:02d}min"
                )

            else:

                duracao = (
                    f"{minutos}min "
                    f"{segundos_restantes:02d}s"
                )

            data_sessao = datetime.fromisoformat(
    sessao["criado_em"].replace("Z", "+00:00")
)

data_formatada = data_sessao.astimezone().strftime(
    "%d/%m/%Y às %H:%M"
)

st.markdown(
    f"""
    **📚 {sessao["materia_nome"]}**

    ⏱️ {duracao}

    🕐 {data_formatada}

    ---
    """
)

 else:

        st.info(
            "Nenhuma sessão de estudo registrada ainda. 🌷"
        )

elif pagina == "📊 Estatísticas":

    st.header("📊 Meu progresso")

    st.info("Seus gráficos e estatísticas aparecerão aqui. 📈")


elif pagina == "🔗 Meus lugares":

    st.header("🔗 Meus lugares")

    st.info("Aqui vamos colocar seus links para Notion, OneNote, Word, Drive etc. 🌷")
