import streamlit as st
import time
import base64
from supabase import create_client
from datetime import datetime
from zoneinfo import ZoneInfo

quarto_interativo = st.components.v2.component(
    "quarto_interativo",
    html="""
        <div id="cenario"></div>
    """,
    css="""
        #cenario {
            width: 700px;
            max-width: 100%;
            margin: 0 auto;
        }

        #quarto {
            position: relative;
            width: 700px;
            max-width: 100%;
        }

        #fundo {
            width: 700px;
            max-width: 100%;
            display: block;
        }

        #livros {
            position: absolute;
            width: 18%;
            cursor: grab;
            user-select: none;
            z-index: 2;
        }

        #coelho {
            position: absolute;
            width: 39%;
            left: 50%;
            bottom: 4%;
            transform: translateX(-50%);
            z-index: 3;
        }
    """,
    js="""
        export default function(component) {

            const {
                data,
                parentElement,
                setTriggerValue
            } = component;

            const cenario = parentElement.querySelector(
                "#cenario"
            );

            if (!data) {
                return;
            }

            cenario.innerHTML = `
                <div id="quarto">

                    <img
                        id="fundo"
                        src="data:image/png;base64,${data.quarto}"
                    >

                    ${
                        data.livros_comprados
                        ? `
                            <img
                                id="livros"
                                src="data:image/png;base64,${data.livros}"
                                style="
                                    left: ${data.livros_x}%;
                                    bottom: ${data.livros_y}%;
                                "
                            >
                        `
                        : ""
                    }

                    <img
                        id="coelho"
                        src="data:image/png;base64,${data.coelho}"
                    >

                </div>
            `;

            const livros = cenario.querySelector("#livros");
            const quarto = cenario.querySelector("#quarto");

            if (!livros) {
                return;
            }

            let arrastando = false;
            let deslocamentoX = 0;
            let deslocamentoY = 0;

            livros.addEventListener(
                "mousedown",
                function(evento) {

                    arrastando = true;

                    const livrosRect =
                        livros.getBoundingClientRect();

                    deslocamentoX =
                        evento.clientX - livrosRect.left;

                    deslocamentoY =
                        evento.clientY - livrosRect.top;

                    livros.style.cursor = "grabbing";
                }
            );

            document.addEventListener(
                "mousemove",
                function(evento) {

                    if (!arrastando) {
                        return;
                    }

                    const quartoRect =
                        quarto.getBoundingClientRect();

                    let novaPosicaoX =
                        evento.clientX
                        - quartoRect.left
                        - deslocamentoX;

                    let novaPosicaoY =
                        evento.clientY
                        - quartoRect.top
                        - deslocamentoY;

                    const maxX =
                        quartoRect.width
                        - livros.offsetWidth;

                    const maxY =
                        quartoRect.height
                        - livros.offsetHeight;

                    novaPosicaoX =
                        Math.max(
                            0,
                            Math.min(
                                novaPosicaoX,
                                maxX
                            )
                        );

                    novaPosicaoY =
                        Math.max(
                            0,
                            Math.min(
                                novaPosicaoY,
                                maxY
                            )
                        );

                    livros.style.left =
                        novaPosicaoX + "px";

                    livros.style.top =
                        novaPosicaoY + "px";

                    livros.style.bottom = "auto";
                }
            );

            document.addEventListener(
                "mouseup",
                function() {

                    if (!arrastando) {
                        return;
                    }

                    arrastando = false;

                    livros.style.cursor = "grab";

                    const quartoRect =
                        quarto.getBoundingClientRect();

                    const livrosRect =
                        livros.getBoundingClientRect();

                    const posicaoX =
                        (
                            livrosRect.left
                            - quartoRect.left
                        )
                        / quartoRect.width
                        * 100;

                    const posicaoY =
                        (
                            quartoRect.bottom
                            - livrosRect.bottom
                        )
                        / quartoRect.height
                        * 100;

                    setTriggerValue(
                        "livros_movidos",
                        {
                            x: Math.round(posicaoX),
                            y: Math.round(posicaoY)
                        }
                    );
                }
            );
        }
    """
)

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

if "ultima_recompensa" not in st.session_state:
    st.session_state.ultima_recompensa = None
    
if "materias" not in st.session_state:
    st.session_state.materias = []

if "loja_aberta" not in st.session_state:
    st.session_state.loja_aberta = False

if "livros_comprados" not in st.session_state:
    st.session_state.livros_comprados = False
    
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

/* Esconde o bonequinho/STOP do Streamlit */
[data-testid="stStatusWidget"] {
    visibility: hidden;
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

    carteira = (
        supabase
        .table("carteira")
        .select(
            """
            id,
            moedas,
            livros_comprados,
            livros_x,
            livros_y,
            coelho_x,
            coelho_y
            """
        )
        .limit(1)
        .execute()
    )

    moedas = (
        carteira.data[0]["moedas"]
        if carteira.data
        else 0
    )

    livros_comprados = (
        carteira.data[0]["livros_comprados"]
        if carteira.data
        else False
    )

    livros_x = (
        carteira.data[0]["livros_x"]
        if carteira.data
        else 10
    )

    livros_y = (
        carteira.data[0]["livros_y"]
        if carteira.data
        else 8
    )

    coelho_x = (
        carteira.data[0]["coelho_x"]
        if carteira.data
        else 50
    )

    coelho_y = (
        carteira.data[0]["coelho_y"]
        if carteira.data
        else 4
    )

    st.markdown(
        f"""
        <div style="
            text-align: right;
            font-size: 22px;
            margin-bottom: 10px;
        ">
            🪙 <b>{moedas}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.ultima_recompensa:

        recompensa = st.session_state.ultima_recompensa

        st.success(
            f"""
🎉 **Sessão concluída!**

📚 **{recompensa["materia"]}**

⏱️ Você estudou **{recompensa["minutos"]} minutos**

🪙 Você ganhou **+{recompensa["moedas_ganhas"]} moedas!**

💰 Saldo atual: **{recompensa["saldo_total"]} moedas**
"""
        )

        if st.button("✨ Fechar recompensa"):

            st.session_state.ultima_recompensa = None

            st.rerun()

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

        with open("quarto.png", "rb") as arquivo:
            quarto_base64 = base64.b64encode(
                arquivo.read()
            ).decode("utf-8")

        if st.session_state.ultima_recompensa:
            imagem_coelho = "coelhofeliz.png"

        elif st.session_state.cronometro_rodando:
            imagem_coelho = "coelhoestudando.png"

        else:
            imagem_coelho = "coelhinho.png"

        with open(imagem_coelho, "rb") as arquivo:
            coelhinho_base64 = base64.b64encode(
                arquivo.read()
            ).decode("utf-8")

        if livros_comprados:

            with open("livros.png", "rb") as arquivo:
                livros_base64 = base64.b64encode(
                    arquivo.read()
                ).decode("utf-8")

        resultado_quarto = quarto_interativo(
            data={
                "quarto": quarto_base64,
                "coelho": coelhinho_base64,
                "livros": (
                    livros_base64
                    if livros_comprados
                    else ""
                ),
                "livros_comprados": livros_comprados,
                "livros_x": livros_x,
                "livros_y": livros_y
            },
            key="meu_quarto",
            on_livros_movidos_change=lambda: None
        )

        if resultado_quarto.livros_movidos:

            nova_posicao = (
                resultado_quarto.livros_movidos
            )

            novo_x = nova_posicao["x"]

            novo_y = nova_posicao["y"]

            supabase.table(
                "carteira"
            ).update({
                "livros_x": novo_x,
                "livros_y": novo_y
            }).eq(
                "id",
                carteira.data[0]["id"]
            ).execute()

            st.rerun()
            
        if st.button(
            "🪙 Loja do coelhinho",
            key="botao_loja",
            use_container_width=True
        ):

            st.session_state.loja_aberta = (
                not st.session_state.loja_aberta
            )

            st.rerun()


        if st.session_state.loja_aberta:

            st.markdown("### 🪙 Loja do Coelhinho")

            col_item, col_info = st.columns([1, 2])

            with col_item:

                st.image(
                    "livros.png",
                    width=120
                )

            with col_info:

                st.markdown("#### 📚 Pilha de livros")

                st.write("Preço: 🪙 1 moeda")

            if livros_comprados:

                 st.success("Você já possui este item! 📚")

            else:

                    if st.button(
                        "🪙 Comprar por 1 moeda",
                        key="comprar_livros"
                    ):

                        carteira = (
                            supabase
                            .table("carteira")
                            .select("*")
                            .limit(1)
                            .execute()
                        )

                        saldo_atual = carteira.data[0]["moedas"]

                        if saldo_atual >= 1:

                            novo_saldo = saldo_atual - 1

                            supabase.table(
                                "carteira"
                            ).update({
                                "moedas": novo_saldo,
                                "livros_comprados": True
                            }).eq(
                                "id",
                                carteira.data[0]["id"]
                            ).execute()

                            st.success(
                                "🎉 Você comprou a pilha de livros!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Você não tem moedas suficientes! 🥺"
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

                        # 🪙 Calcular moedas
                        moedas_ganhas = int(tempo_total // 60)
    
                        if moedas_ganhas > 0:
    
                            carteira = (
                                supabase
                                .table("carteira")
                                .select("*")
                                .limit(1)
                                .execute()
                            )
    
                            saldo_atual = carteira.data[0]["moedas"]
    
                            novo_saldo = (
                                saldo_atual + moedas_ganhas
                            )
    
                            supabase.table("carteira").update({
                                "moedas": novo_saldo
                            }).eq(
                                "id",
                                carteira.data[0]["id"]
                            ).execute()
                        
                    minutos = int(tempo_total // 60)

                    st.session_state.ultima_recompensa = {
                        "materia": materia_escolhida,
                        "minutos": minutos,
                        "moedas_ganhas": moedas_ganhas,
                        "saldo_total": novo_saldo
                    }

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

            segundos_restantes = int(segundos % 60)

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

            data_sao_paulo = data_sessao.astimezone(
                ZoneInfo("America/Sao_Paulo")
            )

            data_formatada = data_sao_paulo.strftime(
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
