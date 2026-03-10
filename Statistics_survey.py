import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------
# Page setup
# ---------------------------------------------------
st.set_page_config(
    page_title="Introduction to Social Statistics Survey",
    page_icon="📊",
    layout="centered"
)

# ---------------------------------------------------
# Storage
# For Streamlit Cloud, this file works during the app session,
# but CSV storage is not ideal for long-term persistence.
# ---------------------------------------------------
BASE_DIR = Path(".")
DATA_FILE = BASE_DIR / "statistics_survey_responses.csv"

# Use Streamlit secrets if available; otherwise fallback
INSTRUCTOR_PASSWORD = st.secrets.get("instructor_password", "password123")

# ---------------------------------------------------
# Helpers
# ---------------------------------------------------
def load_data():
    if DATA_FILE.exists():
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=[
        "timestamp",
        "name",
        "name_key",
        "age",
        "work_status",
        "lives_in_texas",
        "year_student",
        "first_generation",
        "veteran",
        "major",
        "movie_genre",
        "music_genre",
        "favorite_food",
        "favorite_season",
        "morning_or_night",
        "pet_preference"
    ])


def save_response(response_dict):
    df_existing = load_data()
    df_new = pd.DataFrame([response_dict])
    df_all = pd.concat([df_existing, df_new], ignore_index=True)
    df_all.to_csv(DATA_FILE, index=False)


def normalize_name(name):
    return " ".join(name.strip().lower().split())


def value_counts_df(df, column, label):
    counts = df[column].value_counts(dropna=False).reset_index()
    counts.columns = [label, "Count"]
    counts["Percent"] = (counts["Count"] / counts["Count"].sum() * 100).round(1)
    return counts


# ---------------------------------------------------
# Load data
# ---------------------------------------------------
df = load_data()

# ---------------------------------------------------
# Header
# ---------------------------------------------------
st.title("Introduction to Social Statistics Survey")
st.write(
    "This is a fun survey designed to help you get to know your classmates a bit better. "
    "Once you submit, you will be able to see the class results in aggregate."
)

st.info("Please submit only once. Only aggregate class results are shown to students.")

# ---------------------------------------------------
# Survey form
# ---------------------------------------------------
with st.form("statistics_survey_form", clear_on_submit=True):
    st.subheader("About You")

    name = st.text_input("Full name")
    age = st.number_input("Age", min_value=16, max_value=100, value=18, step=1)

    work_status = st.radio(
        "Which best describes you?",
        options=["Work full-time", "Work part-time", "Student only"]
    )

    lives_in_texas = st.radio(
        "Do you live in Texas?",
        options=["Yes", "No"]
    )

    year_student = st.selectbox(
        "What year student are you?",
        options=[
            "Freshman",
            "Sophomore",
            "Junior",
            "Senior",
            "Graduate student",
            "Other"
        ]
    )

    first_generation = st.radio(
        "Are you a first-generation student?",
        options=["Yes", "No", "Not sure"]
    )

    veteran = st.radio(
        "Are you a veteran?",
        options=["Yes", "No"]
    )

    major = st.text_input("What is your major?")

    st.subheader("Fun Questions")

    movie_genre = st.selectbox(
        "What is your favorite movie genre?",
        options=[
            "Action",
            "Comedy",
            "Drama",
            "Horror",
            "Romance",
            "Science Fiction",
            "Fantasy",
            "Thriller",
            "Documentary",
            "Animation",
            "Other"
        ]
    )

    music_genre = st.selectbox(
        "What is your favorite genre of music?",
        options=[
            "Pop",
            "Rock",
            "Hip-Hop/Rap",
            "Country",
            "R&B",
            "Electronic",
            "Jazz",
            "Classical",
            "Latin",
            "Metal",
            "Other"
        ]
    )

    favorite_food = st.selectbox(
        "Favorite type of food?",
        options=[
            "Mexican",
            "Italian",
            "American",
            "Asian",
            "Mediterranean",
            "BBQ",
            "Seafood",
            "Desserts",
            "Fast food",
            "Other"
        ]
    )

    favorite_season = st.selectbox(
        "Favorite season?",
        options=["Spring", "Summer", "Fall", "Winter"]
    )

    morning_or_night = st.radio(
        "Are you more of a morning person or night person?",
        options=["Morning", "Night", "A bit of both"]
    )

    pet_preference = st.radio(
        "Do you prefer dogs or cats?",
        options=["Dogs", "Cats", "Both", "Neither"]
    )

    consent = st.checkbox("I confirm this is my own response and I am only submitting once.")

    submitted = st.form_submit_button("Submit Survey")

# ---------------------------------------------------
# Submission logic
# ---------------------------------------------------
if submitted:
    clean_name = name.strip()
    name_key = normalize_name(clean_name)

    if not clean_name:
        st.error("Please enter your full name.")
    elif not major.strip():
        st.error("Please enter your major.")
    elif not consent:
        st.error("Please confirm before submitting.")
    elif "name_key" in df.columns and name_key in df["name_key"].astype(str).tolist():
        st.error("A response has already been submitted under this name.")
    else:
        response = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": clean_name,
            "name_key": name_key,
            "age": age,
            "work_status": work_status,
            "lives_in_texas": lives_in_texas,
            "year_student": year_student,
            "first_generation": first_generation,
            "veteran": veteran,
            "major": major.strip(),
            "movie_genre": movie_genre,
            "music_genre": music_genre,
            "favorite_food": favorite_food,
            "favorite_season": favorite_season,
            "morning_or_night": morning_or_night,
            "pet_preference": pet_preference
        }

        try:
            save_response(response)
            st.success("Thanks — your response has been submitted.")
            st.rerun()
        except Exception as e:
            st.error(f"An error occurred while saving your response: {e}")

# ---------------------------------------------------
# Reload data after possible submit
# ---------------------------------------------------
df = load_data()

# ---------------------------------------------------
# Aggregate results
# ---------------------------------------------------
st.markdown("---")
st.header("Live Class Results")

if df.empty:
    st.info("No responses have been submitted yet.")
else:
    st.write(f"**Total responses:** {len(df)}")

    age_series = pd.to_numeric(df["age"], errors="coerce").dropna()
    if not age_series.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Average age", f"{age_series.mean():.1f}")
        c2.metric("Youngest", f"{int(age_series.min())}")
        c3.metric("Oldest", f"{int(age_series.max())}")

    st.subheader("Work Status")
    status_df = value_counts_df(df, "work_status", "Work Status")
    st.dataframe(status_df, width="stretch", hide_index=True)
    st.bar_chart(status_df.set_index("Work Status")["Count"])

    st.subheader("Do You Live in Texas?")
    texas_df = value_counts_df(df, "lives_in_texas", "Lives in Texas")
    st.dataframe(texas_df, width="stretch", hide_index=True)
    st.bar_chart(texas_df.set_index("Lives in Texas")["Count"])

    st.subheader("Year in School")
    year_df = value_counts_df(df, "year_student", "Year")
    st.dataframe(year_df, width="stretch", hide_index=True)
    st.bar_chart(year_df.set_index("Year")["Count"])

    st.subheader("First-Generation Student")
    first_gen_df = value_counts_df(df, "first_generation", "First Generation")
    st.dataframe(first_gen_df, width="stretch", hide_index=True)
    st.bar_chart(first_gen_df.set_index("First Generation")["Count"])

    st.subheader("Veteran Status")
    veteran_df = value_counts_df(df, "veteran", "Veteran")
    st.dataframe(veteran_df, width="stretch", hide_index=True)
    st.bar_chart(veteran_df.set_index("Veteran")["Count"])

    st.subheader("Favorite Movie Genre")
    movie_df = value_counts_df(df, "movie_genre", "Movie Genre")
    st.dataframe(movie_df, width="stretch", hide_index=True)
    st.bar_chart(movie_df.set_index("Movie Genre")["Count"])

    st.subheader("Favorite Music Genre")
    music_df = value_counts_df(df, "music_genre", "Music Genre")
    st.dataframe(music_df, width="stretch", hide_index=True)
    st.bar_chart(music_df.set_index("Music Genre")["Count"])

    st.subheader("Favorite Food")
    food_df = value_counts_df(df, "favorite_food", "Favorite Food")
    st.dataframe(food_df, width="stretch", hide_index=True)
    st.bar_chart(food_df.set_index("Favorite Food")["Count"])

    st.subheader("Favorite Season")
    season_df = value_counts_df(df, "favorite_season", "Favorite Season")
    st.dataframe(season_df, width="stretch", hide_index=True)
    st.bar_chart(season_df.set_index("Favorite Season")["Count"])

    st.subheader("Morning or Night Person")
    mn_df = value_counts_df(df, "morning_or_night", "Preference")
    st.dataframe(mn_df, width="stretch", hide_index=True)
    st.bar_chart(mn_df.set_index("Preference")["Count"])

    st.subheader("Dogs or Cats?")
    pet_df = value_counts_df(df, "pet_preference", "Pet Preference")
    st.dataframe(pet_df, width="stretch", hide_index=True)
    st.bar_chart(pet_df.set_index("Pet Preference")["Count"])

    st.subheader("Most Common Majors")
    major_df = value_counts_df(df, "major", "Major")
    st.dataframe(major_df, width="stretch", hide_index=True)

# ---------------------------------------------------
# Instructor-only view
# ---------------------------------------------------
st.markdown("---")
st.subheader("Instructor Access")

password = st.text_input("Enter instructor password", type="password")

if password:
    if password == INSTRUCTOR_PASSWORD:
        st.success("Instructor access granted.")

        if df.empty:
            st.write("No submissions yet.")
        else:
            credit_df = df[["name", "timestamp"]].copy()
            credit_df["timestamp"] = pd.to_datetime(credit_df["timestamp"], errors="coerce")
            credit_df["timestamp"] = credit_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
            credit_df = credit_df.sort_values("name")
            credit_df.columns = ["Student Name", "Submission Time"]

            st.dataframe(credit_df, width="stretch", hide_index=True)

            csv_download = credit_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download submission list as CSV",
                data=csv_download,
                file_name="statistics_survey_submissions.csv",
                mime="text/csv"
            )
    else:
        st.error("Incorrect password.")