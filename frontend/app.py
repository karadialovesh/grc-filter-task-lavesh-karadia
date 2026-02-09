import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import time

API_URL = "https://grc-filter-task-lavesh-karadia-backend.onrender.com"
st.set_page_config(page_title="GRC Risk Assessment", layout="wide")

def calculate_score(likelihood, impact):
    return likelihood * impact

def get_risk_level(score):
    if 1 <= score <= 5:
        return "Low"
    elif 6 <= score <= 12:
        return "Medium"
    elif 13 <= score <= 18:
        return "High"
    elif 19 <= score <= 25:
        return "Critical"
    return "Unknown"

@st.cache_data(show_spinner=False)
def fetch_risks():
    try:
        response = requests.get(f"{API_URL}/risks")
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to fetch risks.")
            return []
    except  requests.exceptions.ConnectionError:
        st.error("Cannot connect to Backend. Is it running?")
        return []

def submit_risk(asset, threat, likelihood, impact):
    payload = {
        "asset": asset,
        "threat": threat,
        "likelihood": likelihood,
        "impact": impact
    }
    try:
        res = requests.post(f"{API_URL}/assess-risk", json=payload)
        if res.status_code == 200:
            data = res.json()
            st.cache_data.clear()
            return True, f"✅ Risk Added! (ID: {data.get('id')})"
        else:
            return False, f"Error: {res.text}"
    except Exception as e:
        return False, f"Connection Error: {e}"

st.title("🛡️ GRC Risk Assessment Dashboard")

# Sidebar input form
with st.sidebar:
    st.header("Assess New Risk")
    asset = st.text_input("Asset Name", placeholder="e.g. Customer DB")
    threat = st.text_input("Threat", placeholder="e.g. SQL Injection")
    
    likelihood = st.slider("Likelihood (1-5)", 1, 5, 3)
    impact = st.slider("Impact (1-5)", 1, 5, 3)
    
    # Real-time Preview
    preview_score = calculate_score(likelihood, impact)
    preview_level = get_risk_level(preview_score)
    
    st.markdown("---")
    st.subheader("Preview")
    
    color_map = {
        "Low": "#dcfce7", "Medium": "#fef9c3", "High": "#ffedd5", "Critical": "#fee2e2"
    } # Light bg colors
    text_color_map = {
        "Low": "green", "Medium": "orange", "High": "red", "Critical": "red"
    }
    
    bg_color = color_map.get(preview_level, "#f3f4f6")
    text_color = text_color_map.get(preview_level, "black")
    
    st.markdown(f"""
    <div style="
        background-color: {bg_color};
        padding: 15px;
        border-radius: 10px;
        border: 1px solid {text_color};
        text-align: center;
    ">
        <h3 style="margin:0; color: #374151;">Risk Score: {preview_score} / 25</h3>
        <h4 style="margin:5px 0 0 0; color: {text_color};">Level: {preview_level}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Submit Risk", type="primary"):
        if asset and threat:
            success, msg = submit_risk(asset, threat, likelihood, impact)
            if success:
                st.success(msg)
                time.sleep(1)
                st.rerun()
            else:
                st.error(msg)
        else:
            st.warning("Please fill in Asset and Threat.")

# Dashboard visuals
risks_data = fetch_risks()

if risks_data:
    df = pd.DataFrame(risks_data)
    
    # Enhanced metrics cards
    st.markdown("""
    <style>
        .metric-card {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            text-align: center;
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #111827;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 1rem;
            font-weight: 500;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    total_risks = len(df)
    high_critical = len(df[df['level'].isin(['High', 'Critical'])])
    avg_score = df['score'].mean()
    
    def display_card(col, label, value, color="black"):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color: {color}">{value}</div>
        </div>
        """, unsafe_allow_html=True)
    
    display_card(col1, "Total Risks", total_risks, "#2563eb") # Blue
    display_card(col2, "High/Critical Risks", high_critical, "#dc2626") # Red
    display_card(col3, "Average Score", f"{avg_score:.1f}", "#d97706") # Amber
    
    st.divider()

    col_heatmap, col_table = st.columns([1, 1])
    
    with col_heatmap:
        st.subheader("Risk Heatmap")
        
        # Prepare 5x5 Grid Data
        # X = Impact (1-5), Y = Likelihood (1-5)
        # Z should be Risk Level (Color) represented by Score?
        # Requirement: "Cell background color reflects risk level of that score"
        
        z_data = []      # For Color (Score)
        text_data = []   # For Display (Count)
        hover_data = []  # For Hover (Assets)
        
        for l in range(1, 6): # Likelihood (Rows)
            z_row = []
            text_row = []
            hover_row = []
            for i in range(1, 6): # Impact (Columns)
                score = l * i
                z_row.append(score)
                
                # Count risks with this specific L and I
                risks_in_cell = df[(df['likelihood'] == l) & (df['impact'] == i)]
                count = len(risks_in_cell)
                assets = risks_in_cell['asset'].tolist()
                
                text_row.append(str(count) if count > 0 else "")
                hover_row.append("<br>".join(assets) if assets else "No risks")
            
            z_data.append(z_row)
            text_data.append(text_row)
            hover_data.append(hover_row)
        
        # Custom Colorscale to match Score Ranges
        # 1-5 (Low) -> Green
        # 6-12 (Med) -> Yellow
        # 13-18 (High) -> Orange
        # 19-25 (Crit) -> Red
        # Note: Plotly colorscales are normalized 0-1. Max Score is 25.
        # 5/25=0.2, 12/25=0.48, 18/25=0.72
        
        # Simplified Discrete Colorscale approach:
        # We can map scores directly or use a custom continuous scale with hard stops
        colors = [
            [0.0, "green"],   [0.2, "green"],    # 0-5
            [0.2, "gold"],  [0.48, "gold"],    # 5-12
            [0.48, "orange"], [0.72, "orange"],  # 12-18
            [0.72, "red"],    [1.0, "red"]       # 18-25
        ]

        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=[1, 2, 3, 4, 5], # Impact
            y=[1, 2, 3, 4, 5], # Likelihood
            text=text_data,
            texttemplate="%{text}",
            textfont={"size": 16, "color": "black", "family": "Arial, bold"},
            hovertext=hover_data,
            hovertemplate="<b>Likelihood: %{y}<br>Impact: %{x}<br>Score: %{z}</b><br>Assets:<br>%{hovertext}<extra></extra>",
            colorscale=colors,
            zmin=1, zmax=25,
            showscale=False,
            xgap=1, ygap=1 # Grid lines
        ))
        
        fig.update_layout(
            title={
                'text': "Risk Matrix (Likelihood x Impact)",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title="Impact (Damage)",
            yaxis_title="Likelihood (Probability)",
            xaxis=dict(side="bottom", tickmode="linear", dtick=1),
            yaxis=dict(side="left", tickmode="linear", dtick=1, autorange="reversed"),
            width=550,
            height=550
        )
        st.plotly_chart(fig, use_container_width=False)

    with col_table:
        st.subheader("Risk Register")
        
        # Filter
        filter_level = st.selectbox("Select Level", ["All", "Low", "Medium", "High", "Critical"])
        if filter_level != "All":
            display_df = df[df['level'] == filter_level]
        else:
            display_df = df
            
        def get_mitigation(level):
            if level == "Low": return "Accept / monitor"
            if level == "Medium": return "Plan mitigation within 6 months"
            if level == "High": return "Prioritize action + compensating controls (NIST PR.AC)"
            if level == "Critical": return "Immediate mitigation required + executive reporting"
            return ""
            
        display_df['Mitigation'] = display_df['level'].apply(get_mitigation)
        
        # Responsive Table with Mitigation Column
        st.dataframe(
            display_df,
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "asset": "Asset",
                "threat": "Threat",
                "likelihood": st.column_config.NumberColumn("Likelihood", width="small"),
                "impact": st.column_config.NumberColumn("Impact", width="small"),
                "score": st.column_config.NumberColumn("Score", width="small"),
                "level": "Level",
                "Mitigation": st.column_config.TextColumn("Mitigation Action", width="large")
            },
            hide_index=True,
            use_container_width=True # Responsive
        )
        
        # CSV Export
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download CSV",
            csv,
            "risk_register.csv",
            "text/csv",
            key='download-csv',
            type="primary"
        )

else:
    # Empty State
    st.info("No risks yet – add one above.")

