import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import contextily as cx

def create_geospatial_grid(gdf, grid_size_meters):
    """
    Creates a square grid over the extent of a GeoDataFrame.

    Args:
        gdf (GeoDataFrame): The GeoDataFrame to overlay the grid on.
        grid_size_meters (int): The size of each grid cell in meters.

    Returns:
        GeoDataFrame: A GeoDataFrame containing the grid cells that intersect with the input gdf.
    """
    # Get the total bounds of the projected map
    xmin, ymin, xmax, ymax = gdf.total_bounds

    # Create lists of x and y coordinates for the grid
    x_coords = np.arange(np.floor(xmin), np.ceil(xmax) + grid_size_meters, grid_size_meters)
    y_coords = np.arange(np.floor(ymin), np.ceil(ymax) + grid_size_meters, grid_size_meters)

    # Create a list of Polygon objects for each grid cell
    grid_cells = []
    for x in x_coords[:-1]:
        for y in y_coords[:-1]:
            cell = Polygon([
                (x, y), (x + grid_size_meters, y),
                (x + grid_size_meters, y + grid_size_meters), (x, y + grid_size_meters)
            ])
            grid_cells.append(cell)

    # Create a GeoDataFrame from the grid cells with the same CRS as the input
    grid = gpd.GeoDataFrame(grid_cells, columns=['geometry'], crs=gdf.crs)

    # Keep only the grid cells that actually intersect with the map
    grid_intersecting = gpd.overlay(grid, gdf, how='intersection')
    grid_intersecting['grid_id'] = range(len(grid_intersecting)) # Add a unique ID

    return grid_intersecting

def main():
    """
    Main function to execute the geospatial analysis pipeline.
    """
    # --- 1. Load Bangalore Map & Set Correct Projection ---
    # The map needs a projected Coordinate Reference System (CRS) to work with meters.
    # EPSG:32643 is a common CRS for this region (UTM Zone 43N).
    try:
        # Replace 'bangalore_ward.geojson' with the path to your map file
        blr_map = gpd.read_file('bangalore_ward.geojson')
        blr_map_proj = blr_map.to_crs(epsg=32643)
        print("Successfully loaded Bangalore map.")
    except Exception as e:
        print(f"Error: Could not load map file. Make sure 'bangalore_ward.geojson' is in the directory.")
        print(f"Details: {e}")
        return

    # --- 2. Create the 1km x 1km Grid ---
    grid_size = 1000  # 1 km = 1000 meters
    print(f"Creating a {grid_size}m x {grid_size}m grid...")
    grid_blr = create_geospatial_grid(blr_map_proj, grid_size)
    print(f"Successfully created a grid with {len(grid_blr)} cells over Bangalore.")

    # --- 3. Load and Process Restaurant Data ---
    try:
        # Load your new, clean dataset
        restaurants_df = pd.read_csv('Bangalore_Restaurants.csv')
    except FileNotFoundError:
        print("Error: 'Bangalore_Restaurants.csv' not found. Please ensure the file is in the directory.")
        return

    # Clean data: remove rows with missing latitude/longitude
    restaurants_df.dropna(subset=['Latitude', 'Longitude'], inplace=True)

    # Convert the pandas DataFrame to a GeoDataFrame
    # Note: Using the column names 'Longitude' and 'Latitude' from your file
    restaurants_gdf = gpd.GeoDataFrame(
        restaurants_df,
        geometry=gpd.points_from_xy(restaurants_df.Longitude, restaurants_df.Latitude),
        crs='EPSG:4326' # Initial CRS is WGS84 for lat/lon
    )

    # Reproject restaurant points to the same CRS as our grid
    restaurants_proj = restaurants_gdf.to_crs(epsg=32643)
    print(f"Successfully processed {len(restaurants_proj)} restaurants.")

    # --- 4. Perform the Spatial Join ---
    print("Performing spatial join to map restaurants to grid cells...")
    # This finds which grid cell each restaurant point is 'within'
    joined_gdf = gpd.sjoin(restaurants_proj, grid_blr, how="inner", predicate="within")
    print("Spatial join complete.")

    # --- 5. Analyze and Visualize the Results ---
    print("Analyzing restaurant counts per grid cell...")
    # Count the number of restaurants in each grid cell
    restaurant_counts = joined_gdf.groupby('grid_id').size().reset_index(name='restaurant_count')

    # Merge the counts back into our grid GeoDataFrame
    grid_with_counts = grid_blr.merge(restaurant_counts, on='grid_id', how='left')

    # Fill grid cells that have no restaurants with a count of 0
    grid_with_counts['restaurant_count'].fillna(0, inplace=True)

    print("Analysis complete. Generating visualization...")
    # 
    # Create the final plot (a choropleth map)
    fig, ax = plt.subplots(1, 1, figsize=(15, 15))

    # Plot the grid cells, with color intensity based on restaurant count
    grid_with_counts.plot(
        column='restaurant_count',
        ax=ax,
        legend=True,
        cmap='viridis',  # A nice color map for density
        linewidth=0.1,
        edgecolor='black',
        legend_kwds={'label': "Number of Restaurants per 1 sq km", 'orientation': "horizontal"}
    )

    # Add a basemap for context (streets, landmarks, etc.)
    cx.add_basemap(ax, crs=grid_with_counts.crs.to_string(), source=cx.providers.CartoDB.Positron)

    # Final plot cleanup
    ax.set_title('Restaurant Density Across Bangalore (1km x 1km Grid)', fontsize=20, pad=20)
    ax.set_axis_off()

    plt.savefig('bangalore_restaurant_density.png', dpi=300, bbox_inches='tight')
    print("Successfully saved the map as 'bangalore_restaurant_density.png'.")
    plt.show()

if __name__ == '__main__':
    main()

