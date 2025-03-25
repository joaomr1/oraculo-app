import tempfile
import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
#from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
# from openai import error as openai_errors
from loaders import *

TIPOS_ARQUIVOS_VALIDOS = ['Site', 'Youtube', 'Pdf', 'Csv', 'Txt']

CONFIG_MODELOS = {
    'Groq': {
        'modelos': ['llama-3.1-70b-versatile', 'gemma2-9b-it', 'mixtral-8x7b-32768'],
        'chat': ChatGroq
    },
    #'OpenAI': {
    #    'modelos': ['gpt-4o-mini', 'gpt-4o', 'o1-preview', 'o1-mini'],
     #   'chat': ChatOpenAI
    #}
}

MEMORIA = ConversationBufferMemory()

def carrega_arquivos(tipo_arquivo, arquivo):
    if tipo_arquivo == 'Site':
        documento = carrega_site(arquivo)
    elif tipo_arquivo == 'Youtube':
        documento = carrega_youtube(arquivo)
    else:
        with tempfile.NamedTemporaryFile(suffix=f'.{tipo_arquivo.lower()}', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        if tipo_arquivo == 'Pdf':
            documento = carrega_pdf(nome_temp)
        elif tipo_arquivo == 'Csv':
            documento = carrega_csv(nome_temp)
        elif tipo_arquivo == 'Txt':
            documento = carrega_txt(nome_temp)
    return documento

def carrega_modelo(provedor, modelo, api_key, tipo_arquivo, arquivo):
    if not api_key:
        st.error("Por favor, informe a API Key.")
        st.stop()
    if not arquivo:
        st.error("Por favor, forneça o arquivo ou link correspondente.")
        st.stop()

    documento = carrega_arquivos(tipo_arquivo, arquivo)

    system_message = f'''Você é um assistente amigável chamado Oráculo.
    Você possui acesso às seguintes informações vindas 
    de um documento {tipo_arquivo}: 

    ####
    {documento}
    ####

    Utilize as informações fornecidas para basear as suas respostas.

    Sempre que houver $ na sua saída, substita por S.

    Se a informação do documento for algo como "Just a moment...Enable JavaScript and cookies to continue" 
    sugira ao usuário carregar novamente o Oráculo!'''

    template = ChatPromptTemplate.from_messages([
        ('system', system_message),
        ('placeholder', '{chat_history}'),
        ('user', '{input}')
    ])

    chat = CONFIG_MODELOS[provedor]['chat'](model=modelo, api_key=api_key)
    chain = template | chat

    st.session_state['chain'] = chain
    st.session_state['modelo_atual'] = modelo
    st.session_state['provedor_atual'] = provedor
    st.session_state['chat_template'] = template
    st.session_state['documento'] = documento

def pagina_chat():
    st.header('🤖 Bem-vindo ao Oráculo', divider=True)

    chain = st.session_state.get('chain')
    if chain is None:
        st.error('Carregue o Oráculo primeiro.')
        st.stop()

    if 'memoria' not in st.session_state:
        st.session_state['memoria'] = MEMORIA

    memoria = st.session_state['memoria']

    modelo_atual = st.session_state.get('modelo_atual')
    if modelo_atual:
        st.caption(f'Modelo atual: {modelo_atual}')

    for mensagem in memoria.buffer_as_messages:
        chat = st.chat_message(mensagem.type)
        chat.markdown(mensagem.content)

    input_usuario = st.chat_input('Fale com o Oráculo')
    if input_usuario:
        chat = st.chat_message('human')
        chat.markdown(input_usuario)

        chat = st.chat_message('ai')
        try:
            resposta = chat.write_stream(st.session_state['chain'].stream({
                'input': input_usuario,
                'chat_history': memoria.buffer_as_messages
            }))
        except Exception as e:
            st.error(f"Ocorreu um erro ao responder: {str(e)}")

            try:
                groq_api_key = st.session_state.get('api_key_Groq')
                if not groq_api_key:
                    raise Exception("API Key da Groq não encontrada.")
                chat = ChatGroq(model="llama-3.1-70b-versatile", api_key=groq_api_key)
                chain = st.session_state['chat_template'] | chat
                st.session_state['chain'] = chain
                st.session_state['modelo_atual'] = "llama-3.1-70b-versatile"
                resposta = chat.write_stream(chain.stream({
                    'input': input_usuario,
                    'chat_history': memoria.buffer_as_messages
                }))
            except Exception as e:
                st.error("Erro ao trocar para Groq: " + str(e))
                resposta = "O Oráculo está sem acesso às APIs no momento."
        except Exception as e:
            st.error(f"Erro ao gerar resposta: {e}")
            resposta = "O Oráculo teve um problema ao responder. Tente novamente."

        memoria.chat_memory.add_user_message(input_usuario)
        memoria.chat_memory.add_ai_message(resposta)
        st.session_state['memoria'] = memoria

def sidebar():
    tabs = st.tabs(['Upload de Arquivos', 'Seleção de Modelos'])
    with tabs[0]:
        tipo_arquivo = st.selectbox('Selecione o tipo de arquivo', TIPOS_ARQUIVOS_VALIDOS)
        if tipo_arquivo == 'Site':
            arquivo = st.text_input('Digite a URL do site')
        elif tipo_arquivo == 'Youtube':
            arquivo = st.text_input('Digite a URL do vídeo')
        else:
            extensao = tipo_arquivo.lower()
            arquivo = st.file_uploader(f'Faça o upload do arquivo .{extensao}', type=[f'.{extensao}'])

    with tabs[1]:
        provedor = st.selectbox('Selecione o provedor do modelo', CONFIG_MODELOS.keys())
        modelo = st.selectbox('Selecione o modelo', CONFIG_MODELOS[provedor]['modelos'])
        api_key = st.text_input(
            f'Adicione a API Key para o provedor {provedor}',
            value=st.session_state.get(f'api_key_{provedor}')
        )
        st.session_state[f'api_key_{provedor}'] = api_key

    if st.button('Inicializar Oráculo', use_container_width=True):
        carrega_modelo(provedor, modelo, api_key, tipo_arquivo, arquivo)
    if st.button('Apagar Histórico de Conversa', use_container_width=True):
        st.session_state['memoria'] = MEMORIA

def main():
    with st.sidebar:
        sidebar()
    pagina_chat()

if __name__ == '__main__':
    main()