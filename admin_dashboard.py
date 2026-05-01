import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import (
    get_all_users, delete_user, get_all_orders,
    get_monthly_revenue, get_daily_revenue, get_all_coupons, add_coupon,
    get_all_sellers, get_admin_detailed_orders, get_revenue_by_category, get_top_sellers
)

def show_admin_dashboard():
    st.title("Admin Portal")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Users", "All Orders", "Revenue", "Coupons"])

    with tab1:
        st.subheader("User Management")
        users = get_all_users()
        if not users:
            st.info("No users found.")
        else:
            if "admin_msg" in st.session_state:
                m_type, m_text = st.session_state.admin_msg
                if m_type == "success":
                    st.success(m_text)
                else:
                    st.error(m_text)
                del st.session_state.admin_msg
                
            for u in users:
                col1, col2, col3, col4 = st.columns([3, 3, 2, 2])
                col1.write(f"**{u['name']}** ({u['email']})")
                col2.write(f"Role: {u['role'].capitalize()}")
                col3.write(f"Joined: {u['created_at'].strftime('%Y-%m-%d')}")
                if u['role'] != 'admin':
                    if col4.button("Delete User", key=f"del_user_{u['user_id']}"):
                        success = delete_user(u['user_id'])
                        if success:
                            st.session_state.admin_msg = ("success", f"User {u['name']} deleted successfully.")
                        else:
                            st.session_state.admin_msg = ("error", f"Cannot delete {u['name']}. They have associated transactions.")
                        st.rerun()
                else:
                    col4.write("*(Admin)*")
                st.divider()

    with tab2:
        st.subheader("Global Order History")
        
        sellers = get_all_sellers()
        seller_names = ["All"] + [s['shop_name'] for s in sellers]
        status_options = ["All", "pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]
        
        col1, col2 = st.columns(2)
        with col1:
            selected_seller = st.selectbox("Filter by Seller", seller_names)
        with col2:
            selected_status = st.selectbox("Filter by Status", status_options)

        orders = get_admin_detailed_orders()
        if not orders:
            st.info("No orders found in the database.")
        else:
            df_orders = pd.DataFrame(orders)
            
            if selected_seller != "All":
                df_orders = df_orders[df_orders['seller_name'] == selected_seller]
            if selected_status != "All":
                df_orders = df_orders[df_orders['order_status'] == selected_status]
                
            if df_orders.empty:
                st.warning("No orders match the selected filters.")
            else:
                st.dataframe(df_orders, use_container_width=True)

    with tab3:
        st.subheader("Revenue & Analytics")
        daily_data = get_daily_revenue()
        cat_revenue = get_revenue_by_category()
        top_sellers = get_top_sellers()
        
        if not daily_data:
            st.info("Not enough data to generate charts.")
        else:
            df_daily = pd.DataFrame(daily_data)
            df_daily['order_day'] = pd.to_datetime(df_daily['order_day'])
            df_daily = df_daily.sort_values('order_day')
            
            # --- KPI Summary Cards ---
            total_rev = float(df_daily['daily_revenue'].sum())
            total_ord = int(df_daily['total_orders'].sum())
            avg_order = total_rev / total_ord if total_ord else 0
            best_day = df_daily.loc[df_daily['daily_revenue'].idxmax()]
            
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Revenue", f"${total_rev:,.0f}")
            k2.metric("Total Orders", total_ord)
            k3.metric("Avg Order Value", f"${avg_order:,.0f}")
            k4.metric("Best Day", f"${float(best_day['daily_revenue']):,.0f}",
                       delta=best_day['order_day'].strftime('%b %d, %Y'))
            
            st.divider()
            
            # --- Monthly Revenue & Order Volume (aggregated from daily) ---
            df_daily['month'] = df_daily['order_day'].dt.to_period('M')
            df_monthly = df_daily.groupby('month').agg(
                monthly_revenue=('daily_revenue', 'sum'),
                monthly_orders=('total_orders', 'sum')
            ).reset_index()
            df_monthly['month_label'] = df_monthly['month'].astype(str)
            df_monthly['month_dt'] = df_monthly['month'].dt.to_timestamp()
            
            col1, col2 = st.columns(2)
            with col1:
                # Monthly Revenue bar chart
                revenue_vals = [float(v) for v in df_monthly['monthly_revenue']]
                max_rev = max(revenue_vals) if revenue_vals else 1
                bar_colors = [f'rgba(0, {int(120 + 135 * (v / max_rev))}, {int(80 + 46 * (v / max_rev))}, 0.85)' for v in revenue_vals]

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df_monthly['month_label'], y=df_monthly['monthly_revenue'],
                    name='Revenue',
                    marker=dict(
                        color=bar_colors,
                        line=dict(width=1.5, color='#00d97e')
                    ),
                    text=[f'${v:,.0f}' for v in revenue_vals],
                    textposition='outside',
                    textfont=dict(color='#00d97e', size=11, family='Exo 2'),
                    hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
                ))
                fig.update_layout(
                    title='Monthly Revenue',
                    paper_bgcolor='#0d2818', plot_bgcolor='#0a1a14',
                    font=dict(family='Josefin Sans', color='#e0e0e0'),
                    title_font=dict(family='Exo 2', color='#00d97e', size=16),
                    xaxis=dict(gridcolor='#1a4d35', title='Month', showgrid=False),
                    yaxis=dict(gridcolor='#1a4d35', title='Revenue ($)', showgrid=True, gridwidth=1),
                    hovermode='x unified',
                    showlegend=False,
                    bargap=0.25,
                    margin=dict(t=50, b=40, l=50, r=20)
                )
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                # Monthly Order Volume line chart
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(
                    x=df_monthly['month_label'], y=df_monthly['monthly_orders'],
                    mode='lines+markers+text',
                    name='Orders',
                    line=dict(color='#f5a623', width=3, shape='spline'),
                    marker=dict(size=10, color='#f5a623', line=dict(width=2, color='#0a1a14')),
                    fill='tozeroy',
                    fillcolor='rgba(245, 166, 35, 0.15)',
                    text=[str(v) for v in df_monthly['monthly_orders']],
                    textposition='top center',
                    textfont=dict(color='#f5a623', size=11, family='Exo 2'),
                    hovertemplate='<b>%{x}</b><br>Orders: %{y}<extra></extra>'
                ))
                fig2.update_layout(
                    title='Monthly Order Volume',
                    paper_bgcolor='#0d2818', plot_bgcolor='#0a1a14',
                    font=dict(family='Josefin Sans', color='#e0e0e0'),
                    title_font=dict(family='Exo 2', color='#00d97e', size=16),
                    xaxis=dict(gridcolor='#1a4d35', title='Month', showgrid=True, gridwidth=1),
                    yaxis=dict(gridcolor='#1a4d35', title='Number of Orders', showgrid=True, gridwidth=1, dtick=1),
                    hovermode='x unified',
                    showlegend=False,
                    margin=dict(t=50, b=40, l=50, r=20)
                )
                st.plotly_chart(fig2, use_container_width=True)
                
            col3, col4 = st.columns(2)
            with col3:
                if cat_revenue:
                    df_cat = pd.DataFrame(cat_revenue)
                    fig3 = px.pie(df_cat, names='category_name', values='revenue', title='Revenue by Category', hole=0.3,
                                  color_discrete_sequence=['#00d97e', '#00b368', '#f5a623', '#e74c3c', '#8aa89a', '#1a4d35'])
                    fig3.update_layout(
                        paper_bgcolor='#0d2818', plot_bgcolor='#0a1a14',
                        font=dict(family='Josefin Sans', color='#e0e0e0'),
                        title_font=dict(family='Exo 2', color='#00d97e')
                    )
                    st.plotly_chart(fig3, use_container_width=True)
            with col4:
                if top_sellers:
                    df_sellers = pd.DataFrame(top_sellers)
                    fig4 = px.bar(df_sellers, x='shop_name', y='revenue', title='Top Sellers by Revenue', text_auto=True,
                                  labels={'shop_name': 'Seller', 'revenue': 'Revenue ($)'},
                                  color_discrete_sequence=['#00d97e'])
                    fig4.update_layout(
                        paper_bgcolor='#0d2818', plot_bgcolor='#0a1a14',
                        font=dict(family='Josefin Sans', color='#e0e0e0'),
                        title_font=dict(family='Exo 2', color='#00d97e'),
                        xaxis=dict(gridcolor='#1a4d35'), yaxis=dict(gridcolor='#1a4d35')
                    )
                    st.plotly_chart(fig4, use_container_width=True)

    with tab4:
        st.subheader("Coupon Management")
        
        with st.expander("Create New Coupon"):
            with st.form("add_coupon_form"):
                code = st.text_input("Coupon Code (e.g. SUMMER20)")
                c1, c2 = st.columns(2)
                with c1:
                    discount_type = st.selectbox("Discount Type", ["percentage", "fixed"])
                    min_order = st.number_input("Minimum Order Amount ($)", min_value=0.0)
                    start_date = st.date_input("Start Date", datetime.today())
                with c2:
                    discount_value = st.number_input("Discount Value", min_value=0.01)
                    max_uses = st.number_input("Max Uses", min_value=1, value=100)
                    end_date = st.date_input("End Date", datetime.today() + timedelta(days=30))
                
                if st.form_submit_button("Create Coupon"):
                    if not code:
                        st.error("Please enter a coupon code.")
                    elif start_date > end_date:
                        st.error("End date must be after start date.")
                    else:
                        success = add_coupon(code.upper(), discount_type, discount_value, min_order, max_uses, start_date, end_date)
                        if success:
                            st.success("Coupon created successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to create coupon. Code might already exist.")
                            
        st.write("### Active Coupons")
        coupons = get_all_coupons()
        if not coupons:
            st.info("No coupons found.")
        else:
            df_coupons = pd.DataFrame(coupons)
            st.dataframe(df_coupons, use_container_width=True)
