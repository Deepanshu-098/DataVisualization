import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# 1. LOAD DATASET
url = "https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Other/Monterrey/airbnb.csv"
df = pd.read_csv(url)

print("Dataset loaded successfully")
print("Shape:", df.shape)
print("Columns:", df.columns.tolist())

# 2. DATA CLEANING
required_columns = ['latitude', 'longitude', 'price', 'minimum_nights']
missing = [c for c in required_columns if c not in df.columns]

if missing:
    raise ValueError(f"Missing columns in dataset: {missing}")

for col in required_columns:
    if col == 'price':
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(r'[^\d.]', '', regex=True),
            errors='coerce'
        )
    else:
        df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=required_columns)

# Remove invalid geographical coordinates
df = df[
    df['latitude'].between(-90, 90) &
    df['longitude'].between(-180, 180)
]

print("Clean dataset:", df.shape)
print(df.head())

if df.empty:
    raise ValueError("No valid records found in dataset.")

# --------------------------------------------------------------
# 3. CREATE DASH APP
app = Dash(__name__)

max_price = max(1000, int(df['price'].max()))

app.layout = html.Div(
    children=[
        html.H1(
            children="Airbnb Listings - Monterrey",
            style={'textAlign': 'center'}
        ),

        html.H3("Select Maximum Allowed Minimum Nights"),
        dcc.Slider(
            id='night-slider',
            min=int(df['minimum_nights'].min()),
            max=int(df['minimum_nights'].max()),
            value=int(df['minimum_nights'].max()),
            step=1,
            tooltip={"placement": "bottom", "always_visible": True}
        ),

        html.Br(),
        html.H3("Select Price Range"),
        dcc.RangeSlider(
            id='price-slider',
            min=0,
            max=max_price,
            value=[0, min(2500, max_price)],
            tooltip={"placement": "bottom", "always_visible": True}
        ),

        html.Br(),
        html.H4(id='count', style={'color': '#333'}),
        dcc.Graph(
            id='airbnb-map',
            style={'height': '650px'}
        )
    ],
    style={'padding': '20px', 'fontFamily': 'Arial, sans-serif'}
)

# --------------------------------------------------------------
# 4. CALLBACKS
@app.callback(
    Output('count', 'children'),
    Output('airbnb-map', 'figure'),
    Input('night-slider', 'value'),
    Input('price-slider', 'value')
)
def update_map(selected_nights, price_range):
    low_price, high_price = price_range

    # Filter dataset based on slider selections
    filtered_df = df[
        (df['minimum_nights'] <= selected_nights) &
        (df['price'] >= low_price) &
        (df['price'] <= high_price)
    ]

    # Include extra hover details if those columns exist in the CSV
    hover_cols = [
        col for col in ['neighbourhood', 'room_type', 'minimum_nights', 'price']
        if col in filtered_df.columns
    ]
    hover_title = 'name' if 'name' in filtered_df.columns else None

    # Scatter plot overlaid on an interactive map
    fig = px.scatter_map(
        filtered_df,
        lat='latitude',
        lon='longitude',
        color='price',
        hover_name=hover_title,
        hover_data=hover_cols,
        color_continuous_scale=px.colors.sequential.Viridis,
        zoom=11,
        map_style='open-street-map'
    )
    fig.update_traces(marker=dict(size=9, opacity=0.8))
    fig.update_layout(margin={"r": 0, "t": 10, "l": 0, "b": 0})

    count_text = (
        f"Showing {len(filtered_df):,} listings "
        f"(Minimum nights ≤ {selected_nights} | Price: ${low_price:,} – ${high_price:,})"
    )

    return count_text, fig


# --------------------------------------------------------------
# 5. RUN SERVER
if __name__ == '__main__':
    app.run(debug=True)
