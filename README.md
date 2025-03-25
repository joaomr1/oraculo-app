# Oráculo 🤖📚

Aplicação de agente de IA interativa desenvolvida com **Streamlit**, **LangChain** e integração com **OpenAI** e **Groq**.

## 📦 Funcionalidades

- Suporte a arquivos: PDF, CSV, TXT
- Suporte a URLs: Sites e YouTube
- Modelos de linguagem:
  - OpenAI (GPT-4o, etc.)
  - Groq (LLaMA 3, Gemma, Mixtral)
- Memória de conversa
- Fallback automático para Groq se a OpenAI falhar

## 🚀 Como usar

1. Faça upload de um documento ou cole uma URL
2. Selecione o modelo e insira a chave da API
3. Converse com o Oráculo!

## 🌐 Deploy com Streamlit Cloud

1. Suba o projeto no GitHub
2. Vá para https://streamlit.io/cloud
3. Clique em "New App" e selecione:
   - Repositório: `oraculo-app`
   - Branch: `main`
   - Arquivo principal: `oraculo_main.py`
4. Pronto!

## 🔐 Configurar secrets (opcional)

No painel da Streamlit Cloud, adicione suas API keys em `Settings > Secrets`:

```toml
api_key_OpenAI = "sk-..."
api_key_Groq = "gsk_..."
```

---

Feito com ❤️ por João e Inteligência Artificial ⚡
