import streamlit as st
from utils import ocultar_cpf_e_placa_em_pdf

# Configuração do header com imagem e título
header = st.container()
with header:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<style>h1 { margin-left: 0px; font-size: 20px; }</style>', unsafe_allow_html=True)
        st.title('Superintendência de Correição e Informações Estratégicas')
    with col2:
        st.image('./assets/logo_white.png', width=350)
        st.text("")

# Configuração do app Streamlit
st.title("Verificador e Editor de CPF e Placas em PDFs")
st.write("Faça upload de um ou mais arquivos PDF para verificar e ocultar CPFs e placas de veículos.")

# Upload de múltiplos PDFs
pdf_files = st.file_uploader(
    "Arraste e solte os arquivos aqui ou clique para selecionar", 
    type=["pdf"], 
    accept_multiple_files=True,
    help="Limite de 200 MB por arquivo • Apenas arquivos PDF"
)

# Inicializa o dicionário no estado da sessão para armazenar PDFs processados
if 'pdfs_processados' not in st.session_state:
    st.session_state['pdfs_processados'] = {}

if pdf_files:
    # Configuração da barra de progresso interna
    progresso_interno = st.progress(0)  

    for pdf_file in pdf_files:
        # Verifica se o PDF já foi processado na sessão atual
        if pdf_file.name not in st.session_state['pdfs_processados']:
            pdf_bytes = pdf_file.read()
            
            # Processa e armazena o PDF processado em session_state
            pdf_editado = ocultar_cpf_e_placa_em_pdf(pdf_bytes, progresso_interno)
            st.session_state['pdfs_processados'][pdf_file.name] = pdf_editado  # Salva no estado da sessão
            
            # Exibe mensagem de sucesso para cada PDF
            st.success(f"CPF(s) e placa(s) ocultado(s) no arquivo: {pdf_file.name}")

        # Botão para baixar o PDF processado (sem reprocessamento)
        st.download_button(
            label=f"Baixar {pdf_file.name} Editado",
            data=st.session_state['pdfs_processados'][pdf_file.name],  # Usa o PDF armazenado
            file_name=f"tarja_{pdf_file.name}",
            mime="application/pdf"
        )

    # Finaliza a barra de progresso após o processamento de todos os arquivos
    progresso_interno.empty()
