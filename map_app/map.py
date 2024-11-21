import folium
import requests

# Download GeoJSON data for countries
geojson_url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
geojson_data = requests.get(geojson_url).json()

# Initialize the map
map = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB Positron")

# Add GeoJSON with hover effect
folium.GeoJson(
    geojson_data,
    style_function=lambda x: {
        "fillColor": "blue",  # Default color
        "color": "black",  # Border color
        "weight": 1,
        "fillOpacity": 0.2,  # Default opacity
    },
    highlight_function=lambda x: {
        "fillColor": "yellow",  # Highlight color
        "color": "orange",  # Highlight border color
        "weight": 2,
        "fillOpacity": 0.7,  # Highlight opacity
    },
    tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["Country:"]),  # Show country name
).add_to(map)

# Save the map
map.save("templates/map.html")






