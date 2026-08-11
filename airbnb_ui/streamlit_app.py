import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Airbnb Investment Intelligence App",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# MOCK DATA GENERATORS (Temporary until data pipeline is ready)
# -----------------------------------------------------------------------------
@st.cache_data
def load_mock_summary():
    return {
        "avg_nightly_price": 165.50,
        "avg_occupancy": 72.4,
        "est_annual_rev": 43700,
        "active_listings": 1420,
        "avg_rating": 4.81
    }

@st.cache_data
def load_mock_neighbourhoods():
    return pd.DataFrame({
        "city": ["London", "London", "London", "London", "Manchester", "Edinburgh"],
        "neighbourhood": ["Camden", "Westminster", "Tower Hamlets", "Kensington and Chelsea", "Deansgate", "Old Town"],
        "avg_nightly_price": [145.0, 220.0, 125.0, 260.0, 110.0, 155.0],
        "occupancy_rate": [0.76, 0.68, 0.71, 0.62, 0.81, 0.79],
        "est_annual_revenue": [40200, 54500, 32400, 58800, 32500, 44700],
        "investment_score": [89.2, 84.5, 81.0, 78.4, 91.5, 88.0],
        "risk_level": ["Medium", "High", "Low", "High", "Low", "Medium"]
    })

@st.cache_data
def load_mock_listings():
    np.random.seed(42)
    lats = 51.5074 + np.random.normal(0, 0.04, 50)
    lons = -0.1278 + np.random.normal(0, 0.05, 50)
    return pd.DataFrame({
        "listing_id": [f"LST-{1000 + i}" for i in range(50)],
        "name": [f"Property Candidate {i+1}" for i in range(50)],
        "neighbourhood": np.random.choice(["Camden", "Westminster", "Tower Hamlets", "Kensington and Chelsea"], 50),
        "latitude": lats,
        "longitude": lons,
        "price": np.random.randint(70, 350, 50),
        "room_type": np.random.choice(["Entire home/apt", "Private room"], 50, p=[0.7, 0.3]),
        "review_score": np.round(np.random.uniform(4.2, 5.0, 50), 2),
        "reviews_count": np.random.randint(10, 250, 50),
        "est_availability": np.random.randint(100, 330, 50),
        "investment_score": np.random.randint(65, 98, 50)
    })

# Load datasets
mock_summary = load_mock_summary()
df_neighbourhoods = load_mock_neighbourhoods()
df_listings = load_mock_listings()

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS & FILTERS
# -----------------------------------------------------------------------------
st.sidebar.title("🎮 Control Panel")

# Persona Selector
persona = st.sidebar.selectbox(
    "👤 Investor Persona Strategy",
    options=["Balanced Investor", "Revenue Maximiser", "Risk-Averse Investor"],
    help="Adapts recommendation logic, dynamic weights, and metric framing."
)

st.sidebar.divider()
st.sidebar.subheader("📍 Location & Filter Settings")

# City Selector
selected_city = st.sidebar.selectbox(
    "Select City",
    options=["London", "Manchester", "Edinburgh"],
    index=0
)

# Filter neighbourhoods based on selected city
city_neighbourhoods = df_neighbourhoods[df_neighbourhoods["city"] == selected_city]["neighbourhood"].unique()
selected_neighbourhoods = st.sidebar.multiselect(
    "Filter Borough / Neighbourhood",
    options=city_neighbourhoods,
    default=city_neighbourhoods
)

# Granular Filters
price_range = st.sidebar.slider("Nightly Price Range (£)", 30, 500, (50, 300))
selected_room_types = st.sidebar.multiselect(
    "Room Type",
    options=["Entire home/apt", "Private room", "Hotel room", "Shared room"],
    default=["Entire home/apt", "Private room"]
)
min_reviews = st.sidebar.slider("Minimum Review Count", 0, 100, 10)
min_availability = st.sidebar.slider("Minimum Availability (Days/Yr)", 0, 365, 90)

# Apply mock filter logic
filtered_listings = df_listings[
    (df_listings["neighbourhood"].isin(selected_neighbourhoods)) &
    (df_listings["price"].between(price_range[0], price_range[1])) &
    (df_listings["room_type"].isin(selected_room_types)) &
    (df_listings["reviews_count"] >= min_reviews) &
    (df_listings["est_availability"] >= min_availability)
]

# -----------------------------------------------------------------------------
# MAIN APP HEADER
# -----------------------------------------------------------------------------
st.title("🏠 Airbnb Investment Intelligence Platform")
st.caption(f"Active Strategy Profile: **{persona}** | Region Focus: **{selected_city}**")

# Context banner matching persona
if persona == "Revenue Maximiser":
    st.info("⚡ **Revenue Maximiser Mode:** Prioritising properties and areas with higher Average Daily Rate (ADR) and yield metrics.")
elif persona == "Risk-Averse Investor":
    st.warning("🛡️ **Risk-Averse Mode:** Prioritising areas with stable occupancy, high review volume, and strict regulatory compliance.")
else:
    st.success("⚖️ **Balanced Strategy:** Weighing occupancy rate, price ceiling, and guest satisfaction equally.")

# -----------------------------------------------------------------------------
# MAIN NAVIGATION TABS
# -----------------------------------------------------------------------------
tab_overview, tab_market, tab_ai_listings, tab_risk = st.tabs([
    "📊 Executive Overview",
    "🗺️ Market & Spatial Deep-Dive",
    "🤖 AI Review Intelligence & Listings",
    "⚠️ Risks, Regulations & Assumptions"
])

# -----------------------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW
# -----------------------------------------------------------------------------
with tab_overview:
    st.subheader("Key Market Highlights")
    
    # Summary Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Avg Nightly Price", f"£{mock_summary['avg_nightly_price']}")
    m2.metric("Occupancy Proxy Rate", f"{mock_summary['avg_occupancy']}%")
    m3.metric("Est. Annual Revenue", f"£{mock_summary['est_annual_rev']:,}")
    m4.metric("Active Candidates", len(filtered_listings))
    m5.metric("Avg Guest Rating", f"⭐ {mock_summary['avg_rating']}")

    st.divider()

    col_top_areas, col_top_types = st.columns(2)

    with col_top_areas:
        st.subheader("🏆 Top 3 Recommended Neighbourhoods")
        top_3_areas = df_neighbourhoods[df_neighbourhoods["city"] == selected_city].sort_values(
            by="investment_score", ascending=False
        ).head(3)
        
        for idx, row in top_3_areas.iterrows():
            with st.container(border=True):
                st.markdown(f"#### #{row['investment_score']} Score | **{row['neighbourhood']}**")
                st.write(f"• **Est. Annual Revenue:** £{row['est_annual_revenue']:,}")
                st.write(f"• **Avg Price:** £{row['avg_nightly_price']}/night | **Occupancy Proxy:** {int(row['occupancy_rate']*100)}%")
                st.write(f"• **Risk Profile:** `{row['risk_level']}`")

    with col_top_types:
        st.subheader("🏠 Top 3 Recommended Property Types")
        mock_types = [
            {"type": "2-Bed Entire Apartment", "score": "92/100", "rationale": "High demand from small families and business travellers with high ADR."},
            {"type": "1-Bed Entire Home", "score": "87/100", "rationale": "Strongest year-round occupancy proxy with minimal maintenance costs."},
            {"type": "3-Bed Townhouse/House", "score": "81/100", "rationale": "Higher nightly rates for weekend groups, though subject to seasonal variance."}
        ]
        for item in mock_types:
            with st.container(border=True):
                st.markdown(f"#### {item['score']} | **{item['type']}**")
                st.write(f"**Rationale:** {item['rationale']}")

# -----------------------------------------------------------------------------
# TAB 2: MARKET & SPATIAL DEEP-DIVE (Native Snowflake Compatible)
# -----------------------------------------------------------------------------
with tab_market:
    st.subheader("Spatial Market Distribution")
    
    if not filtered_listings.empty:
        # Streamlit Native Map
        st.map(
            filtered_listings,
            latitude="latitude",
            longitude="longitude",
            size="price",
            color="#FF5A5F"
        )
    else:
        st.warning("No listings match the selected sidebar filters.")

    st.divider()
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Average Price by Borough (£)")
        price_by_borough = filtered_listings.groupby("neighbourhood")["price"].mean().reset_index()
        st.bar_chart(
            price_by_borough,
            x="neighbourhood",
            y="price",
            color="#1F77B4"
        )

    with col_chart2:
        st.subheader("Short-Term vs. Long-Term Benchmark Yield (%)")
        df_comp = pd.DataFrame({
            "Borough": ["Camden", "Westminster", "Tower Hamlets"],
            "Short-Term Yield (%)": [8.4, 9.1, 7.2],
            "Long-Term Yield (%)": [4.5, 4.2, 5.0]
        }).set_index("Borough")
        
        st.bar_chart(df_comp)

# -----------------------------------------------------------------------------
# TAB 3: AI REVIEW INTELLIGENCE & LISTINGS
# -----------------------------------------------------------------------------
with tab_ai_listings:
    st.subheader("AI Guest Review Theme Analysis")
    
    col_ai_left, col_ai_right = st.columns([1, 2])
    
    with col_ai_left:
        st.markdown("#### Common Guest Sentiment Themes")
        st.success("🟢 **Top Strengths:** Prime Location, Seamless Self Check-in, High-speed Wi-Fi, Exceptional Cleanliness")
        st.error("🔴 **Top Friction Points:** Street Noise, Small Bathroom Dimensions, Complex Key Lockbox")
        
        st.markdown("#### AI Investment Rationale Generator")
        selected_listing_id = st.selectbox("Select Candidate Listing", filtered_listings["listing_id"].unique() if not filtered_listings.empty else ["LST-1000"])
        
        if st.button("✨ Generate AI Investment Memo Preview"):
            st.info(
                f"**AI Executive Summary for {selected_listing_id}:**\n\n"
                f"This listing shows strong yield potential in {selected_city}. Guest reviews consistently highlight "
                f"location proximity to transit hubs. Main risk factor identified in feedback is noise during peak weekends. "
                f"Recommended action: Install soundproofing upgrades to capture premium ADR."
            )

    with col_ai_right:
        st.markdown("#### Top Candidate Listings")
        st.dataframe(
            filtered_listings[[
                "listing_id", "name", "neighbourhood", "price", 
                "room_type", "review_score", "investment_score"
            ]].sort_values(by="investment_score", ascending=False),
            use_container_width=True
        )

# -----------------------------------------------------------------------------
# TAB 4: RISKS, REGULATIONS & ASSUMPTIONS
# -----------------------------------------------------------------------------
with tab_risk:
    st.subheader("Regulatory Context & Data Limitations")
    
    st.warning(
        "🏛️ **London Regulatory Warning (90-Night Cap):**\n\n"
        "Under London City Hall guidance, short-term residential lettings in Greater London are capped "
        "at a maximum of **90 nights per calendar year** unless official planning permission for material change "
        "of use is granted by the local council."
    )

    st.divider()

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown("### 📊 Inside Airbnb Data Assumptions")
        st.markdown("""
        * **Calendar Availability vs. Bookings:** Unavailable nights on the calendar do **not** distinguish between genuine guest bookings and nights blocked by the host for personal use or maintenance.
        * **Geographic Anonymisation:** Listing map coordinates are randomly anonymised/fuzzed by up to 150 metres by Inside Airbnb to protect host privacy.
        * **Point-in-Time Snapshot:** Data reflects quarterly snapshot downloads rather than continuous real-time feeds.
        """)

    with col_r2:
        st.markdown("### ⚖️ Legal & Financial Disclaimer")
        st.markdown("""
        * **Not Financial Advice:** Financial projections, occupancy proxies, and revenue scores are estimates intended for comparative exploratory analysis only.
        * **Tax & Operating Costs:** Figures exclude localized platform service fees, cleaning overheads, insurance, utilities, and tax liabilities.
        * **Independent Due Diligence:** Users must perform independent legal, planning permission, and financial checks prior to property acquisition.
        """)