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
import os

# Try Docker internal networking first, fallback to localhost
def get_api_base_url():
    """Determine the correct API base URL"""
    docker_url = os.getenv("API_BASE_URL", "http://app:8000")
    localhost_url = "http://localhost:8000"
    
    # Test Docker internal URL first
    try:
        response = requests.get(f"{docker_url}/health", timeout=3)
        if response.status_code == 200:
            return docker_url
    except:
        pass
    
    # Fallback to localhost
    try:
        response = requests.get(f"{localhost_url}/health", timeout=3)
        if response.status_code == 200:
            return localhost_url
    except:
        pass
    
    # Return Docker URL as default if both fail
    return docker_url

# Initialize API_BASE_URL
API_BASE_URL = None

# Helper functions
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_api_data(endpoint, params=None):
    """Fetch data from API with error handling"""
    global API_BASE_URL
    if API_BASE_URL is None:
        API_BASE_URL = get_api_base_url()
    
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def check_api_connection():
    """Check if API is accessible"""
    global API_BASE_URL
    if API_BASE_URL is None:
        API_BASE_URL = get_api_base_url()
    
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
    summary_data = fetch_api_data("/api/stats/summary")
    if summary_data:
        st.sidebar.metric("Total Tracks", f"{summary_data['total_tracks']:,}")
        st.sidebar.metric("Avg Energy", f"{summary_data.get('avg_energy', 0):.3f}")
        st.sidebar.metric("Avg Popularity", f"{summary_data.get('avg_popularity', 0):.1f}")
    
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
    
    # Display key metrics in rows
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tracks", f"{summary_data['total_tracks']:,}")
        st.metric("Avg Energy", f"{summary_data.get('avg_energy', 0):.3f}")
    with col2:
        st.metric("Avg Danceability", f"{summary_data.get('avg_danceability', 0):.3f}")
        st.metric("Avg Valence", f"{summary_data.get('avg_valence', 0):.3f}")
    with col3:
        st.metric("Avg Tempo", f"{summary_data.get('avg_tempo', 0):.1f} BPM")
        st.metric("Avg Loudness", f"{summary_data.get('avg_loudness', 0):.1f} dB")
    with col4:
        st.metric("Avg Popularity", f"{summary_data.get('avg_popularity', 0):.1f}")
        st.metric("Avg Duration", f"{summary_data.get('avg_duration_ms', 0)/1000:.1f}s")
    
    # Top Artists Chart
    st.subheader("🎤 Top Artists by Track Count")
    top_artists_data = fetch_api_data("/api/stats/top-artists", {"limit": 15})
    
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
    tracks_data = fetch_api_data("/api/tracks", params)
    
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
        
        # Interactive scatter plots with multiple feature combinations
        st.subheader("🎨 Audio Features Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            x_axis = st.selectbox("X-Axis Feature", 
                ["tempo", "energy", "loudness", "valence", "acousticness", "popularity"], 
                index=0)
        with col2:
            y_axis = st.selectbox("Y-Axis Feature", 
                ["danceability", "energy", "valence", "popularity", "loudness"], 
                index=0)
        
        # Create scatter plot with selected features
        if x_axis in df_tracks.columns and y_axis in df_tracks.columns:
            fig_scatter = px.scatter(
                df_tracks,
                x=x_axis,
                y=y_axis,
                hover_data=["track_name", "artist", "popularity", "energy"],
                title=f"Track Distribution: {y_axis.title()} vs {x_axis.title()}",
                labels={x_axis: x_axis.replace("_", " ").title(), 
                       y_axis: y_axis.replace("_", " ").title()},
                color=y_axis,
                color_continuous_scale="viridis",
                size="popularity" if "popularity" in df_tracks.columns else None
            )
            fig_scatter.update_layout(height=500)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Tracks table
        st.subheader("📋 Track Details")
        
        # Format the dataframe for better display
        display_df = df_tracks.copy()
        
        # Select columns to display (include new features if available)
        display_cols = ["track_name", "artist", "album"]
        feature_cols = ["popularity", "energy", "danceability", "valence", "tempo", "loudness"]
        display_cols.extend([col for col in feature_cols if col in display_df.columns])
        
        # Round numeric columns
        for col in display_df.columns:
            if col in ["danceability", "energy", "valence", "acousticness", "instrumentalness", "speechiness", "liveness"]:
                if col in display_df.columns:
                    display_df[col] = display_df[col].round(3)
            elif col in ["tempo", "loudness", "popularity"]:
                if col in display_df.columns:
                    display_df[col] = display_df[col].round(1)
        
        st.dataframe(
            display_df[display_cols],
            use_container_width=True,
            height=400
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
    sample_data = fetch_api_data("/api/tracks", {"limit": 500})
    
    if not sample_data or not sample_data["items"]:
        st.error("Unable to load sample data for statistics")
        return
    
    df_sample = pd.DataFrame(sample_data["items"])
    
    # Distribution charts for all audio features
    st.subheader("📊 Audio Feature Distributions")
    
    feature_to_plot = st.selectbox(
        "Select feature to visualize",
        ["energy", "danceability", "valence", "tempo", "loudness", "acousticness", 
         "instrumentalness", "speechiness", "popularity"]
    )
    
    if feature_to_plot in df_sample.columns:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.histogram(
                df_sample,
                x=feature_to_plot,
                nbins=30,
                title=f"Distribution of {feature_to_plot.replace('_', ' ').title()}",
                labels={feature_to_plot: feature_to_plot.replace('_', ' ').title()}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Show statistics for selected feature
            st.markdown(f"**{feature_to_plot.replace('_', ' ').title()} Stats:**")
            st.metric("Mean", f"{df_sample[feature_to_plot].mean():.3f}")
            st.metric("Median", f"{df_sample[feature_to_plot].median():.3f}")
            st.metric("Std Dev", f"{df_sample[feature_to_plot].std():.3f}")
            st.metric("Min", f"{df_sample[feature_to_plot].min():.3f}")
            st.metric("Max", f"{df_sample[feature_to_plot].max():.3f}")
    
    # Correlation heatmap
    st.subheader("🔥 Feature Correlation Heatmap")
    numeric_cols = ["energy", "danceability", "valence", "tempo", "loudness", 
                    "acousticness", "speechiness", "popularity"]
    available_cols = [col for col in numeric_cols if col in df_sample.columns and df_sample[col].notna().any()]
    
    if len(available_cols) > 1:
        corr_matrix = df_sample[available_cols].corr()
        fig_heatmap = px.imshow(
            corr_matrix,
            title="Correlation Matrix of Audio Features",
            color_continuous_scale="RdBu",
            aspect="auto",
            text_auto=".2f"
        )
        fig_heatmap.update_layout(height=500)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Summary statistics table
    st.subheader("📊 Complete Statistics Summary")
    
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