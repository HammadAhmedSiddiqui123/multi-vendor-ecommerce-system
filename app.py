import streamlit as st
import pandas as pd
from database import get_connection, validate_login, register_user
from customer_dashboard import show_customer_dashboard
from seller_dashboard import show_seller_dashboard
from admin_dashboard import show_admin_dashboard

# Configure the Streamlit page
st.set_page_config(page_title="E-Commerce Portal", layout="wide")

# Inject custom CSS — Exo 2 + Josefin Sans fonts & dark emerald theme
st.markdown("""
    <style>
        /* ── Google Fonts ── */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Exo+2:wght@400;500;600;700;800;900&family=Josefin+Sans:wght@300;400;500;600;700&display=swap');

        /* ── Global Typography ── */
        html, body, [class*="css"] {
            font-family: 'Josefin Sans', sans-serif !important;
            font-weight: 500 !important;
        }
        h1 {
            font-family: 'Orbitron', sans-serif !important;
            font-weight: 900 !important;
            color: #00d97e !important;
            letter-spacing: 0.04em;
            text-shadow: 0 0 20px rgba(0, 217, 126, 0.2);
        }
        h2, h3 {
            font-family: 'Exo 2', sans-serif !important;
            font-weight: 700 !important;
            color: #00d97e !important;
            letter-spacing: 0.02em;
        }
        h4, h5, h6 {
            font-family: 'Exo 2', sans-serif !important;
            font-weight: 600 !important;
            color: #4ddfaa !important;
            letter-spacing: 0.02em;
        }
        .stTabs [data-baseweb="tab"] {
            font-family: 'Exo 2', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: 0.02em;
        }

        /* ── Background & Base ── */
        .stApp {
            background-color: #0a1a14 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #071a10 !important;
            border-right: 1px solid #143d28 !important;
        }
        section[data-testid="stSidebar"] * {
            font-family: 'Josefin Sans', sans-serif !important;
        }

        /* ── Accent Colors ── */
        .stButton > button[kind="primary"],
        .stFormSubmitButton > button {
            background: linear-gradient(135deg, #00d97e, #00b368) !important;
            color: #0a1a14 !important;
            font-family: 'Exo 2', sans-serif !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
        }
        .stButton > button[kind="primary"]:hover,
        .stFormSubmitButton > button:hover {
            background: linear-gradient(135deg, #00f590, #00d97e) !important;
            box-shadow: 0 0 20px rgba(0, 217, 126, 0.3) !important;
            transform: translateY(-1px) !important;
        }
        .stButton > button {
            border: 1px solid #1a4d35 !important;
            color: #00d97e !important;
            background-color: #0d2818 !important;
            border-radius: 8px !important;
            font-family: 'Josefin Sans', sans-serif !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        .stButton > button:hover {
            border-color: #00d97e !important;
            background-color: #143d28 !important;
            box-shadow: 0 0 12px rgba(0, 217, 126, 0.15) !important;
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #0d2818 !important;
            border-radius: 10px !important;
            padding: 4px !important;
            gap: 4px !important;
        }
        .stTabs [data-baseweb="tab"] {
            color: #8aa89a !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 8px 16px !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #143d28 !important;
            color: #00d97e !important;
        }
        .stTabs [data-baseweb="tab-highlight"] {
            background-color: #00d97e !important;
        }

        /* ── Inputs & Selects ── */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div,
        .stDateInput > div > div > input {
            background-color: #0d2818 !important;
            border: 1px solid #1a4d35 !important;
            color: #e0e0e0 !important;
            border-radius: 8px !important;
            font-family: 'Josefin Sans', sans-serif !important;
        }
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #00d97e !important;
            box-shadow: 0 0 8px rgba(0, 217, 126, 0.2) !important;
        }

        /* ── Metrics ── */
        [data-testid="stMetric"] {
            background: linear-gradient(145deg, #0d2818, #112e1f) !important;
            border: 1px solid #1a4d35 !important;
            border-radius: 12px !important;
            padding: 16px 20px !important;
        }
        [data-testid="stMetricValue"] {
            font-family: 'Exo 2', sans-serif !important;
            font-weight: 800 !important;
            color: #00d97e !important;
        }
        [data-testid="stMetricLabel"] {
            font-family: 'Josefin Sans', sans-serif !important;
            color: #8aa89a !important;
            text-transform: uppercase !important;
            font-size: 0.75rem !important;
            letter-spacing: 0.08em !important;
        }
        [data-testid="stMetricDelta"] {
            color: #f5a623 !important;
            font-family: 'Josefin Sans', sans-serif !important;
        }

        /* ── Container / Cards ── */
        [data-testid="stExpander"] {
            background-color: #0d2818 !important;
            border: 1px solid #1a4d35 !important;
            border-radius: 12px !important;
        }
        div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
            border-radius: 8px;
        }
        div.stContainer, [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: #1a4d35 !important;
            border-radius: 12px !important;
        }

        /* ── Tables ── */
        .stDataFrame, .stTable {
            border-radius: 12px !important;
            overflow: hidden !important;
        }
        .stDataFrame thead th {
            background-color: #143d28 !important;
            color: #00d97e !important;
            font-family: 'Exo 2', sans-serif !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            font-size: 0.75rem !important;
            letter-spacing: 0.06em !important;
        }
        .stDataFrame tbody td {
            background-color: #0d2818 !important;
            border-color: #1a4d35 !important;
            font-family: 'Josefin Sans', sans-serif !important;
        }

        /* ── Dividers ── */
        hr {
            border-color: #1a4d35 !important;
        }

        /* ── Alerts & Toasts ── */
        .stAlert {
            border-radius: 10px !important;
            font-family: 'Josefin Sans', sans-serif !important;
        }
        [data-testid="stNotification"] {
            font-family: 'Josefin Sans', sans-serif !important;
        }

        /* ── Plotly Chart Overrides ── */
        .js-plotly-plot .plotly .main-svg {
            border-radius: 12px !important;
        }

        /* ── Price / Amount highlights ── */
        .price-highlight {
            color: #f5a623 !important;
            font-family: 'Exo 2', sans-serif !important;
            font-weight: 700 !important;
        }

        /* ── Scrollbar Styling ── */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0a1a14;
        }
        ::-webkit-scrollbar-thumb {
            background: #1a4d35;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #00d97e;
        }

        /* ── Form borders ── */
        [data-testid="stForm"] {
            border: 1px solid #1a4d35 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            background-color: #0d2818 !important;
        }

        /* ── Radio buttons ── */
        .stRadio > div {
            font-family: 'Josefin Sans', sans-serif !important;
        }
        .stRadio [data-testid="stMarkdownContainer"] {
            color: #e0e0e0 !important;
        }

        /* ── Link styling ── */
        a {
            color: #00d97e !important;
        }
        a:hover {
            color: #00f590 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

def login_page():
    st.title("E-Commerce Portal")
    st.write("Please log in or register to access the dashboard.")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    user = validate_login(email, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_info = user
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
                        
    with tab2:
        with st.form("register_form"):
            reg_name = st.text_input("Full Name", placeholder="Enter your name")
            reg_email = st.text_input("Email", placeholder="Enter your email")
            reg_password = st.text_input("Password", type="password", placeholder="Create a password")
            reg_role = st.radio("Account Type", ["customer", "seller"], horizontal=True)
            reg_button = st.form_submit_button("Register")
            
            if reg_button:
                if not reg_name or not reg_email or not reg_password:
                    st.error("Please fill in all fields.")
                else:
                    success = register_user(reg_name, reg_email, reg_password, reg_role)
                    if success:
                        st.success("Registration successful! You can now log in using the Login tab.")
                    else:
                        st.error("Registration failed. That email might already be registered.")

def dashboard():
    user_role = st.session_state.user_info.get('role', 'Unknown')
    
    col1, col2 = st.columns([8, 2])
    with col1:
        st.write(f"Logged in as **{st.session_state.user_info.get('name')}** ({user_role.capitalize()})")
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.rerun()

    st.divider()

    if user_role == 'customer':
        show_customer_dashboard()
    elif user_role == 'seller':
        show_seller_dashboard()
    elif user_role == 'admin':
        show_admin_dashboard()
    else:
        st.error("Unknown user role.")

# Main app logic
if not st.session_state.logged_in:
    login_page()
else:
    dashboard()
