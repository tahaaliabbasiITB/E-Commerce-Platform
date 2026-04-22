import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="E-Com RDBMS Pro", layout="wide", page_icon="🛒")

# FastAPI Backend URL
BASE_URL = "http://127.0.0.1:8000"

# --- API HELPER FUNCTIONS ---
def get_data(endpoint):
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}")
        return response.json() if response.status_code == 200 else None
    except:
        return None

def post_data(endpoint, data):
    return requests.post(f"{BASE_URL}/{endpoint}", json=data)

def put_data(endpoint, data):
    return requests.put(f"{BASE_URL}/{endpoint}", json=data)

def delete_data(endpoint):
    return requests.delete(f"{BASE_URL}/{endpoint}")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🛠️ Admin Control")
page = st.sidebar.radio("Navigate to:", ["📊 Analytics Dashboard", "📦 Inventory Manager", "👥 User Directory", "🧾 Sales Records"])

# --- PAGE 1: ANALYTICS DASHBOARD (READ) ---
if page == "📊 Analytics Dashboard":
    st.title("Business Intelligence Dashboard")
    st.caption("Pulling live relational data from Neon PostgreSQL via FastAPI Logic Tier")

    # Metrics Summary
    summary = get_data("dashboard/summary")
    if summary:
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Total Revenue", f"{summary['revenue']:,.2f}")
        with m2:
            st.metric("Product Count", summary['product_count'])
        with m3:
            st.metric("Low Stock Alerts", summary['low_stock_alerts'], delta="-20%", delta_color="inverse")

    st.divider()

    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Inventory Distribution")
        inv = get_data("inventory")
        prod = get_data("products")
        if inv and prod:
            df_inv = pd.DataFrame(inv)
            df_prod = pd.DataFrame(prod)
            df_merged = pd.merge(df_inv, df_prod, on="product_id")
            fig = px.bar(df_merged, x="product_name", y="stock_quantity", color="stock_quantity", 
                         labels={"product_name": "Product", "stock_quantity": "Stock"})
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Order Status Metrics")
        orders = get_data("orders")
        if orders:
            df_o = pd.DataFrame(orders)
            fig_pie = px.pie(df_o, names="status", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_pie, use_container_width=True)

# --- PAGE 2: INVENTORY MANAGER (FULL CRUD: C, U, D) ---
elif page == "📦 Inventory Manager":
    st.title("Product & Inventory Management (CRUD)")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 View Catalog", "➕ Add Product", "✏️ Edit Product", "🗑️ Remove Product"])

    # READ
    with tab1:
        st.subheader("Current RDBMS Product Records")
        all_prods = get_data("products")
        if all_prods:
            st.dataframe(pd.DataFrame(all_prods), use_container_width=True, hide_index=True)

    # CREATE
    with tab2:
        st.subheader("Insert New Product")
        with st.form("create_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Product Name")
            price = c2.number_input("Base Price ($)", min_value=1.0, format="%.2f")
            cat = c1.number_input("Category ID", min_value=1, step=1)
            ven = c2.number_input("Vendor ID", min_value=1, step=1)
            stock = st.number_input("Initial Inventory Stock", min_value=0)
            desc = st.text_area("Product Description")
            
            if st.form_submit_button("Submit to Database"):
                payload = {"product_name": name, "description": desc, "base_price": price, 
                           "category_id": cat, "vendor_id": ven, "stock": stock}
                res = post_data("products/create", payload)
                if res.status_code == 200:
                    st.success("SUCCESS: Product & Inventory records created!")
                else:
                    st.error(f"FAILED: {res.text}")

    # UPDATE
    with tab3:
        st.subheader("Update Existing Product")
        upd_id = st.number_input("Enter Product ID to modify", min_value=1, step=1)
        
        if st.button("Fetch Product Details"):
            all_prods = get_data("products")
            target = next((p for p in all_prods if p['product_id'] == upd_id), None)
            if target:
                st.session_state['edit_prod'] = target
            else:
                st.error("Product ID not found in database.")

        if 'edit_prod' in st.session_state:
            with st.form("update_form"):
                u_name = st.text_input("Update Name", value=st.session_state['edit_prod']['product_name'])
                u_price = st.number_input("Update Price", value=float(st.session_state['edit_prod']['base_price']))
                u_desc = st.text_area("Update Description", value=st.session_state['edit_prod']['description'])
                
                if st.form_submit_button("Save Changes (PUT)"):
                    upd_payload = {"product_name": u_name, "base_price": u_price, "description": u_desc}
                    res = put_data(f"products/{upd_id}", upd_payload)
                    if res.status_code == 200:
                        st.success(f"UPDATED: Product {upd_id} modified successfully.")
                        del st.session_state['edit_prod']
                    else:
                        st.error("Update failed.")

    # DELETE
    with tab4:
        st.subheader("Permanent Record Deletion")
        del_id = st.number_input("Enter Product ID to delete", min_value=1, step=1)
        st.warning("Action is permanent! This will trigger a CASCADE delete in the RDBMS.")
        if st.button("Confirm DELETE", type="primary"):
            res = delete_data(f"products/{del_id}")
            if res.status_code == 200:
                st.info(f"DELETED: Product {del_id} removed from system.")
            else:
                st.error("Delete command rejected.")

# --- PAGE 3: USER DIRECTORY ---
elif page == "👥 User Directory":
    st.title("User & Stakeholder Directory")
    users = get_data("users")
    if users:
        df_u = pd.DataFrame(users)
        st.dataframe(df_u[["user_id", "first_name", "last_name", "email", "role_id"]], use_container_width=True)

# --- PAGE 4: SALES RECORDS ---
elif page == "🧾 Sales Records":
    st.title("Transactional History")
    orders = get_data("orders")
    if orders:
        st.subheader("Orders Table")
        st.dataframe(pd.DataFrame(orders), use_container_width=True)
    
    payments = get_data("payments")
    if payments:
        st.subheader("Payments Table")
        st.dataframe(pd.DataFrame(payments), use_container_width=True)