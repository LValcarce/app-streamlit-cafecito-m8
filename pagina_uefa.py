import streamlit as st

def mostrar_datos_uefa():
    st.subheader("📊 Jugadores - UEFA Champions League 2024-2025")
    st.write("Estadísticas básicas de jugadores extraídas directamente de la UEFA.")
    
    st.markdown(
        """
        👉 Haz clic en el siguiente enlace para acceder a las estadísticas oficiales:
        
        [🔗 Ir a UEFA Player Stats](https://www.uefa.com/uefachampionsleague/statistics/players/)
        """,
        unsafe_allow_html=True
    )


