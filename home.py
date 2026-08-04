import streamlit as st
import subprocess
import sys
import os

# Page configuration
st.set_page_config(
    page_title="Restaurant Intelligence Hub - Home",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        margin-bottom: 3rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 3.5rem;
        margin: 0;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.3rem;
        margin: 1rem 0 0 0;
        opacity: 0.9;
    }
    
    .app-card {
        background: white;
        padding: 2.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 2rem 0;
        border: 2px solid transparent;
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .app-card:hover {
        border-color: #667eea;
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }
    
    .app-card h2 {
        color: #667eea;
        font-size: 2rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .app-card p {
        color: #6c757d;
        font-size: 1.1rem;
        line-height: 1.6;
        margin-bottom: 2rem;
    }
    
    .feature-list {
        text-align: left;
        margin: 1.5rem 0;
    }
    
    .feature-list li {
        margin: 0.5rem 0;
        color: #495057;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.8rem 2.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 2rem;
        color: #6c757d;
        border-top: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main navigation page."""
    
    # Reset button
    if st.button("🔄 Reset Selection", key="reset"):
        if 'app_choice' in st.session_state:
            del st.session_state.app_choice
        st.rerun()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🍽️ Restaurant Intelligence Hub</h1>
        <p>Choose your analysis platform to get started</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div class="app-card">
            <h2>🎯 ML Predictions</h2>
            <p>Advanced machine learning-powered restaurant location analysis with comprehensive insights and detailed reasoning.</p>
            <div class="feature-list">
                <ul>
                    <li>✅ AI-powered location scoring</li>
                    <li>✅ Interactive heatmaps</li>
                    <li>✅ Detailed market analysis</li>
                    <li>✅ Competition insights</li>
                    <li>✅ Export reports (CSV & HTML)</li>
                    <li>✅ Real-time recommendations</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Launch ML Predictions", key="ml_predictions"):
            st.session_state.app_choice = "ml_predictions"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="app-card">
            <h2>📊 Analytics Dashboard</h2>
            <p>Comprehensive analytics and insights platform for restaurant location data analysis and visualization.</p>
            <div class="feature-list">
                <ul>
                    <li>✅ Advanced data visualization</li>
                    <li>✅ Statistical analysis</li>
                    <li>✅ Trend identification</li>
                    <li>✅ Performance metrics</li>
                    <li>✅ Comparative analysis</li>
                    <li>✅ Custom reporting</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📈 Launch Analytics Dashboard", key="analytics"):
            st.session_state.app_choice = "analytics"
            st.rerun()
    
    # Handle app redirection
    if 'app_choice' in st.session_state:
        if st.session_state.app_choice == "ml_predictions":
            st.success("✅ Redirecting to ML Predictions...")
            
            # Import and run the ML predictions app
            try:
                import app
                st.markdown("### 🎯 ML Predictions App")
                app.main()
            except Exception as e:
                st.error(f"Error loading ML Predictions: {str(e)}")
                st.info("Please ensure app.py is in the same directory and contains a main() function.")
            
        elif st.session_state.app_choice == "analytics":
            st.success("✅ Redirecting to Analytics Dashboard...")
            
            # Import and run the analytics app
            try:
                import app2
                st.markdown("### 📊 Analytics Dashboard")
                app2.main()
            except Exception as e:
                st.error(f"Error loading Analytics Dashboard: {str(e)}")
                st.info("Please ensure app2.py is in the same directory and contains a main() function.")
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p><strong>Restaurant Intelligence Hub</strong> - Powered by Advanced Analytics & Machine Learning</p>
        <p>Choose the platform that best fits your analysis needs</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar information
    with st.sidebar:
        st.markdown("### 🏠 Navigation")
        st.markdown("""
        **Welcome to Restaurant Intelligence Hub!**
        
        This is your central navigation point to access our two powerful analysis platforms:
        
        **🎯 ML Predictions**
        - Machine learning-powered recommendations
        - Interactive maps and visualizations
        - Detailed insights and reasoning
        - Export capabilities
        
        **📊 Analytics Dashboard**
        - Comprehensive data analysis
        - Advanced visualizations
        - Statistical insights
        - Performance metrics
        
        Choose the platform that best suits your needs!
        """)
        
        st.markdown("### 📞 Support")
        st.markdown("""
        Need help choosing the right platform?
        
        - **ML Predictions**: For location recommendations
        - **Analytics Dashboard**: For data analysis
        
        Both platforms use the same underlying data but provide different analysis approaches.
        """)

if __name__ == "__main__":
    main()
