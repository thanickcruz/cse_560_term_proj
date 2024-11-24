from flask import Flask, render_template, request, jsonify

# Add the parent directory and import db functions
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from scripts.config import load_config
from scripts.connect import connect
import psycopg2

app = Flask(__name__)

# main page
@app.route("/")
def home():
    return render_template("index.html")

# map on main page
@app.route("/map")
def map():
    return render_template("map.html")  # Serve the map file

@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")  # Serve the leaderboard page

# query database from map interface
def query_country(country_name):
    """Query the database for information about the specified country."""
    query = """
    select name,
	    	playlists.track_id track_id,
		    playlists.track_name track_name,
		    duration_ms,
		    explicit,
		    current_popularity,
		    acousticness,
		    danceability,
		    instrumentalness,
		    key_signature,
		    mode,
		    tempo,
		    time_signature,
		    valence,
		    date_released,
		    artists.artist_id artist_id,
		    artists.artist_name artist_name,
		    genre
    from playlists
    join tracks on playlists.track_id=tracks.track_id
    join albums on playlists.album_id=albums.album_id
    join trackartists ta on playlists.track_id=ta.track_id
    join genreartists ga on ta.artist_id=ga.artist_id
    join artists on ga.artist_id=artists.artist_id
    where name like %s
    order by current_popularity desc
    limit 1;
    """
    try:
        # Connect to the PostgreSQL database
        config=load_config(filename="../../database.ini")
        connection = connect(config)
        cursor = connection.cursor()
        # Execute the query with the provided parameter
        cursor.execute(query, (f'%{country_name}%',))
        result = cursor.fetchall()
        # Close the connection
        cursor.close()
        connection.close()
        return result
    except Exception as e:
        print(f"Database error: {e}")
        return None
    
def format_country_name(country_name):
    # handle abbreviated countries from database
    rebels={'United States of America':'USA',
            'United Arab Emirates': 'UAE'}
    if country_name in rebels:
        return rebels[country_name]
    return country_name

@app.route('/query-country', methods=['POST'])
def query_country_endpoint():
    """Handle POST requests to query country data."""
    data = request.json
    country_name = format_country_name(data.get('country'))

    if not country_name:
        return jsonify({'error': 'No country provided'}), 400

    try:
        # Execute the query
        result = query_country(country_name)
        if result:
            # Convert result to a list of dictionaries for easier JSON conversion
            keys = ['name', 'track_id', 'track_name', 'duration_ms', 'explicit', 'current_popularity',
                    'acousticness', 'danceability', 'instrumentalness', 'key_signature', 'mode',
                    'tempo', 'time_signature', 'valence', 'date_released', 'artist_id', 'artist_name', 'genre']
            formatted_result = [dict(zip(keys, row)) for row in result]
            return jsonify({'result': formatted_result})
        else:
            return jsonify({'error': f'No data found for {country_name}'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# query database for leaderboard
def get_leaderboard():
    """Query the database for the top 10 most popular tracks with combined artist names."""
    query = """
   SELECT tracks.track_name, 
       STRING_AGG(DISTINCT artists.artist_name, ', ') AS artist_names,
       tracks.current_popularity, 
       COUNT(DISTINCT playlists.name) AS country_count 
    FROM tracks
    JOIN playlists ON tracks.track_id = playlists.track_id
    JOIN trackartists ON tracks.track_id = trackartists.track_id
    JOIN artists ON trackartists.artist_id = artists.artist_id
    GROUP BY tracks.track_id, tracks.track_name, tracks.current_popularity
    ORDER BY tracks.current_popularity DESC, country_count DESC
    LIMIT 10;
    """
    try:
        # Connect to the PostgreSQL database
        config = load_config(filename="../../database.ini")
        connection = connect(config)
        cursor = connection.cursor()
        # Execute the query
        cursor.execute(query)
        result = cursor.fetchall()
        # Close the connection
        cursor.close()
        connection.close()
        return result
    except Exception as e:
        print(f"Database error: {e}")
        return None

@app.route('/query-leaderboard', methods=['GET'])
def top_tracks_endpoint():
    """Endpoint to get the top 10 tracks."""
    try:
        tracks = get_leaderboard()
        if tracks:
            keys = ['track_name', 'artist_name', 'current_popularity', 'country_count']
            formatted_tracks = [dict(zip(keys, row)) for row in tracks]
            return jsonify({'result': formatted_tracks})
        else:
            return jsonify({'error': 'No tracks found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
    

