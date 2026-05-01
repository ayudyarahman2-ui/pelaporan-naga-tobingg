import streamlit as st
import pandas as pd
import datetime
import json
import os

st.set_page_config(page_title="PT Naga Tobing", layout="wide")

# ===== STYLE =====
st.markdown("""
<style>
.main {background-color: #f5f7fa;}
.stButton>button {
    background-color: #2e86de;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ===== LOAD DATA =====
def load_data(file):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame()

df_kandang = load_data("data_kandang.csv")
df_kirim = load_data("data_pengiriman.csv")

with open("users.json") as f:
    users = json.load(f)

# ===== LOGIN =====
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("Login Sistem PT Naga Tobing")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state.login = True
            st.session_state.user = username
            st.session_state.role = users[username]["role"]
            st.success("Login berhasil")
        else:
            st.error("Login gagal")

    st.stop()

# ===== SIDEBAR =====
st.sidebar.write(f"User: {st.session_state.user}")
st.sidebar.write(f"Role: {st.session_state.role}")

def logout():
    st.session_state.login = False

st.sidebar.button("Logout", on_click=logout)

# ===============================
# ===== KARYAWAN =====
# ===============================
if st.session_state.role == "karyawan":
    st.title("Panel Karyawan")

    menu = st.sidebar.radio("Menu", ["Laporan Kandang", "Pengiriman Ayam"])

    # ===== FORM KANDANG =====
    if menu == "Laporan Kandang":
        st.subheader("Form Laporan Harian")

        tanggal = datetime.date.today()

        hidup = st.number_input("Jumlah ternak hidup", 0)
        mati = st.number_input("Jumlah ternak mati", 0)
        sakit = st.number_input("Jumlah ternak sakit", 0)

        pakan = st.number_input("Pakan (kg)", 0.0)
        stok = st.number_input("Stok (kg)", 0.0)

        kondisi = st.selectbox("Kondisi", ["Baik", "Cukup", "Buruk"])
        suhu = st.number_input("Suhu (°C)", 0.0)
        catatan = st.text_area("Catatan")

        if st.button("Simpan Laporan"):
            new = pd.DataFrame([{
                "tanggal": tanggal,
                "user": st.session_state.user,
                "hidup": hidup,
                "mati": mati,
                "sakit": sakit,
                "pakan": pakan,
                "stok": stok,
                "kondisi": kondisi,
                "suhu": suhu,
                "catatan": catatan
            }])
            new.to_csv("data_kandang.csv", mode='a', header=not os.path.exists("data_kandang.csv"), index=False)
            st.success("Tersimpan")

        st.subheader("Riwayat Saya")
        if not df_kandang.empty:
            st.dataframe(df_kandang[df_kandang["user"] == st.session_state.user])

    # ===== FORM PENGIRIMAN =====
    if menu == "Pengiriman Ayam":
        st.subheader("Form Pengiriman")

        tanggal = datetime.date.today()

        tujuan = st.text_input("Tujuan")
        jumlah = st.number_input("Jumlah (ekor)", 0)
        berat = st.number_input("Berat (kg)", 0.0)
        status = st.selectbox("Status", ["Selesai", "Dalam Perjalanan", "Pending"])
        catatan = st.text_area("Catatan")

        if st.button("Simpan Pengiriman"):
            new = pd.DataFrame([{
                "tanggal": tanggal,
                "user": st.session_state.user,
                "tujuan": tujuan,
                "jumlah": jumlah,
                "berat": berat,
                "status": status,
                "catatan": catatan
            }])
            new.to_csv("data_pengiriman.csv", mode='a', header=not os.path.exists("data_pengiriman.csv"), index=False)
            st.success("Tersimpan")

        st.subheader("Riwayat Pengiriman")
        if not df_kirim.empty:
            st.dataframe(df_kirim[df_kirim["user"] == st.session_state.user])

# ===============================
# ===== ADMIN =====
# ===============================
elif st.session_state.role == "admin":
    st.title("Dashboard Admin")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Mati", int(df_kandang["mati"].sum()) if not df_kandang.empty else 0)
    col2.metric("Total Sakit", int(df_kandang["sakit"].sum()) if not df_kandang.empty else 0)
    col3.metric("Total Pengiriman", len(df_kirim) if not df_kirim.empty else 0)

    # ===== GRAFIK =====
    st.subheader("Grafik Kematian")
    if not df_kandang.empty:
        st.line_chart(df_kandang.groupby("tanggal")["mati"].sum())

    st.subheader("Grafik Pengiriman")
    if not df_kirim.empty:
        st.bar_chart(df_kirim.groupby("tanggal")["jumlah"].sum())

    # ===== DATA =====
    st.subheader("Data Kandang")
    if not df_kandang.empty:
        st.dataframe(df_kandang)

    st.subheader("Data Pengiriman")
    if not df_kirim.empty:
        st.dataframe(df_kirim)

    # ===== EXPORT =====
    if not df_kandang.empty or not df_kirim.empty:
        gabung = pd.concat([
            df_kandang.assign(tipe="kandang"),
            df_kirim.assign(tipe="pengiriman")
        ])

        csv = gabung.to_csv(index=False).encode('utf-8')
        st.download_button("Export Semua Data", csv, "laporan.csv", "text/csv")
