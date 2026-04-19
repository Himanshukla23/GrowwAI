import streamlit as st
import asyncio
import pandas as pd
from datetime import datetime
from src.phase2.app.schemas import RecommendationRequest
import os
from src.phase4.backend.services.orchestrator import run_recommendation_pipeline
from src.phase3.database import get_unique_locations, get_unique_cuisines, get_stats
from scripts.init_data import main as init_data

# Setup Database if missing
def handle_init_db():
    stats = get_stats()
    # If no records in database, auto-initialize
    if stats.get("record_count", 0) == 0:
        with st.status("📦 First-time setup: Initializing dataset from Hugging Face...", expanded=True) as status:
            try:
                init_data()
                status.update(label="✅ Dataset initialized successfully!", state="complete", expanded=False)
            except Exception as e:
                status.update(label=f"❌ Initialization failed: {str(e)}", state="error")

# Secrets Management (for Streamlit Cloud)
def sync_secrets():
    # If growing in Streamlit Cloud, move st.secrets to os.environ
    for key in ["GROQ_API_KEY", "GROQ_MODEL", "API_AUTH_TOKEN"]:
        if key in st.secrets and key not in os.environ:
            os.environ[key] = st.secrets[key]

handle_init_db()
sync_secrets()

# Page Configuration
st.set_page_config(
    page_title="The Curator | AI Restaurant Recommendations",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }
    .stApp {
        background-color: transparent;
    }
    .title-text {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: -webkit-linear-gradient(#f12711, #f5af19);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        margin-bottom: 20px;
        text-align: center;
    }
    .subtitle-text {
        color: #ddd;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 40px;
    }
    .restaurant-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .restaurant-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.08);
        border-color: #f5af19;
    }
    .badge {
        background: #f5af19;
        color: #000;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 10px;
    }
    .ai-explanation {
        font-style: italic;
        color: #ccc;
        border-left: 3px solid #f5af19;
        padding-left: 15px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="title-text">THE CURATOR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Premium AI-Powered Restaurant Discovery</p>', unsafe_allow_html=True)

    # Sidebar for filters
    with st.sidebar:
        st.header("🔍 Preferences")
        
        # Load unique values for dropdowns
        try:
            unique_locations = get_unique_locations()
            unique_cuisines = get_unique_cuisines()
        except Exception:
            unique_locations = ["New Delhi", "Gurgaon", "Noida", "Faridabad"]
            unique_cuisines = ["North Indian", "Chinese", "Italian", "Continental"]

        location = st.selectbox("Where are you?", unique_locations)
        cuisine = st.selectbox("What are you craving?", unique_cuisines)
        
        col1, col2 = st.columns(2)
        with col1:
            budget = st.selectbox("Budget", ["Low", "Medium", "High"])
        with col2:
            min_rating = st.slider("Min Rating", 1.0, 5.0, 3.5, 0.1)
            
        extra_preferences = st.text_area("Anything extra? (e.g., Rooftop, Pet-friendly)", placeholder="Tell the AI what you're looking for...")
        
        get_btn = st.button("✨ Get Recommendations", use_container_width=True)

    # Main Area
    if get_btn:
        with st.spinner("🤖 AI is curating the perfect spot for you..."):
            # Prepare request
            request = RecommendationRequest(
                location=location,
                cuisine=cuisine,
                budget=budget.lower(),
                min_rating=float(min_rating),
                extra_preferences=str(extra_preferences or "")
            )
            
            # Execute pipeline
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                results = loop.run_until_complete(run_recommendation_pipeline(request))
                recs = results.get("recommendations", [])
                
                if not recs:
                    st.warning("😔 No restaurants matched your criteria. Try loosening your filters!")
                else:
                    st.success(f"Found {len(recs)} amazing matches for you!")
                    
                    for i, rec in enumerate(recs):
                        with st.container():
                            st.markdown(f"""
                            <div class="restaurant-card">
                                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                    <h3 style="margin-top: 0; color: #f5af19;">{i+1}. {rec.name}</h3>
                                    <span class="badge">⭐ {rec.rating}</span>
                                </div>
                                <div style="display: flex; gap: 15px; color: #888; font-size: 0.9rem; margin-bottom: 10px;">
                                    <span>📍 {rec.location}</span>
                                    <span>🍳 {rec.cuisine}</span>
                                    <span>💰 {rec.cost}</span>
                                </div>
                                <div class="ai-explanation">
                                    {rec.reason}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error calling AI Service: {str(e)}")
            finally:
                loop.close()

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.8rem;">
            Powered by Groq Llama 3.1 8B • Phase 4 Orchestration
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
