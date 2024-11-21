from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/map")
def map():
    return render_template("map.html")  # Serve the map file

if __name__ == "__main__":
    app.run(debug=True)

