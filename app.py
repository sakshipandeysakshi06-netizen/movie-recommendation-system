import streamlit as st
import pandas as pd


from recommendation import MovieRecommender


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #0f1117;
    color: white;
}

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
    color: white;
    margin-top: 20px;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #aaaaaa;
    margin-bottom: 35px;
}

.movie-card {
    background: linear-gradient(145deg, #1c1f2b, #151722);
    border: 1px solid #303442;
    border-radius: 18px;
    padding: 24px;
    margin-bottom: 22px;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.35);
}

.movie-number {
    color: #ff4b4b;
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 10px;
}

.movie-title {
    font-size: 26px;
    font-weight: 700;
    color: white;
    margin-bottom: 12px;
}

.movie-info {
    font-size: 16px;
    color: #cccccc;
    margin-bottom: 12px;
}

.score {
    display: inline-block;
    background-color: #292e3d;
    color: #ffcc00;
    padding: 7px 14px;
    border-radius: 20px;
    font-weight: 600;
}

section[data-testid="stSidebar"] {
    background-color: #151821;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD RECOMMENDER
# ============================================================

@st.cache_resource
def load_recommender():

    recommender = MovieRecommender(
        "data/ratings.csv",
        "data/movies.csv"
    )

    return recommender


try:

    recommender = load_recommender()

except Exception as e:

    st.error("Unable to load the recommendation system.")

    st.error(str(e))

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Settings")

    st.subheader("👤 User Settings")

    user_id = st.number_input(
        "Enter User ID",
        min_value=1,
        value=1,
        step=1
    )

    number_of_movies = st.slider(
        "Number of Recommendations",
        min_value=1,
        max_value=20,
        value=10
    )

    st.divider()

    st.subheader("💡 How it works")

    st.markdown("""
**1.** User ratings are collected.

**2.** Similar users are identified.

**3.** Their movie preferences are analyzed.

**4.** Movies not watched by the user are selected.

**5.** The highest-scoring movies are recommended.
""")


# ============================================================
# MAIN TITLE
# ============================================================

st.markdown(
    '<div class="main-title">🎬 Movie Recommendation System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Discover movies based on users with similar preferences</div>',
    unsafe_allow_html=True
)


# ============================================================
# GET RECOMMENDATIONS
# ============================================================

try:

    recommendations = recommender.recommend_movies(
        user_id=int(user_id),
        number_of_movies=int(number_of_movies)
    )

except Exception as e:

    st.error("Something went wrong while generating recommendations.")

    st.error(str(e))

    st.stop()


# ============================================================
# DISPLAY RECOMMENDATIONS
# ============================================================

st.subheader("🍿 Recommended Movies")


if recommendations is None or recommendations.empty:

    st.warning("No recommendations found for this user.")

else:

    recommendations = recommendations.reset_index(drop=True)

    for index, movie in recommendations.iterrows():

        title = movie.get("title", "Unknown Movie")

        genres = movie.get("genres", "Unknown")

        score = movie.get("recommendation_score", 0)

        try:
            score = float(score)
        except:
            score = 0.0


        # IMPORTANT:
        # The HTML starts directly after the triple quote.
        # This prevents Streamlit from treating it as code.

        movie_html = f"""<div class="movie-card">
<div class="movie-number">🎬 Recommendation #{index + 1}</div>
<div class="movie-title">{title}</div>
<div class="movie-info">🎭 <b>Genres:</b> {genres}</div>
<div class="score">⭐ Recommendation Score: {score:.2f}</div>
</div>"""

        st.markdown(
            movie_html,
            unsafe_allow_html=True
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    '<div style="text-align:center; padding:25px; color:#888888;">'
    '<b>🎬 Movie Recommendation System</b>'
    '<br><br>'
    'Powered by Collaborative Filtering and Cosine Similarity'
    '</div>',
    unsafe_allow_html=True
)
# ============================================================
# MOVIE CHATBOT
# ============================================================

st.divider()

st.subheader("🤖 Movie Assistant")

st.markdown(
    "Ask me about your recommended movies, genres, or what you should watch!"
)

# Store chat history
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": (
                "Hi! 👋 I'm your Movie Assistant. "
                "Ask me things like:\n\n"
                "- Which movie should I watch?\n"
                "- What comedy movies do I have?\n"
                "- Show me my recommendations.\n"
                "- Tell me about the first movie."
            )
        }
    ]

# Display previous messages
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input
user_message = st.chat_input("Ask about your movie recommendations...")

if user_message:

    # Add user message
    st.session_state.chat_messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    question = user_message.lower().strip()

    # --------------------------------------------------------
    # Generate chatbot response
    # --------------------------------------------------------

    response = ""

    # If no recommendations exist
    if recommendations is None or recommendations.empty:

        response = (
            "I couldn't find recommendations for the selected user. "
            "Please try another User ID."
        )

    else:

        # Convert recommendation data into an easier format
        movie_data = recommendations.reset_index(drop=True)

        # ----------------------------------------------------
        # 1. Show recommendations
        # ----------------------------------------------------

        if (
            "recommend" in question
            or "suggest" in question
            or "movies" in question
        ):

            response = "🎬 Here are your recommended movies:\n\n"

            for i, movie in movie_data.iterrows():

                title = movie.get("title", "Unknown Movie")
                genres = movie.get("genres", "Unknown")
                score = movie.get("recommendation_score", 0)

                try:
                    score = float(score)
                except:
                    score = 0.0

                response += (
                    f"**{i + 1}. {title}**\n"
                    f"🎭 Genres: {genres}\n"
                    f"⭐ Score: {score:.2f}\n\n"
                )

        # ----------------------------------------------------
        # 2. Best movie
        # ----------------------------------------------------

        elif (
            "best" in question
            or "top" in question
            or "first" in question
            or "watch" in question
        ):

            movie = movie_data.iloc[0]

            title = movie.get("title", "Unknown Movie")
            genres = movie.get("genres", "Unknown")
            score = movie.get("recommendation_score", 0)

            try:
                score = float(score)
            except:
                score = 0.0

            response = (
                f"🍿 **I recommend watching {title}.**\n\n"
                f"🎭 Genres: {genres}\n"
                f"⭐ Recommendation Score: {score:.2f}\n\n"
                "This movie received the highest recommendation score "
                "among your current recommendations."
            )

        # ----------------------------------------------------
        # 3. Comedy movies
        # ----------------------------------------------------

        elif "comedy" in question:

            matches = movie_data[
                movie_data["genres"]
                .fillna("")
                .str.lower()
                .str.contains("comedy")
            ]

            if matches.empty:
                response = "😕 I don't see any comedy movies in your current recommendations."

            else:
                response = "😂 Your recommended comedy movies are:\n\n"

                for _, movie in matches.iterrows():

                    response += (
                        f"🎬 **{movie['title']}**\n"
                        f"🎭 {movie['genres']}\n\n"
                    )

        # ----------------------------------------------------
        # 4. Action movies
        # ----------------------------------------------------

        elif "action" in question:

            matches = movie_data[
                movie_data["genres"]
                .fillna("")
                .str.lower()
                .str.contains("action")
            ]

            if matches.empty:
                response = "😕 I don't see any action movies in your current recommendations."

            else:
                response = "💥 Your recommended action movies are:\n\n"

                for _, movie in matches.iterrows():

                    response += (
                        f"🎬 **{movie['title']}**\n"
                        f"🎭 {movie['genres']}\n\n"
                    )

        # ----------------------------------------------------
        # 5. Romance movies
        # ----------------------------------------------------

        elif "romance" in question:

            matches = movie_data[
                movie_data["genres"]
                .fillna("")
                .str.lower()
                .str.contains("romance")
            ]

            if matches.empty:
                response = "😕 I don't see any romance movies in your current recommendations."

            else:
                response = "❤️ Your recommended romance movies are:\n\n"

                for _, movie in matches.iterrows():

                    response += (
                        f"🎬 **{movie['title']}**\n"
                        f"🎭 {movie['genres']}\n\n"
                    )

        # ----------------------------------------------------
        # 6. Ask about a specific movie
        # ----------------------------------------------------

        else:

            found_movie = None

            for _, movie in movie_data.iterrows():

                title = str(movie.get("title", ""))

                if title.lower() in question:
                    found_movie = movie
                    break

            if found_movie is not None:

                title = found_movie.get("title", "Unknown Movie")
                genres = found_movie.get("genres", "Unknown")
                score = found_movie.get("recommendation_score", 0)

                try:
                    score = float(score)
                except:
                    score = 0.0

                response = (
                    f"🎬 **{title}**\n\n"
                    f"🎭 Genres: {genres}\n"
                    f"⭐ Recommendation Score: {score:.2f}\n\n"
                    "This movie is included in your personalized recommendations."
                )

            else:

                response = (
                    "🤔 I can help you with your recommendations!\n\n"
                    "Try asking:\n"
                    "- **Which movie should I watch?**\n"
                    "- **Show me my recommendations**\n"
                    "- **Which comedy movies do I have?**\n"
                    "- **Which action movies do I have?**\n"
                    "- **Which romance movies do I have?**"
                )

    # Add assistant response
    st.session_state.chat_messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

    # Refresh page so new messages appear
    st.rerun()


# ============================================================
# FOOTER
# ============================================================