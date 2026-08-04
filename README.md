# Restaurant Intelligence Hub

A comprehensive restaurant location analysis platform with two specialized applications.

## 🏠 Navigation System

The platform consists of three main components:

### 1. Home Page (`home.py`)
- **Purpose**: Central navigation hub
- **Features**: Choose between ML Predictions and Analytics Dashboard
- **Run**: `streamlit run home.py`

### 2. ML Predictions (`app.py`)
- **Purpose**: AI-powered restaurant location recommendations
- **Features**: 
  - Machine learning predictions
  - Interactive heatmaps
  - Detailed insights and reasoning
  - Export capabilities (CSV & HTML)
- **Run**: `streamlit run app.py`

### 3. Analytics Dashboard (`app2.py`)
- **Purpose**: Comprehensive data analysis and visualization
- **Features**:
  - Advanced data visualization
  - Statistical analysis
  - Trend identification
  - Performance metrics
- **Run**: `streamlit run app2.py`

## 🚀 Getting Started

1. **Start with the Home Page**:
   ```bash
   streamlit run home.py
   ```

2. **Choose Your Platform**:
   - Click "🚀 Launch ML Predictions" for AI recommendations
   - Click "📈 Launch Analytics Dashboard" for data analysis

3. **Navigate Between Apps**:
   - Use the "🏠 Back to Home" button in each app
   - Use the "🔄 Reset Selection" button to clear choices

## 📊 Data Requirements

Both applications require the following CSV files:
- `bengaluru_restaurant_grid_10k_scored.csv` (preferred)
- `bengaluru_restaurant_grid_10k_gridded.csv` (fallback)

## 🎯 Use Cases

### ML Predictions (`app.py`)
- **Best for**: Getting specific restaurant location recommendations
- **When to use**: Planning new restaurant locations
- **Output**: Ranked recommendations with detailed reasoning

### Analytics Dashboard (`app2.py`)
- **Best for**: Understanding market trends and data patterns
- **When to use**: Market research and competitive analysis
- **Output**: Comprehensive data visualizations and insights

## 🔧 Technical Details

- **Framework**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly, Folium
- **Export Formats**: CSV, HTML

## 📁 File Structure

```
restaurant/
├── home.py          # Navigation hub
├── app.py           # ML Predictions app
├── app2.py          # Analytics Dashboard
├── bengaluru_restaurant_grid_10k_scored.csv
├── bengaluru_restaurant_grid_10k_gridded.csv
└── README.md
```

## 🎨 Features

### Home Page
- Beautiful gradient design
- Clear platform descriptions
- Easy navigation
- Feature comparison

### ML Predictions
- AI-powered scoring
- Interactive maps
- Detailed reasoning
- Export functionality

### Analytics Dashboard
- Multiple visualization types
- Filtering capabilities
- Statistical analysis
- Performance metrics

## 🚀 Quick Start Commands

```bash
# Start the navigation hub
streamlit run home.py

# Or run apps directly
streamlit run app.py      # ML Predictions
streamlit run app2.py     # Analytics Dashboard
```

## 📞 Support

Both platforms use the same underlying data but provide different analysis approaches:
- **ML Predictions**: For location recommendations
- **Analytics Dashboard**: For data analysis

Choose the platform that best fits your analysis needs!



