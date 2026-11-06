import streamlit as st
import os

st.set_page_config(page_title="MTUCI RAG Bot", layout="wide")
st.title("🤖 Бот-помощник МТУСИ")


@st.cache_resource
def load_bot():
    from rag import RAGBot
    return RAGBot()


bot = load_bot()

with st.expander("⚙️ Настройки"):
    if st.button("Сбросить", key="reset_btn"):
        st.rerun()


query = st.text_input("📝 Ваш вопрос о документах МТУСИ:", 
                      placeholder="Например: как зачисляют студентов на 1 курс?")


if st.button("✨ Задать вопрос", key="ask_btn"):
    if not query.strip():
        st.warning("Введите вопрос!")
    else:
        with st.spinner("🤔 Ищу ответ в документах..."):
            try:
                result = bot.ask(query)
                with st.expander("📄 Полный ответ"):
                    st.markdown(result['answer'])
                
                with st.expander("📚 Источники"):
                    for i, source in enumerate(result['sources'], 1):
                        st.subheader(f"Источник {i}")
                        # distance == 0 (идеальное совпадение) иначе вызывал ZeroDivisionError
                        distance = float(source['distance'])
                        relevance = "идеальное совпадение" if distance < 1e-6 else f"1/{distance:.2f}"
                        st.info(f"Релевантность: {relevance}")
                        st.text(source['text'][:300] + "..." if len(source['text']) > 300 else source['text'])
            except Exception as e:
                st.error(f"Ошибка: {e}")


st.markdown("---")
st.caption("RAG-бот для документов МТУСИ | Студенческий ML-практикум")
