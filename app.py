import streamlit as st
from pagina_uefa import mostrar_datos_uefa
from pagina_api import mostrar_datos_api



# ---------- Función de Login ----------
def check_password():
    st.title("🔐 App Deportiva Módulo 8 - Login")
    st.image("imagen.webp", width=300)


    def password_entered():
        if st.session_state["password"] == "MPAD":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Contraseña", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Contraseña", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Contraseña incorrecta")
        return False
    else:
        return True

# ---------- Interfaz Principal ----------
if check_password():
    st.sidebar.title("⚽ App Deportiva Módulo 8")
    pagina = st.sidebar.radio("Menú de navegación:", 
                              ["Inicio", "Jugadores (UEFA)", "Jugadores (API Cafecito)"])

    if pagina == "Inicio":
        st.title("🏟️ Bienvenido al análisis deportivo")
        st.write("Selecciona una página desde el menú lateral para comenzar.")
        

    elif pagina == "Jugadores (UEFA)":
        mostrar_datos_uefa()
    elif pagina == "Jugadores (API Cafecito)":
        mostrar_datos_api()
  






