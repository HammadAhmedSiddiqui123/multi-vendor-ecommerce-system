import streamlit as st
import pandas as pd
import plotly.express as px
from database import (
    get_or_create_seller, get_seller_stats, get_seller_products,
    add_product, delete_product, get_seller_orders, get_categories,
    update_order_status, update_product_stock
)

def show_seller_dashboard():
    st.title("Seller Portal")
    
    user_info = st.session_state.user_info
    seller_id = get_or_create_seller(user_info['user_id'], user_info['name'])
    
    if not seller_id:
        st.error("Could not load seller profile.")
        return

    tab1, tab2, tab3 = st.tabs(["Dashboard", "My Products", "Orders"])

    with tab1:
        st.subheader("Overview")
        stats = get_seller_stats(seller_id)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Completed Orders", stats['total_orders'])
        with col2:
            st.metric("Total Revenue", f"${stats['total_revenue']}")
            
        st.divider()
        st.subheader("Low Stock Alerts")
        products = get_seller_products(seller_id)
        low_stock = [p for p in products if p['stock'] < 10]
        if not low_stock:
            st.success("All products are well stocked!")
        else:
            for p in low_stock:
                st.warning(f"**{p['product_name']}** has only {p['stock']} units left!")

    with tab2:
        st.subheader("Manage Products")
        
        if "seller_msg" in st.session_state:
            m_type, m_text = st.session_state.seller_msg
            if m_type == "success":
                st.success(m_text)
                st.toast(m_text)
            else:
                st.error(m_text)
            del st.session_state.seller_msg

        with st.expander("Add New Product"):
            with st.form("add_product_form"):
                p_name = st.text_input("Product Name")
                p_desc = st.text_area("Description")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    p_price = st.number_input("Price ($)", min_value=0.01, value=10.0)
                with c2:
                    p_stock = st.number_input("Stock", min_value=0, value=10)
                with c3:
                    categories = get_categories()
                    p_cat = st.selectbox("Category", categories if categories else ["Electronics", "Clothing", "Books"])
                    
                if st.form_submit_button("Save Product"):
                    if not p_name or not p_desc:
                        st.error("Please fill all details.")
                    else:
                        result = add_product(seller_id, p_name, p_desc, p_price, p_stock, p_cat)
                        if result == True:
                            st.session_state.seller_msg = ("success", f"Product '{p_name}' added successfully!")
                            st.rerun()
                        elif result == "exists":
                            st.warning(f"You already have an active product named '{p_name}'. Please use a different name or update the existing stock.")
                        else:
                            st.error("Failed to add product. Please try again.")
                            
        st.write("### Your Products")
        products = get_seller_products(seller_id) # reload to be safe
        if not products:
            st.info("You haven't added any products yet.")
        else:
            st.write("#### Product Stock Levels")
            df_products = pd.DataFrame(products)
            fig_stock = px.bar(df_products, x='product_name', y='stock', 
                               title="Stock Level per Product", 
                               labels={'product_name': 'Product', 'stock': 'Units in Stock'}, 
                               text_auto=True,
                               color_discrete_sequence=['#00d97e'])
            fig_stock.update_layout(
                paper_bgcolor='#0d2818', plot_bgcolor='#0a1a14',
                font=dict(family='Josefin Sans', color='#e0e0e0'),
                title_font=dict(family='Exo 2', color='#00d97e'),
                xaxis=dict(gridcolor='#1a4d35'), yaxis=dict(gridcolor='#1a4d35')
            )
            st.plotly_chart(fig_stock, use_container_width=True)
            st.divider()
                
            for p in products:
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                col1.write(f"**{p['product_name']}**")
                col2.write(f"${p['price']}")
                col3.write(f"Current Stock: {p['stock']}")
                
                with col4:
                    new_stock = st.number_input("Update Stock", value=p['stock'], min_value=0, key=f"stock_{p['product_id']}", label_visibility="collapsed")
                    if st.button("Save", key=f"save_stock_{p['product_id']}"):
                        if new_stock != p['stock']:
                            if update_product_stock(p['product_id'], new_stock):
                                st.success("Stock updated!")
                                st.rerun()
                            else:
                                st.error("Update failed.")
                with col5:
                    if st.button("Delete", key=f"del_{p['product_id']}"):
                        delete_product(p['product_id'])
                        st.rerun()

    with tab3:
        st.subheader("Customer Orders & Analytics")
        
        orders = get_seller_orders(seller_id)
        
        if not orders:
            st.info("No orders for your products yet.")
        else:
            df_orders = pd.DataFrame(orders)
            
            with st.expander("View Order Analytics", expanded=True):
                col1, col2 = st.columns(2)
                
                df_orders['order_date_dt'] = pd.to_datetime(df_orders['order_date'])
                df_daily = df_orders.groupby(df_orders['order_date_dt'].dt.date)['subtotal'].sum().reset_index()
                fig_rev = px.line(df_daily, x='order_date_dt', y='subtotal', markers=True, title="Daily Revenue", labels={'order_date_dt': 'Date', 'subtotal': 'Revenue ($)'},
                                  color_discrete_sequence=['#00d97e'])
                fig_rev.update_layout(
                    paper_bgcolor='#0d2818', plot_bgcolor='#0a1a14',
                    font=dict(family='Josefin Sans', color='#e0e0e0'),
                    title_font=dict(family='Exo 2', color='#00d97e'),
                    xaxis=dict(gridcolor='#1a4d35'), yaxis=dict(gridcolor='#1a4d35')
                )
                col1.plotly_chart(fig_rev, use_container_width=True)
                
                status_counts = df_orders['order_status'].value_counts().reset_index()
                status_counts.columns = ['status', 'count']
                fig_status = px.pie(status_counts, names='status', values='count', title="Orders by Status", hole=0.3,
                                    color_discrete_sequence=['#00d97e', '#00b368', '#f5a623', '#e74c3c', '#8aa89a', '#1a4d35'])
                fig_status.update_layout(
                    paper_bgcolor='#0d2818', plot_bgcolor='#0a1a14',
                    font=dict(family='Josefin Sans', color='#e0e0e0'),
                    title_font=dict(family='Exo 2', color='#00d97e')
                )
                col2.plotly_chart(fig_status, use_container_width=True)
                
            st.divider()
            
            status_options_filter = ["All", "pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]
            selected_status = st.selectbox("Filter Orders by Status", status_options_filter)
            
            filtered_orders = orders
            if selected_status != "All":
                filtered_orders = [o for o in orders if o['order_status'] == selected_status]
                
            if not filtered_orders:
                st.warning("No orders match the selected status.")
            else:
                for o in filtered_orders:
                    with st.container(border=True):
                        st.write(f"**Order #{o['order_id']}** - {o['order_date'].strftime('%Y-%m-%d')}")
                        st.write(f"**Customer:** {o['customer_name']}")
                        st.write(f"**Product:** {o['product_name']} (Qty: {o['quantity']})")
                        st.write(f"**Subtotal:** ${o['subtotal']}")
                        
                        status_options = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
                        current_status = o['order_status']
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            new_status = st.selectbox(
                                "Update Status", 
                                status_options, 
                                index=status_options.index(current_status) if current_status in status_options else 0,
                                key=f"status_{o['order_id']}_{o['product_name']}"
                            )
                        with col2:
                            st.write("")
                            st.write("")
                            if st.button("Update", key=f"btn_status_{o['order_id']}_{o['product_name']}"):
                                if new_status != current_status:
                                    success = update_order_status(o['order_id'], new_status)
                                    if success:
                                        st.success(f"Order #{o['order_id']} status updated to {new_status}!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to update status.")
