import streamlit as st
import pandas as pd
import requests

API_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Excel Data Import", page_icon="📊")

st.title("📊 Excel Student Data Import")
st.markdown("Upload your existing Excel file containing student and academic data. The system will automatically map the columns to the database schema.")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls", "csv"])

if uploaded_file is not None:
    try:
        # Show a preview of the data
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.subheader("Data Preview")
        st.dataframe(df.head())
        
        st.info(f"Total Rows Detected: {len(df)}")
        st.info(f"Columns Detected: {', '.join(df.columns.tolist())}")

        if st.button("Import Data"):
            with st.spinner("Uploading and processing data..."):
                # Reset file pointer
                uploaded_file.seek(0)
                files = {"file": (uploaded_file.name, uploaded_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                
                # In a real app we'd pass headers={"Authorization": f"Bearer {st.session_state.token}"}
                response = requests.post(f"{API_URL}/excel/upload", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ Import Successful!")
                    
                    st.subheader("Import Summary")
                    st.write(f"- **Total Rows Processed:** {data['total_rows_processed']}")
                    st.write(f"- **New Students Added:** {data['records_added']}")
                    st.write(f"- **Students Updated:** {data['records_updated']}")
                    
                    st.subheader("Column Mapping Result")
                    mapping_df = pd.DataFrame(list(data['columns_mapped'].items()), columns=["Original Excel Column", "Mapped Database Field"])
                    st.table(mapping_df)
                else:
                    st.error(f"Failed to import data. Error: {response.text}")
                    
    except Exception as e:
        st.error(f"Error reading file: {e}")
