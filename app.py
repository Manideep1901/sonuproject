import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from database import (
    create_table, create_user, verify_user,
    add_expense, get_all_expenses, get_spending_by_mood, 
    get_spending_by_category_mood, get_eco_impact_by_mood
)
from datetime import date
import time

# ------------------ PAGE SETUP --------------------
st.set_page_config(
    page_title=" Smart Expense Tracker", 
    page_icon="💰", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------- CUSTOM STYLING -----------------
st.markdown("""
<style>
    /* Main Theme */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: #6c757d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Card Styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .login-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        max-width: 500px;
        margin: 2rem auto;
    }
    
    /* Button Styling */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# ----------------- INITIALIZE DATABASE ------------
create_table()

# ----------------- AUTHENTICATION -----------------
def initialize_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None

def login_user(username, password):
    user = verify_user(username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.user_id = user['id']
        st.session_state.username = user['username']
        return True
    return False

def logout_user():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None

def show_login_page():
    st.markdown('<h1 class="main-header">💰 Smart Expense Tracker</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Smart Expense Tracking • Financial Wellness • Sustainable Living</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # Login Section
        st.subheader("🔐 Welcome Back!")
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("🚀 Login to Dashboard")
            
            if login_button:
                if username and password:
                    if login_user(username, password):
                        st.success(f"🎉 Welcome back, {username}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        st.markdown("---")
        
        # Signup Section
        st.subheader("👤 New User?")
        with st.form("signup_form"):
            new_username = st.text_input("Choose Username", placeholder="Create a username")
            new_email = st.text_input("Email (optional)", placeholder="your.email@example.com")
            new_password = st.text_input("Choose Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
            signup_button = st.form_submit_button("✨ Create Account")
            
            if signup_button:
                if new_username and new_password:
                    if new_password == confirm_password:
                        user_id = create_user(new_username, new_password, new_email)
                        if user_id:
                            st.success("✅ Account created successfully! Please login.")
                        else:
                            st.error("❌ Username already exists. Please choose another.")
                    else:
                        st.error("❌ Passwords do not match")
                else:
                    st.warning("⚠️ Please fill in all required fields")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------- MAIN APP ----------------------
def main_app():
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown('<h1 class="main-header">💰 Smart Expense Tracker</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Track your expenses, analyze moods, and plan sustainably 🌱</p>', unsafe_allow_html=True)
    
    with col3:
        st.write(f"**Welcome, {st.session_state.username}!** 👋")
        if st.button("🚪 Logout"):
            logout_user()
            st.rerun()
    
    # ----------------- SIDEBAR MENU -------------------
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        menu = st.radio("Go to", 
            ["📊 Dashboard", "➕ Add Expense", "📋 View Expenses", "🔮 Predict Spending", "😊 Mood Analysis", "🌍 Eco Impact"])
        
        st.markdown("---")
        st.markdown("### 💡 Quick Stats")
        data = get_all_expenses(st.session_state.user_id)
        if data:
            df = pd.DataFrame(data)
            total_spent = df["amount"].sum()
            st.metric("Total Spending", f"₹{total_spent:,.2f}")
            st.metric("Total Expenses", len(data))
        else:
            st.info("No expenses yet!")
    
    # ---------------- DASHBOARD PAGE -------------------
    if menu == "📊 Dashboard":
        st.subheader("📊 Summary Dashboard")
        data = get_all_expenses(st.session_state.user_id)
        
        if not data:
            st.info("🎉 Welcome! Start by adding your first expense to see your dashboard.")
        else:
            df = pd.DataFrame(data)
            
            # Top Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                total_spent = df["amount"].sum()
                st.metric("💸 Total Spending", f"₹{total_spent:.2f}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                eco_factor = {"Food": 2.0, "Travel": 3.0, "Shopping": 1.5, "Bills": 0.5, "Other": 1.0}
                df["Eco Impact"] = df.apply(lambda x: x["amount"]/100 * eco_factor.get(x["category"], 1), axis=1)
                total_eco = df["Eco Impact"].sum()
                st.metric("🌍 Eco Impact", f"{total_eco:.2f} kg CO₂")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                avg_expense = df["amount"].mean()
                st.metric("📊 Avg Expense", f"₹{avg_expense:.2f}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                total_expenses = len(df)
                st.metric("📈 Total Entries", f"{total_expenses}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Main Content
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.write("### 📈 Recent Expenses")
                st.dataframe(df.head(10), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Spending by Category
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.write("### 🏷️ Spending by Category")
                category_totals = df.groupby("category")["amount"].sum().reset_index()
                st.bar_chart(category_totals.set_index("category"))
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                # Average spending per mood
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.write("### 😊 Spending by Mood")
                avg_mood = df.groupby("mood")["amount"].mean().reset_index()
                st.bar_chart(avg_mood.set_index("mood"))
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Predict next 7 days spending
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.write("### 🔮 Weekly Forecast")
                if len(df) >= 3:
                    df["date"] = pd.to_datetime(df["date"])
                    df.sort_values("date", inplace=True)
                    df["Days"] = (df["date"] - df["date"].min()).dt.days
                    
                    X = df["Days"].values.reshape(-1,1)
                    y = df["amount"].values
                    
                    model = LinearRegression()
                    model.fit(X, y)
                    
                    future_days = np.array([X[-1][0]+i for i in range(1,8)]).reshape(-1,1)
                    predicted = model.predict(future_days)
                    
                    for i, pred in enumerate(predicted[:4]):  # Show first 4 days
                        st.write(f"**Day +{i+1}:** ₹{pred:.2f}")
                else:
                    st.info("Need 3+ expenses for predictions")
                st.markdown('</div>', unsafe_allow_html=True)
    
    # ----------------- ADD EXPENSE PAGE ----------------
    elif menu == "➕ Add Expense":
        st.subheader("➕ Add a New Expense")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            exp_date = st.date_input("📅 Date", date.today())
            category = st.selectbox("📂 Category", ["🍔 Food", "🚗 Travel", "🛍️ Shopping", "📱 Bills", "🎯 Other"])
            mood = st.selectbox("😊 Your Mood", ["😊 Happy", "😢 Sad", "😐 Neutral", "🎉 Excited", "😴 Tired"])
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            amount = st.number_input("💰 Amount (₹)", min_value=0.0, step=10.0)
            description = st.text_input("📝 Description", placeholder="What was this expense for?")
            
            if st.button("💾 Save Expense"):
                if amount > 0:
                    # Remove emoji from category for database
                    clean_category = category.split(' ')[-1] if ' ' in category else category
                    clean_mood = mood.split(' ')[-1] if ' ' in mood else mood
                    
                    add_expense(st.session_state.user_id, str(exp_date), clean_category, amount, description, clean_mood)
                    st.success("✅ Expense added successfully!")
                else:
                    st.warning("⚠️ Please enter a valid amount")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ----------------- VIEW EXPENSES PAGE -------------
    elif menu == "📋 View Expenses":
        st.subheader("📋 All Expenses")
        data = get_all_expenses(st.session_state.user_id)
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                total = df["amount"].sum()
                st.metric("💰 Total Spending", f"₹{total:.2f}")
            with col2:
                st.metric("📊 Total Expenses", len(data))
        else:
            st.info("No expenses added yet!")
    
    # ------------- PREDICTIVE SPENDING ----------------
    elif menu == "🔮 Predict Spending":
        st.subheader("🔮 Predictive Spending Forecast")
        data = get_all_expenses(st.session_state.user_id)
        
        if len(data) < 3:
            st.warning("Not enough data to make predictions (minimum 3 entries required).")
        else:
            df = pd.DataFrame(data)
            df["date"] = pd.to_datetime(df["date"])
            df.sort_values("date", inplace=True)
            df["Days"] = (df["date"] - df["date"].min()).dt.days
            
            X = df["Days"].values.reshape(-1,1)
            y = df["amount"].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            future_days = np.array([X[-1][0]+i for i in range(1,8)]).reshape(-1,1)
            predicted = model.predict(future_days)
            
            forecast_df = pd.DataFrame({
                "Day": [f"Day +{i}" for i in range(1,8)],
                "Predicted Amount (₹)": predicted.round(2)
            })
            
            st.table(forecast_df)
            
            # Visual representation
            st.write("### 📈 Forecast Trend")
            st.line_chart(forecast_df.set_index("Day"))
    
    # --------------- MOOD ANALYSIS -------------------
    elif menu == "😊 Mood Analysis":
        st.subheader("😊 Mood Linked Spending Analysis")
        data = get_all_expenses(st.session_state.user_id)
        
        if not data:
            st.info("No expenses added yet!")
        else:
            df = pd.DataFrame(data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### 💰 Total Spending by Mood")
                mood_summary = pd.DataFrame(get_spending_by_mood(st.session_state.user_id))
                if not mood_summary.empty:
                    st.bar_chart(mood_summary.set_index("mood"))
                else:
                    st.info("No mood data available")
            
            with col2:
                st.write("### 🏷️ Spending by Category & Mood")
                category_mood_summary = pd.DataFrame(get_spending_by_category_mood(st.session_state.user_id))
                if not category_mood_summary.empty:
                    st.dataframe(category_mood_summary)
                else:
                    st.info("No category-mood data available")
    
    # ---------------- ECO IMPACT ----------------------
    elif menu == "🌍 Eco Impact":
        st.subheader("🌍 Eco Impact Calculator")
        data = get_all_expenses(st.session_state.user_id)
        
        if not data:
            st.info("No expenses added yet!")
        else:
            df = pd.DataFrame(data)
            eco_factor = {
                "Food": 2.0, "Travel": 3.0, "Shopping": 1.5, 
                "Bills": 0.5, "Other": 1.0
            }
            
            df["Eco Impact (kg CO₂)"] = df.apply(
                lambda x: x["amount"]/100 * eco_factor.get(x["category"], 1), axis=1
            )
            
            total_impact = df["Eco Impact (kg CO₂)"].sum()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("🌱 Total Carbon Footprint", f"{total_impact:.2f} kg CO₂")
                st.metric("🌳 Equivalent Tree Months", f"{total_impact / 21:.1f} months")
                
                st.write("### 📊 Eco Impact by Category")
                category_impact = df.groupby("category")["Eco Impact (kg CO₂)"].sum().reset_index()
                st.bar_chart(category_impact.set_index("category"))
            
            with col2:
                st.write("### 🔍 Detailed Breakdown")
                eco_mood = pd.DataFrame(get_eco_impact_by_mood(st.session_state.user_id))
                if not eco_mood.empty:
                    st.dataframe(eco_mood)
                
                st.write("### 💡 Eco Tips")
                tips = [
                    "🚗 Use public transport to reduce travel impact",
                    "🍔 Choose local and seasonal foods",
                    "🛍️ Avoid impulse shopping",
                    "📱 Go paperless with digital bills",
                    "💡 Energy-efficient choices save money & environment"
                ]
                for tip in tips:
                    st.write(f"• {tip}")

# ----------------- APP FLOW ----------------------
def main():
    initialize_session_state()
    
    if not st.session_state.logged_in:
        show_login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()