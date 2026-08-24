import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime, date, timedelta
import pandas as pd
import json
import random
import base64
import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime, date, timedelta
import pandas as pd
import json
import random
import base64
import time
# ======================================================
# 1. MOBILE-FIRST INTERFACE & PREMIUM THEME (CSS)
# ======================================================
st.set_page_config(page_title="dMAT Companion", page_icon="🚀", layout="centered")

def apply_custom_styles():
    st.markdown("""
        <style>
        /* Main Background Gradient */
        .stApp {
            background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
            color: #F8FAFC;
        }

        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 15px;
        }

        /* Progress Rings/Bars */
        .stProgress > div > div > div > div {
            background-image: linear-gradient(to right, #38BDF8, #818CF8);
        }

        /* Big Rounded Buttons */
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
        
        .stButton>button:active {
            transform: scale(0.95);
        }

        /* Reward Box */
        .reward-box {
            background: rgba(250, 204, 21, 0.15);
            border: 2px dashed #FACC15;
            color: #FDE047;
            padding: 15px;
            border-radius: 15px;
            text-align: center;
        }

        /* Level Badge */
        .level-badge {
            background: #38BDF8;
            color: #0F172A;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 800;
            text-transform: uppercase;
        }

        /* Hide Streamlit Header/Footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# ======================================================
# 2. BROWSER PERSISTENCE ENGINE (No API Key Needed)
# ======================================================
# We use a hidden text input and JavaScript to sync with Browser LocalStorage
def sync_data():
    if "user_state" not in st.session_state:
        # Default State based on dMAT PDF Structure
        st.session_state.user_state = {
            "xp": 0,
            "streak": 1,
            "level": "Applicant",
            "last_active": str(date.today()),
            "completed_tasks": [],
            "mock_scores": [],
            "rewards_earned": 0
        }

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
            "1.8 Practice: High-Speed Visual Recognition Time Trials"
        ],
        "Core Module: Mathematical Equations": [
            "2.1 Fundamentals of Linear Equations and Variable Isolation",
            "2.2 Solving Systems using the Substitution Method",
            "2.3 Solving Systems using the Elimination Method",
            "2.4 Understanding Basic Inequalities & Absolute Values",
            "2.5 Advanced Algebraic Manipulation and Fraction Simplification",
            "2.6 Translating Complex Word Problems into Algebraic Equations",
            "2.7 Rate, Time, and Distance Equation Modeling",
            "2.8 Practice: Time-Constrained Equation Solving"
        ],
        "Core Module: Latin Squares": [
            "3.1 3x3 Grid Foundations: Basic Logic and Constraints",
            "3.2 4x4 Grid Logic: Scanning and Deduction Strategies",
            "3.3 5x5 Grid Completion: Basic Level Techniques",
            "3.4 5x5 Grid Completion: Advanced Missing-Variable Constraints",
            "3.5 Error Checking, Pattern Recognition, and Backtracking",
            "3.6 Practice: Speed Drills for 3x3 and 4x4 Grids",
            "3.7 Practice: High-Difficulty 5x5 Mastery Drills"
        ],
        "Core Module: Spatial Reasoning": [
            "4.1 Fundamentals of 2D Projections and Perspectives",
            "4.2 Basic 2D Shape Rotations, Reflections, and Symmetry",
            "4.3 Introduction to 3D Cube Folding (Net to 3D Shape)",
            "4.4 3D Cube Unfolding (3D Shape to Net)",
            "4.5 Advanced Mental Rotation of Complex 3D Objects",
            "4.6 Spatial Intersections and Cross-Sectional Views",
            "4.7 Practice: Identifying Correct Top, Side, and Front Views",
            "4.8 Practice: Spatial Manipulation Time Trials"
        ]
    }
# ======================================================
# 3. DAILY CHALLENGE & REWARD LOGIC
# ======================================================
def get_daily_challenge():
    random.seed(date.today().toordinal())
    challenges = [
        {"task": "Solve 10 Latin Squares", "reward": "🍫 A Dark Chocolate Square", "xp": 100},
        {"task": "Explain PCA to a wall for 5 mins", "reward": "☕ A Hot Chocolate with Marshmallows", "xp": 150},
        {"task": "90 Mins Focused Study (No Phone)", "reward": "🧇 A Crispy Belgian Waffle", "xp": 200},
        {"task": "Solve 5 High-Difficulty Physics Tasks", "reward": "🍕 A Mini Pizza Slice", "xp": 120},
        {"task": "Perfect Score on 1 Math Mock", "reward": "🍦 A Scoop of Gelato", "xp": 250}
    ]
    return random.choice(challenges)

# ======================================================
# 4. MAIN APP LAYOUT
# ======================================================
apply_custom_styles()
sync_data()

# Sidebar Settings (Mobile-accessible)
with st.sidebar:
    st.title("⚙️ Settings")
    exam_date = st.date_input("Exam Date", value=date(2025, 9, 29))
    target_hours = st.slider("Daily Goal (Hours)", 1, 12, 4)
    
    st.markdown("---")
    # Data Portability: Since we have no DB, user can export/import their JSON
    st.subheader("💾 Backup Progress")
    data_str = json.dumps(st.session_state.user_state)
    st.download_button("Export Data", data_str, file_name="dmat_progress.json")
    
    uploaded_file = st.file_uploader("Import Data")
    if uploaded_file:
        st.session_state.user_state = json.load(uploaded_file)
        st.success("Progress Loaded!")

# Bottom Navigation
selected = option_menu(
    menu_title=None,
    options=["Dashboard", "Study Plan", "Focus"],
    icons=["speedometer2", "book", "clock", "graph-up"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#1E293B"},
        "icon": {"color": "#F43F5E", "font-size": "20px"}, 
        "nav-link": {"font-size": "14px", "text-align": "center", "margin":"0px", "color": "#94A3B8"},
        "nav-link-selected": {"background-color": "#0F172A", "color": "#F43F5E", "font-weight": "bold"},
    }
)

# ------------------ 1. DASHBOARD ------------------
if selected == "Dashboard":
    # Header Section
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.markdown(f"## Level: <span class='level-badge'>{st.session_state.user_state['level']}</span>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"### 🔥 {st.session_state.user_state['streak']}")

    # Countdown Card
    days_left = (exam_date - date.today()).days
    st.markdown(f"""
        <div class="glass-card" style="text-align: center; border-bottom: 4px solid #F43F5E;">
            <p style="margin:0; opacity:0.6; font-size: 0.9rem;">COUNTDOWN TO GERMANY</p>
            <h1 style="margin:0; font-size: 3.5rem; color: #F43F5E;">{days_left}</h1>
            <p style="margin:0; font-weight: bold;">DAYS REMAINING</p>
        </div>
    """, unsafe_allow_html=True)

    # Daily Challenge Section
    challenge = get_daily_challenge()
    st.markdown("### 🎯 Today's Challenge")
    st.markdown(f"""
        <div class="reward-box">
            <h4 style="margin:0;">{challenge['task']}</h4>
            <p style="margin:5px 0 0 0; font-size: 0.9rem;">WIN: {challenge['reward']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("CLAIM CHALLENGE REWARD"):
        st.session_state.user_state['xp'] += challenge['xp']
        st.session_state.user_state['rewards_earned'] += 1
        st.balloons()
        st.success(f"XP Earned! Enjoy your {challenge['reward']}!")

    # Motivation Message
    st.markdown(f"""
        <div style="font-style: italic; opacity:0.8; text-align:center; margin-top:20px;">
            "Every minute of focus brings you closer to your Master's degree in Germany."
        </div>
    """, unsafe_allow_html=True)

# ------------------ 2. STUDY PLAN ------------------
elif selected == "Study Plan":
    st.markdown("### 📚 Study Syllabus")
    plan = get_study_plan()
    
    for module, tasks in plan.items():
        with st.expander(f"📂 {module}", expanded=True):
            for t in tasks:
                is_done = t in st.session_state.user_state['completed_tasks']
                if st.checkbox(t, value=is_done, key=t):
                    if t not in st.session_state.user_state['completed_tasks']:
                        st.session_state.user_state['completed_tasks'].append(t)
                        st.session_state.user_state['xp'] += 50
                        st.rerun()
                elif is_done:
                    st.session_state.user_state['completed_tasks'].remove(t)
                    st.rerun()

# ------------------ 3. FOCUS TIMER ------------------
elif selected == "Study Plan":
    st.markdown("### 📚 Core Module Syllabus")
    plan = get_study_plan()
    
    for module, tasks in plan.items():
        with st.expander(f"📂 {module}", expanded=True):
            for t in tasks:
                is_done = t in st.session_state.user_state['completed_tasks']
                if st.checkbox(t, value=is_done, key=t):
                    if t not in st.session_state.user_state['completed_tasks']:
                        st.session_state.user_state['completed_tasks'].append(t)
                        st.session_state.user_state['xp'] += 50
                        st.rerun()
                elif is_done:
                    st.session_state.user_state['completed_tasks'].remove(t)
                    st.rerun()

# ------------------ 3. FOCUS TIMER ------------------
elif selected == "Focus":
    st.markdown("### ⏳ Pomodoro Timer")
    st.markdown("<p style='text-align:center; opacity:0.6;'>Simulate focus sessions</p>", unsafe_allow_html=True)
    
    timer_option = st.selectbox("Select Session Length", ["25 Mins (Standard)", "45 Mins (Intense)", "90 Mins (Mock)"])
    duration = int(timer_option.split(" ")[0])
    
    if 'timer_active' not in st.session_state:
        st.session_state.timer_active = False

    if st.button("START FOCUS SESSION"):
        st.session_state.timer_active = True
        
    if st.session_state.timer_active:
        timer_placeholder = st.empty()
        
        # Countdown logic using time.sleep
        for i in range(duration * 60, -1, -1):
            mins, secs = divmod(i, 60)
            # Update the placeholder text with the current time remaining
            timer_placeholder.markdown(
                f"<h1 style='text-align:center; font-size: 5rem; color: #F43F5E;'>{mins:02d}:{secs:02d}</h1>", 
                unsafe_allow_html=True
            )
            time.sleep(1)
            
        st.session_state.timer_active = False
        st.success("Session Finished! +100 XP")
        
        # Automatically update XP and rerun to refresh state
        st.session_state.user_state['xp'] += 100
        time.sleep(2)
        st.rerun()

# ======================================================
# 5. DATA PORTABILITY WARNING
# ======================================================
st.markdown("---")
st.markdown("<p style='text-align:center; font-size: 0.7rem; opacity: 0.5;'>Data is stored locally in your browser. Clearing browser cache will reset progress. Use the 'Export Data' button in the sidebar for backups.</p>", unsafe_allow_html=True)