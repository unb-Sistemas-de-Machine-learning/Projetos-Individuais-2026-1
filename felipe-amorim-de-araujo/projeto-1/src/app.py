import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from agent import Agent
from price_checker import verify_price
from wishlist import Wishlist

st.set_page_config(page_title="Agente Literário", page_icon="📚", layout="centered")

@st.cache_resource
def load_agent():
    return Agent()

agent = load_agent()
wishlist = Wishlist()

st.title("📚 Agente Literário")
st.caption("Recomendações personalizadas e ofertas nas principais livrarias brasileiras.")

tab_rec, tab_wish = st.tabs(["Recomendações", "Lista de Desejos"])

with tab_rec:
    st.header("Quais livros você já leu?")
    st.write("Informe os títulos que você gostou para receber recomendações personalizadas.")

    with st.form("form_recomendacao"):
        books_input = st.text_area(
            "Livros lidos (um por linha):",
            placeholder="1984\nO Alquimista\nDom Casmurro",
            height=150,
        )
        k = st.slider("Quantidade de recomendações:", min_value=1, max_value=10, value=5)
        submitted = st.form_submit_button("Recomendar", type="primary")

    if submitted:
        books = [b.strip() for b in books_input.strip().splitlines() if b.strip()]
        if not books:
            st.warning("Informe ao menos um livro.")
        else:
            with st.spinner("Buscando recomendações e verificando preços..."):
                try:
                    recommendations = agent.recommend(books, k=k)
                    st.success(f"{len(recommendations)} recomendações encontradas!")

                    for i, rec in enumerate(recommendations, 1):
                        with st.expander(f"📖 {i}. {rec['title']}", expanded=True):
                            st.markdown(f"**Por que você vai gostar:**\n{rec['justification']}")

                            if rec.get("minimum_price"):
                                st.markdown(
                                    f"💰 **Menor preço:** R$ {rec['minimum_price']:.2f}"
                                    + (f" — {rec['cheapest_store']}" if rec.get("cheapest_store") else "")
                                )
                            if rec.get("offers"):
                                st.markdown("**Preços por loja:**")
                                for offer in rec["offers"]:
                                    st.markdown(f"- [{offer.store}]({offer.url}) — R$ {offer.price:.2f}")
                            else:
                                st.info("Preço não encontrado nas lojas consultadas.")

                            if st.button("➕ Adicionar à lista de desejos", key=f"add_{i}"):
                                added = wishlist.add(rec["title"])
                                st.success("Adicionado!" if added else "Já está na sua lista de desejos.")

                except Exception as e:
                    st.error(f"Erro ao processar recomendações: {e}")

with tab_wish:
    st.header("Minha Lista de Desejos")
    items = wishlist.list()

    if not items:
        st.info("Sua lista de desejos está vazia. Adicione livros pela aba de recomendações.")
    else:
        for item in items:
            col_title, col_price, col_remove = st.columns([4, 2, 1])

            with col_title:
                label = f"📚 **{item.title}**" + (f" — {item.authors}" if item.authors else "")
                st.markdown(label)

            with col_price:
                if st.button("Verificar preço", key=f"price_{item.title}"):
                    with st.spinner("Buscando..."):
                        offers = verify_price(item.title)
                    if offers:
                        for o in offers:
                            st.write(f"[{o.store}]({o.url}): R$ {o.price:.2f}")
                    else:
                        st.info("Não encontrado.")

            with col_remove:
                if st.button("🗑️", key=f"remove_{item.title}", help="Remover da lista"):
                    wishlist.remove(item.title)
                    st.rerun()
