import streamlit as st
import math

# Oldal beállítása
st.set_page_config(page_title="Perfúziós Kalkulátor", layout="centered")

# Stílus - Profi megjelenés
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .result-card { padding: 20px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #007bff; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🫀 Gyermek Szívsebészeti Kalkulátor")

# --- BEMENETI ADATOK (BAL OLDAL / FENT) ---
with st.sidebar:
    st.header("📋 Beteg adatai")
    suly = st.number_input("Súly (kg)", value=5.1, step=0.1)
    magassag = st.number_input("Magasság (cm)", value=63, step=1)
    akt_hkt = st.slider("Aktuális Hematokrit (%)", 10, 60, 47)
    
    st.divider()
    prime_vol = st.number_input("Gép feltöltés (ml)", value=330)
    target_hkt = st.slider("Cél Hkt a gépen (%)", 20, 40, 30)

# --- SZÁMÍTÁSOK ---
# BSA (Mosteller formula: sqrt(H*W/3600))
bsa = math.sqrt((magassag * suly) / 3600)
# BV (Beteg vérmennyisége: 85 ml/kg)
bv = suly * 85
# Várható Hkt (vér nélkül)
expected_hkt_no_blood = (bv * (akt_hkt / 100)) / (bv + prime_vol) * 100

# VVT Szükséglet számítása (Hkt_donor = 70%)
# Formula: (BV*Hkt_p + VVT*Hkt_d) / (BV + Prime + VVT) = Target_Hkt
hkt_donor = 0.70
vvt_needed = ( (target_hkt/100) * (bv + prime_vol) - (bv * (akt_hkt/100)) ) / (hkt_donor - (target_hkt/100))
vvt_needed = max(0, vvt_needed) # Ne legyen negatív

# Perctérfogat (CI alapértelmezett: 2.8)
ci = 2.8
hzv = ci * bsa

# --- MEGJELENÍTÉS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Alapértékek")
    st.metric("Testfelszín (BSA)", f"{bsa:.2f} m²")
    st.metric("Vérmennyiség (BV)", f"{int(bv)} ml")
    st.metric("Perctérfogat (HZV)", f"{hzv:.2f} l/min")

with col2:
    st.subheader("🩸 Hematokrit & Vér")
    st.metric("Hkt a gépen (vér nélkül)", f"{expected_hkt_no_blood:.1f} %")
    st.metric("Szükséges vér (VVT)", f"{int(vvt_needed)} ml", delta=f"Cél: {target_hkt}%")

st.markdown("---")

# --- ESZKÖZÖK (DINAMIKUS LOGIKA) ---
st.subheader("⚙️ Javasolt Eszközök")

# Oxigenátor logika
if suly < 4: ox = "Kids 100 (0,7 l/min)"
elif suly < 22: ox = "Kids 101 (2,5 l/min)"
elif suly < 40: ox = "Trilly Euroset (3,0 l/min)"
elif suly < 65: ox = "FX 15 Terumo (4,0 l/min)"
else: ox = "Inspire/Fusion (> 4,0 l/min)"

# Kanül logika (egyszerűsített súly/flow alapján)
if hzv < 1.5:
    kanul = "Artériás: 8-12 Fr | Vénás: 12-18 Fr"
elif hzv < 3.0:
    kanul = "Artériás: 16-20 Fr | Vénás: 18-24 Fr"
else:
    kanul = "Artériás: 18-24 Fr | Vénás: 24-32 Fr"

c_a, c_b = st.columns(2)
with c_a:
    st.info(f"**Oxigenátor:**\n\n{ox}")
with c_b:
    st.success(f"**Kanülök:**\n\n{kanul}")

# --- MEGJEGYZÉSEK ---
st.warning(f"💡 **Heparin dózis:** {int(suly*400)} IE (400 IE/kg-al számolva)")
if suly < 10:
    st.caption("Megjegyzés: 10 kg alatt FFP (mint VVT), 10 kg felett 5% Albumin javasolt.")
