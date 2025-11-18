import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# Page configuration
st.set_page_config(
    page_title="Spotify ETL API Dashboard",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Helper functions
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_api_data(endpoint, params=None):
    """Fetch data from API with error handling"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def check_api_connection():
    """Check if API is accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

# Main dashboard
def main():
    st.title("🎵 Spotify ETL API Dashboard")
    st.markdown("### Interactive dashboard showcasing the Spotify track dataset through API")
    
    # API connection status
    if not check_api_connection():
        st.error("🚨 API Connection Failed!")
        st.markdown("""
        **Please ensure the API is running:**
        ```bash
        make setup && make logs
        ```
        The dashboard will automatically retry the connection.
        """)
        time.sleep(2)
        st.rerun()
        return
    
    st.success("✅ API Connected Successfully!")
    
    # Sidebar for filters and controls
    st.sidebar.header("🎛️ Filters & Controls")
    
    # Get summary stats first
    summary_data = fetch_api_data("/stats/summary")
    if summary_data:
        st.sidebar.metric("Total Tracks", f"{summary_data['total_tracks']:,}")
        st.sidebar.metric("Avg Danceability", f"{summary_data['avg_danceability']:.3f}")
        st.sidebar.metric("Avg Tempo", f"{summary_data['avg_tempo']:.1f} BPM")
    
    st.sidebar.markdown("---")
    
    # Filter controls
    search_query = st.sidebar.text_input("🔍 Search tracks/artists", "")
    artist_filter = st.sidebar.text_input("👤 Filter by artist", "")
    
    # Danceability filter
    min_danceability = st.sidebar.slider(
        "💃 Min Danceability", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.0, 
        step=0.1
    )
    
    # Tempo filter
    tempo_range = st.sidebar.slider(
        "🎵 Tempo Range (BPM)",
        min_value=50.0,
        max_value=200.0,
        value=(50.0, 200.0),
        step=10.0
    )
    
    # Sorting options
    sort_by = st.sidebar.selectbox(
        "📊 Sort by",
        options=["danceability", "tempo", "track_name"],
        index=0
    )
    
    sort_order = st.sidebar.selectbox(
        "⬆️⬇️ Order",
        options=["desc", "asc"],
        index=0
    )
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📊 Analytics", "🎵 Track Explorer", "📈 Statistics"])
    
    with tab1:
        show_analytics_tab(summary_data)
    
    with tab2:
        show_track_explorer_tab(
            search_query, artist_filter, min_danceability, 
            tempo_range, sort_by, sort_order
        )
    
    with tab3:
        show_statistics_tab()

def show_analytics_tab(summary_data):
    """Analytics tab with visualizations"""
    st.header("📊 Dataset Analytics")
    
    if not summary_data:
        st.error("Unable to load summary data")
        return
    
    # Display key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Total Tracks", 
            f"{summary_data['total_tracks']:,}",
            help="Total number of tracks in the database"
        )
    with col2:
        st.metric(
            "Average Danceability", 
            f"{summary_data['avg_danceability']:.3f}",
            help="Average danceability score (0-1 scale)"
        )
    with col3:
        st.metric(
            "Average Tempo", 
            f"{summary_data['avg_tempo']:.1f} BPM",
            help="Average tempo in beats per minute"
        )
    
    # Top Artists Chart
    st.subheader("🎤 Top Artists by Track Count")
    top_artists_data = fetch_api_data("/stats/top-artists", {"limit": 15})
    
    if top_artists_data:
        df_artists = pd.DataFrame(top_artists_data)
        
        fig_artists = px.bar(
            df_artists.head(10), 
            x='count', 
            y='artist',
            orientation='h',
            title="Top 10 Artists by Number of Tracks",
            labels={'count': 'Number of Tracks', 'artist': 'Artist'},
            color='count',
            color_continuous_scale='viridis'
        )
        fig_artists.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_artists, use_container_width=True)
        
        # Show data table
        with st.expander("📋 View Top Artists Data"):
            st.dataframe(df_artists, use_container_width=True)

def show_track_explorer_tab(search_query, artist_filter, min_danceability, tempo_range, sort_by, sort_order):
    """Track explorer tab with filtering"""
    st.header("🎵 Track Explorer")
    
    # Build API parameters
    params = {
        "limit": 100,
        "offset": 0,
        "sort": sort_by,
        "order": sort_order
    }
    
    if search_query:
        params["q"] = search_query
    if artist_filter:
        params["artist"] = artist_filter
    if min_danceability > 0:
        params["min_danceability"] = min_danceability
    if tempo_range[0] > 50 or tempo_range[1] < 200:
        params["tempo_min"] = tempo_range[0]
        params["tempo_max"] = tempo_range[1]
    
    # Fetch tracks data
    tracks_data = fetch_api_data("/tracks", params)
    
    if not tracks_data:
        st.error("Unable to load tracks data")
        return
    
    # Display results summary
    total_results = tracks_data.get("total", 0)
    shown_results = len(tracks_data.get("items", []))
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Matches", f"{total_results:,}")
    with col2:
        st.metric("Showing", f"{shown_results}")
    
    if tracks_data["items"]:
        df_tracks = pd.DataFrame(tracks_data["items"])
        
        # Scatter plot of Danceability vs Tempo
        st.subheader("💃 Danceability vs Tempo Analysis")
        fig_scatter = px.scatter(
            df_tracks,
            x="tempo",
            y="danceability",
            hover_data=["track_name", "artist"],
            title="Track Distribution: Danceability vs Tempo",
            labels={"tempo": "Tempo (BPM)", "danceability": "Danceability"},
            color="danceability",
            color_continuous_scale="viridis"
        )
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Tracks table
        st.subheader("📋 Track Details")
        
        # Format the dataframe for better display
        display_df = df_tracks.copy()
        if "danceability" in display_df.columns:
            display_df["danceability"] = display_df["danceability"].round(3)
        if "tempo" in display_df.columns:
            display_df["tempo"] = display_df["tempo"].round(1)
        
        st.dataframe(
            display_df[["track_name", "artist", "album", "danceability", "tempo"]],
            use_container_width=True,
            column_config={
                "track_name": "Track Name",
                "artist": "Artist",
                "album": "Album",
                "danceability": st.column_config.NumberColumn(
                    "Danceability",
                    help="Danceability score (0-1)",
                    format="%.3f"
                ),
                "tempo": st.column_config.NumberColumn(
                    "Tempo",
                    help="Tempo in BPM",
                    format="%.1f"
                )
            }
        )
        
        # Pagination info
        if tracks_data.get("next_offset"):
            st.info(f"📄 Showing first {shown_results} results of {total_results:,} total matches. Use API directly for full pagination.")
    
    else:
        st.warning("No tracks found matching your criteria. Try adjusting the filters.")

def show_statistics_tab():
    """Statistics tab with detailed analysis"""
    st.header("📈 Detailed Statistics")
    
    # Fetch a larger sample for statistics
    sample_data = fetch_api_data("/tracks", {"limit": 500})
    
    if not sample_data or not sample_data["items"]:
        st.error("Unable to load sample data for statistics")
        return
    
    df_sample = pd.DataFrame(sample_data["items"])
    
    # Distribution charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💃 Danceability Distribution")
        fig_dance = px.histogram(
            df_sample,
            x="danceability",
            nbins=20,
            title="Distribution of Danceability Scores",
            labels={"danceability": "Danceability", "count": "Number of Tracks"}
        )
        fig_dance.update_layout(height=400)
        st.plotly_chart(fig_dance, use_container_width=True)
    
    with col2:
        st.subheader("🎵 Tempo Distribution")
        fig_tempo = px.histogram(
            df_sample,
            x="tempo",
            nbins=20,
            title="Distribution of Tempo (BPM)",
            labels={"tempo": "Tempo (BPM)", "count": "Number of Tracks"}
        )
        fig_tempo.update_layout(height=400)
        st.plotly_chart(fig_tempo, use_container_width=True)
    
    # Summary statistics
    st.subheader("📊 Sample Statistics Summary")
    
    numeric_cols = ["danceability", "tempo"]
    available_cols = [col for col in numeric_cols if col in df_sample.columns and df_sample[col].notna().any()]
    
    if available_cols:
        stats_df = df_sample[available_cols].describe()
        st.dataframe(stats_df, use_container_width=True)
    
    # API Performance Information
    st.subheader("⚡ API Performance")
    st.info("""
    **Sample Data Info:**
    - This tab shows statistics from a sample of 500 tracks
    - Full dataset statistics available via `/stats/summary` endpoint
    - Use the Track Explorer tab to filter and analyze specific subsets
    """)

# Footer
def show_footer():
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        🎵 Spotify ETL API Dashboard | Built with Streamlit & FastAPI
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    show_footer()