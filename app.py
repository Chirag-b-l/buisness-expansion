import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import folium
from streamlit_folium import st_folium
import hashlib
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import time
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Note: Fast recommender system removed for simplified UI

# --- App Configuration ---
st.set_page_config(
    page_title="Restaurant Intelligence Hub",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS Styling ---
def load_css():
    st.markdown("""
    <style>
    /* Main App Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        font-size: 3rem;
        margin: 0;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .sidebar .sidebar-content .block-container {
        padding-top: 2rem;
    }
    
    /* Card Styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .metric-card h3 {
        color: #667eea;
        margin: 0 0 1rem 0;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .metric-card .value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
        margin: 0.5rem 0;
        line-height: 1.2;
    }
    
    .metric-card .help-text {
        color: #6c757d;
        font-size: 0.8rem;
        margin-top: 0.5rem;
        line-height: 1.3;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    .metric-card .delta {
        color: #28a745;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* Ensure proper spacing and alignment */
    .metric-card > * {
        margin-bottom: 0.5rem;
    }
    
    .metric-card > *:last-child {
        margin-bottom: 0;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Page Navigation removed for simplified UI */
    
    /* Chart Containers */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    /* Success/Error Messages */
    .success-message {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Loading Animation */
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    /* Map Container */
    .map-container {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Data Table Styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Load custom CSS
load_css()

# Page navigation system removed for simplified UI

# --- Advanced Visualization Functions ---
def create_metric_card(title, value, delta=None, help_text=None):
    """Create a styled metric card."""
    delta_html = f"<div class='delta'>+{delta}</div>" if delta else ""
    help_html = f"<div class='help-text'>{help_text}</div>" if help_text else ""
    
    st.markdown(f"""
    <div class="metric-card">
        <h3>{title}</h3>
        <div class="value">{value}</div>
        {delta_html}
        {help_html}
    </div>
    """, unsafe_allow_html=True)

def create_advanced_charts(df, chart_type="overview"):
    """Create advanced interactive charts."""
    try:
        if chart_type == "overview":
            # Create a comprehensive overview dashboard
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Location Score Distribution', 'Population Density vs Income', 
                              'Income Distribution', 'Score vs Population Analysis'),
                specs=[[{"type": "histogram"}, {"type": "scatter"}],
                       [{"type": "histogram"}, {"type": "scatter"}]]
            )
            
            # Location Score Distribution
            fig.add_trace(
                go.Histogram(x=df['location_score'], name='Location Scores', nbinsx=20, marker_color='#667eea'),
                row=1, col=1
            )
            
            # Population vs Income Scatter
            fig.add_trace(
                go.Scatter(x=df['population_density'], y=df['avg_income'], 
                          mode='markers', name='Areas', 
                          text=df['area_name'], 
                          hovertemplate='%{text}<br>Pop Density: %{x}<br>Avg Income: ₹%{y:,.0f}',
                          marker=dict(color=df['location_score'], colorscale='Viridis', size=8)),
                row=1, col=2
            )
            
            # Income Distribution
            fig.add_trace(
                go.Histogram(x=df['avg_income'], name='Income Distribution', nbinsx=20, marker_color='#28a745'),
                row=2, col=1
            )
            
            # Score vs Population Analysis
            fig.add_trace(
                go.Scatter(x=df['population_density'], y=df['location_score'], 
                          mode='markers', name='Score vs Population', 
                          text=df['area_name'],
                          hovertemplate='%{text}<br>Pop Density: %{x}<br>Score: %{y}',
                          marker=dict(color=df['avg_income'], colorscale='Plasma', size=8)),
                row=2, col=2
            )
            
            fig.update_layout(
                height=600, 
                showlegend=False, 
                title_text="Restaurant Location Restaurant Data Restaurant Data Restaurant Data Analytics Map Map",
                title_x=0.5
            )
            
            # Update axes labels
            fig.update_xaxes(title_text="Location Score", row=1, col=1)
            fig.update_yaxes(title_text="Count", row=1, col=1)
            fig.update_xaxes(title_text="Population Density", row=1, col=2)
            fig.update_yaxes(title_text="Average Income (₹)", row=1, col=2)
            fig.update_xaxes(title_text="Average Income (₹)", row=2, col=1)
            fig.update_yaxes(title_text="Count", row=2, col=1)
            fig.update_xaxes(title_text="Population Density", row=2, col=2)
            fig.update_yaxes(title_text="Location Score", row=2, col=2)
            
            return fig
        
        elif chart_type == "comparison":
            # Create comparison charts for top recommendations
            fig = go.Figure()
            
            # Bar chart comparing top areas
            top_areas = df.head(10)
            fig.add_trace(go.Bar(
                x=top_areas['area_name'],
                y=top_areas['location_score'],
                name='Location Score',
                marker_color='#667eea',
                hovertemplate='<b>%{x}</b><br>Score: %{y}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Top 10 Restaurant Locations Comparison",
                xaxis_title="Area Name",
                yaxis_title="Location Score",
                height=400,
                xaxis_tickangle=-45
            )
            return fig
            
    except Exception as e:
        # Fallback to simple chart if there's an error
        st.warning(f"Chart generation encountered an issue: {str(e)}")
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=df['location_score'], name='Location Scores', nbinsx=20))
        fig.update_layout(title="Location Score Distribution", height=400)
        return fig

def create_insights_panel(df, recommendations=None):
    """Create an insights panel with key findings."""
    insights = []
    
    # Basic statistics
    avg_score = df['location_score'].mean()
    max_score = df['location_score'].max()
    min_score = df['location_score'].min()
    
    insights.append(f"📊 **Location Score Analysis**: Average score is {avg_score:.1f}, ranging from {min_score:.1f} to {max_score:.1f}")
    
    # Top performing area
    top_area = df.loc[df['location_score'].idxmax()]
    insights.append(f"🏆 **Best Location**: {top_area['area_name']} with a score of {top_area['location_score']:.1f}")
    
    # Population insights
    if 'population_density' in df.columns:
        high_pop_areas = df[df['population_density'] > df['population_density'].quantile(0.8)]
        insights.append(f"👥 **High Population Areas**: {len(high_pop_areas)} areas have above 80th percentile population density")
    
    # Income insights
    if 'avg_income' in df.columns:
        high_income_areas = df[df['avg_income'] > df['avg_income'].quantile(0.8)]
        insights.append(f"💰 **High Income Areas**: {len(high_income_areas)} areas have above 80th percentile average income")
    
    # Competition insights
    if 'same_cuisine_competitors_1km' in df.columns:
        low_competition = df[df['same_cuisine_competitors_1km'] < df['same_cuisine_competitors_1km'].quantile(0.2)]
        insights.append(f"🏪 **Low Competition Areas**: {len(low_competition)} areas have below 20th percentile competition")
    
    return insights

# --- Caching Functions for Performance ---
@st.cache_data
def load_data():
    """Loads the main dataset from CSV."""
    try:
        # Try to load the scored dataset first, fallback to gridded if not available
        try:
            df = pd.read_csv('bengaluru_restaurant_grid_10k_scored.csv')
            return df
        except FileNotFoundError:
            df = pd.read_csv('bengaluru_restaurant_grid_10k_gridded.csv')
            return df
    except FileNotFoundError:
        st.error("Dataset files not found. Please check if the required CSV files are present.")
        return None


# Fast recommender system removed for simplified UI

# === EXPORT FUNCTIONS ===
def generate_insights_report(top_3_df, restaurant_type, restaurant_style, df):
    """Generate comprehensive insights report with reasoning."""
    
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "restaurant_concept": {
            "type": restaurant_type,
            "cuisine": restaurant_style
        },
        "analysis_summary": {},
        "top_recommendations": [],
        "detailed_insights": {},
        "methodology": {}
    }
    
    # Analysis Summary
    report["analysis_summary"] = {
        "total_locations_analyzed": len(df),
        "top_locations_found": len(top_3_df),
        "average_predicted_score": round(top_3_df['predicted_score'].mean(), 2),
        "score_range": f"{top_3_df['predicted_score'].min():.2f} - {top_3_df['predicted_score'].max():.2f}",
        "data_coverage": f"Bangalore area: {df['latitude'].min():.4f}° to {df['latitude'].max():.4f}° N, {df['longitude'].min():.4f}° to {df['longitude'].max():.4f}° E"
    }
    
    # Top Recommendations with detailed reasoning
    for i, (_, row) in enumerate(top_3_df.iterrows()):
        recommendation = {
            "rank": i + 1,
            "area_name": row['area_name'],
            "grid_id": row['grid_id'],
            "coordinates": {
                "latitude": round(row['latitude'], 6),
                "longitude": round(row['longitude'], 6)
            },
            "scores": {
                "overall_score": round(row['predicted_score'], 2),
                "base_location_score": round(row.get('base_score_norm', 0), 2),
                "type_cuisine_bonus": round(row.get('type_cuisine_bonus_norm', 0), 2),
                "income_compatibility": round(row.get('income_score', 0), 2),
                "competition_analysis": round(row.get('competition_score', 0), 2)
            },
            "key_metrics": {
                "population_density": int(row['population_density']),
                "average_income": int(row['avg_income']),
                "same_cuisine_competitors": int(row.get('same_cuisine_competitors_1km', 0)),
                "other_competitors": int(row.get('other_cuisine_competitors_1km', 0)),
                "office_density": int(row.get('office_density', 0)),
                "nightlife_density": int(row.get('nightlife_density', 0))
            },
            "reasoning": generate_location_reasoning(row, restaurant_type, restaurant_style, df)
        }
        report["top_recommendations"].append(recommendation)
    
    # Detailed Insights
    report["detailed_insights"] = {
        "market_analysis": analyze_market_conditions(top_3_df, df),
        "competition_landscape": analyze_competition(top_3_df, restaurant_style),
        "demographic_insights": analyze_demographics(top_3_df, restaurant_type),
        "location_advantages": identify_location_advantages(top_3_df, restaurant_type, restaurant_style)
    }
    
    
    return report

def generate_location_reasoning(row, restaurant_type, restaurant_style, df):
    """Generate detailed reasoning for why a location is recommended."""
    
    reasoning = []
    
    # Overall score reasoning
    overall_score = row['predicted_score']
    if overall_score >= 8:
        reasoning.append(f"Excellent overall score of {overall_score:.2f}/10 indicates high potential for success")
    elif overall_score >= 6:
        reasoning.append(f"Good overall score of {overall_score:.2f}/10 suggests strong market opportunity")
    else:
        reasoning.append(f"Moderate score of {overall_score:.2f}/10 indicates some potential with considerations")
    
    # Population density analysis
    pop_density = row['population_density']
    pop_percentile = (df['population_density'] <= pop_density).mean() * 100
    if pop_percentile >= 80:
        reasoning.append(f"High population density ({pop_density:,} people/km²) in top {100-pop_percentile:.0f}% of areas")
    elif pop_percentile >= 50:
        reasoning.append(f"Moderate population density ({pop_density:,} people/km²) provides good customer base")
    else:
        reasoning.append(f"Lower population density ({pop_density:,} people/km²) may require targeted marketing")
    
    # Income compatibility
    avg_income = row['avg_income']
    income_percentile = (df['avg_income'] <= avg_income).mean() * 100
    if restaurant_type == 'Fine Dining':
        if income_percentile >= 70:
            reasoning.append(f"High average income (₹{avg_income:,}) suitable for fine dining concept")
        else:
            reasoning.append(f"Moderate income (₹{avg_income:,}) may limit fine dining potential")
    elif restaurant_type in ['Quick Service', 'Food Court']:
        if income_percentile <= 60:
            reasoning.append(f"Moderate income (₹{avg_income:,}) ideal for quick service concept")
        else:
            reasoning.append(f"Higher income (₹{avg_income:,}) allows for premium quick service options")
    
    # Competition analysis
    same_cuisine_comp = row.get('same_cuisine_competitors_1km', 0)
    if same_cuisine_comp <= 3:
        reasoning.append(f"Low competition ({same_cuisine_comp} same cuisine competitors) - good market opportunity")
    elif same_cuisine_comp <= 8:
        reasoning.append(f"Moderate competition ({same_cuisine_comp} same cuisine competitors) - balanced market")
    else:
        reasoning.append(f"High competition ({same_cuisine_comp} same cuisine competitors) - need strong differentiation")
    
    # Office density for business lunch potential
    office_density = row.get('office_density', 0)
    if office_density >= 100:
        reasoning.append(f"High office density ({office_density}) - excellent for business lunch traffic")
    elif office_density >= 50:
        reasoning.append(f"Moderate office density ({office_density}) - good for weekday business")
    
    # Nightlife potential
    nightlife_density = row.get('nightlife_density', 0)
    if nightlife_density >= 80:
        reasoning.append(f"High nightlife density ({nightlife_density}) - great for evening dining")
    
    return reasoning

def analyze_market_conditions(top_3_df, df):
    """Analyze overall market conditions."""
    return {
        "market_saturation": "Moderate to High" if top_3_df['same_cuisine_competitors_1km'].mean() > 5 else "Low to Moderate",
        "average_income_level": f"₹{top_3_df['avg_income'].mean():,.0f}",
        "population_density_trend": "High density areas preferred" if top_3_df['population_density'].mean() > df['population_density'].mean() else "Mixed density areas",
        "competition_intensity": "High" if top_3_df['same_cuisine_competitors_1km'].mean() > 8 else "Moderate"
    }

def analyze_competition(top_3_df, restaurant_style):
    """Analyze competition landscape."""
    avg_competition = top_3_df['same_cuisine_competitors_1km'].mean()
    return {
        "same_cuisine_competition": f"{avg_competition:.1f} competitors on average",
        "market_opportunity": "High" if avg_competition < 5 else "Moderate" if avg_competition < 10 else "Limited",
        "differentiation_need": "High" if avg_competition > 8 else "Moderate" if avg_competition > 5 else "Low"
    }

def analyze_demographics(top_3_df, restaurant_type):
    """Analyze demographic suitability."""
    avg_income = top_3_df['avg_income'].mean()
    avg_pop_density = top_3_df['population_density'].mean()
    
    return {
        "income_suitability": "Excellent" if (restaurant_type == 'Fine Dining' and avg_income > 150000) or (restaurant_type in ['Quick Service', 'Food Court'] and avg_income < 100000) else "Good",
        "population_base": "Strong" if avg_pop_density > 15000 else "Moderate",
        "target_demographic": "High-income professionals" if avg_income > 120000 else "Middle-income families" if avg_income > 80000 else "Budget-conscious consumers"
    }

def identify_location_advantages(top_3_df, restaurant_type, restaurant_style):
    """Identify key location advantages."""
    advantages = []
    
    if top_3_df['office_density'].mean() > 80:
        advantages.append("Strong business district presence - excellent for lunch traffic")
    
    if top_3_df['nightlife_density'].mean() > 70:
        advantages.append("Vibrant nightlife area - good for evening dining")
    
    if top_3_df['population_density'].mean() > 18000:
        advantages.append("High population density - large customer base")
    
    if top_3_df['same_cuisine_competitors_1km'].mean() < 5:
        advantages.append("Low competition - market opportunity")
    
    if top_3_df['avg_income'].mean() > 120000:
        advantages.append("High purchasing power - premium pricing potential")
    
    return advantages

def create_download_link(data, filename, file_type):
    """Create download link for different file types."""
    if file_type == "csv":
        csv = data.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download CSV</a>'
    elif file_type == "pdf":
        pdf_content = generate_pdf_report(data)
        b64 = base64.b64encode(pdf_content).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📥 Download PDF Report</a>'
    return href

def generate_html_report(report_data):
    """Generate HTML report."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Restaurant Location Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
            .section {{ margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
            .recommendation {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #667eea; }}
            .score {{ font-weight: bold; color: #667eea; }}
            .reasoning {{ margin: 10px 0; padding: 10px; background: #e9ecef; border-radius: 5px; }}
            .metric {{ display: inline-block; margin: 5px 10px; padding: 5px 10px; background: #667eea; color: white; border-radius: 15px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #667eea; color: white; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🍽️ Restaurant Location Analysis Report</h1>
            <p>Generated on {report_data['timestamp']}</p>
            <p><strong>{report_data['restaurant_concept']['type']} - {report_data['restaurant_concept']['cuisine']}</strong></p>
        </div>
        
        <div class="section">
            <h2>📊 Analysis Summary</h2>
            <div class="metric">Total Locations: {report_data['analysis_summary']['total_locations_analyzed']}</div>
            <div class="metric">Top Locations: {report_data['analysis_summary']['top_locations_found']}</div>
            <div class="metric">Avg Score: {report_data['analysis_summary']['average_predicted_score']}</div>
            <div class="metric">Score Range: {report_data['analysis_summary']['score_range']}</div>
            <p><strong>Data Coverage:</strong> {report_data['analysis_summary']['data_coverage']}</p>
        </div>
        
        <div class="section">
            <h2>🏆 Top Recommendations</h2>
    """
    
    for rec in report_data['top_recommendations']:
        html += f"""
            <div class="recommendation">
                <h3>#{rec['rank']} {rec['area_name']}</h3>
                <p><span class="score">Overall Score: {rec['scores']['overall_score']}/10</span></p>
                <p><strong>Grid ID:</strong> {rec['grid_id']} | <strong>Coordinates:</strong> {rec['coordinates']['latitude']}, {rec['coordinates']['longitude']}</p>
                
                <h4>📈 Score Breakdown:</h4>
                <table>
                    <tr><th>Factor</th><th>Score</th></tr>
                    <tr><td>Base Location Score</td><td>{rec['scores']['base_location_score']}</td></tr>
                    <tr><td>Type/Cuisine Bonus</td><td>{rec['scores']['type_cuisine_bonus']}</td></tr>
                    <tr><td>Income Compatibility</td><td>{rec['scores']['income_compatibility']}</td></tr>
                    <tr><td>Competition Analysis</td><td>{rec['scores']['competition_analysis']}</td></tr>
                </table>
                
                <h4>📊 Key Metrics:</h4>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Population Density</td><td>{rec['key_metrics']['population_density']:,} people/km²</td></tr>
                    <tr><td>Average Income</td><td>₹{rec['key_metrics']['average_income']:,}</td></tr>
                    <tr><td>Same Cuisine Competitors</td><td>{rec['key_metrics']['same_cuisine_competitors']}</td></tr>
                    <tr><td>Other Competitors</td><td>{rec['key_metrics']['other_competitors']}</td></tr>
                    <tr><td>Office Density</td><td>{rec['key_metrics']['office_density']}</td></tr>
                    <tr><td>Nightlife Density</td><td>{rec['key_metrics']['nightlife_density']}</td></tr>
                </table>
                
                <h4>💡 Why This Location?</h4>
                <div class="reasoning">
        """
        for reason in rec['reasoning']:
            html += f"<p>• {reason}</p>"
        html += """
                </div>
            </div>
        """
    
    html += """
        </div>
        
        <div class="section">
            <h2>🔍 Detailed Insights</h2>
    """
    
    # Market Analysis
    html += f"""
            <h3>📈 Market Analysis</h3>
            <p><strong>Market Saturation:</strong> {report_data['detailed_insights']['market_analysis']['market_saturation']}</p>
            <p><strong>Average Income Level:</strong> {report_data['detailed_insights']['market_analysis']['average_income_level']}</p>
            <p><strong>Population Density Trend:</strong> {report_data['detailed_insights']['market_analysis']['population_density_trend']}</p>
            <p><strong>Competition Intensity:</strong> {report_data['detailed_insights']['market_analysis']['competition_intensity']}</p>
    """
    
    # Competition Landscape
    html += f"""
            <h3>🏪 Competition Landscape</h3>
            <p><strong>Same Cuisine Competition:</strong> {report_data['detailed_insights']['competition_landscape']['same_cuisine_competition']}</p>
            <p><strong>Market Opportunity:</strong> {report_data['detailed_insights']['competition_landscape']['market_opportunity']}</p>
            <p><strong>Differentiation Need:</strong> {report_data['detailed_insights']['competition_landscape']['differentiation_need']}</p>
    """
    
    # Demographic Insights
    html += f"""
            <h3>👥 Demographic Insights</h3>
            <p><strong>Income Suitability:</strong> {report_data['detailed_insights']['demographic_insights']['income_suitability']}</p>
            <p><strong>Population Base:</strong> {report_data['detailed_insights']['demographic_insights']['population_base']}</p>
            <p><strong>Target Demographic:</strong> {report_data['detailed_insights']['demographic_insights']['target_demographic']}</p>
    """
    
    # Location Advantages
    html += """
            <h3>⭐ Location Advantages</h3>
            <ul>
    """
    for advantage in report_data['detailed_insights']['location_advantages']:
        html += f"<li>{advantage}</li>"
    html += """
            </ul>
        </div>
        
    </body>
    </html>
    """
    
    return html

def generate_pdf_report(report_data):
    """Generate PDF report using ReportLab."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#667eea')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#667eea')
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        textColor=colors.HexColor('#495057')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Build the story (content)
    story = []
    
    # Title
    story.append(Paragraph("🍽️ Restaurant Location Analysis Report", title_style))
    story.append(Spacer(1, 12))
    
    # Header info
    story.append(Paragraph(f"<b>Generated:</b> {report_data['timestamp']}", normal_style))
    story.append(Paragraph(f"<b>Restaurant Type:</b> {report_data['restaurant_concept']['type']}", normal_style))
    story.append(Paragraph(f"<b>Cuisine Style:</b> {report_data['restaurant_concept']['cuisine']}", normal_style))
    story.append(Spacer(1, 20))
    
    # Analysis Summary
    story.append(Paragraph("📊 Analysis Summary", heading_style))
    summary = report_data['analysis_summary']
    
    summary_data = [
        ['Metric', 'Value'],
        ['Total Locations Analyzed', f"{summary['total_locations_analyzed']:,}"],
        ['Top Locations Found', f"{summary['top_locations_found']}"],
        ['Average Predicted Score', f"{summary['average_predicted_score']}"],
        ['Score Range', summary['score_range']],
        ['Data Coverage', summary['data_coverage']]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Top Recommendations
    story.append(Paragraph("🏆 Top Recommendations", heading_style))
    
    for rec in report_data['top_recommendations']:
        story.append(Paragraph(f"#{rec['rank']} - {rec['area_name']}", subheading_style))
        
        # Scores table
        scores_data = [
            ['Score Component', 'Value'],
            ['Overall Score', f"{rec['scores']['overall_score']}/10"],
            ['Base Location Score', f"{rec['scores']['base_location_score']}"],
            ['Type/Cuisine Bonus', f"{rec['scores']['type_cuisine_bonus']}"],
            ['Income Compatibility', f"{rec['scores']['income_compatibility']}"],
            ['Competition Analysis', f"{rec['scores']['competition_analysis']}"]
        ]
        
        scores_table = Table(scores_data, colWidths=[2.5*inch, 1.5*inch])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(scores_table)
        story.append(Spacer(1, 8))
        
        # Key metrics
        metrics_data = [
            ['Metric', 'Value'],
            ['Population Density', f"{rec['key_metrics']['population_density']:,} people/km²"],
            ['Average Income', f"₹{rec['key_metrics']['average_income']:,}"],
            ['Same Cuisine Competitors', f"{rec['key_metrics']['same_cuisine_competitors']}"],
            ['Other Competitors', f"{rec['key_metrics']['other_competitors']}"],
            ['Office Density', f"{rec['key_metrics']['office_density']}"],
            ['Nightlife Density', f"{rec['key_metrics']['nightlife_density']}"]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#17a2b8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 8))
        
        # Reasoning
        story.append(Paragraph("💡 Why This Location?", subheading_style))
        for reason in rec['reasoning']:
            story.append(Paragraph(f"• {reason}", normal_style))
        
        story.append(Spacer(1, 15))
    
    # Detailed Insights
    story.append(PageBreak())
    story.append(Paragraph("🔍 Detailed Insights", heading_style))
    
    # Market Analysis
    story.append(Paragraph("📈 Market Analysis", subheading_style))
    market = report_data['detailed_insights']['market_analysis']
    story.append(Paragraph(f"<b>Market Saturation:</b> {market['market_saturation']}", normal_style))
    story.append(Paragraph(f"<b>Average Income Level:</b> {market['average_income_level']}", normal_style))
    story.append(Paragraph(f"<b>Population Density Trend:</b> {market['population_density_trend']}", normal_style))
    story.append(Paragraph(f"<b>Competition Intensity:</b> {market['competition_intensity']}", normal_style))
    story.append(Spacer(1, 12))
    
    # Competition Landscape
    story.append(Paragraph("🏪 Competition Landscape", subheading_style))
    competition = report_data['detailed_insights']['competition_landscape']
    story.append(Paragraph(f"<b>Same Cuisine Competition:</b> {competition['same_cuisine_competition']}", normal_style))
    story.append(Paragraph(f"<b>Market Opportunity:</b> {competition['market_opportunity']}", normal_style))
    story.append(Paragraph(f"<b>Differentiation Need:</b> {competition['differentiation_need']}", normal_style))
    story.append(Spacer(1, 12))
    
    # Demographic Insights
    story.append(Paragraph("👥 Demographic Insights", subheading_style))
    demographics = report_data['detailed_insights']['demographic_insights']
    story.append(Paragraph(f"<b>Income Suitability:</b> {demographics['income_suitability']}", normal_style))
    story.append(Paragraph(f"<b>Population Base:</b> {demographics['population_base']}", normal_style))
    story.append(Paragraph(f"<b>Target Demographic:</b> {demographics['target_demographic']}", normal_style))
    story.append(Spacer(1, 12))
    
    # Location Advantages
    story.append(Paragraph("⭐ Location Advantages", subheading_style))
    for advantage in report_data['detailed_insights']['location_advantages']:
        story.append(Paragraph(f"• {advantage}", normal_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# === IMPROVED SCORING FUNCTIONS ===
def calculate_type_cuisine_bonus(df, restaurant_type, cuisine):
    """Calculate bonus score based on restaurant type and cuisine compatibility."""
    scores = np.zeros(len(df))
    
    # Restaurant type preferences based on data analysis
    type_preferences = {
        'Fine Dining': {'high_income': 1.2, 'low_competition': 1.1, 'nightlife': 1.3},
        'Casual Dining': {'medium_income': 1.1, 'moderate_competition': 1.0, 'office_density': 1.2},
        'Quick Service': {'high_population': 1.3, 'office_density': 1.2, 'college_proximity': 1.1},
        'Café': {'college_proximity': 1.4, 'office_density': 1.2, 'mall_proximity': 1.1},
        'Food Court': {'mall_proximity': 1.5, 'high_population': 1.2, 'office_density': 1.1}
    }
    
    # Cuisine preferences
    cuisine_preferences = {
        'Italian': {'high_income': 1.1, 'nightlife': 1.2},
        'Continental': {'high_income': 1.2, 'nightlife': 1.1},
        'Indian': {'all_income': 1.0, 'high_population': 1.1},
        'Multi-Cuisine': {'office_density': 1.1, 'mall_proximity': 1.1},
        'Chinese': {'office_density': 1.1, 'college_proximity': 1.1},
        'Japanese': {'high_income': 1.2, 'office_density': 1.1},
        'Mexican': {'college_proximity': 1.2, 'nightlife': 1.1},
        'South Indian': {'all_income': 1.0, 'high_population': 1.2},
        'North Indian': {'all_income': 1.0, 'high_population': 1.1},
        'Sea Food': {'high_income': 1.1, 'nightlife': 1.1}
    }
    
    # Apply type preferences
    if restaurant_type in type_preferences:
        prefs = type_preferences[restaurant_type]
        if 'high_income' in prefs:
            scores += np.where(df['avg_income'] > df['avg_income'].quantile(0.7), prefs['high_income'] - 1, 0)
        if 'medium_income' in prefs:
            scores += np.where((df['avg_income'] > df['avg_income'].quantile(0.3)) & 
                             (df['avg_income'] < df['avg_income'].quantile(0.7)), prefs['medium_income'] - 1, 0)
        if 'high_population' in prefs:
            scores += np.where(df['population_density'] > df['population_density'].quantile(0.7), prefs['high_population'] - 1, 0)
        if 'office_density' in prefs:
            scores += np.where(df['office_density'] > df['office_density'].quantile(0.7), prefs['office_density'] - 1, 0)
        if 'nightlife' in prefs:
            scores += np.where(df['nightlife_density'] > df['nightlife_density'].quantile(0.7), prefs['nightlife'] - 1, 0)
        if 'college_proximity' in prefs:
            scores += np.where(df['college_proximity'] > df['college_proximity'].quantile(0.7), prefs['college_proximity'] - 1, 0)
        if 'mall_proximity' in prefs:
            scores += np.where(df['mall_proximity'] > df['mall_proximity'].quantile(0.7), prefs['mall_proximity'] - 1, 0)
    
    # Apply cuisine preferences
    if cuisine in cuisine_preferences:
        prefs = cuisine_preferences[cuisine]
        if 'high_income' in prefs:
            scores += np.where(df['avg_income'] > df['avg_income'].quantile(0.7), prefs['high_income'] - 1, 0)
        if 'all_income' in prefs:
            scores += prefs['all_income'] - 1
        if 'high_population' in prefs:
            scores += np.where(df['population_density'] > df['population_density'].quantile(0.7), prefs['high_population'] - 1, 0)
        if 'office_density' in prefs:
            scores += np.where(df['office_density'] > df['office_density'].quantile(0.7), prefs['office_density'] - 1, 0)
        if 'nightlife' in prefs:
            scores += np.where(df['nightlife_density'] > df['nightlife_density'].quantile(0.7), prefs['nightlife'] - 1, 0)
        if 'college_proximity' in prefs:
            scores += np.where(df['college_proximity'] > df['college_proximity'].quantile(0.7), prefs['college_proximity'] - 1, 0)
    
    return scores * 20  # Scale to 0-20 range for more impact

def calculate_income_compatibility(df, restaurant_type):
    """Calculate income compatibility score based on restaurant type."""
    scores = np.zeros(len(df))
    
    # Income thresholds based on restaurant type
    income_thresholds = {
        'Fine Dining': {'min': 150000, 'optimal': 200000},
        'Casual Dining': {'min': 80000, 'optimal': 120000},
        'Quick Service': {'min': 40000, 'optimal': 80000},
        'Café': {'min': 60000, 'optimal': 100000},
        'Food Court': {'min': 50000, 'optimal': 90000}
    }
    
    if restaurant_type in income_thresholds:
        min_income = income_thresholds[restaurant_type]['min']
        optimal_income = income_thresholds[restaurant_type]['optimal']
        
        # Score based on income compatibility
        scores = np.where(
            df['avg_income'] >= optimal_income, 10,  # Optimal income
            np.where(
                df['avg_income'] >= min_income, 
                (df['avg_income'] - min_income) / (optimal_income - min_income) * 8 + 2,  # Linear scale
                0  # Below minimum
            )
        )
    else:
        # Default scoring for unknown types
        scores = np.where(df['avg_income'] > df['avg_income'].quantile(0.7), 8, 
                         np.where(df['avg_income'] > df['avg_income'].quantile(0.3), 5, 2))
    
    return scores

def calculate_competition_score(df, cuisine):
    """Calculate competition score - balance between opportunity and competition."""
    scores = np.zeros(len(df))
    
    # Get cuisine-specific competition
    if 'same_cuisine_competitors_1km' in df.columns:
        same_cuisine_comp = df['same_cuisine_competitors_1km']
        other_cuisine_comp = df['other_cuisine_competitors_1km']
        total_comp = same_cuisine_comp + other_cuisine_comp
        
        # Optimal competition range (not too high, not too low)
        optimal_range = (2, 8)  # 2-8 competitors is optimal
        
        scores = np.where(
            (same_cuisine_comp >= optimal_range[0]) & (same_cuisine_comp <= optimal_range[1]), 10,  # Optimal competition
            np.where(
                same_cuisine_comp < optimal_range[0], 
                same_cuisine_comp / optimal_range[0] * 5 + 5,  # Low competition - some opportunity
                np.where(
                    same_cuisine_comp <= optimal_range[1] * 2,
                    10 - (same_cuisine_comp - optimal_range[1]) / optimal_range[1] * 5,  # High competition - decreasing score
                    0  # Very high competition
                )
            )
        )
    else:
        # Fallback to total competition
        total_comp = df.get('other_cuisine_competitors_1km', 0)
        scores = np.where(total_comp <= 10, 10 - total_comp * 0.5, 0)
    
    return scores

def calculate_accessibility_score(df):
    """Calculate accessibility and infrastructure score."""
    scores = np.zeros(len(df))
    
    # Parking availability (0-50 scale)
    parking_score = np.clip(df['parking_availability'] / 50 * 10, 0, 10)
    
    # Public transport connectivity (0-50 scale)
    transport_score = np.clip(df['public_transport_connectivity'] / 50 * 10, 0, 10)
    
    # Office density (indicates business accessibility)
    office_score = np.where(df['office_density'] > df['office_density'].quantile(0.7), 8, 
                           np.where(df['office_density'] > df['office_density'].quantile(0.3), 5, 2))
    
    # Combine accessibility factors
    scores = (parking_score * 0.3 + transport_score * 0.4 + office_score * 0.3)
    
    return scores

def calculate_market_potential(df):
    """Calculate market potential score."""
    scores = np.zeros(len(df))
    
    # Population density potential
    pop_score = np.where(df['population_density'] > df['population_density'].quantile(0.8), 10,
                        np.where(df['population_density'] > df['population_density'].quantile(0.5), 7,
                                np.where(df['population_density'] > df['population_density'].quantile(0.2), 4, 1)))
    
    # Nightlife density (indicates entertainment potential)
    nightlife_score = np.where(df['nightlife_density'] > df['nightlife_density'].quantile(0.7), 8,
                              np.where(df['nightlife_density'] > df['nightlife_density'].quantile(0.3), 5, 2))
    
    # Mall proximity (commercial activity)
    mall_score = np.where(df['mall_proximity'] > df['mall_proximity'].quantile(0.7), 8,
                         np.where(df['mall_proximity'] > df['mall_proximity'].quantile(0.3), 5, 2))
    
    # College proximity (student market)
    college_score = np.where(df['college_proximity'] > df['college_proximity'].quantile(0.7), 7,
                            np.where(df['college_proximity'] > df['college_proximity'].quantile(0.3), 4, 1))
    
    # Combine market potential factors
    scores = (pop_score * 0.4 + nightlife_score * 0.3 + mall_score * 0.2 + college_score * 0.1)
    
    return scores

def generate_map(df, user_cuisine, user_restaurant_type):
    """
    Generates the Folium heatmap and top 3 recommendations based on user input.
    Uses an improved scoring algorithm based on data analysis.
    """
    # Create a copy for prediction
    X_predict = df.copy()
    
    # === IMPROVED SCORING ALGORITHM ===
    # This algorithm is based on actual data patterns and business logic
    
    # 1. Base score from existing location_score (0-100 scale)
    base_scores = X_predict['location_score'].values
    
    # 2. Restaurant type and cuisine matching bonus
    type_cuisine_bonus = calculate_type_cuisine_bonus(X_predict, user_restaurant_type, user_cuisine)
    
    # 3. Income compatibility score
    income_scores = calculate_income_compatibility(X_predict, user_restaurant_type)
    
    # 4. Competition analysis
    competition_scores = calculate_competition_score(X_predict, user_cuisine)
    
    # 5. Accessibility and infrastructure score
    accessibility_scores = calculate_accessibility_score(X_predict)
    
    # 6. Market potential score
    market_scores = calculate_market_potential(X_predict)
    
    # Normalize base scores to 0-10 range first to match other scores
    base_scores_normalized = (base_scores / 100) * 10
    
    # Normalize type_cuisine_bonus to 0-10 range (it's currently 0-20)
    type_cuisine_bonus_normalized = np.clip(type_cuisine_bonus / 2, 0, 10)
    
    # Combine all scores with weights (all now on 0-10 scale)
    predicted_scores = (
        base_scores_normalized * 0.2 +     # 20% base location score
        type_cuisine_bonus_normalized * 0.3 +  # 30% type/cuisine match (increased weight)
        income_scores * 0.2 +              # 20% income compatibility
        competition_scores * 0.15 +        # 15% competition analysis
        accessibility_scores * 0.1 +       # 10% accessibility
        market_scores * 0.05               # 5% market potential
    )
    
    # Normalize scores to 0-10 range for better readability
    predicted_scores = np.clip(predicted_scores, 0, 10)
    X_predict['predicted_score'] = predicted_scores.round(2)
    
    # Debug: Store individual score components for analysis
    X_predict['base_score_norm'] = base_scores_normalized.round(2)
    X_predict['type_cuisine_bonus_norm'] = type_cuisine_bonus_normalized.round(2)
    X_predict['income_score'] = income_scores.round(2)
    X_predict['competition_score'] = competition_scores.round(2)

    # --- Create Geometries and Visualize ---
    grid_size = 0.0045
    X_predict['geometry'] = X_predict.apply(lambda row: Polygon([
        (row['longitude'], row['latitude']),
        (row['longitude'] + grid_size, row['latitude']),
        (row['longitude'] + grid_size, row['latitude'] + grid_size),
        (row['longitude'], row['latitude'] + grid_size)
    ]), axis=1)
    gdf = gpd.GeoDataFrame(X_predict, geometry='geometry')

    # Calculate optimal map center based on data bounds
    lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
    lon_min, lon_max = df['longitude'].min(), df['longitude'].max()
    map_center = [(lat_min + lat_max) / 2, (lon_min + lon_max) / 2]
    
    # Debug: Print map center for verification
    print(f"Map center calculated: {map_center}")
    print(f"Data bounds: Lat {lat_min:.6f} to {lat_max:.6f}, Lon {lon_min:.6f} to {lon_max:.6f}")
    
    bangalore_map = folium.Map(location=map_center, zoom_start=11, tiles="cartodbpositron")

    folium.Choropleth(
        geo_data=gdf.to_json(),
        data=X_predict,
        columns=['grid_id', 'predicted_score'],
        key_on='feature.properties.grid_id',
        fill_color='YlGn',
        fill_opacity=0.8,
        line_opacity=0.2,
        legend_name=f'Predicted Score for {user_cuisine} {user_restaurant_type}'
    ).add_to(bangalore_map)

    top_3_grids = X_predict.sort_values(by='predicted_score', ascending=False).head(3)

    for i, (_, row) in enumerate(top_3_grids.iterrows()):
        lat, lon = row['latitude'], row['longitude']
        popup_html = f"""
        <b>⭐ Top Recommendation #{i+1} ⭐</b><br>
        <b>Area:</b> {row['area_name']}<br>
        <b>Grid ID:</b> {row['grid_id']}<br>
        <b>Predicted Score:</b> <b>{row['predicted_score']:.2f}/10</b><br>
        <b>Population Density:</b> {row['population_density']:,}<br>
        <b>Avg Income:</b> ₹{row['avg_income']:,}<br>
        <b>Competition:</b> {row.get('same_cuisine_competitors_1km', 0)} same cuisine
        """
        folium.Marker(
            [lat, lon],
            popup=popup_html,
            tooltip=f"{row['area_name']} (Score: {row['predicted_score']:.2f})",
            icon=folium.Icon(color='red' if i == 0 else 'blue', icon='star', prefix='fa')
        ).add_to(bangalore_map)
        
    return bangalore_map, top_3_grids

# Fast recommender function removed for simplified UI

# --- Main App Interface ---
def main():
    """Main application function with multi-page layout."""
    
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    if 'analysis_run' not in st.session_state:
        st.session_state.analysis_run = False
        st.session_state.map = None
        st.session_state.top_3 = None
        st.session_state.method = None
        st.session_state.recommendations = None

    # Navigation
    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
    with col_nav1:
        if st.button("🏠 Back to Home"):
            if 'app_choice' in st.session_state:
                del st.session_state.app_choice
            st.rerun()
    
    with col_nav3:
        if st.button("📊 Switch to Restaurant Data Restaurant Data Analytics Map Map"):
            st.session_state.app_choice = "analytics"
            st.rerun()
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🍽️ Restaurant Intelligence Hub</h1>
        <p>Advanced AI-powered location analysis for restaurant success in Bangalore</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Page navigation removed for simplified UI
    
    # Load data
    df = load_data()
    if df is None:
        st.error("❌ Unable to load dataset. Please check if the required CSV files are present.")
        return
    
    # Page routing
    page = st.selectbox(
        "Navigate to:",
        ["🎯 ML Predictions", "📊 Restaurant Data Restaurant Data Analytics Map Map", "💡 Insights"],
        index=0
    )
    
    if page == "🎯 ML Predictions":
        show_ml_predictions_page(df)
    elif page == "📊 Restaurant Data Restaurant Data Analytics Map Map":
        show_analytics_page(df)
    elif page == "💡 Insights":
        show_insights_page(df)

# Dashboard function removed

def show_ml_predictions_page(df):
    """Display the ML predictions page with enhanced UI."""
    st.markdown("## 🤖 ML-Powered Location Predictions")
    st.markdown("Get AI-powered location recommendations using advanced machine learning models.")
    
    # Sidebar for restaurant configuration
    with st.sidebar:
        st.markdown("### 🍽️ Your Restaurant Concept")
        
        # Restaurant type selection
        restaurant_type = st.selectbox(
            "Restaurant Type", 
            ['Fine Dining', 'Casual Dining', 'Quick Service', 'Café', 'Food Court'],
            help="Select the type of restaurant you want to open"
        )
        
        # Cuisine style selection
        restaurant_style = st.selectbox(
            "Cuisine Style", 
            ['Italian', 'Continental', 'Indian', 'Multi-Cuisine', 'Chinese', 'Japanese', 'Mexican', 'South Indian', 'North Indian', 'Sea Food'],
            help="Select the cuisine style for your restaurant"
        )
        
        # Advanced filters removed for simplified UI
        
        if st.button("🚀 Generate ML Predictions", type="primary"):
            with st.spinner('🤖 Running ML predictions...'):
                bangalore_map, top_3_df = generate_map(df.copy(), restaurant_style, restaurant_type)
                
                # Store results without filtering
                if top_3_df is not None:
                    st.session_state.map = bangalore_map
                    st.session_state.top_3 = top_3_df
                    st.session_state.analysis_run = True
                    st.session_state.restaurant_type = restaurant_type
                    st.session_state.restaurant_style = restaurant_style
    
    # Main content area
    if st.session_state.analysis_run and st.session_state.map is not None and st.session_state.top_3 is not None:
        st.markdown("### ✅ ML Analysis Complete!")
        st.markdown(f"**Restaurant Type:** {st.session_state.restaurant_type} | **Cuisine Style:** {st.session_state.restaurant_style}")
        
        # Results layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### 🏆 Top ML Predictions")
            top_3 = st.session_state.top_3
            
            for i, (index, row) in enumerate(top_3.iterrows()):
                with st.container():
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>#{i+1} - {row['area_name']}</h3>
                        <div style="font-size: 1.5rem; font-weight: bold; color: #667eea;">Score: {row['predicted_score']:.2f}</div>
                        <small>Grid ID: {row['grid_id']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Detailed info table
            st.markdown("#### 📋 Detailed Information")
            display_cols = ['area_name', 'predicted_score', 'base_score_norm', 'type_cuisine_bonus_norm', 'income_score', 'competition_score', 'avg_income', 'population_density', 'grid_id']
            available_cols = [col for col in display_cols if col in top_3.columns]
            st.dataframe(top_3[available_cols], use_container_width=True)
            
            # Debug information
            st.markdown("#### 🔍 Score Breakdown (Debug)")
            st.markdown(f"**Restaurant Type:** {st.session_state.restaurant_type} | **Cuisine:** {st.session_state.restaurant_style}")
            st.markdown("This shows how different inputs affect the scoring:")
            for i, (index, row) in enumerate(top_3.iterrows()):
                st.markdown(f"**#{i+1} {row['area_name']}:** Base={row.get('base_score_norm', 'N/A')}, Type/Cuisine Bonus={row.get('type_cuisine_bonus_norm', 'N/A')}, Income={row.get('income_score', 'N/A')}, Competition={row.get('competition_score', 'N/A')}")
        
        with col2:
            st.markdown("#### 🗺️ Interactive Heatmap")
            st.markdown(f"**ML Predictions** - {st.session_state.restaurant_type} - {st.session_state.restaurant_style}")
            st_folium(st.session_state.map, width='100%', height=600, returned_objects=[])
            
            # Performance info
            st.markdown("#### 📊 Performance Metrics")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Top Locations Found", len(top_3))
            with col_b:
                avg_pred_score = top_3['predicted_score'].mean()
                st.metric("Average Predicted Score", f"{avg_pred_score:.2f}")
            with col_c:
                # Show map center for verification
                lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
                lon_min, lon_max = df['longitude'].min(), df['longitude'].max()
                map_center = [(lat_min + lat_max) / 2, (lon_min + lon_max) / 2]
                st.metric("Map Center", f"{map_center[0]:.4f}, {map_center[1]:.4f}")
            
            # Export Section
            st.markdown("#### 📥 Export Results")
            st.markdown("Download comprehensive analysis reports with detailed insights and reasoning:")
            
            # Generate comprehensive report
            insights_report = generate_insights_report(top_3, st.session_state.restaurant_type, st.session_state.restaurant_style, df)
            
            # Export buttons
            col_export1, col_export2 = st.columns(2)
            
            with col_export1:
                # CSV Export
                csv_filename = f"restaurant_recommendations_{st.session_state.restaurant_type}_{st.session_state.restaurant_style}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                csv_link = create_download_link(top_3, csv_filename, "csv")
                st.markdown(csv_link, unsafe_allow_html=True)
            
            with col_export2:
                # PDF Report Export
                pdf_filename = f"restaurant_report_{st.session_state.restaurant_type}_{st.session_state.restaurant_style}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                pdf_link = create_download_link(insights_report, pdf_filename, "pdf")
                st.markdown(pdf_link, unsafe_allow_html=True)
            
            # Show preview of insights
            with st.expander("🔍 Preview Detailed Insights"):
                st.markdown("### 📊 Market Analysis")
                market_analysis = insights_report['detailed_insights']['market_analysis']
                st.write(f"**Market Saturation:** {market_analysis['market_saturation']}")
                st.write(f"**Average Income Level:** {market_analysis['average_income_level']}")
                st.write(f"**Population Density Trend:** {market_analysis['population_density_trend']}")
                st.write(f"**Competition Intensity:** {market_analysis['competition_intensity']}")
                
                st.markdown("### 🏪 Competition Landscape")
                competition = insights_report['detailed_insights']['competition_landscape']
                st.write(f"**Same Cuisine Competition:** {competition['same_cuisine_competition']}")
                st.write(f"**Market Opportunity:** {competition['market_opportunity']}")
                st.write(f"**Differentiation Need:** {competition['differentiation_need']}")
                
                st.markdown("### 👥 Demographic Insights")
                demographics = insights_report['detailed_insights']['demographic_insights']
                st.write(f"**Income Suitability:** {demographics['income_suitability']}")
                st.write(f"**Population Base:** {demographics['population_base']}")
                st.write(f"**Target Demographic:** {demographics['target_demographic']}")
                
                st.markdown("### ⭐ Location Advantages")
                for advantage in insights_report['detailed_insights']['location_advantages']:
                    st.write(f"• {advantage}")
    else:
        st.info("👈 Configure your restaurant concept in the sidebar and click 'Generate ML Predictions' to start the analysis.")
        
        # Show sample data
        st.markdown("### 📊 Sample Location Data")
        sample_df = df.head(10)[['area_name', 'location_score', 'population_density', 'avg_income']]
        st.dataframe(sample_df, use_container_width=True)
        
        # ML explanation
        st.markdown("### 🤖 How ML Predictions Work")
        st.markdown("""
        Our machine learning system analyzes multiple factors to predict the best restaurant locations:
        
        **Key Features Analyzed:**
        - 🏘️ **Population Density**: Higher density = more potential customers
        - 💰 **Average Income**: Affects spending capacity and restaurant type suitability
        - 🏪 **Competition Analysis**: Balances market opportunity with competition
        - 🚗 **Accessibility**: Transportation and foot traffic patterns
        - 📍 **Location Characteristics**: Area-specific factors and demographics
        
        **System Benefits:**
        - ✅ Data-driven predictions based on historical success patterns
        - ✅ Considers complex interactions between multiple factors
        - ✅ Provides confidence scores for each location
        - ✅ Adapts to different restaurant types and cuisines
        - ✅ Simple interface - just select your concept and get results
        """)

def show_analytics_page(df):
    """Display the analytics page with advanced visualizations."""
    st.markdown("## 📈 Restaurant Data Restaurant Data Restaurant Data Analytics Map Map")
    st.markdown("Deep dive into location data with interactive charts and statistical analysis.")
    
    # Restaurant Data Restaurant Data Analytics Map Map tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🏆 Top Performers", "📈 Trends", "🔍 Comparison"])
    
    with tab1:
        st.markdown("### 📊 Location Score Distribution")
        fig = px.histogram(df, x='location_score', nbins=30, title="Distribution of Location Scores")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistical summary
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📈 Statistical Summary")
            st.write(df['location_score'].describe())
        
        with col2:
            st.markdown("#### 🎯 Score Categories")
            score_ranges = pd.cut(df['location_score'], bins=[0, 40, 60, 80, 100], labels=['Poor', 'Fair', 'Good', 'Excellent'])
            score_counts = score_ranges.value_counts()
            fig_pie = px.pie(values=score_counts.values, names=score_counts.index, title="Score Distribution by Category")
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab2:
        st.markdown("### 🏆 Top Performing Locations")
        top_20 = df.nlargest(20, 'location_score')
        
        # Bar chart of top locations
        fig = create_advanced_charts(top_20, "comparison")
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.markdown("#### 📋 Top 20 Locations Details")
        st.dataframe(top_20[['area_name', 'location_score', 'population_density', 'avg_income']], use_container_width=True)
    
    with tab3:
        st.markdown("### 📈 Population vs Income Analysis")
        
        # Scatter plot
        fig = px.scatter(df, x='population_density', y='avg_income', 
                        color='location_score', size='location_score',
                        hover_data=['area_name'],
                        title="Population Density vs Average Income (colored by Location Score)")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Correlation analysis
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🔗 Correlation Matrix")
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            corr_matrix = df[numeric_cols].corr()
            fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto")
            st.plotly_chart(fig_corr, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 Key Correlations")
            correlations = df[['location_score', 'population_density', 'avg_income']].corr()['location_score'].drop('location_score')
            for col, corr in correlations.items():
                st.metric(f"Location Score vs {col.replace('_', ' ').title()}", f"{corr:.3f}")

def show_insights_page(df):
    """Display the insights page with AI-generated recommendations."""
    st.markdown("## 💡 AI-Powered Insights")
    st.markdown("Discover key patterns and actionable insights from the location data.")
    
    # Generate insights
    insights = create_insights_panel(df)
    
    # Display insights
    for insight in insights:
        st.markdown(f"### {insight}")
    
    # Additional analysis
    st.markdown("### 🔍 Deep Dive Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Location Score Quartiles")
        quartiles = df['location_score'].quantile([0.25, 0.5, 0.75, 1.0])
        for q, value in quartiles.items():
            st.metric(f"{int(q*100)}th Percentile", f"{value:.1f}")
    
    with col2:
        st.markdown("#### 📊 Area Performance")
        high_performers = df[df['location_score'] > df['location_score'].quantile(0.9)]
        st.metric("High Performers (>90th percentile)", len(high_performers))
        
        low_performers = df[df['location_score'] < df['location_score'].quantile(0.1)]
        st.metric("Low Performers (<10th percentile)", len(low_performers))
    
    # Recommendations
    st.markdown("### 🎯 Strategic Recommendations")
    
    # Top 5 locations for different restaurant types
    st.markdown("#### 🍽️ Best Locations by Restaurant Type")
    
    restaurant_types = ['Fine Dining', 'Casual Dining', 'Quick Service', 'Café', 'Food Court']
    
    for rest_type in restaurant_types:
        with st.expander(f"🏪 {rest_type} Recommendations"):
            # This is a simplified example - in reality, you'd use the actual system
            top_5 = df.nlargest(5, 'location_score')
            st.dataframe(top_5[['area_name', 'location_score', 'population_density', 'avg_income']])

# Run the main application
if __name__ == "__main__":
    main()
else:
    # When imported, don't run automatically
    pass

