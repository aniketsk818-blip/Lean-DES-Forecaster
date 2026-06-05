import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Thesis DES Parametric Engine", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; color: #212529; }
    .card { background-color: #FFFFFF; border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); border: 1px solid #E9ECEF; margin-bottom: 20px; }
    .kpi-title { font-size: 15px; color: #0F2942; text-transform: uppercase; font-weight: 700; }
    .kpi-bau { font-size: 26px; font-weight: 700; color: #DC3545; }
    .kpi-lean { font-size: 26px; font-weight: 700; color: #198754; }
    .kpi-label { font-size: 12px; color: #6C757D; font-weight: 600; letter-spacing: 0.5px; margin-top: 10px; }
    .section-header { font-size: 20px; font-weight: 600; color: #0F2942; border-bottom: 2px solid #E9ECEF; padding-bottom: 5px; margin-bottom: 15px; margin-top: 10px;}
    .analysis-text { font-size: 14px; color: #495057; background-color: #E9ECEF; padding: 15px; border-left: 4px solid #198754; border-radius: 4px; margin-bottom: 30px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. STATIC PROJECT GEOMETRY
# ==========================================
project_baselines = {
    "Project1.xlsx": {"piles": 522.2, "exc_vol": 143097.5, "conc_vol": 205380.0, "steel": 27579.6, "shuttering": 1016705.7, "plaster": 954019.5, "screed": 245319.3, "mep": 3456.0},
    "Project2.xlsx": {"piles": 541.1, "exc_vol": 129649.7, "conc_vol": 101430.0, "steel": 13620.6, "shuttering": 502115.4, "plaster": 471153.8, "screed": 121153.8, "mep": 3456.0},
    "Project3.xlsx": {"piles": 413.3, "exc_vol": 92985.8,  "conc_vol": 154140.0, "steel": 20698.8, "shuttering": 763049.1, "plaster": 715997.8, "screed": 184113.7, "mep": 3456.0}
}

# ==========================================
# 3. SIDEBAR CONTROLS
# ==========================================
st.sidebar.title("Operational DES Engine")
selected_proj = st.sidebar.selectbox("Select Project Scope:", list(project_baselines.keys()))
base = project_baselines[selected_proj]

# --- DYNAMIC SCOPE MODIFIERS ---
with st.sidebar.expander("Scope Geometry Adjustments", expanded=False):
    live_piles = st.number_input("Total Foundation Piles (Nos)", value=float(base['piles']))
    live_exc = st.number_input("Excavation Qty (m³)", value=float(base['exc_vol']))
    live_conc = st.number_input("RCC Concrete Qty (m³)", value=float(base['conc_vol']))
    live_steel = st.number_input("Reinforcement Steel (MT)", value=float(base['steel']))
    live_shut = st.number_input("Shuttering Area (m²)", value=float(base['shuttering']))
    live_plaster = st.number_input("Base Plaster Mortar Area (m²)", value=float(base['plaster']))
    live_screed = st.number_input("Base Screed & Tile Area (m²)", value=float(base['screed']))
    live_mep = st.number_input("MEP Shaft Works (Rmts)", value=float(base['mep']))

scope = {'piles': live_piles, 'exc_vol': live_exc, 'conc_vol': live_conc, 'steel': live_steel, 
         'shuttering': live_shut, 'plaster': live_plaster, 'screed': live_screed, 'mep': live_mep}

# --- PHASE 1: SHORE PILING ---
with st.sidebar.expander("Phase 1: Shore Piling Levers", expanded=False):
    st.markdown("**Lean Strategy Toggles**")
    p_vsm = st.checkbox("Execute Piling Value Stream Mapping (VSM)?", value=False)
    p_jit = st.checkbox("Execute Piling Just-In-Time Concrete (JIT)?", value=False)
    p_par = st.checkbox("Execute Concurrent Parallel Twin-Rigs?", value=False)
    st.markdown("**Duration Levers (Mins/Pile)**")
    p_pos = st.slider("Rig Positioning", 10.0, 50.0, 35.0)
    p_soil = st.slider("Boring (0-8m Soil)", 20.0, 80.0, 55.0)
    p_rock = st.slider("Boring (8-18m Rock)", 60.0, 200.0, 125.0)
    p_flush = st.slider("Cleaning & Flushing", 15.0, 60.0, 40.0)
    p_cage = st.slider("Cage Lowering", 15.0, 60.0, 45.0)
    p_wait = st.slider("RMC Wait Lag", 15.0, 120.0, 90.0)
    p_conc = st.slider("Concreting Work", 30.0, 100.0, 65.0)
    p_shift = st.slider("Rig Shifting", 10.0, 60.0, 40.0)

# --- PHASE 2: MASS EXCAVATION ---
with st.sidebar.expander("Phase 2: Mass Excavation Levers", expanded=False):
    st.markdown("**Lean Strategy Toggles**")
    e_vsm = st.checkbox("Execute Haul Route Optimization (VSM)?", value=False)
    e_jit = st.checkbox("Execute Tipper Fleet Balancing (JIT)?", value=False)
    st.markdown("**Duration Levers (Mins/Trip)**")
    e_in = st.slider("Inbound Positioning", 1.0, 15.0, 8.0, step=0.5)
    e_load = st.slider("Shovel Loading Time", 2.0, 15.0, 6.0, step=0.5)
    e_out = st.slider("Outbound Positioning", 1.0, 15.0, 10.0, step=0.5)
    e_idle = st.slider("Idle Wait Waste", 1.0, 30.0, 13.24, step=0.01)

# --- PHASE 3: RCC SUPERSTRUCTURE ---
with st.sidebar.expander("Phase 3: RCC Levers", expanded=False):
    st.markdown("**Lean Strategy Toggles**")
    r_jit = st.checkbox("Execute JIT RMC Balancing?", value=False)
    r_lean_yd = st.checkbox("Execute Lean Yard Prefabrication?", value=False)
    st.markdown("**Duration Levers**")
    r_dur = st.slider("RCC Max Duration (Days)", 800.0, 2000.0, 1584.0, step=10.0)
    r_entry = st.slider("RMC Entry & Gate Process (Mins)", 1.0, 20.0, 10.0, step=0.5)
    r_queue = st.slider("RMC Queue & Parking (Mins)", 1.0, 30.0, 10.0, step=0.5)
    r_disc = st.slider("RMC Discharge (Mins)", 10.0, 45.0, 25.0, step=0.5)
    r_exit = st.slider("RMC Wash & Exit (Mins)", 5.0, 20.0, 10.0, step=0.5)

# --- PHASE 4: FINISHES & MEP ---
with st.sidebar.expander("Phase 4: Finishes & MEP Levers", expanded=False):
    st.markdown("**Lean Strategy Toggles**")
    f_vsm = st.checkbox("Execute Industrialized Drywall (VSM)?", value=False)
    f_jit = st.checkbox("Execute Prefabricated Riser Kits (JIT)?", value=False)
    st.markdown("**Duration & Waste Levers**")
    f_dur = st.slider("Net Isolated Finishing Duration Post-RCC (Days)", 300.0, 800.0, 600.0, step=10.0)
    f_plas_w = st.slider("Internal Plaster Mortar Waste Coefficient (%)", 2.0, 20.0, 12.5, step=0.5)
    f_scr_w = st.slider("Floor Screed & Tiling Scrap Loss Coefficient (%)", 2.0, 15.0, 8.0, step=0.5)
    f_mep_w = st.slider("Vertical MEP Shaft Rework/Clash Variance Rate (%)", 2.0, 15.0, 8.5, step=0.5)

# ==========================================
# 4. DETERMINISTIC ENGINE (EXACT MATH)
# ==========================================
def run_simulation(s, p_vsm, p_jit, p_par, p_pos, p_soil, p_rock, p_flush, p_cage, p_wait, p_conc, p_shift,
                   e_vsm, e_jit, e_in, e_load, e_out, e_idle,
                   r_jit, r_lean_yd, r_dur, r_entry, r_queue, r_disc, r_exit,
                   f_vsm, f_jit, f_dur, f_plas_w, f_scr_w, f_mep_w):
    
    # --- PHASE 1: PILING MATH ---
    if p_vsm: p_pos, p_flush, p_cage, p_shift = p_pos*0.7, p_flush*0.7, p_cage*0.7, p_shift*0.7
    if p_jit: p_wait = 36.0
    
    p_cycle = p_pos + p_soil + p_rock + p_flush + p_cage + p_wait + p_conc + p_shift
    p_piles_per_day = (540.0 / p_cycle) * 1.66
    p_days = s['piles'] / p_piles_per_day
    if p_par: p_days *= 0.85
    
    p_idle_lts = (s['piles'] * (p_cage + p_wait) / 60.0) * 6.5
    p_work_lts = s['piles'] * 93.5  
    p_carbon = ((p_idle_lts + p_work_lts) * 2.68 / 1000) + 0.54
    
    # --- PHASE 2: EXCAVATION MATH ---
    if e_vsm: e_in, e_out = 1.0, 1.0
    if e_jit: e_idle *= 0.20
    
    e_cycle = e_in + e_load + e_out + e_idle
    e_trips = s['exc_vol'] / 10.0
    e_trips_per_day = (540.0 / e_cycle) * 2.0
    e_days = e_trips / e_trips_per_day
    
    e_dig_fuel = s['exc_vol'] * 0.3125 
    e_haul_fuel = e_trips * 5.0
    e_idle_fuel = (e_trips * e_idle / 60.0) * 4.5
    # CORRECTED OVERHEAD: 15.0 kWh/day instead of 135.0 to match the exact Excel output math
    e_carbon = ((e_dig_fuel + e_haul_fuel + e_idle_fuel) * 2.68 / 1000) + (e_days * 15.0 * 0.82 / 1000)

    # --- PHASE 3: RCC MATH ---
    if r_jit: r_dur *= 0.85
    r_trips = s['conc_vol'] / 6.0
    rmc_cycle = r_entry + r_queue + r_disc + r_exit
    r_site_fuel = (r_trips * rmc_cycle / 60.0) * 2.5
    r_trans_fuel = r_trips * 5.0
    
    steel_eff = 1.8 if r_lean_yd else 3.5
    r_elec = (s['steel'] * steel_eff) + (s['conc_vol'] * 1.4222) + (202.5 * r_dur)
    r_carbon = ((r_site_fuel + r_trans_fuel) * 2.68 / 1000) + (r_elec * 0.82 / 1000)
    
    # --- PHASE 4: FINISHES MATH ---
    if f_vsm: 
        f_dur *= 0.70
        f_plas_w *= 0.35 
    
    hoist_draw = 263.25 if f_jit else 405.0 
    f_elec = f_dur * hoist_draw
    
    f_plas_carb = s['plaster'] * (f_plas_w / 100.0) * 0.015
    f_scr_carb = s['screed'] * (f_scr_w / 100.0) * 0.02
    f_til_carb = s['screed'] * ((f_scr_w * 1.25) / 100.0) * 0.03 
    f_mep_carb = s['mep'] * (f_mep_w / 100.0) * 0.04
    
    f_carbon = (f_elec * 0.82 / 1000) + f_plas_carb + f_scr_carb + f_til_carb + f_mep_carb

    return p_days, e_days, r_dur, f_dur, p_carbon, e_carbon, r_carbon, f_carbon

# ---------------------------------------------------------
# GENERATE FORECAST A: Strict BAU parameters (No Toggles)
# ---------------------------------------------------------
a_p_days, a_e_days, a_r_days, a_f_days, a_p_carb, a_e_carb, a_r_carb, a_f_carb = run_simulation(
    scope, False, False, False, 35.0, 55.0, 125.0, 40.0, 45.0, 90.0, 65.0, 40.0,
    False, False, 8.0, 6.0, 10.0, 13.24,
    False, False, 1584.0, 10.0, 10.0, 25.0, 10.0,
    False, False, 600.0, 12.5, 8.0, 8.5
)

# ---------------------------------------------------------
# GENERATE FORECAST B: Live Simulation parameters (With Toggles)
# ---------------------------------------------------------
b_p_days, b_e_days, b_r_days, b_f_days, b_p_carb, b_e_carb, b_r_carb, b_f_carb = run_simulation(
    scope, p_vsm, p_jit, p_par, p_pos, p_soil, p_rock, p_flush, p_cage, p_wait, p_conc, p_shift,
    e_vsm, e_jit, e_in, e_load, e_out, e_idle,
    r_jit, r_lean_yd, r_dur, r_entry, r_queue, r_disc, r_exit,
    f_vsm, f_jit, f_dur, f_plas_w, f_scr_w, f_mep_w
)

# --- TOTALS ---
total_days_a = a_p_days + a_e_days + a_r_days + a_f_days
total_carb_a = a_p_carb + a_e_carb + a_r_carb + a_f_carb
total_days_b = b_p_days + b_e_days + b_r_days + b_f_days
total_carb_b = b_p_carb + b_e_carb + b_r_carb + b_f_carb

def var_html(lean, bau):
    if bau == 0: return ""
    var = ((lean - bau) / bau) * 100
    if abs(var) < 0.01: return f'<span style="color: #6C757D; font-size: 14px; margin-left: 8px;">(0.0%)</span>'
    color = "#198754" if var < 0 else "#DC3545"
    arrow = "↓" if var < 0 else "↑"
    return f'<span style="color: {color}; font-size: 14px; margin-left: 8px;">({arrow} {abs(var):.1f}%)</span>'

# ==========================================
# 5. DASHBOARD LAYOUT & ANALYSIS
# ==========================================
st.title(f"Operational Baseline vs. Lean Optimization: {selected_proj[:-5]}")

col1, col2 = st.columns(2)
with col1:
    st.markdown(f'''
    <div class="card">
        <div class="kpi-title">Forecast A (Completed Project BAU Logic)</div>
        <hr style="margin: 10px 0; border-color: #E9ECEF;">
        <div style="margin-bottom: 12px;">
            <div style="font-size: 12px; color: #6C757D;">TOTAL CARBON FOOTPRINT</div>
            <div class="kpi-bau">{total_carb_a:,.1f} T</div>
        </div>
        <div>
            <div style="font-size: 12px; color: #6C757D;">TOTAL ACTIVE SCHEDULE</div>
            <div class="kpi-bau">{total_days_a:,.0f} Days</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
with col2:
    st.markdown(f'''
    <div class="card">
        <div class="kpi-title">Forecast B (Live Scope + Lean Parameters)</div>
        <hr style="margin: 10px 0; border-color: #E9ECEF;">
        <div style="margin-bottom: 12px;">
            <div style="font-size: 12px; color: #6C757D;">TOTAL CARBON FOOTPRINT</div>
            <div class="kpi-lean">{total_carb_b:,.1f} T {var_html(total_carb_b, total_carb_a)}</div>
        </div>
        <div>
            <div style="font-size: 12px; color: #6C757D;">TOTAL ACTIVE SCHEDULE</div>
            <div class="kpi-lean">{total_days_b:,.0f} Days {var_html(total_days_b, total_days_a)}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

# --- DURATION MATRIX ---
st.markdown('<div class="section-header">Operational Duration Metrics (Days)</div>', unsafe_allow_html=True)
df_dur = pd.DataFrame({
    "Construction Phase": ["Deep Piling", "Mass Excavation", "RCC Superstructure", "Finishes Post-RCC"],
    "Forecast A (BAU Baseline)": [a_p_days, a_e_days, a_r_days, a_f_days],
    "Forecast B (Lean Output)": [b_p_days, b_e_days, b_r_days, b_f_days],
    "% Schedule Mitigated": [
        ((b_p_days - a_p_days) / a_p_days) * 100 if a_p_days else 0,
        ((b_e_days - a_e_days) / a_e_days) * 100 if a_e_days else 0,
        ((b_r_days - a_r_days) / a_r_days) * 100 if a_r_days else 0,
        ((b_f_days - a_f_days) / a_f_days) * 100 if a_f_days else 0
    ]
})
st.dataframe(df_dur.style.format({
    "Forecast A (BAU Baseline)": "{:,.1f}", "Forecast B (Lean Output)": "{:,.1f}", "% Schedule Mitigated": "{:+,.1f}%"
}).map(lambda x: 'color: #198754' if isinstance(x, float) and x < -0.01 else ('color: #DC3545' if isinstance(x, float) and x > 0.01 else 'color: #6C757D'), subset=["% Schedule Mitigated"]), use_container_width=True)

# --- CARBON MATRIX ---
st.markdown('<div class="section-header">Environmental Logistics Impact (Tonnes CO₂e)</div>', unsafe_allow_html=True)
df_carb = pd.DataFrame({
    "Construction Phase": ["Deep Piling", "Mass Excavation", "RCC Superstructure", "Finishes & MEP"],
    "Forecast A (BAU Baseline)": [a_p_carb, a_e_carb, a_r_carb, a_f_carb],
    "Forecast B (Lean Output)": [b_p_carb, b_e_carb, b_r_carb, b_f_carb],
    "% Carbon Mitigated": [
        ((b_p_carb - a_p_carb) / a_p_carb) * 100 if a_p_carb else 0,
        ((b_e_carb - a_e_carb) / a_e_carb) * 100 if a_e_carb else 0,
        ((b_r_carb - a_r_carb) / a_r_carb) * 100 if a_r_carb else 0,
        ((b_f_carb - a_f_carb) / a_f_carb) * 100 if a_f_carb else 0
    ]
})
st.dataframe(df_carb.style.format({
    "Forecast A (BAU Baseline)": "{:,.2f}", "Forecast B (Lean Output)": "{:,.2f}", "% Carbon Mitigated": "{:+,.1f}%"
}).map(lambda x: 'color: #198754' if isinstance(x, float) and x < -0.01 else ('color: #DC3545' if isinstance(x, float) and x > 0.01 else 'color: #6C757D'), subset=["% Carbon Mitigated"]), use_container_width=True)

st.markdown("""
<div class="analysis-text">
    <strong>Analytical Insights:</strong> This explicit apples-to-apples configuration proves the mathematical value of Lean project controls. The engine captures your deterministic logic perfectly: toggling "Industrialized Drywall (VSM)" automatically enforces the exact 30% duration cut and 65% waste drop across the active scope volume. Toggling "Tipper Fleet Balancing (JIT)" structurally overrides the excavator idle wait constraints via Match-Factor optimization. The negative variances below quantify the precise emissions eliminated by these site-management decisions without altering the building's physical envelope.
</div>
""", unsafe_allow_html=True)