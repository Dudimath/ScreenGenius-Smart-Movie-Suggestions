from flask import Flask, render_template, request
import numpy as np
import pandas as pd
from tensorflow.keras.models import model_from_json

app = Flask(__name__)

# Load the recommendation model when the application starts
with open("recommendation_model.json", "r") as json_file:
    loaded_model_json = json_file.read()

# Create a new model from the loaded architecture
loaded_model = model_from_json(loaded_model_json)

# Load the model weights from the HDF5 file
loaded_model.load_weights("recommendation_model_weights.h5")

# Load movie data that includes movie titles
ratings_df = pd.read_csv("dataset/ratings.csv")
movies_df = pd.read_csv("dataset/movies.csv")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_id = int(request.form["user_id"])

        all_movie_ids = np.unique(ratings_df['movieId'])

        # Create a list to store movie recommendations with titles and predicted ratings
        movie_recommendations = []

        # Predict ratings for the user for all movies
        for movie_id in all_movie_ids:
            predicted_rating = int(loaded_model.predict([np.array([user_id]), np.array([movie_id])])[0][0])

            # Find the movie title based on the movie ID
            movie_title = movies_df[movies_df['movieId'] == movie_id]['title'].values[0]

            # Append the recommendation to the list
            movie_recommendations.append({"title": movie_title, "predicted_rating": predicted_rating})

        # Sort the recommendations by predicted rating in descending order
        sorted_recommendations = sorted(movie_recommendations, key=lambda x: x["predicted_rating"], reverse=True)

        # Get the top 5 movie recommendations
        top_5_recommendations = sorted_recommendations[:5]

        # Render the recommendations on the web page along with the user ID
        return render_template("recommendations.html", recommendations=top_5_recommendations, user_id=user_id)

    # Render the initial form on a GET request
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)






