import folium
import requests
import re

map_path="templates/map.html"

print('Creating Folium map...')

# Initialize the map
map = folium.Map(location=[20, 0],
                 zoom_start=2, 
                 tiles="CartoDB Positron",
                 max_bounds=True)

# Download GeoJSON data for countries
geojson_url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
geojson_data = requests.get(geojson_url).json()

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
    # JavaScript code for click event as a string
).add_to(map)

# Save the map
map.save(map_path)

print('Folium map created!')

print('Adding custom functions...')

# handle clicking
def append_click_event_to_onEachFeature(html_file):
    # Read the HTML content
    with open(html_file, 'r') as file:
        html_content = file.read()

    # Search for the pattern that contains `layer.on({` to insert the click event handler
    pattern = re.compile(r'(layer\.on\(\{)', re.DOTALL)
    match = re.search(pattern, html_content)

    if not match:
        print("Pattern not found.")
        return

    # The click event handler code to append
    click_event_code = """
        click: function(e) {
            var countryName = e.target.feature.properties.name;

            // Send country name to the backend via a POST request
            fetch('/query-country', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ country: countryName }),
            })
            .then(response => response.json())
            .then(data => {
                console.log('Query result:', data);
                
             // Update the HTML container in the parent page
                var resultsHeading = window.parent.document.getElementById("country-header");
                if (resultsHeading) {
                    // Clear any existing content in the heading container
                    resultsHeading.innerHTML = "";
                    // Create a new h3 element
                    var h3Element = document.createElement("h3");
                    h3Element.textContent = countryName; // Set the country name as the content

                    // Append the h3 element to the header container
                    resultsHeading.appendChild(h3Element);
                }
                var resultsContainer = window.parent.document.getElementById("results-content");
                if (resultsContainer) {
                    if (data.result) {
                        resultsContainer.innerHTML = ""; // Clear previous results
                        data.result.forEach(row => {
                            const rowDiv = document.createElement("div");
                            rowDiv.classList.add("result-row");
                            rowDiv.innerHTML = `
                                <p><strong>Track:</strong> ${row.track_name} by ${row.artist_name}</p>
                                <p><strong>Genre:</strong> ${row.genre}</p>
                                <p><strong>Duration:</strong> ${row.duration_ms} ms</p>
                                <p><strong>Release Date:</strong> ${row.date_released}</p>
                                <hr>
                            `;
                            resultsContainer.appendChild(rowDiv);
                        });
                    } else {
                        resultsContainer.innerHTML = `<p>No data found for "${countryName}".</p>`;
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                var resultsContainer = window.parent.document.getElementById("results-content");
                if (resultsContainer) {
                    resultsContainer.innerHTML = `<p>Error fetching data. Please try again later.</p>`;
                }
            });
        },
    """

    # Insert the click event handler after `layer.on({`
    updated_html_content = html_content[:match.end()] + click_event_code + html_content[match.end():]

    # Write the modified content back to the file
    with open(html_file, 'w') as file:
        file.write(updated_html_content)

    print(f"Click event handler has been added to {html_file}")
# append_click_event_to_onEachFeature

append_click_event_to_onEachFeature(map_path)
