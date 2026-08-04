# app.py
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from scipy.stats import mode
from folium.plugins import Fullscreen

# --- Page Configuration ---
st.set_page_config(
    page_title="Bengaluru Restaurant Insights",
    page_icon="🗺️",
    layout="wide",
)

# --- Data Loading and Processing (Cached for Performance) ---
@st.cache_data
def load_and_process_data():
    print("--- Running Data Processing (this will only run once) ---")
    
    # Part 1: Global Analysis
    restaurants_df = pd.read_csv("Bangalore_Restaurants.csv")
    all_cuisines = restaurants_df['Category'].str.split(', ').explode()
    top_city_cuisines = all_cuisines.value_counts().nlargest(10).index.tolist()

    # Part 2: Load Grid and Assign Localities
    grid_final = gpd.read_file("blr_restaurant_grids.geojson")
    restaurants_gdf = gpd.GeoDataFrame(
        restaurants_df,
        geometry=gpd.points_from_xy(restaurants_df['Longitude'], restaurants_df['Latitude']),
        crs="EPSG:4326"
    ).to_crs(grid_final.crs)
    restaurants_with_grid_id = gpd.sjoin(restaurants_gdf, grid_final, how="inner", predicate="within")
    dominant_localities = restaurants_with_grid_id.groupby('index_right')['Locality'].apply(lambda x: x.mode().iloc[0] if not x.mode().empty else "N/A")
    dominant_localities.name = "locality"
    grid_final = grid_final.join(dominant_localities)
    grid_final['locality'].fillna("Not Available", inplace=True)

    # Part 3: Format Data
    grid_final.fillna(0, inplace=True)
    grid_final['categories'].replace(0, "None", inplace=True)
    def format_categories(row):
        if row['categories'] == "None": return "None"
        unique_cuisines = list(dict.fromkeys(row['categories'].split(', ')))
        return ", ".join(unique_cuisines[:6] + ['...'] if len(unique_cuisines) > 6 else unique_cuisines)
    grid_final['display_cuisines'] = grid_final.apply(format_categories, axis=1)
    grid_final['formatted_avg_rating'] = grid_final['avg_rating'].apply(lambda x: f"{x:.2f}" if x > 0 else "N/A")
    grid_final['formatted_avg_pricing'] = grid_final['avg_pricing'].apply(lambda x: f"₹{int(x)}" if x > 0 else "N/A")

    # Part 4: Generate Insights
    def generate_advanced_insight(row, top_cuisines):
        count = row['restaurant_count']
        if count < 5: return "Analysis: This area is significantly underserved, with very few restaurants.\nOpportunity: A new establishment of almost any popular cuisine could capture the local market."
        price_point = "high-end" if row['avg_pricing'] > 400 else "mid-range" if row['avg_pricing'] > 200 else "budget-friendly"
        rating_level = "highly-rated" if row['avg_rating'] > 4.0 else "well-regarded" if row['avg_rating'] > 3.5 else "average-rated"
        all_grid_cuisines = set(row['categories'].split(', '))
        dominant_cuisine = pd.Series(row['categories'].split(', ')).value_counts().index[0]
        character = f"This grid is a busy, {rating_level} hub for {price_point} dining, dominated by {dominant_cuisine} cuisine."
        missing_cuisines = [c for c in top_cuisines if c not in all_grid_cuisines]
        if not missing_cuisines: opportunity = "The market here is highly competitive and saturated across major cuisine types. Proceed with caution."
        else:
            gap = " and ".join(missing_cuisines[:2])
            opportunity = f"There appears to be a market gap for popular options like {gap}. A new {price_point} restaurant focusing on these cuisines could perform well."
        return f"Analysis: {character}\nOpportunity: {opportunity}"
    grid_final['insight'] = grid_final.apply(lambda row: generate_advanced_insight(row, top_city_cuisines), axis=1)
    
    # Part 5: Create HTML Card (This is the updated function)
    def make_html_card(row):
        # Split the insight into Analysis and Opportunity
        try:
            analysis_text, opportunity_text = row['insight'].split('\n')
            analysis_text = analysis_text.replace('Analysis: ', '')
            opportunity_text = opportunity_text.replace('Opportunity: ', '')
        except ValueError:
            analysis_text = row['insight']
            opportunity_text = "No specific opportunity identified."

        return f"""
        <div style="font-family: 'Segoe UI', Roboto, sans-serif; width: 420px;">
            <div style="background-color: #2C3E50; color: white; padding: 10px 15px; border-radius: 6px 6px 0 0; font-size: 20px; font-weight: bold;">
                📍 {row['locality']}
            </div>
            <div style="background-color: #34495E; color: #ECF0F1; padding: 15px; border-radius: 0 0 6px 6px; line-height: 1.6;">
                
                <div style="font-size: 13px; color: #BDC3C7; margin-bottom: 12px; display: flex; justify-content: space-between;">
                    <span><b style="color: white;">{int(row['restaurant_count'])}</b> Restaurants</span>
                    <span><b style="color: white;">{row['formatted_avg_rating']}</b> ⭐ Avg Rating</span>
                    <span><b style="color: white;">{row['formatted_avg_pricing']}</b> Avg Price</span>
                </div>

                <hr style="border-color: #2C3E50; margin: 0 0 12px 0;">

                <div style="margin-bottom: 12px;">
                    <b style="color: white; font-size: 15px;">Market Analysis</b><br>
                    <span style="font-size: 14px;">{analysis_text}</span>
                </div>

                <div style="background-color: rgba(46, 204, 113, 0.1); border-left: 4px solid #2ECC71; padding: 10px; border-radius: 4px;">
                    <b style="color: #2ECC71; font-size: 15px;">Business Opportunity</b><br>
                    <span style="font-size: 14px; color: white;">{opportunity_text}</span>
                </div>
            </div>
        </div>
        """
    grid_final['tooltip_html'] = grid_final.apply(make_html_card, axis=1)
    return grid_final.to_crs(epsg=4326)

# --- The Main App Interface ---
st.title("Bengaluru Restaurant Market Analysis 🗺️")
st.markdown("""
Welcome! This interactive map helps identify opportunities for new restaurants in Bengaluru. 
Hover over a grid cell to see a detailed analysis of the local food scene, including market gaps and competition.
""")

grid_data = load_and_process_data()

# Create the Folium map
m = folium.Map(location=[12.9716, 77.5946], zoom_start=11, tiles="CartoDB dark_matter")

# Create the GeoJson layer
geojson_layer = folium.GeoJson(
    grid_data,
    style_function=lambda x: {'fillColor': 'grey', 'color': '#555555', 'weight': 0.8, 'fillOpacity': 0.05, 'opacity': 0.2},
    highlight_function=lambda x: {'fillColor': '#FFFF00', 'color': '#000000', 'fillOpacity': 0.5, 'weight': 1},
    tooltip=folium.features.GeoJsonTooltip(
        fields=['tooltip_html'],
        aliases=[''],
        labels=False,
        sticky=False,
        style="background-color: transparent; border-color: transparent; box-shadow: none; padding: 0px;"
    ),
)
geojson_layer.add_to(m)

Fullscreen().add_to(m)

# Display the map in Streamlit
st_folium(m, use_container_width=True, height=700)