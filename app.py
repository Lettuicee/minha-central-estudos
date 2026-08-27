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
            width: 100%;
            height: 100%;
        }

        #quarto {
            position: relative;
            width: 700px;
            max-width: 100%;
            margin: 0 auto;
        }

        #fundo {
            width: 100%;
            display: block;
        }

        .movel {
            position: absolute;
            cursor: grab;
            user-select: none;
        }

        #livros {
            width: 12%;
            z-index: 2;
        }

        #coelho {
            width: 25%;
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

            if (!data) {
                return;
            }

            const cenario = parentElement.querySelector(
                "#cenario"
            );

            let quarto = cenario.querySelector(
                "#quarto"
            );

            if (!quarto) {

                quarto = document.createElement("div");

                quarto.id = "quarto";

                const fundo =
                    document.createElement("img");

                fundo.id = "fundo";

                quarto.appendChild(fundo);

                cenario.appendChild(quarto);
            }


            const fundo = quarto.querySelector(
                "#fundo"
            );

            fundo.src =
                "data:image/png;base64," +
                data.quarto;


            let livros = quarto.querySelector(
                "#livros"
            );

            if (data.livros_comprados) {

                if (!livros) {

                    livros =
                        document.createElement("img");

                    livros.id = "livros";

                    livros.className = "movel";

                    quarto.appendChild(livros);
                }

                livros.src =
                    "data:image/png;base64," +
                    data.livros;

                livros.style.left =
                    data.livros_x + "%";

                livros.style.top =
                    data.livros_y + "%";

            } else if (livros) {

                livros.remove();
            }


            let coelho = quarto.querySelector(
                "#coelho"
            );

            if (!coelho) {

                coelho =
                    document.createElement("img");

                coelho.id = "coelho";

                coelho.className = "movel";

                quarto.appendChild(coelho);
            }

            coelho.src =
                "data:image/png;base64," +
                data.coelho;

            coelho.style.left =
                data.coelho_x + "%";

            coelho.style.top =
                data.coelho_y + "%";


            function tornarArrastavel(
                elemento,
                nomeObjeto
            ) {

                if (!elemento) {
                    return;
                }

                let arrastando = false;
                let deslocamentoX = 0;
                let deslocamentoY = 0;


                elemento.onmousedown =
                    function(evento) {

                        arrastando = true;

                        const elementoRect =
                            elemento.getBoundingClientRect();

                        deslocamentoX =
                            evento.clientX
                            - elementoRect.left;

                        deslocamentoY =
                            evento.clientY
                            - elementoRect.top;

                        elemento.style.cursor =
                            "grabbing";

                        evento.preventDefault();
                    };


                elemento.onmousemove =
                    function(evento) {

                        if (!arrastando) {
                            return;
                        }

                        const quartoRect =
                            quarto.getBoundingClientRect();

                        let x =
                            evento.clientX
                            - quartoRect.left
                            - deslocamentoX;

                        let y =
                            evento.clientY
                            - quartoRect.top
                            - deslocamentoY;

                        const maxX =
                            quartoRect.width
                            - elemento.offsetWidth;

                        const maxY =
                            quartoRect.height
                            - elemento.offsetHeight;

                        x = Math.max(
                            0,
                            Math.min(x, maxX)
                        );

                        y = Math.max(
                            0,
                            Math.min(y, maxY)
                        );

                        elemento.style.left =
                            x + "px";

                        elemento.style.top =
                            y + "px";
                    };


                elemento.onmouseup =
                    function() {

                        if (!arrastando) {
                            return;
                        }

                        arrastando = false;

                        elemento.style.cursor =
                            "grab";

                        const quartoRect =
                            quarto.getBoundingClientRect();

                        const elementoRect =
                            elemento.getBoundingClientRect();

                        const x =
                            Math.round(
                                (
                                    elementoRect.left
                                    - quartoRect.left
                                )
                                / quartoRect.width
                                * 100
                            );

                        const y =
                            Math.round(
                                (
                                    elementoRect.top
                                    - quartoRect.top
                                )
                                / quartoRect.height
                                * 100
                            );

                        setTriggerValue(
                            "objeto_movido",
                            {
                                objeto: nomeObjeto,
                                x: x,
                                y: y
                            }
                        );
                    };
            }

            tornarArrastavel(
                livros,
                "livros"
            );

            tornarArrastavel(
                coelho,
                "coelho"
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

if "materia_aberta" not in st.session_state:
    st.session_state.materia_aberta = None
    
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

    if st.session_state.materia_aberta is not None:

        materia_aberta_id = (
            st.session_state.materia_aberta
        )

        resposta_materia = (
            supabase
            .table("materias")
            .select("*")
            .eq("id", materia_aberta_id)
            .execute()
        )

        if resposta_materia.data:

            materia = resposta_materia.data[0]

            if st.button("← Voltar para matérias"):

                st.session_state.materia_aberta = None

                st.rerun()

            st.title(
                f"📚 {materia['nome']}"
            )

            st.write(
                f"🎓 {materia['semestre']}"
            )

            st.write(
                f"👩‍🏫 "
                f"{materia['professor'] or 'Professor não informado'}"
            )

            st.divider()

            st.subheader("📖 Conteúdos da matéria")

            with st.form(
                "form_novo_topico",
                clear_on_submit=True
            ):

                titulo_topico = st.text_input(
                    "Nome da aula ou tópico"
                )

                adicionar_topico = (
                    st.form_submit_button(
                        "➕ Adicionar"
                    )
                )

                if adicionar_topico:

                    if titulo_topico:

                        try:

                            supabase.table(
                                "topicos"
                            ).insert({

                                "materia_id": materia["id"],

                                "titulo": titulo_topico

                            }).execute()

                            st.rerun()

                        except Exception as e:

                            st.error(
                                "Erro ao salvar o tópico:"
                            )

                            st.code(str(e))

                    else:

                        st.warning(
                            "Digite o nome do tópico."
                        )


            try:

                resposta_topicos = (
                    supabase
                    .table("topicos")
                    .select("*")
                    .eq(
                        "materia_id",
                        materia["id"]
                    )
                    .order(
                        "criado_em"
                    )
                    .execute()
                )

                topicos = resposta_topicos.data

            except Exception as e:

                st.error(
                    "Erro ao carregar os tópicos:"
                )

                st.code(str(e))

                topicos = []


            if topicos:

                for topico in topicos:
            
                    with st.expander(
                        f"📖 {topico['titulo']}"
                    ):
            
                        conteudo_atual = (
                            topico["conteudo"] or ""
                        )
            
                        with st.form(
                            f"form_conteudo_{topico['id']}"
                        ):
            
                            novo_conteudo = st.text_area(
                                "📝 Anotações",
                                value=conteudo_atual,
                                height=250,
                                key=f"conteudo_{topico['id']}"
                            )
            
                            salvar_conteudo = (
                                st.form_submit_button(
                                    "💾 Salvar anotações"
                                )
                            )
            
                            if salvar_conteudo:
            
                                try:
            
                                    supabase.table(
                                        "topicos"
                                    ).update({
                                        "conteudo": novo_conteudo
                                    }).eq(
                                        "id",
                                        topico["id"]
                                    ).execute()
            
                                    st.success(
                                        "Anotações salvas! 📚"
                                    )
            
                                    st.rerun()
            
                                except Exception as e:
            
                                    st.error(
                                        "Erro ao salvar as anotações:"
                                    )
            
                                    st.code(str(e))

            else:

                st.info(
                    "Você ainda não adicionou nenhum "
                    "tópico nesta matéria."
                )

        else:

            st.warning(
                "Essa matéria não foi encontrada."
            )

            st.session_state.materia_aberta = None


    else:

        with st.form(
            "form_materia",
            clear_on_submit=True
        ):
    
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
        
                with st.container(
                    border=True
                ):
        
                    st.subheader(
                        f"📚 {materia['nome']}"
                    )
        
                    st.write(
                        f"🎓 {materia['semestre']}"
                    )
        
                    st.write(
                        f"👩‍🏫 "
                        f"{materia['professor'] or 'Professor não informado'}"
                    )
        
                
                    if st.button(
                        "📖 Abrir matéria",
                        key=f"abrir_{materia['id']}",
                        use_container_width=True
                    ):
        
                        st.session_state.materia_aberta = (
                            materia["id"]
                        )
        
                        st.rerun()
        
        
                    col1, col2 = st.columns(2)
            
        
                    with col1:
        
                        if st.button(
                            "✏️ Editar",
                            key=f"editar_{materia['id']}",
                            use_container_width=True
                        ):
        
                            st.session_state[
                                "materia_editando"
                            ] = materia["id"]
        
                            st.rerun()
        
        
                    with col2:
        
                        if st.button(
                            "🗑️ Excluir",
                            key=f"excluir_{materia['id']}",
                            use_container_width=True
                        ):
        
                            supabase.table(
                                "materias"
                            ).delete().eq(
                                "id",
                                materia["id"]
                            ).execute()
        
                            st.rerun()
        
        
                if (
                    st.session_state.get(
                        "materia_editando"
                    )
                    == materia["id"]
                ):
        
                    st.divider()
        
                    st.subheader(
                        f"✏️ Editando: {materia['nome']}"
                    )
        
                    with st.form(
                        f"form_editar_{materia['id']}"
                    ):
        
                        novo_nome = st.text_input(
                            "Nome da matéria",
                            value=materia["nome"]
                        )
        
                        novo_semestre = st.selectbox(
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
                            ],
                            index=[
                                "1º semestre",
                                "2º semestre",
                                "3º semestre",
                                "4º semestre",
                                "5º semestre",
                                "6º semestre",
                                "7º semestre",
                                "8º semestre"
                            ].index(
                                materia["semestre"]
                            )
                        )
        
                        novo_professor = st.text_input(
                            "Professor(a)",
                            value=materia["professor"] or ""
                        )
        
        
                        salvar = st.form_submit_button(
                            "💾 Salvar alterações"
                        )
        
        
                        if salvar:
        
                            supabase.table(
                                "materias"
                            ).update({
        
                                "nome": novo_nome,
        
                                "semestre": novo_semestre,
        
                                "professor": novo_professor
        
                            }).eq(
                                "id",
                                materia["id"]
                            ).execute()
        
        
                            st.session_state[
                                "materia_editando"
                            ] = None
        
                            st.rerun()
    
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
                "livros_y": livros_y,
                "coelho_x": coelho_x,
                "coelho_y": coelho_y
            },
            key="meu_quarto",
            on_objeto_movido_change=lambda: None
        )

        if resultado_quarto.objeto_movido:

            movimento = resultado_quarto.objeto_movido

            novo_x = movimento["x"]

            novo_y = movimento["y"]

            objeto = movimento["objeto"]


            if objeto == "livros":

                supabase.table(
                    "carteira"
                ).update({
                    "livros_x": novo_x,
                    "livros_y": novo_y
                }).eq(
                    "id",
                    carteira.data[0]["id"]
                ).execute()


            elif objeto == "coelho":

                supabase.table(
                    "carteira"
                ).update({
                    "coelho_x": novo_x,
                    "coelho_y": novo_y
                }).eq(
                    "id",
                    carteira.data[0]["id"]
                ).execute()


            st.rerun()

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
