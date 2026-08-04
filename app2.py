# app2.py
import os
from pathlib import Path
import logging

import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen
from PIL import Image, UnidentifiedImageError

# Configure simple logging (logs go to console, not UI)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Page Configuration ---
st.set_page_config(
    page_title="Bengaluru Restaurant Insights",
    page_icon="🗺️",
    layout="wide",
)


# --- Data Loading and Processing (Cached for Performance) ---
@st.cache_data
def load_and_process_data(
    restaurants_csv_path: str = "Bangalore_Restaurants.csv",
    grid_geojson_path: str = "blr_restaurant_grids.geojson",
):
    """
    Load restaurants CSV and grid geojson, perform joins and compute fields used
    by the map tooltips. Returns a GeoDataFrame in EPSG:4326.
    """
    logger.info("Running data processing for load_and_process_data()")

    # --- Read restaurants CSV ---
    if not Path(restaurants_csv_path).exists():
        raise FileNotFoundError(f"Restaurants CSV not found: {restaurants_csv_path}")
    restaurants_df = pd.read_csv(restaurants_csv_path)

    # Ensure Category column exists
    if "Category" not in restaurants_df.columns:
        restaurants_df["Category"] = ""
    all_cuisines = restaurants_df["Category"].astype(str).str.split(", ").explode()
    top_city_cuisines = all_cuisines.value_counts().nlargest(10).index.tolist()

    # --- Read grid GeoJSON ---
    if not Path(grid_geojson_path).exists():
        raise FileNotFoundError(f"Grid geojson not found: {grid_geojson_path}")
    grid_final = gpd.read_file(grid_geojson_path)

    # Ensure grid has a CRS; if not assume EPSG:4326
    if grid_final.crs is None:
        try:
            grid_final = grid_final.set_crs(epsg=4326, allow_override=True)
        except Exception:
            # Last-resort: leave it and try to align later
            logger.warning("Grid CRS missing and set_crs failed; proceeding with default EPSG:4326 assumption.")
            grid_final.crs = "EPSG:4326"

    # --- Create restaurants GeoDataFrame ---
    # require Longitude & Latitude columns; if missing, create empty geometry
    if {"Longitude", "Latitude"}.issubset(restaurants_df.columns):
        restaurants_gdf = gpd.GeoDataFrame(
            restaurants_df,
            geometry=gpd.points_from_xy(restaurants_df["Longitude"], restaurants_df["Latitude"]),
            crs="EPSG:4326",
        )
    else:
        # create empty GeoDataFrame with same index if coords are missing
        restaurants_gdf = gpd.GeoDataFrame(restaurants_df.copy(), geometry=None, crs="EPSG:4326")
        logger.warning("Longitude/Latitude columns missing in restaurants CSV; restaurants_gdf will be empty of geometry.")

    # Try to align CRSes
    try:
        restaurants_gdf = restaurants_gdf.to_crs(grid_final.crs)
    except Exception:
        try:
            restaurants_gdf = restaurants_gdf.to_crs(epsg=4326)
        except Exception:
            logger.exception("Failed to set restaurants_gdf CRS. Continuing; spatial join may fail.")

    # --- Spatial join: restaurants -> grid index_right ---
    restaurants_with_grid_id = None
    if restaurants_gdf.geometry.notnull().any():
        try:
            # newer geopandas uses predicate
            restaurants_with_grid_id = gpd.sjoin(
                restaurants_gdf, grid_final, how="inner", predicate="within"
            )
        except TypeError:
            # older geopandas uses 'op' argument
            try:
                restaurants_with_grid_id = gpd.sjoin(
                    restaurants_gdf, grid_final, how="inner", op="within"
                )
            except Exception:
                logger.exception("Spatial join failed (both predicate and op attempts). Continuing without join.")
                restaurants_with_grid_id = None
        except Exception:
            logger.exception("Spatial join failed unexpectedly. Continuing without join.")
            restaurants_with_grid_id = None
    else:
        logger.info("No valid restaurant geometry available; skipping spatial join.")

    # --- Determine dominant locality per grid cell ---
    if restaurants_with_grid_id is not None and "Locality" in restaurants_with_grid_id.columns:
        def safe_mode(series):
            if series.empty:
                return "N/A"
            m = series.mode()
            return m.iloc[0] if not m.empty else "N/A"

        dominant_localities = (
            restaurants_with_grid_id.groupby("index_right")["Locality"].apply(safe_mode)
        )
        dominant_localities.name = "locality"
        # Join back; ensure index alignment
        grid_final = grid_final.join(dominant_localities, how="left")
    else:
        # fallback: set locality column to Not Available
        grid_final["locality"] = "Not Available"

    grid_final["locality"] = grid_final["locality"].fillna("Not Available")

    # --- Sanitize numeric columns so formatting won't crash ---
    for col in ["avg_rating", "avg_pricing", "restaurant_count"]:
        if col in grid_final.columns:
            grid_final[col] = pd.to_numeric(grid_final[col], errors="coerce").fillna(0)
        else:
            grid_final[col] = 0

    # Ensure categories column exists and is string
    if "categories" not in grid_final.columns:
        grid_final["categories"] = "None"
    grid_final["categories"] = grid_final["categories"].fillna("None").astype(str).replace("0", "None")

    # --- Format display columns ---
    def format_categories_row(categories_str: str):
        if not categories_str or categories_str.strip().lower() in {"none", "0"}:
            return "None"
        unique_cuisines = list(dict.fromkeys([c.strip() for c in categories_str.split(",") if c.strip()]))
        if len(unique_cuisines) > 6:
            return ", ".join(unique_cuisines[:6] + ["..."])
        return ", ".join(unique_cuisines)

    grid_final["display_cuisines"] = grid_final["categories"].apply(format_categories_row)
    grid_final["formatted_avg_rating"] = grid_final["avg_rating"].apply(lambda x: f"{x:.2f}" if x > 0 else "N/A")
    grid_final["formatted_avg_pricing"] = grid_final["avg_pricing"].apply(lambda x: f"₹{int(x)}" if x > 0 else "N/A")

    # --- Generate Insights per grid ---
    def generate_advanced_insight(row, top_cuisines):
        count = int(row.get("restaurant_count", 0) or 0)
        if count < 5:
            return (
                "Analysis: This area is significantly underserved, with very few restaurants.\n"
                "Opportunity: A new establishment of almost any popular cuisine could capture the local market."
            )

        avg_pricing = float(row.get("avg_pricing", 0) or 0)
        avg_rating = float(row.get("avg_rating", 0) or 0)
        price_point = "high-end" if avg_pricing > 400 else "mid-range" if avg_pricing > 200 else "budget-friendly"
        rating_level = "highly-rated" if avg_rating > 4.0 else "well-regarded" if avg_rating > 3.5 else "average-rated"

        cats = str(row.get("categories", "") or "")
        all_grid_cuisines = {c.strip() for c in cats.split(",") if c.strip()}
        if all_grid_cuisines:
            dominant_cuisine = next(iter(all_grid_cuisines))
        else:
            dominant_cuisine = "various cuisines"

        character = f"This grid is a busy, {rating_level} hub for {price_point} dining, dominated by {dominant_cuisine} cuisine."
        missing_cuisines = [c for c in top_cuisines if c not in all_grid_cuisines]
        if not missing_cuisines:
            opportunity = "The market here is highly competitive and saturated across major cuisine types. Proceed with caution."
        else:
            gap = " and ".join(missing_cuisines[:2])
            opportunity = f"There appears to be a market gap for popular options like {gap}. A new {price_point} restaurant focusing on these cuisines could perform well."

        return f"Analysis: {character}\nOpportunity: {opportunity}"

    grid_final["insight"] = grid_final.apply(lambda r: generate_advanced_insight(r, top_city_cuisines), axis=1)

    # --- Create HTML tooltip safely (avoid crashes on missing/newline) ---
    def make_html_card(row):
        insight_text = str(row.get("insight", "") or "")
        parts = insight_text.split("\n")
        analysis_text = parts[0].replace("Analysis: ", "") if len(parts) >= 1 else "No analysis available."
        opportunity_text = parts[1].replace("Opportunity: ", "") if len(parts) >= 2 else "No specific opportunity identified."

        # safe numeric conversions
        try:
            rcnt = int(float(row.get("restaurant_count", 0) or 0))
        except Exception:
            rcnt = 0
        avg_rating = row.get("formatted_avg_rating", "N/A")
        avg_pricing = row.get("formatted_avg_pricing", "N/A")
        locality = row.get("locality", "Not Available")

        return f"""
        <div style="font-family: 'Segoe UI', Roboto, sans-serif; width: 420px;">
            <div style="background-color: #2C3E50; color: white; padding: 10px 15px; border-radius: 6px 6px 0 0; font-size: 20px; font-weight: bold;">
                📍 {locality}
            </div>
            <div style="background-color: #34495E; color: #ECF0F1; padding: 15px; border-radius: 0 0 6px 6px; line-height: 1.6;">
                <div style="font-size: 13px; color: #BDC3C7; margin-bottom: 12px; display: flex; justify-content: space-between;">
                    <span><b style="color: white;">{rcnt}</b> Restaurants</span>
                    <span><b style="color: white;">{avg_rating}</b> ⭐ Avg Rating</span>
                    <span><b style="color: white;">{avg_pricing}</b> Avg Price</span>
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

    # Apply tooltip generation
    grid_final["tooltip_html"] = grid_final.apply(make_html_card, axis=1)

    # Return GeoDataFrame in EPSG:4326 for folium compatibility
    try:
        out = grid_final.to_crs(epsg=4326)
    except Exception:
        # If conversion fails, try to set crs then return
        try:
            out = grid_final.set_crs(epsg=4326, allow_override=True)
        except Exception:
            out = grid_final  # last resort
    return out


def main():
    """Analytics Dashboard App"""
    st.title("Bengaluru Restaurant Market Analysis 🗺️")
    st.markdown(
        """
    Welcome! This interactive map helps identify opportunities for new restaurants in Bengaluru. 
    Hover over a grid cell to see a detailed analysis of the local food scene, including market gaps and competition.
    """
    )

    # --- Add Picture Here ---
    img_path = Path(
        r"C:\Users\LENOVO\OneDrive - presidencyuniversity.in\Desktop\restaurant\restaurant_density_map.png"
    )

    if img_path.exists():
        try:
            img_obj = Image.open(img_path)
            st.image(img_obj, caption="Restaurant Density Map", use_column_width=True)
        except UnidentifiedImageError:
            st.warning("Image file found but could not be opened as an image. Skipping display.")
        except PermissionError:
            st.warning("Permission denied when opening the image. Move the image to a readable folder or update permissions.")
        except Exception as e:
            st.warning(f"Could not load image: {e}")
    else:
        st.info("Restaurant density image not found at the provided path. Continuing without image.")

    # Load processed grid data (show spinner while loading)
    try:
        with st.spinner("Loading and processing data..."):
            grid_data = load_and_process_data()
    except FileNotFoundError as e:
        st.error(f"Required data file missing: {e}")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")
        st.stop()

    # Create the Folium map
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=11, tiles="CartoDB dark_matter")

    # Create the GeoJson layer
    try:
        geojson_layer = folium.GeoJson(
            grid_data,
            style_function=lambda x: {
                "fillColor": "grey",
                "color": "#555555",
                "weight": 0.8,
                "fillOpacity": 0.05,
                "opacity": 0.2,
            },
            highlight_function=lambda x: {
                "fillColor": "#FFFF00",
                "color": "#000000",
                "fillOpacity": 0.5,
                "weight": 1,
            },
            tooltip=folium.features.GeoJsonTooltip(
                fields=["tooltip_html"],
                aliases=[""],
                labels=False,
                sticky=False,
                style="background-color: transparent; border-color: transparent; box-shadow: none; padding: 0px;",
            ),
        )
        geojson_layer.add_to(m)
    except Exception:
        logger.exception("Failed to create GeoJson layer with tooltip. Adding layer without tooltip as fallback.")
        try:
            folium.GeoJson(grid_data).add_to(m)
        except Exception:
            st.error("Failed to add GeoJSON to the map.")
            st.stop()

    # Add fullscreen control
    try:
        Fullscreen().add_to(m)
    except Exception:
        logger.exception("Could not add Fullscreen plugin to the folium map (plugin may be unavailable).")

    # Display the map in Streamlit
    st_folium(m, use_container_width=True, height=700)


if __name__ == "__main__":
    main()
