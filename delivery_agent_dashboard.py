import streamlit as st
import pandas as pd
from database import get_or_create_delivery_agent, get_agent_shipments, update_shipment_status_by_agent

def show_delivery_agent_dashboard():
    st.title("Delivery Agent Portal")
    
    user_info = st.session_state.user_info
    agent_id = get_or_create_delivery_agent(user_info['user_id'], user_info['name'])
    
    if not agent_id:
        st.error("Could not load delivery agent profile.")
        return

    st.subheader("Your Assigned Shipments")
    
    shipments = get_agent_shipments(agent_id)
    
    if not shipments:
        st.info("You currently have no assigned shipments. Enjoy your break!")
    else:
        for s in shipments:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**Order ID:** {s['order_id']}")
                    st.write(f"**Tracking Code:** {s['tracking_code']}")
                    st.write(f"**Status:** {s['status'].upper()}")
                
                with col2:
                    st.write("**Customer:**")
                    st.write(f"👤 {s['customer_name']}")
                    st.write(f"📞 {s['customer_phone']}")
                    st.write(f"📍 {s['street']}, {s['city']} - {s['postal_code']}")
                    
                with col3:
                    st.write("**Update Status:**")
                    if s['status'] == 'delivered':
                        st.success("Delivered!")
                    else:
                        status_options = ['dispatched', 'in_transit', 'delivered']
                        current_status = s['status']
                        if current_status not in status_options:
                            status_options.insert(0, current_status)
                        
                        new_status = st.selectbox(
                            "Status", 
                            status_options, 
                            index=status_options.index(current_status),
                            key=f"status_{s['shipment_id']}"
                        )
                        
                        if st.button("Update", key=f"btn_{s['shipment_id']}"):
                            if new_status != current_status:
                                if update_shipment_status_by_agent(s['shipment_id'], new_status):
                                    st.success(f"Shipment marked as {new_status}!")
                                    st.rerun()
                                else:
                                    st.error("Failed to update status.")
