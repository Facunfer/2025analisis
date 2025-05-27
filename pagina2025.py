import pandas as pd
import geopandas as gpd
import streamlit as st
import folium
from streamlit_folium import folium_static
import plotly.graph_objects as go
import numpy as np

# --- CARGA DE DATOS ---
df_2025 = pd.read_csv("https://raw.githubusercontent.com/Facunfer/2025analisis/refs/heads/main/RESULTADOS%202025%20-%20CABA_1_1_DIP%20(1)%20(3)%20(1).csv")
df_2023 = pd.read_csv("https://raw.githubusercontent.com/Facunfer/2025analisis/refs/heads/main/RESULTADOS%202023%20-%20Hoja%201%20(2)%20(1).csv")

df_2025.columns = df_2025.columns.str.strip().str.upper()
df_2023.columns = df_2023.columns.str.strip().str.upper()

df_2025.rename(columns={
    'DESCRIPCION_CANDIDATURA': 'PARTIDO',
    'DESCRIPCION_UBICACION': 'BARRIO',
    'CANT_VOTOS': 'VOTOS'
}, inplace=True)

df_2023.rename(columns={
    'AGRUPACION_NOMBRE': 'PARTIDO',
    'VOTOS_CANTIDAD': 'VOTOS',
    'SECCION_NOMBRE': 'COMUNA'
}, inplace=True)

df_2025['PARTIDO'] = df_2025['PARTIDO'].str.upper().str.strip()
df_2023['PARTIDO'] = df_2023['PARTIDO'].str.upper().str.strip()
df_2025['BARRIO'] = df_2025['BARRIO'].str.upper().str.strip()
df_2023['BARRIO'] = df_2023['BARRIO'].str.upper().str.strip()

# --- INTERFAZ DE PESTAÑAS ---
tabs = st.tabs(["Análisis por Barrio", "Análisis por Comuna"])

# --- PESTAÑA 1: BARRIOS ---
with tabs[0]:
    # (Todo el código actual ya presente para análisis por barrio se mantiene sin cambios aquí)
    # --- INICIO DE CÓDIGO DE BARRIOS ---
 df_2025.rename(columns={
    'DESCRIPCION_CANDIDATURA': 'PARTIDO',
    'DESCRIPCION_UBICACION': 'BARRIO',
    'CANT_VOTOS': 'VOTOS'
}, inplace=True)

df_2023.rename(columns={
    'AGRUPACION_NOMBRE': 'PARTIDO',
    'VOTOS_CANTIDAD': 'VOTOS',
    'SECCION_NOMBRE': 'COMUNA'
}, inplace=True)

df_2025['PARTIDO'] = df_2025['PARTIDO'].str.upper().str.strip()
df_2023['PARTIDO'] = df_2023['PARTIDO'].str.upper().str.strip()
df_2025['BARRIO'] = df_2025['BARRIO'].str.upper().str.strip()
df_2023['BARRIO'] = df_2023['BARRIO'].str.upper().str.strip()

# --- MAPA ---
partido_lla = "LA LIBERTAD AVANZA"

v2025 = df_2025[df_2025['PARTIDO'] == partido_lla].groupby('BARRIO')['VOTOS'].sum().reset_index(name='VOTOS_2025')
v2023 = df_2023[df_2023['PARTIDO'] == partido_lla].groupby('BARRIO')['VOTOS'].sum().reset_index(name='VOTOS_2023')

tot_2025 = df_2025.groupby('BARRIO')['VOTOS'].sum().reset_index(name='TOTAL_2025')

df_2023_validos = df_2023[df_2023['PARTIDO'].isin([
    "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD",
    "JUNTOS POR EL CAMBIO",
    "UNION POR LA PATRIA",
    "LA LIBERTAD AVANZA"
])]
tot_2023 = df_2023_validos.groupby('BARRIO')['VOTOS'].sum().reset_index(name='TOTAL_2023')

df_barrio = v2025.merge(v2023, on='BARRIO', how='outer').fillna(0)
df_barrio = df_barrio.merge(tot_2025, on='BARRIO', how='left').merge(tot_2023, on='BARRIO', how='left')

df_barrio['PORC_2025'] = df_barrio['VOTOS_2025'] / df_barrio['TOTAL_2025'] * 100
df_barrio['PORC_2023'] = df_barrio['VOTOS_2023'] / df_barrio['TOTAL_2023'] * 100
df_barrio['DIF_ABS'] = df_barrio['VOTOS_2025'] - df_barrio['VOTOS_2023']
df_barrio['DIF_PORC'] = df_barrio['PORC_2025'] - df_barrio['PORC_2023']

comunas_2025 = df_2025[['BARRIO', 'COMUNA']].drop_duplicates()
df_barrio = df_barrio.merge(comunas_2025, on='BARRIO', how='left')

with tabs[0]:
 st.title("Mapa de Votos de La Libertad Avanza por Barrio")

 comunas_disponibles = sorted(df_barrio['COMUNA'].dropna().unique())
 comuna_seleccionada = st.selectbox("Seleccioná una comuna para visualizar:", ["Todas"] + comunas_disponibles)

 if comuna_seleccionada != "Todas":
    df_barrio = df_barrio[df_barrio['COMUNA'] == comuna_seleccionada]

 url_geojson = "https://cdn.buenosaires.gob.ar/datosabiertos/datasets/ministerio-de-educacion/barrios/barrios.geojson"
 geo = gpd.read_file(url_geojson)
 geo['BARRIO'] = geo['nombre'].str.upper()
 geo_filtrado = geo.merge(df_barrio, on='BARRIO', how='inner')

 # Mostrar mapa
 opcion = st.selectbox(
    "Seleccioná la capa a visualizar:",
    [
        "Cantidad de Votos LLA 2025",
        "Porcentaje LLA 2025",
        "Crecimiento en Votos 2023-2025",
        "Crecimiento porcentual 2023_2025"
    ]
 )

 config = {
    "Cantidad de Votos LLA 2025": {
        "col": "VOTOS_2025",
        "legend": "Votos LLA 2025",
        "formato": lambda x: f"{int(x):,} votos",
        "thresholds": [0, 1000, 2000, 4000, 6000, 8000, 10000, 12000]
    },
    "Porcentaje LLA 2025": {
        "col": "PORC_2025",
        "legend": "% LLA 2025",
        "formato": lambda x: f"{x:.1f}%",
        "thresholds": [20, 25, 27, 29, 31, 33, 36, 40, 45, 50]
    },
    "Crecimiento en Votos 2023-2025": {
        "col": "DIF_ABS",
        "legend": "Crecimiento de votos",
        "formato": lambda x: f"{int(x):+d} votos",
        "thresholds": [-1000, -500, 0, 500, 1000, 2000, 4000, 6000]
    },
    "Crecimiento porcentual 2023_2025": {
        "col": "DIF_PORC",
        "legend": "Crecimiento porcentual",
        "formato": lambda x: f"{x:+.1f}%",
        "thresholds": [-10, -5, 0, 2, 5, 10, 15, 20]
    }
 }

 columna = config[opcion]["col"]
 formatear = config[opcion]["formato"]
 leyenda = config[opcion]["legend"]
 thresholds_base = config[opcion]["thresholds"]

 min_val = geo_filtrado[columna].min()
 max_val = geo_filtrado[columna].max()
 thresholds_validos = thresholds_base.copy()
 if min_val < min(thresholds_validos):
    thresholds_validos = [min_val - 1] + thresholds_validos
 if max_val > max(thresholds_validos):
    thresholds_validos = thresholds_validos + [max_val + 1]

 m = folium.Map(location=[-34.61, -58.42], zoom_start=11)
 folium.Choropleth(
    geo_data=geo_filtrado,
    data=geo_filtrado,
    columns=['BARRIO', columna],
    key_on='feature.properties.BARRIO',
    fill_color='RdYlGn',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=leyenda,
    threshold_scale=thresholds_validos,
    reset=True
 ).add_to(m)

 for _, row in geo_filtrado.iterrows():
    valor = row[columna]
    if pd.notnull(valor):
        tooltip = f"{row['BARRIO'].title()}: {formatear(valor)}"
        centroide = row['geometry'].centroid
        folium.map.Marker(
            [centroide.y, centroide.x],
            icon=folium.DivIcon(html=f"<div style='font-size: 10px; color: black; text-align: center;'>{tooltip}</div>")
        ).add_to(m)

 folium.LayerControl().add_to(m)
 folium_static(m)

 # --- GRAFICOS DE BARRAS ---
 grupo_equivalentes = {
    'LA LIBERTAD AVANZA': 'LLA',
    'ES AHORA BUENOS AIRES': 'SANTORO',
    'BUENOS AIRES PRIMERO': 'PRO/JXC',
    'UNION POR LA PATRIA': 'SANTORO',
    'JUNTOS POR EL CAMBIO': 'PRO/JXC'
 }

 color_agrupaciones = {'LLA': 'indigo', 'SANTORO': 'darkblue', 'PRO/JXC': 'goldenrod'}

 votos_2025 = df_2025[df_2025['PARTIDO'].isin(grupo_equivalentes)].copy()
 votos_2025['AGRUPACION'] = votos_2025['PARTIDO'].map(grupo_equivalentes)
 votos_2025 = votos_2025.groupby(['BARRIO', 'AGRUPACION'])['VOTOS'].sum().reset_index(name='VOTOS_2025')

 votos_2023 = df_2023[df_2023['PARTIDO'].isin(grupo_equivalentes)].copy()
 votos_2023['AGRUPACION'] = votos_2023['PARTIDO'].map(grupo_equivalentes)
 votos_2023 = votos_2023.groupby(['BARRIO', 'AGRUPACION'])['VOTOS'].sum().reset_index(name='VOTOS_2023')

 df_votos = votos_2025.merge(votos_2023, on=['BARRIO', 'AGRUPACION'], how='outer').fillna(0)
 df_votos['DIF'] = df_votos['VOTOS_2025'] - df_votos['VOTOS_2023']
 df_votos['TOTAL'] = df_votos['VOTOS_2025'] + df_votos['VOTOS_2023']
 df_votos['PORC_2025'] = df_votos['VOTOS_2025'] / df_votos['TOTAL'] * 100
 df_votos['PORC_2023'] = df_votos['VOTOS_2023'] / df_votos['TOTAL'] * 100
 df_votos['DIF_PORC'] = df_votos['PORC_2025'] - df_votos['PORC_2023']

 if comuna_seleccionada != "Todas":
    df_votos = df_votos[df_votos['BARRIO'].isin(df_barrio['BARRIO'].unique())]

 # --- GRAFICO ABSOLUTO ---
 barrios_top = df_votos[df_votos['AGRUPACION'] == 'LLA'].nlargest(10, 'DIF')['BARRIO']
 df_top = df_votos[df_votos['BARRIO'].isin(barrios_top)]
 fig_abs = go.Figure()
 for agrup in ['LLA', 'SANTORO', 'PRO/JXC']:
    df_sub = df_top[df_top['AGRUPACION'] == agrup].set_index('BARRIO').loc[barrios_top].reset_index()
    fig_abs.add_trace(go.Bar(
        x=df_sub['BARRIO'],
        y=df_sub['DIF'],
        name=agrup,
        marker_color=color_agrupaciones[agrup],
        text=df_sub['DIF'],
        textposition='outside',
        textfont_size=16,
        offsetgroup=agrup
    ))
 fig_abs.update_layout(
    barmode='group',
    title="Crecimiento absoluto (2025 vs 2023)",
    xaxis_title="Barrio",
    yaxis_title="Crecimiento en votos",
    height=600,
    xaxis_tickangle=-45
 )
 st.plotly_chart(fig_abs)

 # --- GRAFICO PORCENTUAL CORREGIDO Y COMPLETO ---
 agrupaciones_2025 = {
    "LA LIBERTAD AVANZA": "LLA",
    "ES AHORA BUENOS AIRES": "SANTORO",
    "BUENOS AIRES PRIMERO": "PRO/JXC"
 }
 agrupaciones_2023 = {
    "LA LIBERTAD AVANZA": "LLA",
    "UNION POR LA PATRIA": "SANTORO",
    "JUNTOS POR EL CAMBIO": "PRO/JXC"
 }

 v25 = df_2025[df_2025['PARTIDO'].isin(agrupaciones_2025)].copy()
 v25['AGRUP'] = v25['PARTIDO'].map(agrupaciones_2025)
 v25 = v25.groupby(['BARRIO', 'AGRUP'])['VOTOS'].sum().reset_index(name='VOTOS_2025')

 total25 = df_2025.groupby('BARRIO')['VOTOS'].sum().reset_index(name='TOTAL_2025')
 v25 = v25.merge(total25, on='BARRIO', how='left')
 v25['PORC_2025'] = v25['VOTOS_2025'] / v25['TOTAL_2025'] * 100

 v23 = df_2023[df_2023['PARTIDO'].isin(agrupaciones_2023)].copy()
 v23['AGRUP'] = v23['PARTIDO'].map(agrupaciones_2023)
 v23 = v23.groupby(['BARRIO', 'AGRUP'])['VOTOS'].sum().reset_index(name='VOTOS_2023')

 total23 = df_2023[df_2023['PARTIDO'].isin(agrupaciones_2023)].groupby('BARRIO')['VOTOS'].sum().reset_index(name='TOTAL_2023')
 v23 = v23.merge(total23, on='BARRIO', how='left')
 v23['PORC_2023'] = v23['VOTOS_2023'] / v23['TOTAL_2023'] * 100

 porc = v25.merge(v23, on=['BARRIO', 'AGRUP'], how='outer').fillna(0)
 porc['DIF_PORC'] = porc['PORC_2025'] - porc['PORC_2023']

 if comuna_seleccionada != "Todas":
    porc = porc[porc['BARRIO'].isin(df_barrio['BARRIO'].unique())]

 barrios_top_porc = porc[porc['AGRUP'] == 'LLA'].nlargest(10, 'DIF_PORC')['BARRIO']
 porc_top = porc[porc['BARRIO'].isin(barrios_top_porc)]
 fig_porc = go.Figure()

 colores = {'LLA': 'indigo', 'SANTORO': 'darkblue', 'PRO/JXC': 'goldenrod'}

 for agrup in ['LLA', 'SANTORO', 'PRO/JXC']:
    df_sub = porc_top[porc_top['AGRUP'] == agrup].set_index('BARRIO').loc[barrios_top_porc].reset_index()
    fig_porc.add_trace(go.Bar(
        x=df_sub['BARRIO'],
        y=df_sub['DIF_PORC'],
        name=agrup,
        marker_color=colores[agrup],
        text=df_sub['DIF_PORC'].round(1).astype(str) + '%',
        textposition='outside',
        textfont_size=16,
        offsetgroup=agrup
    ))

 fig_porc.update_layout(
    barmode='group',
    title="Crecimiento en puntos porcentuales (2025 vs 2023)",
    xaxis_title="Barrio",
    yaxis_title="Puntos porcentuales",
    height=600,
    xaxis_tickangle=-45
 )
 st.plotly_chart(fig_porc)

 # --- PESTAÑA 2: COMUNAS ---
with tabs[1]:
    st.title("Análisis por Comuna")

    st.session_state.clear()

    partido_lla = "LA LIBERTAD AVANZA"

    votos_2025_com = df_2025[df_2025['PARTIDO'] == partido_lla].groupby('COMUNA')['VOTOS'].sum().reset_index(name='VOTOS_2025')
    votos_2023_com = df_2023[df_2023['PARTIDO'] == partido_lla].groupby('COMUNA')['VOTOS'].sum().reset_index(name='VOTOS_2023')
    total_2025_com = df_2025.groupby('COMUNA')['VOTOS'].sum().reset_index(name='TOTAL_2025')
    validos_2023 = df_2023[df_2023['PARTIDO'].isin([
        "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD",
        "JUNTOS POR EL CAMBIO",
        "UNION POR LA PATRIA",
        "LA LIBERTAD AVANZA"])]
    total_2023_com = validos_2023.groupby('COMUNA')['VOTOS'].sum().reset_index(name='TOTAL_2023')

    df_comuna = votos_2025_com.merge(votos_2023_com, on='COMUNA', how='outer').fillna(0)
    df_comuna = df_comuna.merge(total_2025_com, on='COMUNA', how='left').merge(total_2023_com, on='COMUNA', how='left')

    df_comuna['PORC_2025'] = df_comuna['VOTOS_2025'] / df_comuna['TOTAL_2025'] * 100
    df_comuna['PORC_2023'] = df_comuna['VOTOS_2023'] / df_comuna['TOTAL_2023'] * 100
    df_comuna['DIF_ABS'] = df_comuna['VOTOS_2025'] - df_comuna['VOTOS_2023']
    df_comuna['DIF_PORC'] = df_comuna['PORC_2025'] - df_comuna['PORC_2023']

    geo_url = "https://cdn.buenosaires.gob.ar/datosabiertos/datasets/ministerio-de-educacion/comunas/comunas.geojson"
    geo = gpd.read_file(geo_url)
    geo['COMUNA'] = geo['comuna'].astype(int).apply(lambda x: f"COMUNA {x:02d}")
    df_comuna['COMUNA'] = df_comuna['COMUNA'].str.extract(r'(\d+)')
    df_comuna['COMUNA'] = df_comuna['COMUNA'].astype(int).apply(lambda x: f"COMUNA {x:02d}")
    geo_comuna = geo.merge(df_comuna, on='COMUNA', how='left')

    comunas_disponibles = sorted(df_comuna['COMUNA'].dropna().unique())
    comuna_seleccionada = st.selectbox("Seleccioná una comuna para visualizar:", ["Todas"] + comunas_disponibles)
    if comuna_seleccionada != "Todas":
        df_comuna = df_comuna[df_comuna['COMUNA'] == comuna_seleccionada]

    geo_comuna = geo.merge(df_comuna, on='COMUNA', how='left')

    capa = st.selectbox("Seleccioná la capa de visualización:", [
        "Cantidad de Votos LLA 2025",
        "Porcentaje LLA 2025",
        "Crecimiento en Votos 2023-2025",
        "Crecimiento porcentual 2023_2025"
    ])

    config = {
        "Cantidad de Votos LLA 2025": {
            "col": "VOTOS_2025",
            "legend": "Votos LLA 2025",
            "formato": lambda x: f"{int(x):,} votos"
        },
        "Porcentaje LLA 2025": {
            "col": "PORC_2025",
            "legend": "% LLA 2025",
            "formato": lambda x: f"{x:.1f}%"
        },
        "Crecimiento en Votos 2023-2025": {
            "col": "DIF_ABS",
            "legend": "Crecimiento de votos",
            "formato": lambda x: f"{int(x):+d} votos"
        },
        "Crecimiento porcentual 2023_2025": {
            "col": "DIF_PORC",
            "legend": "Crecimiento porcentual",
            "formato": lambda x: f"{x:+.1f}%"
        }
    }

    columna = config[capa]['col']
    formatear = config[capa]['formato']
    leyenda = config[capa]['legend']

    geo_comuna = geo_comuna[pd.notnull(geo_comuna[columna])]
    geo_comuna[columna] = pd.to_numeric(geo_comuna[columna], errors='coerce')

    thresholds_validos = list(pd.cut(geo_comuna[columna], bins=8).unique().categories.left)
    thresholds_validos.append(geo_comuna[columna].max())

    m = folium.Map(location=[-34.61, -58.42], zoom_start=11)

    folium.Choropleth(
        geo_data=geo_comuna,
        data=geo_comuna,
        columns=['COMUNA', columna],
        key_on='feature.properties.COMUNA',
        fill_color='RdYlGn',
        fill_opacity=0.75,
        line_opacity=0.3,
        nan_fill_color='white',
        legend_name=leyenda,
        threshold_scale=thresholds_validos,
        reset=True
    ).add_to(m)

    for _, row in geo_comuna.iterrows():
        valor = row[columna]
        if pd.notnull(valor):
            numero_comuna = row['COMUNA'].split()[-1]
            tooltip = f"Comuna {numero_comuna}: {formatear(valor)}"
            centroide = row['geometry'].centroid
            folium.Marker(
                [centroide.y, centroide.x],
                icon=folium.DivIcon(html=f"<div style='font-size: 10px; color: black; text-align: center;'>{tooltip}</div>")
            ).add_to(m)

    folium_static(m)
    agrup_2025 = {
    "LA LIBERTAD AVANZA": "LLA",
    "ES AHORA BUENOS AIRES": "SANTORO",
    "BUENOS AIRES PRIMERO": "PRO/JXC"
}
agrup_2023 = {
    "LA LIBERTAD AVANZA": "LLA",
    "UNION POR LA PATRIA": "SANTORO",
    "JUNTOS POR EL CAMBIO": "PRO/JXC"
}

v25 = df_2025[df_2025['PARTIDO'].isin(agrup_2025)].copy()
v25['AGRUP'] = v25['PARTIDO'].map(agrup_2025)
v25 = v25.groupby(['COMUNA', 'AGRUP'])['VOTOS'].sum().reset_index(name='VOTOS_2025')

v23 = df_2023[df_2023['PARTIDO'].isin(agrup_2023)].copy()
v23['AGRUP'] = v23['PARTIDO'].map(agrup_2023)
v23 = v23.groupby(['COMUNA', 'AGRUP'])['VOTOS'].sum().reset_index(name='VOTOS_2023')

df_comparado = v25.merge(v23, on=['COMUNA', 'AGRUP'], how='outer').fillna(0)
df_comparado['DIF'] = df_comparado['VOTOS_2025'] - df_comparado['VOTOS_2023']

total25 = df_2025.groupby('COMUNA')['VOTOS'].sum().reset_index(name='TOTAL_2025')
validos_2023 = df_2023[df_2023['PARTIDO'].isin(agrup_2023)]
total23 = validos_2023.groupby('COMUNA')['VOTOS'].sum().reset_index(name='TOTAL_2023')

df_comparado = df_comparado.merge(total25, on='COMUNA', how='left').merge(total23, on='COMUNA', how='left')
df_comparado['PORC_2025'] = df_comparado['VOTOS_2025'] / df_comparado['TOTAL_2025'] * 100
df_comparado['PORC_2023'] = df_comparado['VOTOS_2023'] / df_comparado['TOTAL_2023'] * 100
df_comparado['DIF_PORC'] = df_comparado['PORC_2025'] - df_comparado['PORC_2023']

# --- Gráfico de crecimiento absoluto ---
top_comunas = df_comparado[df_comparado['AGRUP'] == 'LLA'].nlargest(10, 'DIF')['COMUNA']
df_top = df_comparado[df_comparado['COMUNA'].isin(top_comunas)]
colores = {'LLA': 'indigo', 'SANTORO': 'darkblue', 'PRO/JXC': 'goldenrod'}

fig_abs = go.Figure()
for agrup in ['LLA', 'SANTORO', 'PRO/JXC']:
    df_sub = df_top[df_top['AGRUP'] == agrup].set_index('COMUNA').loc[top_comunas].reset_index()
    fig_abs.add_trace(go.Bar(
        x=df_sub['COMUNA'],
        y=df_sub['DIF'],
        name=agrup,
        marker_color=colores[agrup],
        text=df_sub['DIF'],
        textposition='outside',
        textfont_size=16,
        offsetgroup=agrup
    ))
fig_abs.update_layout(
    barmode='group',
    title="Crecimiento absoluto por comuna (2025 vs 2023)",
    xaxis_title="Comuna",
    yaxis_title="Crecimiento en votos",
    height=600,
    xaxis_tickangle=-45
)
st.plotly_chart(fig_abs)

# --- Gráfico de crecimiento porcentual ---
top_comunas_porc = df_comparado[df_comparado['AGRUP'] == 'LLA'].nlargest(10, 'DIF_PORC')['COMUNA']
df_top_porc = df_comparado[df_comparado['COMUNA'].isin(top_comunas_porc)]
fig_porc = go.Figure()
for agrup in ['LLA', 'SANTORO', 'PRO/JXC']:
    df_sub = df_top_porc[df_top_porc['AGRUP'] == agrup].set_index('COMUNA').loc[top_comunas_porc].reset_index()
    fig_porc.add_trace(go.Bar(
        x=df_sub['COMUNA'],
        y=df_sub['DIF_PORC'],
        name=agrup,
        marker_color=colores[agrup],
        text=df_sub['DIF_PORC'].round(1).astype(str) + '%',
        textposition='outside',
        textfont_size=16,
        offsetgroup=agrup
    ))
fig_porc.update_layout(
    barmode='group',
    title="Crecimiento en puntos porcentuales por comuna (2025 vs 2023)",
    xaxis_title="Comuna",
    yaxis_title="Puntos porcentuales",
    height=600,
    xaxis_tickangle=-45
)
st.plotly_chart(fig_porc)


 