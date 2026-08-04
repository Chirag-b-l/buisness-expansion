#!/usr/bin/env python3
"""
Ultra-Fast Restaurant Location Recommendation System
Optimized for speed - no ML training, just fast recommendations
"""

import pandas as pd
import numpy as np
import os
import time

class FastRestaurantRecommender:
    def __init__(self, data_path):
        """Initialize with minimal data loading"""
        print("⚡ Loading data...")
        start = time.time()
        
        # Load only essential columns
        essential_cols = [
            'area_name', 'latitude', 'longitude', 'restaurant_type', 'restaurant_style',
            'population_density', 'avg_income', 'avg_bill_per_person',
            'restaurant_star_rating', 'review_count', 'avg_review_score',
            'same_cuisine_competitors_1km', 'other_cuisine_competitors_1km',
            'office_density', 'nightlife_density', 'mall_proximity',
            'college_proximity', 'parking_availability', 'public_transport_connectivity',
            'location_score'
        ]
        
        self.df = pd.read_csv(data_path, usecols=essential_cols)
        
        # Pre-calculate custom scores once
        self.custom_scores = self.calculate_custom_scores_fast()
        
        load_time = time.time() - start
        print(f"✅ Data loaded in {load_time:.2f} seconds!")
        
    def normalize_fast(self, series):
        """Fast normalization using numpy"""
        min_val = series.min()
        max_val = series.max()
        return (series - min_val) / (max_val - min_val + 1e-9)
    
    def calculate_custom_scores_fast(self):
        """Calculate custom scores using only essential data"""
        print("🔢 Pre-calculating custom scores...")
        
        # Get only the columns we need
        cols = [
            "population_density", "avg_income", "avg_bill_per_person",
            "restaurant_star_rating", "review_count", "avg_review_score",
            "same_cuisine_competitors_1km", "other_cuisine_competitors_1km",
            "office_density", "nightlife_density", "mall_proximity",
            "college_proximity", "parking_availability", "public_transport_connectivity"
        ]
        
        # Normalize all features at once
        data = self.df[cols].values
        normalized_data = np.zeros_like(data)
        
        for i, col in enumerate(cols):
            col_data = data[:, i]
            min_val = col_data.min()
            max_val = col_data.max()
            normalized_data[:, i] = (col_data - min_val) / (max_val - min_val + 1e-9)
        
        # Apply weighted formula using numpy
        scores = (
            2 * normalized_data[:, 0] +  # population_density
            2 * normalized_data[:, 1] +  # avg_income
            1 * normalized_data[:, 2] +  # avg_bill_per_person
            1 * normalized_data[:, 3] +  # restaurant_star_rating
            0.5 * normalized_data[:, 4] +  # review_count
            1 * normalized_data[:, 5] +  # avg_review_score
            -2 * normalized_data[:, 6] +  # same_cuisine_competitors_1km
            -0.5 * normalized_data[:, 7] +  # other_cuisine_competitors_1km
            1.5 * normalized_data[:, 8] +  # office_density
            1 * normalized_data[:, 9] +  # nightlife_density
            1 * (1 / (normalized_data[:, 10] + 1e-9)) +  # mall_proximity (inverse)
            1 * (1 / (normalized_data[:, 11] + 1e-9)) +  # college_proximity (inverse)
            1 * normalized_data[:, 12] +  # parking_availability
            1 * normalized_data[:, 13]   # public_transport_connectivity
        )
        
        # Normalize to 0-100 range
        min_score = scores.min()
        max_score = scores.max()
        normalized_scores = ((scores - min_score) / (max_score - min_score + 1e-9)) * 100
        
        return normalized_scores
    
    def get_available_options(self):
        """Get available options quickly"""
        types = sorted(self.df['restaurant_type'].unique())
        styles = sorted(self.df['restaurant_style'].unique())
        return types, styles
    
    def recommend_locations_fast(self, restaurant_type, restaurant_style, top_n=3, use_custom_scoring=False):
        """Ultra-fast recommendation using pre-calculated data"""
        
        # Fast filtering using boolean indexing
        mask = (self.df['restaurant_type'] == restaurant_type) & (self.df['restaurant_style'] == restaurant_style)
        filtered_indices = self.df[mask].index
        
        if len(filtered_indices) == 0:
            return []
        
        # Get filtered data
        filtered_df = self.df.loc[filtered_indices].copy()
        
        if use_custom_scoring:
            # Use pre-calculated custom scores
            filtered_df['score'] = self.custom_scores[filtered_indices]
        else:
            # Use existing location scores
            filtered_df['score'] = filtered_df['location_score']
        
        # Sort and get top N
        top_locations = filtered_df.nlargest(top_n, 'score')
        
        # Convert to results efficiently
        results = []
        for _, row in top_locations.iterrows():
            results.append({
                'area_name': row['area_name'],
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'location_score': round(row['score'], 2),
                'population_density': int(row['population_density']),
                'avg_income': int(row['avg_income']),
                'avg_bill_per_person': int(row['avg_bill_per_person']),
                'restaurant_star_rating': round(row['restaurant_star_rating'], 2),
                'review_count': int(row['review_count']),
                'avg_review_score': round(row['avg_review_score'], 2),
                'same_cuisine_competitors_1km': int(row['same_cuisine_competitors_1km']),
                'other_cuisine_competitors_1km': int(row['other_cuisine_competitors_1km']),
                'office_density': int(row['office_density']),
                'nightlife_density': int(row['nightlife_density']),
                'mall_proximity': round(row['mall_proximity'], 2),
                'college_proximity': round(row['college_proximity'], 2),
                'parking_availability': round(row['parking_availability'], 2),
                'public_transport_connectivity': int(row['public_transport_connectivity'])
            })
        
        return results

def display_recommendations_fast(recommendations, restaurant_type, restaurant_style):
    """Fast display of recommendations"""
    if not recommendations:
        print(f"\n❌ No recommendations found for {restaurant_type} - {restaurant_style}")
        return
    
    print(f"\n🍽  TOP 3 RECOMMENDATIONS FOR {restaurant_type.upper()} - {restaurant_style.upper()}")
    print("=" * 80)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n📍 RANK #{i}: {rec['area_name']}")
        print(f"   Location Score: {rec['location_score']}/100")
        print(f"   Coordinates: {rec['latitude']:.6f}, {rec['longitude']:.6f}")
        print(f"   Population Density: {rec['population_density']:,} people/km²")
        print(f"   Average Income: ₹{rec['avg_income']:,}")
        print(f"   Average Bill: ₹{rec['avg_bill_per_person']}")
        print(f"   Star Rating: {rec['restaurant_star_rating']}/5.0")
        print(f"   Review Count: {rec['review_count']:,}")
        print(f"   Review Score: {rec['avg_review_score']}/5.0")
        print(f"   Same Cuisine Competitors (1km): {rec['same_cuisine_competitors_1km']}")
        print(f"   Other Cuisine Competitors (1km): {rec['other_cuisine_competitors_1km']}")
        print(f"   Office Density: {rec['office_density']}")
        print(f"   Nightlife Density: {rec['nightlife_density']}")
        print(f"   Mall Proximity: {rec['mall_proximity']} km")
        print(f"   College Proximity: {rec['college_proximity']} km")
        print(f"   Parking Availability: {rec['parking_availability']}%")
        print(f"   Public Transport Connectivity: {rec['public_transport_connectivity']}/10")

def main():
    """Ultra-fast main function"""
    print("🍽  ULTRA-FAST RESTAURANT RECOMMENDATION SYSTEM")
    print("=" * 60)
    
    # Check for enhanced dataset first
    dataset_path = 'bengaluru_restaurant_grid_10k_scored.csv'
    if not os.path.exists(dataset_path):
        dataset_path = 'bengaluru_restaurant_grid_10k_gridded.csv'
        print("📊 Using original dataset")
    else:
        print("📊 Using enhanced dataset with custom scoring")
    
    # Initialize the fast recommender
    try:
        recommender = FastRestaurantRecommender(dataset_path)
    except FileNotFoundError:
        print("❌ Error: Dataset file not found!")
        return
    
    # Get available options
    types, styles = recommender.get_available_options()
    
    print(f"\n📋 Available Restaurant Types: {', '.join(types)}")
    print(f"📋 Available Restaurant Styles: {', '.join(styles)}")
    
    while True:
        print("\n" + "="*60)
        print("Enter your restaurant preferences:")
        
        # Get restaurant type
        while True:
            restaurant_type = input("\n🍕 Restaurant Type (cuisine): ").strip().title()
            if restaurant_type in types:
                break
            else:
                print(f"❌ Invalid type. Please choose from: {', '.join(types)}")
        
        # Get restaurant style
        while True:
            restaurant_style = input("🏪 Restaurant Style: ").strip().title()
            if restaurant_style in styles:
                break
            else:
                print(f"❌ Invalid style. Please choose from: {', '.join(styles)}")
        
        # Ask for scoring method
        while True:
            scoring_choice = input("\n🔢 Use custom weighted scoring? (y/n): ").strip().lower()
            if scoring_choice in ['y', 'yes', 'n', 'no']:
                break
            else:
                print("Please enter 'y' for yes or 'n' for no.")
        
        use_custom = scoring_choice in ['y', 'yes']
        
        # Get recommendations
        print(f"\n🔍 Finding best locations for {restaurant_type} - {restaurant_style}...")
        start_time = time.time()
        recommendations = recommender.recommend_locations_fast(restaurant_type, restaurant_style, use_custom_scoring=use_custom)
        end_time = time.time()
        print(f"⚡ Recommendations found in {end_time - start_time:.3f} seconds!")
        
        # Display recommendations
        display_recommendations_fast(recommendations, restaurant_type, restaurant_style)
        
        # Ask if user wants to continue
        while True:
            continue_choice = input("\n🔄 Would you like to get recommendations for another restaurant? (y/n): ").strip().lower()
            if continue_choice in ['y', 'yes', 'n', 'no']:
                break
            else:
                print("Please enter 'y' for yes or 'n' for no.")
        
        if continue_choice in ['n', 'no']:
            break
    
    print("\n👋 Thank you for using the Ultra-Fast Restaurant Recommendation System!")

if __name__ == "__main__":
    main()