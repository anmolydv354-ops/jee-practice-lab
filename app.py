import streamlit as st
import pandas as pd

# ==============================
# PAGE SETUP
# ==============================

st.set_page_config(
    page_title="JEE Practice Lab",
    page_icon="🎓",
    layout="wide"
)

# ==============================
# LOAD QUESTIONS
# ==============================

@st.cache_data
def load_questions():
    return pd.read_csv("questions.csv")

df = load_questions()

# ==============================
# HEADER
# ==============================

st.title("🎓 JEE Practice Lab")
st.markdown(
    """
    ### 🎯 About the Project

    **JEE Practice Lab** is a Python-based adaptive
    practice platform designed to help JEE students
    practice questions and understand their strengths
    and weaknesses.

    **Key Features:**
    - JEE Main and JEE Advanced practice
    - Subject and chapter-based practice
    - Difficulty-based filtering
    - Automatic scoring and accuracy analysis
    - Chapter-wise weakness detection
    - Personalized practice recommendations
    - Progress tracking

    **Technology:** Python • Streamlit • Pandas
    """
)
st.subheader(
    "Adaptive JEE Practice & Performance Analysis"
)

st.write(
    "The objective of this project is to build a "
    "data-driven JEE practice platform that helps "
    "students identify weak chapters and improve "
    "their preparation through targeted practice."
)

st.divider()

# ==============================
# SIDEBAR
# ==============================

st.sidebar.header("⚙️ Test Settings")

# Exam
exam = st.sidebar.selectbox(
    "Exam",
    sorted(df["exam"].unique())
)

# Subject
subject = st.sidebar.selectbox(
    "Subject",
    sorted(
        df[df["exam"] == exam]["subject"].unique()
    )
)

# Chapter
chapter_list = sorted(
    df[
        (df["exam"] == exam) &
        (df["subject"] == subject)
    ]["chapter"].unique()
)

chapter = st.sidebar.selectbox(
    "Chapter",
    chapter_list
)

# Difficulty
difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["All", "Easy", "Medium", "Hard"]
)

# ==============================
# FILTER QUESTIONS
# ==============================

available_questions = df[
    (df["exam"] == exam) &
    (df["subject"] == subject) &
    (df["chapter"] == chapter)
]

if difficulty != "All":

    available_questions = available_questions[
        available_questions["difficulty"] == difficulty
    ]

# ==============================
# QUESTION COUNT
# ==============================

if len(available_questions) == 0:

    st.sidebar.warning(
        "No questions available for this selection."
    )

    number_of_questions = 0

elif len(available_questions) == 1:

    number_of_questions = 1

    st.sidebar.info(
        "Only 1 question available."
    )

else:

    number_of_questions = st.sidebar.slider(
        "Number of Questions",
        min_value=1,
        max_value=len(available_questions),
        value=min(3, len(available_questions))
    )

# ==============================
# SESSION STATE
# ==============================

if "questions" not in st.session_state:
    st.session_state.questions = None

if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "performance_history" not in st.session_state:
    st.session_state.performance_history = []
# ==============================
# START TEST
# ==============================

if st.button(
    "🚀 Start Test",
    type="primary"
):

    if number_of_questions > 0:

        st.session_state.questions = (
            available_questions
            .sample(number_of_questions)
            .to_dict("records")
        )

        st.session_state.submitted = False

# ==============================
# DISPLAY TEST
# ==============================

if st.session_state.questions:

    st.header("📝 Test")

    answers = {}

    for i, question in enumerate(
        st.session_state.questions
    ):

        st.markdown(
            f"### Question {i + 1}"
        )

        st.write(
            question["question"]
        )

        options = {
            "A": question["option_a"],
            "B": question["option_b"],
            "C": question["option_c"],
            "D": question["option_d"]
        }

        selected = st.radio(
            "Select your answer:",
            list(options.keys()),
            format_func=lambda x:
                f"{x}. {options[x]}",
            key=f"answer_{i}"
        )

        answers[i] = selected

        st.divider()

    # ==========================
    # SUBMIT TEST
    # ==========================

    if st.button(
        "✅ Submit Test",
        type="primary"
    ):

        score = 0
        results = []

        for i, question in enumerate(
            st.session_state.questions
        ):

            user_answer = answers[i]

            correct_answer = question["answer"]

            is_correct = (
                user_answer == correct_answer
            )

            if is_correct:
                score += 1

            results.append({

                "question":
                    question["question"],

                "user_answer":
                    user_answer,

                "correct_answer":
                    correct_answer,

                "correct":
                    is_correct,

                "explanation":
                    question["explanation"]

            })

        st.session_state.score = score

st.session_state.results = results

# Save performance history
st.session_state.performance_history.append({
    "exam": exam,
    "subject": subject,
    "chapter": chapter,
    "difficulty": difficulty,
    "score": score,
    "total": len(st.session_state.questions),
    "accuracy": (score / len(st.session_state.questions)) * 100
})

st.session_state.submitted = True

# ==============================
# RESULTS
# ==============================

if st.session_state.submitted:

    st.divider()

    st.header("📊 Your Results")

    total = len(
        st.session_state.questions
    )

    score = st.session_state.score

    accuracy = (
        score / total
    ) * 100

    # Metrics
    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Score",
            f"{score}/{total}"
        )

    with col2:

        st.metric(
            "Accuracy",
            f"{accuracy:.1f}%"
        )

    with col3:

        if accuracy >= 80:

            performance = "Strong"

        elif accuracy >= 60:

            performance = "Moderate"

        else:

            performance = "Needs Practice"

        st.metric(
            "Performance",
            performance
        )

    # ==========================
    # RECOMMENDATION
    # ==========================

    st.subheader(
        "🔎 Smart Recommendation"
    )

    if accuracy < 60:

        st.warning(
            f"Focus on practicing more "
            f"**{chapter}** questions."
        )

    elif accuracy < 80:

        st.info(
            f"You have a reasonable understanding "
            f"of **{chapter}**, but more practice "
            f"could improve your accuracy."
        )

    else:

        st.success(
            f"Strong performance in **{chapter}**! "
            f"Try harder questions next."
        )

    # ==========================
    # ANSWER REVIEW
    # ==========================

    st.subheader(
        "📚 Answer Review"
    )

    for i, result in enumerate(
        st.session_state.results
    ):

        st.markdown(
            f"**Question {i + 1}**"
        )

        st.write(
            result["question"]
        )

        if result["correct"]:

            st.success(
                f"Correct ✅ — "
                f"Answer: {result['correct_answer']}"
            )

        else:

            st.error(
                f"Incorrect ❌ — "
                f"Your answer: "
                f"{result['user_answer']} | "
                f"Correct answer: "
                f"{result['correct_answer']}"
            )

        st.caption(
            f"Explanation: "
            f"{result['explanation']}"
        )

        st.divider()
        # ==============================
# PROGRESS DASHBOARD
# ==============================

if st.session_state.performance_history:

    st.divider()

    st.header("📊 Progress Dashboard")

    history_df = pd.DataFrame(
        st.session_state.performance_history
    )

    total_tests = len(history_df)

    total_questions = history_df["total"].sum()

    total_correct = history_df["score"].sum()

    overall_accuracy = (
        total_correct / total_questions
    ) * 100

    chapters_practiced = (
        history_df["chapter"].nunique()
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📝 Tests Taken",
            total_tests
        )

    with col2:
        st.metric(
            "❓ Questions",
            total_questions
        )

    with col3:
        st.metric(
            "🎯 Overall Accuracy",
            f"{overall_accuracy:.1f}%"
        )

    with col4:
        st.metric(
            "📚 Chapters",
            chapters_practiced
        )
        
# ==============================
# PERSONALIZED RECOMMENDATION
# ==============================

if st.session_state.performance_history:

    st.divider()

    st.header("🎯 Personalized Practice")

    history_df = pd.DataFrame(
        st.session_state.performance_history
    )

    # Calculate average accuracy for each chapter
    recommendation_df = (
        history_df
        .groupby(["exam", "subject", "chapter"])
        .agg(
            Average_Accuracy=("accuracy", "mean"),
            Questions=("total", "sum")
        )
        .reset_index()
    )

    # Find the weakest chapter
    weakest = recommendation_df.loc[
        recommendation_df["Average_Accuracy"].idxmin()
    ]

    weak_accuracy = weakest["Average_Accuracy"]
    weak_chapter = weakest["chapter"]

    st.write(
        f"Your current weakest chapter is "
        f"**{weak_chapter}** with an average accuracy "
        f"of **{weak_accuracy:.1f}%**."
    )

    if weak_accuracy < 60:

        st.warning(
            f"📚 Recommendation: Practice more "
            f"**{weak_chapter}** questions before "
            f"moving to harder problems."
        )

    elif weak_accuracy < 80:

        st.info(
            f"📈 Recommendation: Continue practicing "
            f"**{weak_chapter}** to improve your accuracy."
        )

    else:

        st.success(
            f"🔥 You are performing strongly in "
            f"**{weak_chapter}**. Try harder questions "
            f"or move to another chapter."
        )
# ==============================
# WEAKNESS ANALYSIS
# ==============================

if st.session_state.performance_history:

    st.divider()

    st.header("📈 Weakness Analysis")

    history_df = pd.DataFrame(
        st.session_state.performance_history
    )

    chapter_analysis = (
        history_df
        .groupby(["exam", "subject", "chapter"])
        .agg(
            Tests=("chapter", "count"),
            Questions=("total", "sum"),
            Average_Accuracy=("accuracy", "mean")
        )
        .reset_index()
    )

    chapter_analysis["Average_Accuracy"] = (
        chapter_analysis["Average_Accuracy"]
        .round(1)
    )

    def get_status(accuracy):

        if accuracy < 60:
            return "🔴 Weak"

        elif accuracy < 80:
            return "🟡 Improving"

        else:
            return "🟢 Strong"

    chapter_analysis["Status"] = (
        chapter_analysis["Average_Accuracy"]
        .apply(get_status)
    )

    st.dataframe(
        chapter_analysis,
        use_container_width=True,
        hide_index=True
    )


# ==============================
# FOOTER
# ==============================

st.divider()

st.caption(
    "JEE Practice Lab | "
    "Python + Streamlit + Pandas"
)
st.divider()

st.caption(
    "JEE Practice Lab | "
    "Developed as an independent academic project"
)

st.caption(
    "Built with Python • Streamlit • Pandas"
)