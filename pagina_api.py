import streamlit as st
import requests
import pandas as pd
import json
import plotly.express as px

# URL y token de autenticación para la API
API_URL = "https://api-cafecito.onrender.com/matches/competition/europe-champions-league-2024-2025"
HEADERS = {
    "Authorization": "Bearer EAAHlp1ycWFIBOzFZASIPjVtB1n30C8jUBKHo"
}

# Funciones cacheadas para obtener datos
@st.cache_data(show_spinner="🔄 Cargando partidos desde la API...")
def obtener_partidos():
    response = requests.get(API_URL, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@st.cache_data
def obtener_jugadores(match_id):
    url = f"https://api-cafecito.onrender.com/match/players/{match_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None

@st.cache_data
def obtener_eventos(match_id):
    url = f"https://api-cafecito.onrender.com/match/events/{match_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None

# Función principal para mostrar la tabla de partidos
def mostrar_datos_api():
    st.subheader("\U0001F310 Datos de la API de Cafecito")

    data = obtener_partidos()
    if data:
        df = pd.DataFrame(data)

        if df.empty:
            st.warning("La API no devolvió ningún dato.")
            return

        columnas = ["date", "home_team", "away_team", "home_score", "away_score", "match_id"]
        nombres_columnas = {
            "date": "Fecha",
            "home_team": "Local",
            "away_team": "Visitante",
            "home_score": "Goles Local",
            "away_score": "Goles Visitante",
            "match_id": "ID Partido"
        }

        df_reducido = df[columnas].rename(columns=nombres_columnas)
        st.dataframe(df_reducido)

        match_id = st.selectbox("\U0001F50E Selecciona un partido por ID", df_reducido["ID Partido"])
        mostrar_jugadores_del_partido(match_id)

    else:
        st.error("\u274C No se pudieron obtener los partidos desde la API.")

# Función para mostrar los jugadores de un partido y eventos del jugador seleccionado
def mostrar_jugadores_del_partido(match_id):
    data = obtener_jugadores(match_id)
    if not data:
        st.error("\u274C No se pudieron obtener los jugadores.")
        return

    try:
        home_players = data.get("homePlayers", [])
        away_players = data.get("awayPlayers", [])

        equipo_local = data.get("homeTeamName", "Equipo Local")
        equipo_visitante = data.get("awayTeamName", "Equipo Visitante")

        for jugador in home_players:
            jugador["equipo"] = equipo_local
        for jugador in away_players:
            jugador["equipo"] = equipo_visitante

        jugadores_totales = home_players + away_players

        if jugadores_totales:
            df = pd.DataFrame(jugadores_totales)

            columnas_a_mostrar = ["playerName", "jerseyNumber", "formationSlot", "matchStart", "equipo"]
            columnas_existentes = [col for col in columnas_a_mostrar if col in df.columns]
            df = df[columnas_existentes]
            df.columns = ["Jugador", "Dorsal", "Posición", "Titular", "Equipo"]

            st.subheader(f"\U0001F465 Jugadores del partido: {equipo_local} vs {equipo_visitante}")
            st.dataframe(df)

            jugadores_unicos = df[["Jugador", "Equipo"]].drop_duplicates()
            jugador_seleccionado = st.selectbox("\U0001F3AF Elige un jugador para ver sus eventos", jugadores_unicos["Jugador"])

            player_id = None
            for jugador in jugadores_totales:
                if jugador["playerName"] == jugador_seleccionado:
                    player_id = jugador["playerId"]
                    break

            if player_id:
                st.subheader(f"\U0001F4CB Eventos de {jugador_seleccionado}")
                mostrar_eventos_de_jugador(match_id, player_id)
            else:
                st.warning("No se encontró el ID del jugador seleccionado.")
        else:
            st.info("No se encontraron jugadores para este partido.")
    except Exception as e:
        st.error(f"\u26A0\ufe0f Error al procesar los datos de jugadores: {e}")

# Función para mostrar eventos filtrados por jugador
def mostrar_eventos_de_jugador(match_id, player_id):
    data = obtener_eventos(match_id)
    if not data or "events" not in data:
        st.warning("⚠️ La estructura de datos recibida no contiene 'events'.")
        st.json(data)
        return

    eventos = data["events"]

    if not isinstance(eventos, list):
        st.warning("⚠️ 'events' no es una lista válida.")
        st.json(eventos)
        return

    eventos_jugador = [e for e in eventos if isinstance(e, dict) and e.get("playerId") == player_id]

    if eventos_jugador:
        df_eventos = pd.DataFrame(eventos_jugador)

        def extraer_display_name(x):
            try:
                if isinstance(x, str):
                    x = json.loads(x)
                if isinstance(x, dict) and "displayName" in x:
                    return x["displayName"]
            except Exception:
                pass
            return "Desconocido"

        df_eventos["tipo_evento"] = df_eventos["type"].apply(extraer_display_name)

        resumen = df_eventos["tipo_evento"].value_counts().reset_index()
        resumen.columns = ["Tipo de Evento", "Total"]

        st.subheader("📊 Resumen de eventos del jugador")
        st.dataframe(resumen)

        fig = px.bar(resumen, x="Tipo de Evento", y="Total", color="Tipo de Evento", text="Total",
                     title="Distribución de eventos del jugador")
        st.plotly_chart(fig)

        st.download_button(
            label="📥 Descargar resumen como CSV",
            data=resumen.to_csv(index=False).encode('utf-8'),
            file_name="resumen_eventos.csv",
            mime="text/csv"
        )

        st.markdown(
            """
            <button onclick="window.print()" style="background-color:#4CAF50; color:white; padding:10px; font-size:16px; border:none; border-radius:5px; cursor:pointer;">
                🖨️ Imprimir Página
            </button>
            """,
            unsafe_allow_html=True
        )

        st.subheader("📋 Detalle completo de los eventos")
        columnas = ["minute", "tipo_evento"]
        if all(c in df_eventos.columns for c in columnas):
            st.dataframe(df_eventos[columnas])
        else:
            st.dataframe(df_eventos)
    else:
        st.info("Este jugador no tiene eventos registrados en este partido.")


