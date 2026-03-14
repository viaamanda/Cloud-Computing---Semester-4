import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import os
from io import BytesIO
from streamlit_option_menu import option_menu

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="✈️ Dashboard Kelompok 2", layout="wide")
st.markdown("""
<style>
/* ====== Sidebar ====== */
[data-testid="stSidebar"] {
    background-color: #0a1a3f; /* navy gelap */
    color: white;
}

/* ====== Judul Sidebar ====== */
h2, h3, h4, label, .st-emotion-cache-1v0mbdj, .st-emotion-cache-1cypcdb {
    color: #a9d6e5 !important; /* biru lembut */
    font-weight: 600;
}

/* ====== Multiselect Box ====== */
.stMultiSelect > div {
    background-color: #1d65a6 !important;
    border-radius: 10px;
}
.stMultiSelect [data-baseweb="tag"] {
    background-color: #007bff !important;
    color: white !important;
    border-radius: 5px;
    font-weight: 500;
}

/* ====== Dropdown ====== */
.stSelectbox > div, .stMultiSelect > div {
    background-color: #1d65a6 !important;
    color: white !important;
}
.stSelectbox div[role="listbox"] {
    background-color: #1d65a6 !important;
    color: white !important;
}

/* ====== Slider ====== */
.stSlider > div[data-baseweb="slider"] > div {
    color: white !important;
}
.stSlider > div[data-baseweb="slider"] > div > div {
    background-color: #00BFFF !important; /* biru muda slider */
}
.stSlider [role="slider"] {
    background-color: #1e90ff !important;
    border: 2px solid #89cff0 !important;
}

/* ====== Date Input ====== */
.stDateInput > div > input {
    background-color: #1d65a6 !important;
    color: white !important;
    border-radius: 8px;
    border: 1px solid #5dade2;
}

/* ====== Tombol Download ====== */
.stDownloadButton > button {
    background-color: #1e90ff !important;
    color: white !important;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}
.stDownloadButton > button:hover {
    background-color: #007acc !important;
    color: #eaf6ff !important;
}

/* ====== Expander ====== */
.streamlit-expanderHeader {
    background-color: #13315c !important;
    color: white !important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# OPTIONAL CUSTOM CSS
# ==============================
css_path = "style.css"
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ==============================
# COLOR PALETTE
# ==============================
color_palette = [
    "#0b3c5d",  # deep navy
    "#1d65a6",  # steel blue
    "#2e8bc0",  # blue
    "#89cff0",  # sky blue
    "#a9d6e5",  # light pastel blue
    "#13315c",  # dark indigo
    "#006494",  # bright cyan-blue
    "#247ba0",  # soft ocean blue
    "#5dade2",  # light blue
    "#7fb3d5"   # muted soft blue
]

# ==============================
# LOAD DATA
# ==============================
DEFAULT_FILE = "flights_cleaned_fix.parquet"

@st.cache_data
def load_data(path):
    if path.endswith(".parquet"):
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path)
    df = df.loc[:, ~df.columns.duplicated()]
    return df

df = None
if os.path.exists(DEFAULT_FILE):
    try:
        df = load_data(DEFAULT_FILE)
        st.sidebar.success(f"✅ File dimuat: {DEFAULT_FILE}")
    except Exception as e:
        st.sidebar.error(f"Gagal membaca file lokal: {e}")
else:
    uploaded = st.sidebar.file_uploader("📂 Upload dataset (CSV/Parquet)", type=["csv", "parquet"])
    if uploaded:
        try:
            if uploaded.name.endswith(".parquet"):
                df = pd.read_parquet(uploaded)
            else:
                df = pd.read_csv(uploaded)
            st.sidebar.success("✅ Dataset berhasil di-upload.")
        except Exception as e:
            st.sidebar.error(f"Gagal memuat file upload: {e}")

if df is None:
    st.warning("⚠️ Silakan upload file dataset atau pastikan file lokal tersedia.")
    st.stop()

# ==============================
# CLEANING
# ==============================
df = df.copy()
df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
numeric_cols = ["dep_delay","arr_delay","total_delay","distance","air_time",
                "humidity","pressure","temperature","wind_speed","delay_difference","temperature_c"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

# ==============================
# SIDEBAR MENU
# ==============================
with st.sidebar:
    selected = option_menu(
        "Dashboard Menu",
        ["Home", "Statistics & KPI", "Visualization & Interpretation", "About"],
        icons=["house", "bar-chart", "activity", "info-circle"],
        menu_icon="chat-square-text",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#0a1a3f"},
            "icon": {"color": "white", "font-size": "20px"},
            "nav-link": {
                "color": "white",
                "font-size": "15px",
                "text-align": "left",
                "margin": "5px 0",
                "border-radius": "10px",
            },
            "nav-link-selected": {
                "background-color": "#1e90ff",  # warna biru aktif
                "font-weight": "700",
                "color": "white",
            },
            "nav-link:hover": {"background-color": "#005bbb"},
        },
    )

st.sidebar.markdown("---")
use_full = st.sidebar.checkbox("Gunakan seluruh dataset (bisa lambat)", value=False)
sample_n = None if use_full else st.sidebar.slider("Sample data (rows):", 1000, 20000, 10000, 1000)

# ==============================
# PAGE: HOME
if selected == "Home":
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        st.image("upn_logo.png", width=130)

    with col2:
        st.markdown(
            """
            <h1 style='text-align:center; margin-bottom:0;'>Dashboard Analisis Delay Penerbangan & Cuaca</h1>
            <h4 style='text-align:center; color:#00BFFF; margin-top:4px;'>
                Analisis keterlambatan penerbangan dan pengaruh cuaca di New York 2013 
            </h4>
            <p style='text-align:center; font-size:15px; margin-top:-10px;'>
                Via Amanda, Muhammad Haikal Pasya Abdillah, Angelina Nirmala Puteri Dika Praktiko, 
                Siti Rania Azaria, Aurelia Krisnanti Wijaya, Maulida Shifa Annisa | Kelompok 2 |  
                UPN "Veteran" Jawa Timur
            </p>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.image("airplane_icon.png", width=120)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ====== Konten Artikel ======
    st.markdown(
        """
        <h3 style='text-align:left;'>🌦️ Bagaimana Cuaca Mempengaruhi Keterlambatan Penerbangan?</h3>

        <p style='text-align:justify; font-size:16px;'>
            Perusahaan penerbangan harus menjaga kepuasan pelanggan karena kualitas pelayanan, terutama ketepatan waktu, 
            sangat berpengaruh terhadap citra dan kinerja perusahaan. Peningkatan kualitas pelayanan memang membutuhkan 
            biaya operasional yang lebih tinggi, namun citra baik yang terbentuk dapat meningkatkan kepercayaan dan 
            penjualan tiket. Ketepatan waktu menjadi indikator penting dalam menilai kualitas pelayanan maskapai karena 
            keterlambatan dapat merugikan penumpang dan perusahaan. Oleh sebab itu, setiap bentuk keterlambatan perlu 
            dianalisis untuk menemukan faktor penyebabnya.
        </p>

        <p style='text-align:justify; font-size:16px;'>
            Salah satu faktor yang diduga mempengaruhi keterlambatan adalah kondisi cuaca, seperti hujan deras, angin kencang, 
            kabut tebal, atau badai, yang bisa mengganggu proses lepas landas dan mendarat demi menjaga keselamatan.  
            Kondisi tersebut tidak hanya membuat pelanggan kecewa, tetapi juga menimbulkan penumpukan jadwal, peningkatan 
            biaya operasional, dan gangguan terhadap jadwal kru serta armada. Jika keterlambatan terjadi terus-menerus, citra 
            maskapai dapat menurun dan pelanggan beralih ke maskapai lain. Oleh karena itu, penting bagi perusahaan penerbangan 
            untuk menganalisis pengaruh cuaca terhadap keterlambatan guna meningkatkan efisiensi dan kinerja operasional.
        </p>

        <p style='text-align:center; font-size:18px; margin-top:30px;'>
            ✨ Jelajahi data dan temukan hubungannya hanya di dashboard ini! ✨
        </p>
        """,
        unsafe_allow_html=True
    )

    # ====== PREVIEW DATASET ======
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h2>📊 Preview Dataset</h2>", unsafe_allow_html=True)
    st.markdown("<h4>Dataset: Delay Penerbangan di New York Tahun 2013</h4>", unsafe_allow_html=True)

    st.dataframe(df.head(50), use_container_width=True)

    # ====== FOOTER ======
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; font-size:14px;'>© 2025 Kelompok 2 | Exploratory Data Analysis Project</p>",
        unsafe_allow_html=True
    )



# ==============================
# PAGE: STATISTICS & KPI
# ==============================
elif selected == "Statistics & KPI":
    st.header("📈 Statistik & KPI")

    df_stats = df if use_full else df.sample(n=min(sample_n, len(df)), random_state=42)

    total_flights = len(df_stats)
    avg_total_delay = df_stats["total_delay"].mean() if "total_delay" in df_stats else float("nan")
    avg_temp = df_stats["temperature_c"].mean() if "temperature_c" in df_stats else float("nan")
    max_delay = df_stats["total_delay"].max() if "total_delay" in df_stats else float("nan")
    top_origin = df_stats["origin"].mode()[0] if "origin" in df_stats and not df_stats["origin"].mode().empty else "N/A"

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Flights", f"{total_flights:,}")
    c2.metric("Avg Total Delay (min)", f"{avg_total_delay:.2f}" if pd.notna(avg_total_delay) else "N/A")
    c3.metric("Avg Temperature (°C)", f"{avg_temp:.1f}" if pd.notna(avg_temp) else "N/A")
    c4.metric("Max Delay (min)", f"{max_delay:.1f}" if pd.notna(max_delay) else "N/A")
    c5.metric("Most Frequent Origin", top_origin)

    st.markdown("---")
    num_cols = df_stats.select_dtypes(include=["number"]).columns.tolist()
    if num_cols:
        st.dataframe(df_stats[num_cols].describe().T)
    else:
        st.warning("Tidak ada kolom numerik ditemukan.")
    st.caption("📋 Statistik deskriptif berdasarkan data aktif.")

# ==============================
# PAGE: VISUALIZATION & INTERPRETATION
# ==============================
elif selected == "Visualization & Interpretation":
    st.header("📊 Visualisasi & Interpretasi Data")

    # ---------- Sidebar Filters ----------
    st.sidebar.subheader("🎛️ Filter Data Visualisasi")
    df_vis = df.copy()

    origins = sorted(df_vis["origin"].dropna().unique()) if "origin" in df_vis else []
    dests = sorted(df_vis["dest"].dropna().unique()) if "dest" in df_vis else []
    carriers = sorted(df_vis["carrier"].dropna().unique()) if "carrier" in df_vis else []

    sel_origins = st.sidebar.multiselect(
        "Origin:",
        origins,
        default=origins[:5] if origins else []
    )

    sel_dests = st.sidebar.multiselect(
        "Destination:",
        dests,
        default=dests[:5] if dests else []
    )

    sel_carriers = st.sidebar.multiselect(
        "Carrier:",
        carriers,
        default=[]
    )

    if "date" in df_vis.columns:
        min_date, max_date = df_vis["date"].min(), df_vis["date"].max()
        sel_date = st.sidebar.date_input(
            "Rentang tanggal:",
            [min_date, max_date]
        )

    if "total_delay" in df_vis.columns:
        min_delay, max_delay = int(df_vis["total_delay"].min()), int(df_vis["total_delay"].max())
        sel_delay = st.sidebar.slider(
            "Rentang delay (menit):",
            min_delay,
            max_delay,
            (min_delay, max_delay)
        )
    else:
        sel_delay = None

    # ---------- Apply Filters ----------
    if sel_origins:
        df_vis = df_vis[df_vis["origin"].isin(sel_origins)]
    if sel_dests:
        df_vis = df_vis[df_vis["dest"].isin(sel_dests)]
    if sel_carriers:
        df_vis = df_vis[df_vis["carrier"].isin(sel_carriers)]
    if "date" in df_vis.columns and sel_date:
        start_d, end_d = pd.to_datetime(sel_date[0]), pd.to_datetime(sel_date[1])
        df_vis = df_vis[(df_vis["date"] >= start_d) & (df_vis["date"] <= end_d)]
    if sel_delay and "total_delay" in df_vis.columns:
        df_vis = df_vis[(df_vis["total_delay"] >= sel_delay[0]) & (df_vis["total_delay"] <= sel_delay[1])]

    # Sampling (biar gak berat)
    df_vis_sample = df_vis if use_full else df_vis.sample(n=min(len(df_vis), sample_n), random_state=42)

    # Info dan download hasil filter
    st.sidebar.success(f"✅ Data aktif: {len(df_vis_sample):,} baris")
    st.sidebar.download_button(
        "💾 Download filtered CSV",
        data=df_vis_sample.to_csv(index=False).encode("utf-8"),
        file_name="filtered_flights.csv",
        mime="text/csv"
    )

    # ---------- Tabs ----------
    tabs = st.tabs([
        " Tren Keterlambatan Harian",
        " Performa Maskapai",
        " Diagram Pencar",
        " Diagram Gelembung",
        " Area / Stacked Plot",
        " Diagram Lingkaran",
        " Diagram Tabel",
        " Diagram Polar",
        " Histogram Delay",
        " Diagram Lollipop",
        " Diagram Terbaik",
        " Heatmap Korelasi",
        " Temperatur per Destinasi"
    ])

    # ========== 1️⃣ Tren Keterlambatan Harian ==========
    with tabs[0]:
        # Pastikan date bertipe datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

        # Hitung rata-rata total_delay per tanggal
        daily_delay = df.groupby('date')['total_delay'].mean().reset_index()

        if not daily_delay.empty:
            # Cari titik delay tertinggi
            max_idx = daily_delay['total_delay'].idxmax()
            max_date = daily_delay.loc[max_idx, 'date']
            max_value = daily_delay.loc[max_idx, 'total_delay']

            # Hitung rata-rata keseluruhan
            mean_delay = daily_delay['total_delay'].mean()

            # Buat figure
            fig = go.Figure()

            # Line utama
            fig.add_trace(go.Scatter(
                x=daily_delay['date'],
                y=daily_delay['total_delay'],
                mode='lines+markers',
                name='Rata-rata Harian',
                line=dict(color='#0074D9', width=3),
                marker=dict(size=5, color='#005B96')
            ))

            # Highlight titik tertinggi
            fig.add_trace(go.Scatter(
                x=[max_date],
                y=[max_value],
                mode='markers+text',
                name='Tertinggi',
                marker=dict(color='red', size=12),
                text=[f'{max_value:.1f}'],
                textposition='top center'
            ))

            # Garis rata-rata
            fig.add_hline(
                y=mean_delay,
                line_dash="dash",
                line_color='#005B96',
                annotation_text=f"Rata-rata: {mean_delay:.1f} menit",
                annotation_position="bottom right"
            )

            # Layout
            fig.update_layout(
                title='Tren Keterlambatan Harian',
                xaxis_title="Tanggal",
                yaxis_title="Rata-rata Total Delay (menit)",
                template='plotly_white',
                hovermode="x unified",
                title_font=dict(size=18, color='#0074D9', family='Arial')
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Data kosong untuk tren harian.")

    # ========== 2️⃣ Performa Maskapai ==========
    with tabs[1]:
        # Hitung rata-rata keterlambatan kedatangan per maskapai
        avg_delay = df.groupby('carrier')['arr_delay'].mean().reset_index()
        avg_delay.columns = ['carrier', 'avg_arr_delay']

        # Balik tanda delay: terlambat -> negatif, lebih cepat -> positif
        avg_delay['adjusted_delay'] = -avg_delay['avg_arr_delay']

        # Plot grafik horizontal
        fig = px.bar(
            avg_delay.sort_values('adjusted_delay', ascending=True),
            x='adjusted_delay',
            y='carrier',
            orientation='h',
            color='adjusted_delay',
            color_continuous_scale=['navy', 'blue', 'skyblue'],
            title='Performa Ketepatan Waktu Kedatangan per Maskapai (Nilai Positif = Lebih Cepat)'
        )

        fig.update_layout(
            xaxis_title="Nilai Performa (menit)",
            yaxis_title="Kode Maskapai",
            title_font=dict(size=16, color='#0074D9', family='Arial'),
            plot_bgcolor='white'
        )

        st.plotly_chart(fig, use_container_width=True)

    # ========== 3️⃣ Diagram Pencar (wind_speed vs total_delay) ==========
    with tabs[2]:
        # Pastikan kolom ada
        if {'wind_speed', 'total_delay'}.issubset(df.columns):
            fig = px.scatter(
                df.dropna(subset=['wind_speed', 'total_delay']),
                x='wind_speed',
                y='total_delay',
                title='Pengaruh Kecepatan Angin terhadap Keterlambatan',
                labels={'wind_speed': 'Kecepatan Angin', 'total_delay': 'Total Delay (menit)'},
                opacity=0.6
            )
            fig.update_traces(marker=dict(color='#0074D9'))
            fig.update_layout(
                xaxis_title="Kecepatan Angin",
                yaxis_title="Total Delay (menit)",
                title_font=dict(size=18, color='#0074D9', family='Arial'),
                plot_bgcolor='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Kolom 'wind_speed' atau 'total_delay' tidak ditemukan.")

    # ========== 4️⃣ Diagram Gelembung (humidity vs delay vs distance) ==========
    with tabs[3]:
        # Pastikan kolom ada
        if {'humidity', 'arr_delay', 'distance'}.issubset(df.columns):
            bubble_data = df[['humidity', 'arr_delay', 'distance', 'origin', 'carrier']].copy()
            bubble_data = bubble_data.dropna(subset=['humidity', 'arr_delay', 'distance'])
            fig = px.scatter(
                bubble_data,
                x='humidity',
                y='arr_delay',
                size='distance',
                color='arr_delay',
                hover_data=['origin', 'carrier'],
                size_max=40,
                color_continuous_scale=['#003366', '#0074D9', '#66B3FF', '#B3E5FF'],
                title='Hubungan Kelembaban, Delay, dan Jarak Tempuh',
                labels={
                    'humidity': 'Kelembaban (%)',
                    'arr_delay': 'Keterlambatan Kedatangan (menit)',
                    'distance': 'Jarak Tempuh (km)'
                },
                opacity=0.7
            )
            fig.update_layout(
                xaxis_title="Kelembaban (%)",
                yaxis_title="Keterlambatan Kedatangan (menit)",
                title_font=dict(size=18, color='#003F7F', family='Arial Black'),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#003F7F', size=12),
                coloraxis_colorbar_title="Delay (menit)",
                showlegend=False
            )
            fig.update_traces(marker=dict(line=dict(width=0)))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Kolom 'humidity', 'arr_delay', atau 'distance' tidak ditemukan.")

    # ========== 5️⃣ Area / Stacked Plot (jumlah penerbangan per bulan per maskapai) ==========
    with tabs[4]:
        # Pastikan date bertipe datetime & buat kolom month
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['month'] = df['date'].dt.to_period('M').astype(str)

        flight_count = df.groupby(['month', 'carrier']).size().reset_index(name='count')

        if not flight_count.empty:
            # Ambil daftar maskapai unik
            unique_carriers = flight_count['carrier'].unique()
            n = len(unique_carriers)

            # Palet gradasi biru
            def generate_blue_gradient(n):
                if n == 1:
                    return ['rgb(11,60,93)']
                start = np.array([11, 60, 93])   # #0b3c5d
                end = np.array([169, 214, 229])  # #a9d6e5
                return [
                    f'rgb({int(start[0] + (end[0] - start[0]) * i / (n-1))},'
                    f'{int(start[1] + (end[1] - start[1]) * i / (n-1))},'
                    f'{int(start[2] + (end[2] - start[2]) * i / (n-1))})'
                    for i in range(n)
                ]

            blue_palette = generate_blue_gradient(n)
            color_map = dict(zip(unique_carriers, blue_palette))

            fig = px.area(
                flight_count,
                x='month',
                y='count',
                color='carrier',
                title='Porsi Maskapai dari Waktu ke Waktu',
                labels={'month': 'Bulan', 'count': 'Jumlah Penerbangan', 'carrier': 'Maskapai'},
                color_discrete_map=color_map
            )

            fig.update_layout(
                xaxis_title="Bulan",
                yaxis_title="Jumlah Penerbangan",
                title_font=dict(size=18, color='#003F7F', family='Arial'),
                plot_bgcolor='white',
                legend_title_text='Maskapai',
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Data kosong untuk area/stacked plot.")

    # ========== 6️⃣ Diagram Lingkaran (total penerbangan per maskapai) ==========
    with tabs[5]:
        flight_share = df['carrier'].value_counts().reset_index()
        flight_share.columns = ['carrier', 'count']

        unique_carriers = flight_share['carrier'].unique()
        n = len(unique_carriers)

        # Buat palet jika banyak maskapai
        def generate_blue_gradient(n):
            if n == 1:
                return ['rgb(11,60,93)']
            start = np.array([11, 60, 93])
            end = np.array([169, 214, 229])
            return [
                f'rgb({int(start[0] + (end[0] - start[0]) * i / (n-1))},'
                f'{int(start[1] + (end[1] - start[1]) * i / (n-1))},'
                f'{int(start[2] + (end[2] - start[2]) * i / (n-1))})'
                for i in range(n)
            ]

        blue_palette = generate_blue_gradient(n)
        color_map = dict(zip(unique_carriers, blue_palette))

        fig = px.pie(
            flight_share,
            names='carrier',
            values='count',
            title='Jumlah Penerbangan Maskapai Secara Keseluruhan',
            color='carrier',
            color_discrete_map=color_map,
            hole=0.3
        )

        fig.update_layout(
            title_font=dict(size=18, color='#003F7F', family='Arial'),
            legend_title_text='Maskapai'
        )

        st.plotly_chart(fig, use_container_width=True)

    # ========== 7️⃣ Diagram Tabel ==========
    with tabs[6]:
        st.dataframe(df.head(20))
        st.caption("📋 Menampilkan 20 baris pertama dari dataset yang digunakan.")

    # ========== 8️⃣ Diagram Polar ==========
    with tabs[7]:
        # Tangani nilai NaN agar tidak menyebabkan error & buat skala
        df['wind_speed'] = df['wind_speed'].fillna(0)
        df['total_delay'] = df['total_delay'].fillna(0)
        df['dep_delay'] = df['dep_delay'].fillna(0)
        df['arr_delay'] = df['arr_delay'].fillna(0)
        df['wind_speed_scaled'] = df['wind_speed'] * 50

        fig = px.scatter_polar(
            df,
            r='wind_speed_scaled',
            theta='carrier',
            color='total_delay',
            size='wind_speed',
            hover_data=['dep_delay', 'arr_delay'],
            title='Pola Kecepatan Angin dan Keterlambatan per Maskapai',
            color_continuous_scale='Blues'
        )

        fig.update_layout(
            template='plotly_white',
            legend_title_text='Total Delay (menit)',
            margin=dict(l=50, r=50, t=80, b=50),
            polar=dict(
                angularaxis=dict(
                    direction='clockwise',
                    tickfont=dict(size=10)
                )
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    # ========== 9️⃣ Histogram keterlambatan ==========
    with tabs[8]:
        # Siapkan data dan filter outlier berlebih supaya rapi
        if {'dep_delay', 'arr_delay'}.issubset(df.columns):
            df_delay = df[['dep_delay', 'arr_delay']].dropna()
            df_delay = df_delay[(df_delay['dep_delay'] < 500) & (df_delay['arr_delay'] < 500)]

            fig1 = px.histogram(
                df_delay, x="arr_delay", nbins=50,
                title="Distribusi Delay Kedatangan"
            )
            fig2 = px.histogram(
                df_delay, x="dep_delay", nbins=50,
                title="Distribusi Delay Keberangkatan"
            )
            st.plotly_chart(fig1, use_container_width=True)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Kolom 'dep_delay' atau 'arr_delay' tidak ditemukan.")

    # ========== 🔟 Diagram Lollipop (Top 15 rute) ==========
    with tabs[9]:
        # Buat kolom rute
        df['route'] = df['origin'] + ' → ' + df['dest']

        # Hitung rata-rata keterlambatan per rute
        route_delay = df.groupby('route')['arr_delay'].mean().sort_values(ascending=False).head(15).reset_index()

        # Buat chart
        fig = go.Figure()

        # Garis (stick lolipop)
        fig.add_trace(go.Scatter(
            x=route_delay['arr_delay'],
            y=route_delay['route'],
            mode='lines',
            line=dict(color='lightgray', width=4),
            showlegend=False
        ))

        # Titik (lollipop head)
        fig.add_trace(go.Scatter(
            x=route_delay['arr_delay'],
            y=route_delay['route'],
            mode='markers',
            marker=dict(size=14, color='#1d65a6', line=dict(width=2, color='white')),
            name='Rata-rata Delay'
        ))

        # Layout aesthetic
        fig.update_layout(
            title='✈️ Top 15 Rute dengan Keterlambatan Kedatangan Tertinggi',
            title_x=0.5,
            xaxis_title='Rata-rata Keterlambatan (menit)',
            yaxis_title='Rute Penerbangan',
            template='plotly_white',
            font=dict(size=12),
            xaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.2)'),
            yaxis=dict(categoryorder='total ascending'),
            margin=dict(l=120, r=50, t=80, b=50),
            plot_bgcolor='rgba(0,0,0,0)',
        )

        st.plotly_chart(fig, use_container_width=True)

    # ========== 1️⃣1️⃣ Diagram Terbaik (wind_speed vs delay_difference per carrier) ==========
    with tabs[10]:
        if {'wind_speed', 'arr_delay', 'dep_delay', 'carrier'}.issubset(df.columns):
            df['delay_difference'] = df['arr_delay'] - df['dep_delay']
            fig = px.scatter(
                df.dropna(subset=['wind_speed', 'delay_difference']),
                x='wind_speed',
                y='delay_difference',
                color='carrier',
                color_discrete_sequence=px.colors.sequential.Blues,
                title='Pengaruh Kecepatan Angin terhadap Delay Difference per Maskapai'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Kolom yang diperlukan untuk visualisasi ini tidak lengkap.")

    # ========== 1️⃣2️⃣ Heatmap Korelasi Faktor Cuaca ==========
    with tabs[11]:
        weather_cols = ["wind_speed", "humidity", "temperature_c", "delay_difference"]
        # Pastikan delay_difference tersedia
        if 'delay_difference' not in df.columns:
            if {'arr_delay', 'dep_delay'}.issubset(df.columns):
                df['delay_difference'] = df['arr_delay'] - df['dep_delay']
        sub_df = df[weather_cols].dropna()
        if not sub_df.empty:
            corr = sub_df.corr()
            fig = px.imshow(
                corr, text_auto=True, aspect="auto",
                color_continuous_scale="Blues",
                title="Korelasi Faktor Cuaca terhadap Delay Difference"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Data tidak cukup untuk menghitung korelasi faktor cuaca.")

    # ========== 1️⃣3️⃣ Perbandingan Temperatur Tiap Bandara Tujuan ==========
    with tabs[12]:
        # Hitung rata-rata temperature per destination
        if 'temperature' in df.columns and 'dest' in df.columns:
            temp_dest = df.groupby('dest')['temperature'].mean().reset_index()
            temp_dest = temp_dest.sort_values('temperature')
            temp_dest = temp_dest.tail(15)  # ambil 15 teratas

            unique_dest = temp_dest['dest'].unique()
            n = len(unique_dest)

            def generate_blue_gradient(n):
                if n == 1:
                    return ['rgb(11,60,93)']
                start = np.array([0, 31, 63])
                end = np.array([163, 216, 255])
                return [
                    f'rgb({int(start[0] + (end[0] - start[0]) * i / (n-1))},'
                    f'{int(start[1] + (end[1] - start[1]) * i / (n-1))},'
                    f'{int(start[2] + (end[2] - start[2]) * i / (n-1))})'
                    for i in range(n)
                ]

            colors = generate_blue_gradient(n)

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=temp_dest['dest'],
                y=temp_dest['temperature'],
                mode='lines',
                line=dict(color='lightgray', width=2),
                showlegend=False
            ))

            fig.add_trace(go.Scatter(
                x=temp_dest['dest'],
                y=temp_dest['temperature'],
                mode='markers',
                marker=dict(size=14, color=colors),
                showlegend=False
            ))

            fig.update_layout(
                title='Perbandingan Temperatur Tiap Bandara Tujuan',
                xaxis_title='Bandara Tujuan (Dest)',
                yaxis_title='Rata-rata Temperatur (°C)',
                title_font=dict(size=18, color='#003F7F', family='Arial'),
                plot_bgcolor='white'
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Kolom 'temperature' atau 'dest' tidak ditemukan.")
# ==============================
# PAGE: ABOUT
# ==============================
elif selected == "About":
    st.title("ℹ️ Tentang Dashboard")
    st.markdown("""
    Dashboard ini dikembangkan untuk **analisis keterlambatan penerbangan dan faktor cuaca** 
    menggunakan dataset penerbangan New York 2013.  
    Dibuat oleh **Kelompok 2**, dalam rangka proyek **Exploratory Data Analysis (EDA)**.
    """)
    st.info("📘 Data diolah menggunakan Streamlit, Pandas, Plotly, dan NumPy.")
