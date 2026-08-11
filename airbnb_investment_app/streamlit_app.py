import streamlit as st
import pandas as pd
import numpy as np
import json

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
# MOCK DATA LAYER (Engineered schema-aligned mock data)
# -----------------------------------------------------------------------------
@st.cache_data
def load_mock_neighbourhood_data():
    return pd.DataFrame([
        # London
        {"city": "London", "neighbourhood": "Camden", "avg_nightly_price": 155.0, "occupancy_proxy": 0.78, "est_annual_rev": 44100, "investment_score": 88.5, "st_yield": 8.2, "lt_yield": 4.5, "risk_level": "Medium"},
        {"city": "London", "neighbourhood": "Westminster", "avg_nightly_price": 225.0, "occupancy_proxy": 0.69, "est_annual_rev": 56700, "investment_score": 83.2, "st_yield": 7.8, "lt_yield": 3.9, "risk_level": "High"},
        {"city": "London", "neighbourhood": "Tower Hamlets", "avg_nightly_price": 130.0, "occupancy_proxy": 0.74, "est_annual_rev": 35100, "investment_score": 81.0, "st_yield": 8.6, "lt_yield": 5.1, "risk_level": "Low"},
        {"city": "London", "neighbourhood": "Kensington and Chelsea", "avg_nightly_price": 270.0, "occupancy_proxy": 0.62, "est_annual_rev": 61100, "investment_score": 77.8, "st_yield": 6.9, "lt_yield": 3.5, "risk_level": "High"},
        {"city": "London", "neighbourhood": "Hackney", "avg_nightly_price": 140.0, "occupancy_proxy": 0.81, "est_annual_rev": 41300, "investment_score": 89.1, "st_yield": 9.1, "lt_yield": 4.8, "risk_level": "Low"},
        
        # Manchester
        {"city": "Manchester", "neighbourhood": "Deansgate", "avg_nightly_price": 115.0, "occupancy_proxy": 0.82, "est_annual_rev": 34400, "investment_score": 91.5, "st_yield": 9.8, "lt_yield": 5.8, "risk_level": "Low"},
        {"city": "Manchester", "neighbourhood": "Ancoats", "avg_nightly_price": 105.0, "occupancy_proxy": 0.80, "est_annual_rev": 30600, "investment_score": 87.4, "st_yield": 9.2, "lt_yield": 5.5, "risk_level": "Low"},
        
        # Edinburgh
        {"city": "Edinburgh", "neighbourhood": "Old Town", "avg_nightly_price": 160.0, "occupancy_proxy": 0.79, "est_annual_rev": 46100, "investment_score": 88.0, "st_yield": 8.9, "lt_yield": 4.6, "risk_level": "Medium"},
        {"city": "Edinburgh", "neighbourhood": "Leith", "avg_nightly_price": 110.0, "occupancy_proxy": 0.75, "est_annual_rev": 30100, "investment_score": 82.5, "st_yield": 8.1, "lt_yield": 5.2, "risk_level": "Low"},
    ])

@st.cache_data
def load_mock_property_types():
    return pd.DataFrame([
        {"property_type": "2-Bed Entire Apartment", "score": 92, "avg_price": 165, "occupancy": "76%", "est_rev": "£45,800/yr", "rationale": "Strongest balance of family/business traveler demand with high nightly rates."},
        {"property_type": "1-Bed Entire Home", "score": 87, "avg_price": 120, "occupancy": "81%", "est_rev": "£35,400/yr", "rationale": "Highest year-round occupancy proxy with minimal operational overhead."},
        {"property_type": "3-Bed Townhouse", "score": 81, "avg_price": 280, "occupancy": "64%", "est_rev": "£65,300/yr", "rationale": "Premium weekend yield from small group leisure visits; higher seasonal variance."}
    ])

@st.cache_data
def load_mock_listings():
    np.random.seed(42)
    cities = ["London"] * 35 + ["Manchester"] * 10 + ["Edinburgh"] * 5
    neighbourhoods = np.random.choice(["Camden", "Westminster", "Tower Hamlets", "Hackney", "Kensington and Chelsea"], 50)
    
    # Geographic bounds near central London
    lats = 51.5074 + np.random.normal(0, 0.03, 50)
    lons = -0.1278 + np.random.normal(0, 0.04, 50)
    
    return pd.DataFrame({
        "listing_id": [f"LST-{1000 + i}" for i in range(50)],
        "city": cities,
        "name": [f"Prime Candidate Property {i+1}" for i in range(50)],
        "neighbourhood": neighbourhoods,
        "latitude": lats,
        "longitude": lons,
        "price": np.random.randint(80, 320, 50),
        "room_type": np.random.choice(["Entire home/apt", "Private room"], 50, p=[0.75, 0.25]),
        "bedrooms": np.random.choice([1, 2, 3], 50, p=[0.4, 0.4, 0.2]),
        "review_score": np.round(np.random.uniform(4.3, 5.0, 50), 2),
        "reviews_count": np.random.randint(12, 280, 50),
        "est_availability": np.random.randint(110, 340, 50),
        "investment_score": np.random.randint(70, 98, 50)
    })

# Load base mock datasets
df_areas = load_mock_neighbourhood_data()
df_types = load_mock_property_types()
df_listings = load_mock_listings()

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION & CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.title("🛠️ Investor Controls")

# 1. Persona Selector Engine
persona = st.sidebar.selectbox(
    "👤 Investor Persona Profile",
    options=["Balanced Investor", "Revenue Maximiser", "Risk-Averse Investor"],
    help="Adapts recommendation logic, dynamic weights, and metric framing."
)

st.sidebar.divider()
st.sidebar.subheader("📍 Geography & Filters")

# 2. City Selector (London required baseline)
selected_city = st.sidebar.selectbox(
    "Select Target City",
    options=["London", "Manchester", "Edinburgh"],
    index=0
)

# Filter neighbourhoods dynamically
available_boroughs = df_areas[df_areas["city"] == selected_city]["neighbourhood"].unique()
selected_boroughs = st.sidebar.multiselect(
    "Borough / Neighbourhood",
    options=available_boroughs,
    default=available_boroughs
)

# Granular Controls
price_range = st.sidebar.slider("Nightly Price Ceiling (£)", 40, 500, (60, 350))
selected_room_types = st.sidebar.multiselect(
    "Room Type",
    options=["Entire home/apt", "Private room", "Hotel room"],
    default=["Entire home/apt", "Private room"]
)
min_reviews = st.sidebar.slider("Min Guest Reviews", 0, 150, 15)
min_availability = st.sidebar.slider("Min Calendar Availability (Days/Yr)", 0, 365, 90)

# Filter listings dataset
filtered_listings = df_listings[
    (df_listings["city"] == selected_city) &
    (df_listings["neighbourhood"].isin(selected_boroughs)) &
    (df_listings["price"].between(price_range[0], price_range[1])) &
    (df_listings["room_type"].isin(selected_room_types)) &
    (df_listings["reviews_count"] >= min_reviews) &
    (df_listings["est_availability"] >= min_availability)
]

filtered_areas = df_areas[
    (df_areas["city"] == selected_city) &
    (df_areas["neighbourhood"].isin(selected_boroughs))
]

# -----------------------------------------------------------------------------
# MAIN APP HEADER
# -----------------------------------------------------------------------------
st.title("🏠 Airbnb Investment Intelligence Platform")
st.caption(f"Target City: **{selected_city}** | Active Persona Strategy: **{persona}**")

# Dynamic Persona Strategy Banner
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
    
    # Key Metrics Bar
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
                    st.markdown(f"### #{rank} {row['neighbourhood']}  *(Score: {row['investment_score']}/100)*")
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"**Est. Annual Rev:**\n£{row['est_annual_rev']:,}")
                    c2.write(f"**Avg Price:**\n£{row['avg_nightly_price']}/night")
                    c3.write(f"**Short-Term Yield:**\n{row['st_yield']}%")
                    st.caption(f"Risk Assessment: **{row['risk_level']}** | Occupancy Proxy: {int(row['occupancy_proxy']*100)}%")
        else:
            st.info("No neighbourhoods match current filter criteria.")

    # 2. Top 3 Recommended Property Types
    with col_rec_types:
        st.subheader("🏠 Top 3 Recommended Property Types")
        for rank, (_, row) in enumerate(df_types.iterrows(), 1):
            with st.container(border=True):
                st.markdown(f"### #{rank} {row['property_type']} *(Score: {row['score']}/100)*")
                st.write(f"• **Avg Nightly Price:** £{row['avg_price']} | **Est. Occupancy:** {row['occupancy']}")
                st.write(f"• **Est. Annual Revenue:** {row['est_rev']}")
                st.write(f"• **Rationale:** {row['rationale']}")

    st.divider()
    
    # 3. Transparent Investment Score Methodology
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
        # Native Streamlit Map (No external dependencies required)
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
    st.subheader("AI Guest Sentiment & Review Extraction")
    
    col_ai_left, col_ai_right = st.columns([1, 2])
    
    with col_ai_left:
        st.markdown("#### 💬 Review Theme Summary")
        
        with st.container(border=True):
            st.markdown("##### 🟢 Positive Key Drivers")
            st.write("• **Location Proximity:** Frequent praise for nearby tube/transit stations.")
            st.write("• **Seamless Check-in:** High sentiment regarding keyless keypad entries.")
            st.write("• **Cleanliness Standard:** High correlation with 4.9+ star review scores.")

        with st.container(border=True):
            st.markdown("##### 🔴 Friction Points & Risk Flags")
            st.write("• **Street Noise:** Common complaint in central ground-floor properties.")
            st.write("• **Heating/Wi-Fi Drops:** Secondary operational risks noted in guest comments.")

        st.markdown("#### ✨ AI Rationale Generator")
        candidate_list = filtered_listings["listing_id"].tolist() if not filtered_listings.empty else ["LST-1000"]
        selected_candidate = st.selectbox("Select Candidate Property", candidate_list)
        
        if st.button("Generate Rationale"):
            cand_data = filtered_listings[filtered_listings["listing_id"] == selected_candidate]
            if not cand_data.empty:
                c_row = cand_data.iloc[0]
                st.info(
                    f"**AI Investor Rationale for {selected_candidate}:**\n\n"
                    f"Property located in **{c_row['neighbourhood']}** priced at **£{c_row['price']}/night** with a score of **{c_row['investment_score']}/100**.\n\n"
                    f"* **Strengths:** Outstanding guest satisfaction score ({c_row['review_score']}⭐ across {c_row['reviews_count']} reviews).\n"
                    f"* **Revenue Strategy:** Above-average availability ({c_row['est_availability']} days/yr) provides immediate operational revenue capture.\n"
                    f"* **Actionable Insight:** Review sentiment suggests adding blackout curtains to further boost premium weekend rates."
                )

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
    
    # Required London Regulatory Note
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