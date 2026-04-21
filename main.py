import streamlit as st
import requests
import re
import pandas as pd

st.set_page_config(page_title="ASOS Scraper", layout="wide")

st.title("ASOS Product Extractor")

url_input = st.text_input("Enter ASOS URL or Product ID:", placeholder="https://www.asos.com/prd/...")

if st.button("Extract"):
    # 1. Parse the ID from URL
    match = re.search(r'(?:/prd/|(?:\b))(\d{8,10})(?:\b)', url_input)
    if match:
        product_id = match.group(1)
        
        # 2. Hit the FastAPI Endpoint
        with st.spinner("Fetching dummy data from FastAPI..."):
            try:
                backend_url = f"http://127.0.0.1:8000/extract?product_id={product_id}"
                response = requests.get(backend_url)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Extraction Complete!")

                    # --- UI DISPLY: TABLE WITH IMAGE ---
                    
                    # We format the data into a list for Pandas
                    # Note: We take the first image from the list for the table
                    table_data = [{
                        "Image": data["images"][0] + "?$n_320w$", # Thumbnail size
                        "Title": data["title"],
                        "Brand": data["brand"],
                        "Product ID": product_id,
                        "Link": data["url"]
                    }]

                    df = pd.DataFrame(table_data)

                    # Display using Streamlit's modern Data Column configuration
                    st.subheader("Product Details")
                    st.data_editor(
                        df,
                        column_config={
                            "Image": st.column_config.ImageColumn(
                                "Product Image", help="Preview of the product"
                            ),
                            "Link": st.column_config.LinkColumn("View on ASOS")
                        },
                        hide_index=True,
                        use_container_width=True
                    )

                else:
                    st.error("Backend API is not responding correctly.")
            except Exception as e:
                st.error(f"Could not connect to Backend: {e}")
    else:
        st.error("Please enter a valid ASOS product URL.")