import json
import random
import time
from datetime import date

import streamlit as st
from streamlit_option_menu import option_menu

# ======================================================
# 1. PAGE CONFIG & THEME
# ======================================================
st.set_page_config(page_title="dMAT Companion", page_icon="🚀", layout="centered")

DEFAULT_STATE = {
    "xp": 0,
    "streak": 1,
    "level": "Applicant",
    "last_active": str(date.today()),
    "completed_tasks": [],
    "mock_scores": [],
    "rewards_earned": 0,
}


def apply_custom_styles():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
            color: #F8FAFC;
        }
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 15px;
        }
        .stProgress > div > div > div > div {
            background-image: linear-gradient(to right, #38BDF8, #818CF8);
        }
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            height: 3.5rem;
            background: linear-gradient(90deg, #F43F5E 0%, #FB7185 100%);
            color: white;
            border: none;
            font-weight: bold;
            font-size: 1.1rem;
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:active { transform: scale(0.95); }
        .reward-box {
            background: rgba(250, 204, 21, 0.15);
            border: 2px dashed #FACC15;
            color: #FDE047;
            padding: 15px;
            border-radius: 15px;
            text-align: center;
        }
        .level-badge {
            background: #38BDF8;
            color: #0F172A;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 800;
            text-transform: uppercase;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ======================================================
# 2. STATE MANAGEMENT
# ======================================================
def init_state():
    """Initialize session state once per session."""
    if "user_state" not in st.session_state:
        st.session_state.user_state = DEFAULT_STATE.copy()
    if "timer_active" not in st.session_state:
        st.session_state.timer_active = False
    if "last_import_id" not in st.session_state:
        st.session_state.last_import_id = None


def merge_with_defaults(loaded: dict) -> dict:
    """Backfill any missing keys so an older/partial export never crashes the app."""
    merged = DEFAULT_STATE.copy()
    merged.update({k: v for k, v in loaded.items() if k in DEFAULT_STATE})
    return merged


def handle_import(uploaded_file):
    """
    Import progress from an uploaded JSON file.

    Streamlit keeps the uploaded file object alive across reruns as long as it's
    still selected in the widget. Without a guard, the import line would re-run
    (and silently overwrite any new progress) on every single rerun triggered by
    unrelated actions like checking a task or clicking a button. We only import
    once per unique uploaded file, tracked via its file_id.
    """
    if uploaded_file is None:
        return
    if uploaded_file.file_id == st.session_state.last_import_id:
        return  # already imported this exact file, skip

    try:
        loaded = json.load(uploaded_file)
        st.session_state.user_state = merge_with_defaults(loaded)
        st.session_state.last_import_id = uploaded_file.file_id
        st.success("Progress Loaded!")
    except (json.JSONDecodeError, UnicodeDecodeError):
        st.error("That file doesn't look like a valid dMAT progress export.")


# ======================================================
# 3. STUDY PLAN / CHALLENGE DATA
# ======================================================
def get_study_plan():
    return {
        "Core Module: Figure Sequences": [
            "1.1 Fundamentals: Basic Rules, Logic, and Sequence Mechanics",
            "1.2 Identifying Single Pattern Changes (Color, Shape, Position)",
            "1.3 Identifying Double & Triple Simultaneous Pattern Changes",
            "1.4 Alternating, Oscillating, and Interlocking Sequences",
            "1.5 Rotational and Directional Movements (Clockwise vs. Counter-Clockwise)",
            "1.6 Exception Handling: Identifying the 'Odd One Out'",
            "1.7 Practice: Basic Sequence Completion Drills",
            "1.8 Practice: High-Speed Visual Recognition Time Trials",
        ],
        "Core Module: Mathematical Equations": [
            "2.1 Fundamentals of Linear Equations and Variable Isolation",
            "2.2 Solving Systems using the Substitution Method",
            "2.3 Solving Systems using the Elimination Method",
            "2.4 Understanding Basic Inequalities & Absolute Values",
            "2.5 Advanced Algebraic Manipulation and Fraction Simplification",
            "2.6 Translating Complex Word Problems into Algebraic Equations",
            "2.7 Rate, Time, and Distance Equation Modeling",
            "2.8 Practice: Time-Constrained Equation Solving",
        ],
        "Core Module: Latin Squares": [
            "3.1 3x3 Grid Foundations: Basic Logic and Constraints",
            "3.2 4x4 Grid Logic: Scanning and Deduction Strategies",
            "3.3 5x5 Grid Completion: Basic Level Techniques",
            "3.4 5x5 Grid Completion: Advanced Missing-Variable Constraints",
            "3.5 Error Checking, Pattern Recognition, and Backtracking",
            "3.6 Practice: Speed Drills for 3x3 and 4x4 Grids",
            "3.7 Practice: High-Difficulty 5x5 Mastery Drills",
        ],
        "Core Module: Spatial Reasoning": [
            "4.1 Fundamentals of 2D Projections and Perspectives",
            "4.2 Basic 2D Shape Rotations, Reflections, and Symmetry",
            "4.3 Introduction to 3D Cube Folding (Net to 3D Shape)",
            "4.4 3D Cube Unfolding (3D Shape to Net)",
            "4.5 Advanced Mental Rotation of Complex 3D Objects",
            "4.6 Spatial Intersections and Cross-Sectional Views",
            "4.7 Practice: Identifying Correct Top, Side, and Front Views",
            "4.8 Practice: Spatial Manipulation Time Trials",
        ],
    }


def get_daily_challenge():
    # Use a local Random instance seeded by today's date so we get a stable
    # "challenge of the day" without mutating the global random state
    # (which could otherwise affect other random calls in the app).
    rng = random.Random(date.today().toordinal())
    challenges = [
        {"task": "Solve 10 Latin Squares", "reward": "🍫 A Dark Chocolate Square", "xp": 100},
        {"task": "Explain PCA to a wall for 5 mins", "reward": "☕ A Hot Chocolate with Marshmallows", "xp": 150},
        {"task": "90 Mins Focused Study (No Phone)", "reward": "🧇 A Crispy Belgian Waffle", "xp": 200},
        {"task": "Solve 5 High-Difficulty Physics Tasks", "reward": "🍕 A Mini Pizza Slice", "xp": 120},
        {"task": "Perfect Score on 1 Math Mock", "reward": "🍦 A Scoop of Gelato", "xp": 250},
    ]
    return rng.choice(challenges)


# ======================================================
# 4. PAGE SECTIONS
# ======================================================
def render_dashboard(exam_date):
    state = st.session_state.user_state

    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.markdown(
            f"## Level: <span class='level-badge'>{state['level']}</span>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(f"### 🔥 {state['streak']}")

    days_left = (exam_date - date.today()).days
    if days_left >= 0:
        countdown_label = "DAYS REMAINING"
        countdown_value = days_left
    else:
        countdown_label = "DAYS SINCE EXAM DATE"
        countdown_value = abs(days_left)

    st.markdown(
        f"""
        <div class="glass-card" style="text-align: center; border-bottom: 4px solid #F43F5E;">
            <p style="margin:0; opacity:0.6; font-size: 0.9rem;">COUNTDOWN TO GERMANY</p>
            <h1 style="margin:0; font-size: 3.5rem; color: #F43F5E;">{countdown_value}</h1>
            <p style="margin:0; font-weight: bold;">{countdown_label}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    challenge = get_daily_challenge()
    st.markdown("### 🎯 Today's Challenge")
    st.markdown(
        f"""
        <div class="reward-box">
            <h4 style="margin:0;">{challenge['task']}</h4>
            <p style="margin:5px 0 0 0; font-size: 0.9rem;">WIN: {challenge['reward']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("CLAIM CHALLENGE REWARD"):
        state["xp"] += challenge["xp"]
        state["rewards_earned"] += 1
        st.balloons()
        st.success(f"XP Earned! Enjoy your {challenge['reward']}!")

    st.markdown(
        """
        <div style="font-style: italic; opacity:0.8; text-align:center; margin-top:20px;">
            "Every minute of focus brings you closer to your Master's degree in Germany."
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_study_plan():
    state = st.session_state.user_state
    st.markdown("### 📚 Study Syllabus")
    plan = get_study_plan()

    for module, tasks in plan.items():
        with st.expander(f"📂 {module}", expanded=True):
            for idx, t in enumerate(tasks):
                is_done = t in state["completed_tasks"]
                # Key includes module + index so identical task text across
                # modules can never collide on the same widget key.
                key = f"task_{module}_{idx}"
                checked = st.checkbox(t, value=is_done, key=key)

                if checked and not is_done:
                    state["completed_tasks"].append(t)
                    state["xp"] += 50
                    st.rerun()
                elif not checked and is_done:
                    state["completed_tasks"].remove(t)
                    st.rerun()


def render_focus_timer():
    state = st.session_state.user_state
    st.markdown("### ⏳ Pomodoro Timer")
    st.markdown(
        "<p style='text-align:center; opacity:0.6;'>Simulate focus sessions</p>",
        unsafe_allow_html=True,
    )

    timer_option = st.selectbox(
        "Select Session Length", ["25 Mins (Standard)", "45 Mins (Intense)", "90 Mins (Mock)"]
    )
    duration = int(timer_option.split(" ")[0])

    if st.button("START FOCUS SESSION", disabled=st.session_state.timer_active):
        st.session_state.timer_active = True

    if st.session_state.timer_active:
        timer_placeholder = st.empty()

        # NOTE: this blocks the Streamlit script thread for the full duration.
        # Fine for a lightweight personal tool, but the tab must stay open and
        # no other widget can be interacted with mid-countdown.
        for i in range(duration * 60, -1, -1):
            mins, secs = divmod(i, 60)
            timer_placeholder.markdown(
                f"<h1 style='text-align:center; font-size: 5rem; color: #F43F5E;'>{mins:02d}:{secs:02d}</h1>",
                unsafe_allow_html=True,
            )
            time.sleep(1)

        state["xp"] += 100
        st.session_state.timer_active = False
        st.success("Session Finished! +100 XP")
        time.sleep(2)
        st.rerun()


# ======================================================
# 5. MAIN APP
# ======================================================
def main():
    apply_custom_styles()
    init_state()

    with st.sidebar:
        st.title("⚙️ Settings")
        exam_date = st.date_input("Exam Date", value=date(2026, 9, 29))
        st.slider("Daily Goal (Hours)", 1, 12, 4, key="target_hours")

        st.markdown("---")
        st.subheader("💾 Backup Progress")

        data_str = json.dumps(st.session_state.user_state, indent=2)
        st.download_button("Export Data", data_str, file_name="dmat_progress.json", mime="application/json")

        uploaded_file = st.file_uploader("Import Data", type="json")
        handle_import(uploaded_file)

    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Study Plan", "Focus"],
        icons=["speedometer2", "book", "clock"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#1E293B"},
            "icon": {"color": "#F43F5E", "font-size": "20px"},
            "nav-link": {"font-size": "14px", "text-align": "center", "margin": "0px", "color": "#94A3B8"},
            "nav-link-selected": {"background-color": "#0F172A", "color": "#F43F5E", "font-weight": "bold"},
        },
    )

    if selected == "Dashboard":
        render_dashboard(exam_date)
    elif selected == "Study Plan":
        render_study_plan()
    elif selected == "Focus":
        render_focus_timer()

    st.markdown("---")
    st.markdown(
        "<p style='text-align:center; font-size: 0.7rem; opacity: 0.5;'>"
        "Progress lives only in this browser tab's session — a page refresh will reset it. "
        "Use the 'Export Data' button in the sidebar to save a backup, and 'Import Data' to restore it."
        "</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
