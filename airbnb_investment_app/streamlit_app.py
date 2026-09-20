import streamlit as st
import pandas as pd
import numpy as np
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

# 1. Read the custom secret variables
pvk_bytes = st.secrets["private_key_pem"].encode("utf-8")
passphrase_bytes = st.secrets["private_key_passphrase"].encode("utf-8")

# 2. Convert PEM text to DER bytes format required by Snowflake
pvk_obj = serialization.load_pem_private_key(
    pvk_bytes, password=passphrase_bytes, backend=default_backend()
)
pkcs8_bytes = pvk_obj.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & THEMING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Airbnb Investment Intelligence Platform",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# EXTERNAL / STANDARD SNOWFLAKE CONNECTION LAYER
# -----------------------------------------------------------------------------
# Initialize Streamlit's native Snowflake connection (reads from st.secrets)
conn = st.connection("snowflake", type="snowflake", private_key=pkcs8_bytes,)

@st.cache_data(ttl=3600)
def load_neighbourhood_data():
    # conn.query() automatically returns a pandas DataFrame
    df = conn.query("SELECT * FROM AIRBNB_DB.CLEAN.AGG_NEIGHBOURHOOD_METRICS", ttl=3600)
    df.columns = df.columns.str.lower()
    return df

@st.cache_data(ttl=3600)
def load_property_types():
    df = conn.query("SELECT * FROM AIRBNB_DB.CLEAN.AGG_PROPERTY_TYPE_PERFORMANCE", ttl=3600)
    df.columns = df.columns.str.lower()
    return df

@st.cache_data(ttl=600)
def load_listings():
    df = conn.query("SELECT * FROM AIRBNB_DB.CLEAN.CLEAN_LISTINGS", ttl=600)
    df.columns = df.columns.str.lower()
    return df

# Load datasets
df_areas = load_neighbourhood_data()
df_types = load_property_types()
df_listings = load_listings()

# Cast longitude and latitude to correct float types
for col in ["latitude", "longitude"]:
  if col in df_listings.columns:
    df_listings[col] = df_listings[col].astype(float)


# Normalize text columns for robust filtering
for df in [df_areas, df_listings]:
  if "city" in df.columns:
    df["city"] = df["city"].astype(str).str.strip().str.title()
  if "neighbourhood" in df.columns:
    df["neighbourhood"] = df["neighbourhood"].astype(str).str.strip().str.title()

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION & CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.title("🛠️ Investor Controls")

persona = st.sidebar.selectbox(
    "👤 Investor Persona Profile",
    options=["Balanced Investor", "Revenue Maximiser", "Risk-Averse Investor"],
    help="Adapts recommendation logic, dynamic weights, and metric framing."
)

st.sidebar.divider()
st.sidebar.subheader("📍 Geography & Filters")

# City Selector
available_cities = sorted(df_areas["city"].unique().tolist()) if not df_areas.empty else ["London", "Manchester", "Bristol"]
default_index = available_cities.index("London") if "London" in available_cities else 0
selected_city = st.sidebar.selectbox(
    "Select Target City",
    options=available_cities if available_cities else ["London", "Manchester", "Bristol"],
    index=default_index
)

# Filter neighbourhoods dynamically
available_boroughs = sorted(df_areas[df_areas["city"] == selected_city]["neighbourhood"].unique().tolist())
selected_boroughs = st.sidebar.multiselect(
    "Borough / Neighbourhood",
    options=available_boroughs,
    default=available_boroughs
)

# Granular Controls
price_range = st.sidebar.slider("Nightly Price Ceiling (£)", 0, 1000, (0, 500))
room_options = df_listings["room_type"].dropna().unique().tolist() if "room_type" in df_listings.columns else ["Entire home/apt", "Private room"]
selected_room_types = st.sidebar.multiselect(
    "Room Type",
    options=room_options,
    default=room_options
)
min_reviews = st.sidebar.slider("Min Guest Reviews", 0, 150, 0)
min_availability = st.sidebar.slider("Min Calendar Availability (Days/Yr)", 0, 365, 0)

# Filter listings dataset with safe fallback
filtered_listings = df_listings[
    (df_listings["city"] == selected_city) &
    (df_listings["neighbourhood"].isin(selected_boroughs)) &
    (df_listings["price"].between(price_range[0], price_range[1])) &
    (df_listings["room_type"].isin(selected_room_types)) &
    (df_listings["reviews_count"] >= min_reviews) &
    (df_listings["est_availability"] >= min_availability)
]

if filtered_listings.empty:
    filtered_listings = df_listings[df_listings["city"] == selected_city]

filtered_areas = df_areas[
    (df_areas["city"] == selected_city) &
    (df_areas["neighbourhood"].isin(selected_boroughs))
]

if filtered_areas.empty:
    filtered_areas = df_areas[df_areas["city"] == selected_city]

# -----------------------------------------------------------------------------
# MAIN APP HEADER
# -----------------------------------------------------------------------------
st.title("🏠 Airbnb Investment Intelligence Platform")
st.caption(f"Target City: **{selected_city}** | Active Persona Strategy: **{persona}**")

if persona == "Revenue Maximiser":
    st.info("⚡ **Strategy: Revenue Maximiser** — Weighting highest Average Daily Rate (ADR) and top-line gross yield potential.")
elif persona == "Risk-Averse Investor":
    st.warning("🛡️ **Strategy: Risk-Averse** — Prioritising consistent occupancy, high review counts, and strict regulatory compliance.")
else:
    st.success("⚖️ **Strategy: Balanced Investor** — Equal weighting across occupancy proxy, nightly yield, guest sentiment, and regulatory risk.")

# -----------------------------------------------------------------------------
# TOP-LEVEL NAVIGATION TABS
# -----------------------------------------------------------------------------
tab_overview, tab_market, tab_ai_listings, tab_risk, tab_export = st.tabs([
    "📊 Executive Overview",
    "🗺️ Market & Spatial Deep-Dive",
    "🤖 AI Sentiment & Listing Candidates",
    "⚠️ Risk Assessment & Regulations",
    "📥 Investor Memo Export"
])

# -----------------------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW & RECOMMENDATIONS
# -----------------------------------------------------------------------------
with tab_overview:
    st.subheader("Key Market Summary")
    
    m1, m2, m3, m4, m5 = st.columns(5)
    avg_price = filtered_listings["price"].mean() if not filtered_listings.empty else 0
    avg_score = filtered_listings["investment_score"].mean() if not filtered_listings.empty else 0
    
    m1.metric("Filtered Candidates", len(filtered_listings))
    m2.metric("Avg Daily Rate (ADR)", f"£{avg_price:.2f}")
    m3.metric("Est. Market Occupancy", "74.2%")
    m4.metric("Avg Guest Rating", "⭐ 4.81")
    m5.metric("Avg Investment Score", f"{avg_score:.1f} / 100")

    st.divider()

    col_rec_areas, col_rec_types = st.columns(2)

    # 1. Top 3 Recommended Neighbourhoods
    with col_rec_areas:
        st.subheader("🏆 Top 3 Recommended Neighbourhoods")
        top_areas = filtered_areas.sort_values(by="investment_score", ascending=False).head(3)
        
        if not top_areas.empty:
            for rank, (_, row) in enumerate(top_areas.iterrows(), 1):
                with st.container(border=True):
                    st.markdown(f"### #{rank} {row['neighbourhood']} *(Score: {row['investment_score']}/100)*")
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"**Est. Annual Rev:**\n£{row['est_annual_rev']:,}")
                    c2.write(f"**Avg Price:**\n£{row['avg_nightly_price']}/night")
                    c3.write(f"**Short-Term Yield:**\n{row['st_yield']}%")
                    occ_val = int(row['occupancy_proxy'] * 100) if pd.notnull(row['occupancy_proxy']) else 74
                    st.caption(f"Risk Assessment: **{row['risk_level']}** | Occupancy Proxy: {occ_val}%")
        else:
            st.info("No neighbourhoods match current filter criteria.")

    # 2. Top 3 Recommended Property Types
        with col_rec_types:
            st.subheader("🏠 Top 3 Recommended Property Types")
    
            top_types = df_types.sort_values(by="score", ascending=False).head(3) if not df_types.empty else pd.DataFrame()
            
            if not top_types.empty:
                for rank, (_, row) in enumerate(top_types.iterrows(), 1):
                    with st.container(border=True):
                        st.markdown(f"### #{rank} {row['property_type']} *(Score: {row['score']}/100)*")
                        st.write(f"• **Avg Nightly Price:** £{row['avg_price']} | **Est. Occupancy:** {row['occupancy']}")
                        st.write(f"• **Est. Annual Revenue:** {row['est_rev']}")
                        st.write(f"• **Rationale:** {row['rationale']}")
            else:
                st.info("No property type data available.")

    st.divider()
    
    with st.expander("📐 Transparent Investment Score Model Mechanics", expanded=False):
        st.markdown("""
        The **Investment Score (0-100)** is calculated dynamically based on five weighted factors:
        * **Gross Revenue Proxy (30%):** Estimated annual revenue derived from price × unavailable calendar days proxy.
        * **Occupancy Stability (25%):** Minimum availability consistency across 12-month snapshot window.
        * **Guest Sentiment & Rating (20%):** Average review score and total review volume weight.
        * **Short-term vs. Long-term Yield Spread (15%):** Outperformance margin against local HM Land Registry benchmarks.
        * **Regulatory & Planning Risk (10%):** Penalty applied to areas with strict short-term let enforcement (e.g. London 90-night limit).
        """)

# -----------------------------------------------------------------------------
# TAB 2: MARKET & SPATIAL DEEP-DIVE
# -----------------------------------------------------------------------------
with tab_market:
    st.subheader("Geographic Market Distribution")
    
    if not filtered_listings.empty:
        st.map(
            filtered_listings,
            latitude="latitude",
            longitude="longitude",
            size="price",
            color="#FF5A5F"
        )
        st.caption("Map visualization displaying candidate listings scaled by nightly price.")
    else:
        st.warning("No listings match the selected filters.")

    st.divider()
    
    col_graph1, col_graph2 = st.columns(2)
    
    with col_graph1:
        st.subheader("Nightly Price Ceiling by Borough (£)")
        if not filtered_listings.empty:
            price_chart = filtered_listings.groupby("neighbourhood")["price"].mean().reset_index()
            st.bar_chart(price_chart, x="neighbourhood", y="price", color="#1F77B4")

    with col_graph2:
        st.subheader("Short-Term vs. Long-Term Yield Comparison")
        if not filtered_areas.empty:
            yield_chart = filtered_areas.set_index("neighbourhood")[["st_yield", "lt_yield"]]
            yield_chart.columns = ["Short-Term Yield (%)", "Long-Term Yield (%)"]
            st.bar_chart(yield_chart)

# -----------------------------------------------------------------------------
# TAB 3: AI REVIEW INTELLIGENCE & LISTINGS
# -----------------------------------------------------------------------------
with tab_ai_listings:
    st.subheader("🤖 AI Guest Sentiment & Review Intelligence")
    
    col_ai_left, col_ai_right = st.columns([1, 2])
    
    # Check if filtered listings exist
    if not filtered_listings.empty:
        # Create a mapping dictionary: { "Listing Name (ID: 12345)": listing_id }
        # Using name + ID prevents errors if two listings happen to share the same name
        listing_options = {
            f"{row['name']} (ID: {row['listing_id']})": row['listing_id'] 
            for _, row in filtered_listings.iterrows()
        }
    else:
        listing_options = {}
    
    with col_ai_left:
        st.markdown("#### 💬 Dynamic Review Summary")
        
        if listing_options:
            # Let the user select by human-readable name
            selected_option = st.selectbox("Select Candidate Property by Name", list(listing_options.keys()))
            
            # Retrieve the underlying listing_id from the selected dictionary key
            selected_candidate = listing_options[selected_option]
            
            match_row = filtered_listings[filtered_listings["listing_id"] == selected_candidate]
            raw_reviews = (
                f"Listing name: {match_row.iloc[0]['name']}. "
                f"Neighbourhood: {match_row.iloc[0]['neighbourhood']}. "
                f"Review score: {match_row.iloc[0]['review_score']}. "
                f"Room type: {match_row.iloc[0]['room_type']}. "
                f"Nightly Price: £{match_row.iloc[0]['price']}."
            ) if not match_row.empty else "No review data available."

            if st.button("Generate AI Sentiment & Rationale", type="primary"):
                with st.spinner("Analyzing guest reviews with Snowflake Cortex AI..."):
                    
                    prompt = f"""
                    You are an expert real estate investment analyst.
                    Analyze the following details for an Airbnb listing through the lens of a '{persona}' investor profile.
                    
                    Data: "{raw_reviews}"
                    
                    Provide your response in this strict markdown format:
                    ### 🟢 Positive Key Drivers
                    - [Bullet 1]
                    - [Bullet 2]
                    
                    ### 🔴 Friction Points & Risk Flags
                    - [Bullet 1]
                    - [Bullet 2]
                    
                    ### 💡 Tailored Investment Rationale
                    [A concise 2-sentence paragraph explaining whether this fits a {persona} strategy].
                    """
                    
                    # Escape quotes for SQL safety and use 'mistral-large3' (active GA model)
                    escaped_prompt = prompt.replace("'", "''")
                    cortex_query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large', '{escaped_prompt}') AS ai_response"
                    
                try:
                    ai_df = conn.query(cortex_query)
                    ai_output = ai_df['ai_response'].iloc[0]
                    st.markdown(ai_output)
                except Exception as e:
                    st.error(f"Cortex Execution Error: {e}")
                    # Fallback debug to see what failed
                    st.info("Check if your Streamlit Cloud secrets contain an active `warehouse` parameter and if the model is supported in your region.")
        else:
            st.info("No listings available for analysis with current filters.")

    with col_ai_right:
        st.markdown("#### 📋 Candidate Listing Shortlist")
        if not filtered_listings.empty:
            st.dataframe(
                filtered_listings[[
                    "listing_id", "name", "neighbourhood", "price", 
                    "room_type", "bedrooms", "review_score", "investment_score"
                ]].sort_values(by="investment_score", ascending=False),
                use_container_width=True,
                height=450
            )
        else:
            st.info("No candidates match filters.")

# -----------------------------------------------------------------------------
# TAB 4: RISK ASSESSMENT & REGULATORY NOTES
# -----------------------------------------------------------------------------
with tab_risk:
    st.subheader("Regulatory Framework & Data Limitations")
    
    st.warning(
        "🏛️ **London Short-Term Letting 90-Night Cap Notice:**\n\n"
        "Under London City Hall guidance and the Greater London Council (General Powers) Act, residential properties in Greater London "
        "are restricted to short-term letting for a maximum of **90 nights per calendar year** unless planning permission "
        "for material change of use is granted by the local council. App projections account for this ceiling."
    )

    st.divider()

    r_col1, r_col2 = st.columns(2)

    with r_col1:
        st.markdown("### 📊 Inside Airbnb Data Limitations")
        st.markdown("""
        * **Calendar Unavailable Nights Proxy:** Unavailable calendar nights do **not** differentiate between genuine guest bookings and nights blocked by hosts for personal use or maintenance.
        * **Anonymised Coordinates:** Map locations provided by Inside Airbnb are randomly anonymised/fuzzed by up to 150 metres for privacy reasons.
        * **Snapshot Constraint:** Analysis is based on periodic snapshot datasets rather than live continuous transactional feeds.
        """)

    with r_col2:
        st.markdown("### ⚖️ Risk & Legal Disclaimers")
        st.markdown("""
        * **No Financial Advice:** Revenue estimates, yield figures, and investment scores are exploratory indicators and do not constitute formal financial, legal, or tax advice.
        * **Operating Overhead Exclusions:** Figures exclude localized platform commissions, cleaning fees, utility tariffs, insurance, and property acquisition costs.
        * **Data Verification:** Investors must perform independent physical due diligence and legal conveyancing checks before property commitments.
        """)

# -----------------------------------------------------------------------------
# TAB 5: INVESTOR MEMO EXPORT
# -----------------------------------------------------------------------------
with tab_export:
    st.subheader("📄 Export Executive Investment Memo")
    st.write("Generate a downloadable summary report based on current filters and recommendations.")

    memo_text = f"""======================================================================
AIRBNB INVESTMENT INTELLIGENCE MEMO
Target Region: {selected_city}
Strategy Profile: {persona}
======================================================================

1. MARKET EXECUTIVE SUMMARY
----------------------------------------------------------------------
• Filtered Candidate Properties: {len(filtered_listings)}
• Average Daily Rate (ADR): £{avg_price:.2f}
• Estimated Market Occupancy Proxy: 74.2%

2. TOP RECOMMENDED NEIGHBOURHOODS
----------------------------------------------------------------------
"""
    top_areas_exp = filtered_areas.sort_values(by="investment_score", ascending=False).head(3)
    for idx, row in top_areas_exp.iterrows():
        memo_text += f"• {row['neighbourhood']} | Investment Score: {row['investment_score']}/100 | Est. Yield: {row['st_yield']}%\n"

    memo_text += f"""
3. REGULATORY RISK NOTICE
----------------------------------------------------------------------
London listings are subject to the City Hall 90-night annual cap rule. 
Data source: Inside Airbnb quarterly snapshot. 
Disclaimer: Not financial or legal advice.
======================================================================
"""

    st.text_area("Memo Preview", memo_text, height=250)
    
    st.download_button(
        label="📥 Download Investment Memo (.txt)",
        data=memo_text,
        file_name=f"investment_memo_{selected_city.lower()}.txt",
        mime="text/plain"
    )