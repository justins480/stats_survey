import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------
# Page setup
# ---------------------------------------------------
st.set_page_config(
    page_title="Introduction to Social Statistics Survey",
    page_icon="📊",
    layout="centered"
)

INSTRUCTOR_PASSWORD = st.secrets["instructor_password"]
GSHEET_NAME = st.secrets["gsheet_name"]

# ---------------------------------------------------
# Google Sheets connection
# ---------------------------------------------------
def connect_to_gsheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )

    client = gspread.authorize(creds)
    sheet = client.open(GSHEET_NAME).sheet1
    return sheet


def load_data():
    expected_cols = [
        "timestamp",
        "name",
        "name_key",
        "age",
        "work_status",
        "lives_in_texas",
        "year_student",
        "first_generation",
        "works_in_cj",
        "veteran",
        "major",
        "study_hours",
        "expected_performance",
        "expected_performance_score",
        "sleep_hours",
        "movie_genre",
        "music_genre",
        "favorite_food",
        "favorite_season",
        "morning_or_night",
        "pet_preference"
    ]

    try:
        sheet = connect_to_gsheet()
        records = sheet.get_all_records()
        df = pd.DataFrame(records)

        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""

        return df[expected_cols]
    except Exception:
        return pd.DataFrame(columns=expected_cols)


def append_response(response_dict):
    sheet = connect_to_gsheet()
    row = [
        response_dict["timestamp"],
        response_dict["name"],
        response_dict["name_key"],
        response_dict["age"],
        response_dict["work_status"],
        response_dict["lives_in_texas"],
        response_dict["year_student"],
        response_dict["first_generation"],
        response_dict["works_in_cj"],
        response_dict["veteran"],
        response_dict["major"],
        response_dict["study_hours"],
        response_dict["expected_performance"],
        response_dict["expected_performance_score"],
        response_dict["sleep_hours"],
        response_dict["movie_genre"],
        response_dict["music_genre"],
        response_dict["favorite_food"],
        response_dict["favorite_season"],
        response_dict["morning_or_night"],
        response_dict["pet_preference"]
    ]
    sheet.append_row(row)


def normalize_name(name):
    return " ".join(name.strip().lower().split())


def value_counts_df(df, column, label):
    counts = (
        df[column]
        .fillna("No response")
        .astype(str)
        .str.strip()
        .replace("", "No response")
        .value_counts(dropna=False)
        .reset_index()
    )
    counts.columns = [label, "Count"]
    counts["Percent"] = (counts["Count"] / counts["Count"].sum() * 100).round(1)
    return counts


def plot_categorical(df, column, title, label_name):
    plot_df = value_counts_df(df, column, label_name)

    st.subheader(title)

    if plot_df.empty:
        st.info("No responses yet.")
        return

    fig, ax = plt.subplots(figsize=(8, 5))

    # 4 or fewer categories -> pie chart
    if len(plot_df) <= 4:
        labels = [
            f"{row[label_name]} ({row['Percent']:.1f}%)"
            for _, row in plot_df.iterrows()
        ]

        ax.pie(
            plot_df["Count"],
            labels=labels,
            autopct="%1.1f%%",
            startangle=90
        )
        ax.axis("equal")
        st.pyplot(fig)

    # 5 or more categories -> bar chart
    else:
        bars = ax.bar(plot_df[label_name], plot_df["Count"])
        ax.set_ylabel("Count")
        ax.set_xlabel("")
        ax.set_title(title)
        plt.xticks(rotation=45, ha="right")

        max_count = plot_df["Count"].max()

        for bar, pct in zip(bars, plot_df["Percent"]):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + max_count * 0.02,
                f"{pct:.1f}%",
                ha="center",
                va="bottom"
            )

        ax.set_ylim(0, max_count * 1.15 if max_count > 0 else 1)
        st.pyplot(fig)

    st.dataframe(plot_df, width="stretch", hide_index=True)


def plot_scatter(df, x_col, y_col, title, x_label, y_label, y_ticks=None, y_ticklabels=None):
    plot_df = df[[x_col, y_col]].copy()
    plot_df[x_col] = pd.to_numeric(plot_df[x_col], errors="coerce")
    plot_df[y_col] = pd.to_numeric(plot_df[y_col], errors="coerce")
    plot_df = plot_df.dropna()

    st.subheader(title)

    if plot_df.empty:
        st.info("No responses yet.")
        return

    fig, ax = plt.subplots(figsize=(8,5))

    # scatter points
    ax.scatter(plot_df[x_col], plot_df[y_col], alpha=0.7)

    # regression line
    z = np.polyfit(plot_df[x_col], plot_df[y_col], 1)
    p = np.poly1d(z)
    ax.plot(plot_df[x_col], p(plot_df[x_col]), linewidth=2)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    if y_ticks is not None:
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_ticklabels)

    st.pyplot(fig)
   


# ---------------------------------------------------
# Likert mapping
# ---------------------------------------------------
likert_map = {
    "Very poorly": 1,
    "Poorly": 2,
    "Average": 3,
    "Well": 4,
    "Very well": 5
}

likert_labels = {
    1: "Very poorly",
    2: "Poorly",
    3: "Average",
    4: "Well",
    5: "Very well"
}

# ---------------------------------------------------
# Load data
# ---------------------------------------------------
df = load_data()

# ---------------------------------------------------
# Header
# ---------------------------------------------------
st.title("Introduction to Social Statistics Survey")
st.write(
    "Hello class. I build this application to collect some quick data. This is a fun survey designed for you to get to know your classmates a bit better. " 
    "Your name will not be revealed to the class, but I will be able to see your responses. "
    "Once you submit, you will be able to see the class results in aggregate just below the survey. However, if you are one of the first onces to complete it, there will not be much to show."
    
)

st.info("Please submit only once. Others will not be able to see your individual answers")

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

    works_in_cj = st.radio(
        "Do you currently work in the criminal justice system?",
        options=["Yes", "No"]
    )

    veteran = st.radio(
        "Are you a veteran?",
        options=["Yes", "No"]
    )

    major = st.selectbox(
        "What is your major?",
        options=[
            "Criminology",
            "Sociology",
            "Social Work",
            "Anthropology",
            "Other"
        ]
    )

    st.subheader("Study and Sleep Questions")

    study_hours = st.number_input(
        "How many hours per week do you study?",
        min_value=0.0,
        max_value=100.0,
        value=5.0,
        step=0.5
    )

    expected_performance = st.selectbox(
        "How well do you expect to perform in this class?",
        options=[
            "Very poorly",
            "Poorly",
            "Average",
            "Well",
            "Very well"
        ]
    )

    sleep_hours = st.number_input(
        "How many hours of sleep do you get per night on average? (Answer to the nearest half hour, e.g., 7.5 for 7 and a half hours)",
        min_value=0.0,
        max_value=15.0,
        value=7.0,
        step=0.5
    )

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

    submitted = st.form_submit_button("Submit Survey")

# ---------------------------------------------------
# Submission logic
# ---------------------------------------------------
if submitted:
    clean_name = name.strip()
    name_key = normalize_name(clean_name)
    expected_performance_score = likert_map[expected_performance]

    if not clean_name:
        st.error("Please enter your full name.")
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
            "works_in_cj": works_in_cj,
            "veteran": veteran,
            "major": major,
            "study_hours": study_hours,
            "expected_performance": expected_performance,
            "expected_performance_score": expected_performance_score,
            "sleep_hours": sleep_hours,
            "movie_genre": movie_genre,
            "music_genre": music_genre,
            "favorite_food": favorite_food,
            "favorite_season": favorite_season,
            "morning_or_night": morning_or_night,
            "pet_preference": pet_preference
        }

        try:
            append_response(response)
            st.success("Thanks — your response has been submitted.")
            st.rerun()
        except Exception as e:
            st.error(f"An error occurred while saving your response: {e}")

# ---------------------------------------------------
# Reload data
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
    st.metric("Total Responses", len(df))

    age_series = pd.to_numeric(df["age"], errors="coerce").dropna()
    if not age_series.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Average age", f"{age_series.mean():.1f}")
        c2.metric("Youngest", f"{int(age_series.min())}")
        c3.metric("Oldest", f"{int(age_series.max())}")

    study_series = pd.to_numeric(df["study_hours"], errors="coerce").dropna()
    sleep_series = pd.to_numeric(df["sleep_hours"], errors="coerce").dropna()

    if not study_series.empty or not sleep_series.empty:
        c1, c2 = st.columns(2)
        if not study_series.empty:
            c1.metric("Average study hours/week", f"{study_series.mean():.1f}")
        if not sleep_series.empty:
            c2.metric("Average sleep hours/night", f"{sleep_series.mean():.1f}")

    plot_categorical(df, "work_status", "Work Status", "Work Status")
    plot_categorical(df, "lives_in_texas", "Do You Live in Texas?", "Lives in Texas")
    plot_categorical(df, "year_student", "Year in School", "Year")
    plot_categorical(df, "first_generation", "First-Generation Student", "First Generation")
    plot_categorical(df, "works_in_cj", "Currently Working in the Criminal Justice System", "Works in CJ")
    plot_categorical(df, "veteran", "Veteran Status", "Veteran")
    plot_categorical(df, "major", "Most Common Majors", "Major")
    plot_categorical(df, "expected_performance", "Expected Performance in This Class", "Expected Performance")
    plot_categorical(df, "movie_genre", "Favorite Movie Genre", "Movie Genre")
    plot_categorical(df, "music_genre", "Favorite Music Genre", "Music Genre")
    plot_categorical(df, "favorite_food", "Favorite Food", "Favorite Food")
    plot_categorical(df, "favorite_season", "Favorite Season", "Favorite Season")
    plot_categorical(df, "morning_or_night", "Morning or Night Person", "Preference")
    plot_categorical(df, "pet_preference", "Dogs or Cats?", "Pet Preference")

    plot_scatter(
        df,
        x_col="study_hours",
        y_col="expected_performance_score",
        title="Study Hours vs Expected Performance",
        x_label="Hours Studied Per Week",
        y_label="Expected Performance",
        y_ticks=[1, 2, 3, 4, 5],
        y_ticklabels=["Very poorly", "Poorly", "Average", "Well", "Very well"]
    )

    plot_scatter(
        df,
        x_col="sleep_hours",
        y_col="expected_performance_score",
        title="Sleep Hours vs Expected Performance",
        x_label="Average Sleep Hours Per Night",
        y_label="Expected Performance",
        y_ticks=[1, 2, 3, 4, 5],
        y_ticklabels=["Very poorly", "Poorly", "Average", "Well", "Very well"]
    )

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
            credit_df = df[[
                "name",
                "timestamp",
                "major",
                "study_hours",
                "expected_performance",
                "sleep_hours"
            ]].copy()

            credit_df["timestamp"] = pd.to_datetime(credit_df["timestamp"], errors="coerce")
            credit_df["timestamp"] = credit_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
            credit_df = credit_df.sort_values("name")
            credit_df.columns = [
                "Student Name",
                "Submission Time",
                "Major",
                "Study Hours/Week",
                "Expected Performance",
                "Sleep Hours/Night"
            ]

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