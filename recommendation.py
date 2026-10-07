import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


class MovieRecommender:

    def __init__(self, ratings_file, movies_file):

        # Load movie and rating data
        self.ratings = pd.read_csv(ratings_file)
        self.movies = pd.read_csv(movies_file)

        # Create User-Movie Rating Matrix
        self.user_movie_matrix = self.ratings.pivot_table(
            index="userId",
            columns="movieId",
            values="rating"
        ).fillna(0)

        # Calculate similarity between users
        similarity = cosine_similarity(
            self.user_movie_matrix
        )

        # Convert similarity into a DataFrame
        self.similarity_df = pd.DataFrame(
            similarity,
            index=self.user_movie_matrix.index,
            columns=self.user_movie_matrix.index
        )

    def recommend_movies(self, user_id, number_of_movies=10):

        # Check whether user exists
        if user_id not in self.user_movie_matrix.index:
            return pd.DataFrame()

        # Find users similar to the selected user
        similar_users = (
            self.similarity_df[user_id]
            .sort_values(ascending=False)
            .iloc[1:11]
        )

        recommendations = {}

        # Look at movies liked by similar users
        for similar_user, similarity_score in similar_users.items():

            user_ratings = self.user_movie_matrix.loc[
                similar_user
            ]

            for movie_id, rating in user_ratings.items():

                # Ignore movies that were not rated
                if rating <= 0:
                    continue

                # Check if our target user has already rated it
                target_rating = self.user_movie_matrix.loc[
                    user_id, movie_id
                ]

                if target_rating == 0:

                    if movie_id not in recommendations:
                        recommendations[movie_id] = 0

                    recommendations[movie_id] += (
                        similarity_score * rating
                    )

        # Sort movies according to recommendation score
        sorted_movies = sorted(
            recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Select top movies
        top_movies = sorted_movies[:number_of_movies]

        if not top_movies:
            return pd.DataFrame()

        movie_ids = [
            movie_id
            for movie_id, score in top_movies
        ]

        # Get movie information
        result = self.movies[
            self.movies["movieId"].isin(movie_ids)
        ].copy()

        # Add recommendation score
        score_dictionary = dict(top_movies)

        result["recommendation_score"] = (
            result["movieId"].map(score_dictionary)
        )

        # Sort by recommendation score
        result = result.sort_values(
            "recommendation_score",
            ascending=False
        )

        return result


# ------------------------------------------------
# TEST THE RECOMMENDER
# ------------------------------------------------

if __name__ == "__main__":

    print("Loading movie recommendation system...")

    recommender = MovieRecommender(
        "data/ratings.csv",
        "data/movies.csv"
    )

    print("Generating recommendations...")

    recommendations = recommender.recommend_movies(
        user_id=1,
        number_of_movies=10
    )

    print("\nRecommended Movies:\n")

    if recommendations.empty:

        print("No recommendations found.")

    else:

        for _, movie in recommendations.iterrows():

            print(
                f"🎬 {movie['title']} "
                f" | Genre: {movie['genres']} "
                f" | Score: "
                f"{movie['recommendation_score']:.2f}"
            )