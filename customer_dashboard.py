import streamlit as st
import pandas as pd
from database import (
    get_or_create_customer, get_categories, get_all_products,
    get_product_details, get_product_reviews, get_customer_orders,
    get_cart_items, add_to_cart, remove_from_cart,
    validate_purchase_for_review, submit_review, validate_coupon,
    process_checkout, get_order_items,
    get_customer_addresses, add_address, update_address, delete_address
)

def show_customer_dashboard():
    st.title("Customer Portal")
    
    # Ensure customer profile exists
    user_info = st.session_state.user_info
    customer_id = get_or_create_customer(user_info['user_id'], user_info['name'], user_info['email'])
    
    if not customer_id:
        st.error("Could not load customer profile.")
        return

    # Navigation
    tab1, tab2, tab3, tab4 = st.tabs(["Shop", "My Cart", "Order History", "My Addresses"])

    with tab1:
        if 'view_product_id' in st.session_state:
            # Show Product Details Exclusively
            if st.button("Back to Shop"):
                del st.session_state['view_product_id']
                st.rerun()
                
            st.divider()
            details = get_product_details(st.session_state['view_product_id'])
            if details:
                st.subheader(f"{details['product_name']}")
                
                col_img, col_info = st.columns([1, 2])
                with col_img:
                    if details['image_url']:
                        st.image(details['image_url'], use_container_width=True)
                    else:
                        st.info("No image available")
                        
                with col_info:
                    st.write(f"**Brand:** {details['brand_name'] or 'N/A'}")
                    st.write(f"**Category:** {details['category_name']} > {details['subcategory_name'] or 'N/A'}")
                    st.write(f"**Price:** ${details['price']}")
                    st.write(f"**Stock:** {details['stock']} available")
                    st.write(f"**Description:**\n{details['description']}")
                    
                    with st.form(key=f"add_cart_detail_{details['product_id']}"):
                        quantity = st.number_input("Qty", min_value=1, max_value=max(1, details['stock']), value=1)
                        submit = st.form_submit_button("Add to Cart")
                        if submit:
                            if details['stock'] > 0:
                                success = add_to_cart(customer_id, details['product_id'], quantity)
                                if success:
                                    st.success(f"Added {quantity} to cart!")
                                else:
                                    st.error("Failed to add to cart.")
                            else:
                                st.error("Out of stock!")
                
                st.divider()
                # Show reviews
                reviews = get_product_reviews(details['product_id'])
                if reviews:
                    st.write("### Reviews")
                    for r in reviews:
                        st.write(f"**{r['customer_name']}** ({r['rating_value']}/5) - {r['review_date'].strftime('%Y-%m-%d')}")
                        st.write(f"> {r['comment']}")
                else:
                    st.write("No reviews yet.")
                    
                # Review Submission
                if validate_purchase_for_review(customer_id, details['product_id']):
                    st.write("### Write a Review")
                    with st.form(key=f"review_form_{details['product_id']}"):
                        rating = st.slider("Rating", 1, 5, 5)
                        comment = st.text_area("Your Review")
                        if st.form_submit_button("Submit Review"):
                            if not comment:
                                st.error("Please write a comment.")
                            else:
                                if submit_review(customer_id, details['product_id'], rating, comment):
                                    st.success("Review submitted!")
                                    st.rerun()
                                else:
                                    st.error("Failed to submit review.")
                    
        else:
            # Show Product Grid
            st.subheader("Discover Products")
            
            # Search & Filter
            col1, col2 = st.columns([3, 1])
            with col1:
                search_query = st.text_input("Search products...", "")
            with col2:
                categories = ["All"] + get_categories()
                selected_category = st.selectbox("Category", categories)
                
            products = get_all_products(search_query, selected_category)
            
            if not products:
                st.info("No products found.")
            else:
                # Display products in a grid
                cols = st.columns(3)
                for idx, product in enumerate(products):
                    with cols[idx % 3]:
                        with st.container(border=True):
                            st.write(f"**{product['product_name']}**")
                            st.write(f"${product['price']}")
                            st.write(f"{product['category_name']}")
                            
                            # Add to Cart form
                            with st.form(key=f"add_cart_{product['product_id']}"):
                                quantity = st.number_input("Qty", min_value=1, max_value=max(1, product['stock']), value=1)
                                submit = st.form_submit_button("Add to Cart")
                                if submit:
                                    if product['stock'] > 0:
                                        success = add_to_cart(customer_id, product['product_id'], quantity)
                                        if success:
                                            st.success(f"Added {quantity} to cart!")
                                        else:
                                            st.error("Failed to add to cart.")
                                    else:
                                        st.error("Out of stock!")
                                        
                            # View Details
                            if st.button("View Details", key=f"details_{product['product_id']}"):
                                st.session_state['view_product_id'] = product['product_id']
                                st.rerun()

    with tab2:
        st.subheader("My Shopping Cart")
        items, cart_id = get_cart_items(customer_id)
        
        if not items:
            st.info("Your cart is empty.")
        else:
            total = 0
            for item in items:
                subtotal = item['price'] * item['quantity']
                total += subtotal
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                col1.write(f"**{item['product_name']}**")
                col2.write(f"${item['price']} x {item['quantity']}")
                col3.write(f"**${subtotal}**")
                if col4.button("Remove", key=f"remove_{item['cart_item_id']}"):
                    remove_from_cart(item['cart_item_id'])
                    st.rerun()
                    
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(f"Subtotal: ${total:.2f}")
                
                coupon_code = st.text_input("Enter Coupon Code")
                if st.button("Apply Coupon"):
                    if coupon_code:
                        res = validate_coupon(coupon_code, total)
                        if res['valid']:
                            st.success(f"Coupon Applied! Saved ${res['discount_amount']:.2f}")
                            st.session_state['discount'] = res['discount_amount']
                            st.session_state['final_total'] = res['new_total']
                            st.session_state['coupon_id'] = res['coupon_id']
                        else:
                            st.error(res['msg'])
                            if 'discount' in st.session_state:
                                del st.session_state['discount']
                                del st.session_state['final_total']
                                del st.session_state['coupon_id']
                                
            with col2:
                final_checkout_amount = total
                coupon_id_to_use = None
                
                if 'final_total' in st.session_state and 'discount' in st.session_state:
                    st.write(f"**Discount:** -${st.session_state['discount']:.2f}")
                    st.subheader(f"Total: ${st.session_state['final_total']:.2f}")
                    final_checkout_amount = st.session_state['final_total']
                    coupon_id_to_use = st.session_state.get('coupon_id')
                else:
                    st.subheader(f"Total: ${total:.2f}")

            # ── Shipping Address Selection ──────────────────────────────
            st.divider()
            st.subheader("Shipping Address")
            
            user_id = user_info['user_id']
            addresses = get_customer_addresses(user_id)
            
            if not addresses:
                st.warning("You have no saved addresses. Please add one in the 'My Addresses' tab before checking out.")
                selected_address_id = None
            else:
                address_options = {}
                for addr in addresses:
                    postal = f", {addr['postal_code']}" if addr['postal_code'] else ""
                    label = f"{addr['label']}: {addr['street']}, {addr['city']}{postal}"
                    address_options[label] = addr['address_id']
                
                # Select address
                option_keys = list(address_options.keys())
                selected_label = st.selectbox("Select delivery address", option_keys)
                selected_address_id = address_options[selected_label]
            
            # ── Checkout Button ─────────────────────────────────────────
            if st.button("Proceed to Checkout", type="primary"):
                if not selected_address_id:
                    st.warning("Please add a delivery address first! Go to the 'My Addresses' tab to add one.")
                else:
                    success = process_checkout(customer_id, cart_id, final_checkout_amount, coupon_id_to_use, selected_address_id)
                    if success:
                        st.success("Checkout successful! Your order has been placed.")
                        # Clear session state items for coupon
                        if 'discount' in st.session_state: del st.session_state['discount']
                        if 'final_total' in st.session_state: del st.session_state['final_total']
                        if 'coupon_id' in st.session_state: del st.session_state['coupon_id']
                        st.rerun()
                    else:
                        st.error("Checkout failed. Please ensure all items are still in stock.")

    with tab3:
        st.subheader("My Orders")
        orders = get_customer_orders(customer_id)
        if not orders:
            st.info("You haven't placed any orders yet.")
        else:
            for order in orders:
                with st.expander(f"Order #{order['order_id']} - ${order['total_amount']} ({order['order_status'].title()})"):
                    st.write(f"**Date:** {order['order_date']}")
                    st.write(f"**Payment Status:** {order['payment_status'] or 'Pending'}")
                    st.write(f"**Shipment Status:** {order['shipment_status'] or 'Pending'}")
                    if order['tracking_code']:
                        st.write(f"**Tracking Code:** {order['tracking_code']}")
                    if order.get('address_label'):
                        st.write(f"**Shipping Address:** {order['address_label']} - {order['address_street']}, {order['address_city']}")
                    
                    st.divider()
                    st.write("#### Order Items")
                    items = get_order_items(order['order_id'])
                    if items:
                        # Display as a clean table
                        df_items = pd.DataFrame(items)
                        df_items.columns = ["Product", "Qty", "Price", "Subtotal", "Seller"]
                        st.table(df_items)
                    else:
                        st.info("No item details found.")

    # ── Tab 4: My Addresses ─────────────────────────────────────────────
    with tab4:
        st.subheader("My Addresses")
        user_id = user_info['user_id']
        addresses = get_customer_addresses(user_id)
        
        # ── Add New Address Form ──
        st.write("#### Add New Address")
        with st.form("add_address_form", clear_on_submit=True):
            a_col1, a_col2 = st.columns(2)
            with a_col1:
                new_label = st.text_input("Label")
                new_street = st.text_input("Street Address")
            with a_col2:
                new_city = st.text_input("City")
                new_postal = st.text_input("Postal Code")
            
            if st.form_submit_button("Save Address", type="primary"):
                if not new_label or not new_street or not new_city:
                    st.error("Label, Street, and City are required.")
                else:
                    result = add_address(user_id, new_label, new_street, new_city, new_postal)
                    if result:
                        st.success("Address saved successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to save address.")
        
        st.divider()

        # ── Existing Addresses ──
        if not addresses:
            st.info("You have no saved addresses yet. Add one above to get started.")
        else:
            st.write("#### Saved Addresses")
            for addr in addresses:
                postal_display = f", {addr['postal_code']}" if addr['postal_code'] else ""
                
                with st.container(border=True):
                    col_info, col_actions = st.columns([4, 2])
                    
                    with col_info:
                        st.write(f"**{addr['label']}**")
                        st.write(f"{addr['street']}, {addr['city']}{postal_display}")
                    
                    with col_actions:
                        btn_cols = st.columns(2)
                        
                        # Edit button - toggles edit mode in session state
                        edit_key = f"editing_addr_{addr['address_id']}"
                        if btn_cols[0].button("Edit", key=f"edit_{addr['address_id']}"):
                            st.session_state[edit_key] = not st.session_state.get(edit_key, False)
                            st.rerun()
                        
                        # Delete
                        if btn_cols[1].button("Delete", key=f"del_{addr['address_id']}"):
                            result = delete_address(addr['address_id'], user_id)
                            if result == "in_use":
                                st.error("Cannot delete this address - it is linked to existing orders.")
                            elif result:
                                st.success("Address deleted.")
                                st.rerun()
                            else:
                                st.error("Failed to delete address.")
                    
                    # Inline Edit Form
                    edit_key = f"editing_addr_{addr['address_id']}"
                    if st.session_state.get(edit_key, False):
                        with st.form(key=f"edit_form_{addr['address_id']}"):
                            e_col1, e_col2 = st.columns(2)
                            with e_col1:
                                edit_label = st.text_input("Label", value=addr['label'])
                                edit_street = st.text_input("Street", value=addr['street'])
                            with e_col2:
                                edit_city = st.text_input("City", value=addr['city'])
                                edit_postal = st.text_input("Postal Code", value=addr['postal_code'] or "")
                            
                            e_btn1, e_btn2 = st.columns(2)
                            with e_btn1:
                                if st.form_submit_button("Update Address", type="primary"):
                                    if not edit_label or not edit_street or not edit_city:
                                        st.error("Label, Street, and City are required.")
                                    else:
                                        result = update_address(addr['address_id'], user_id, edit_label, edit_street, edit_city, edit_postal)
                                        if result:
                                            st.success("Address updated!")
                                            del st.session_state[edit_key]
                                            st.rerun()
                                        else:
                                            st.error("Failed to update address.")
