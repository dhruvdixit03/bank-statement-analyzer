import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from langchain_ollama import OllamaLLM
import re

st.set_page_config(page_title="Markdown to Pie Chart", page_icon="📊", layout="wide")
st.session_state['pie_chart'] = ''
st.markdown("""
    <style>
        body {
            background-color: #f8f9fa;
        }
        .main-container {
            max-width: 800px;
            margin: auto;
            padding: 2rem;
        }
        .stTextArea label {
            font-size: 18px;
            font-weight: bold;
        }
        .stButton>button {
            background-color: #333;
            color: white;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #555;
        }
        .status-container {
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
            border-radius: 10px;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .loading {
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeeba;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>📊 Convert Markdown Table to Pie Chart</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 16px; color: gray;'>A simple, yet powerful tool to visualize expenses from Markdown tables.</p>", unsafe_allow_html=True)

table_folder = "temp/tables"

if 'pie_chart' not in st.session_state:
    st.session_state['pie_chart'] = ''

if 'cat_table' not in st.session_state:
    st.session_state['cat_table'] = ''

def parse_markdown_table(markdown_text):
    lines = markdown_text.strip().split('\n')
    
    headers = [col.strip() for col in lines[0].split('|')[1:-1]]
    
    data = []
    for line in lines[2:]:  
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        if len(cells) == len(headers):  
            data.append(cells)
    
    return pd.DataFrame(data, columns=headers)

if os.path.exists(table_folder):
    table_files = sorted(os.listdir(table_folder))  
    for table_file in table_files:
        file_path = os.path.join(table_folder, table_file)
        with open(file_path, "r", encoding="utf-8") as f:
            table_content = f.read()
            print(f"Table {table_file}:\n{table_content}\n{'='*50}")

# Display processing status
if 'tables' in st.session_state:
    if st.session_state['pie_chart']:
        with st.status("✅ Data processed successfully!", expanded=True) as status:
            st.markdown("<div class='status-container success'>✅ Data processed successfully!</div>", unsafe_allow_html=True)
            st.write("### Final Expense Table")
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("### 📊 Expense Breakdown")
                stored_fig = st.session_state['pie_chart']
                st.pyplot(stored_fig)
            with col2:
                st.markdown("### 📜 Parsed Data")
                stored_df = st.session_state['cat_chart']
                st.dataframe(stored_df, hide_index=True, use_container_width=True)
            
            
                
    elif st.session_state['tables'] and not st.session_state['pie_chart']:
        new_tables = ""

        with st.status("Processing data...", expanded=True) as status:
            st.markdown("<div class='status-container loading'>⏳ Processing transactions...</div>", unsafe_allow_html=True)

            for i, table in enumerate(st.session_state['tables'], 1):
                llm = OllamaLLM(model="categorize_transactions_mistral", num_ctx=8192)
                prompt = 'Make sure you only output the new table and nothing else. No words, just the new table. Possible Categories: Groceries, Transportation, Fees, Rent, Balance, Car, Utilities, Entertainment, Food/Drink, Health, Shopping, Deposits, etc. If the table does not hold transactions do not edit it.'
                new_table = llm.invoke(f'{prompt}\n\n{table}')
                new_tables += f'{new_table}\n\n'
            
            print(new_tables)
            print('\n\n\n')

            phi4 = OllamaLLM(model="sum_categories_phi4", num_ctx=8192)
            prompt = f'''
Based on the following data, create a markdown expense table with two columns: "Category" and "Amount Expensed". Only categories that are expenses, not incomes should be included (salary should not be included). If the table does not include transactions, don't incorporate it. Make sure the table is the only output, with no explanation, extra words, or anything other than the table.

Example Output:
| Category     | Amount (£) |
|--------------|------------|
| Rent         | 500.00     |
| Utilities    | 100.00     |
| Groceries    | 150.00     |

Now, please generate the table from the data below:

{new_tables}'''
            category_table = phi4.invoke(prompt)
            print(category_table)
            

            # Update status to success
            status.update(label="✅ Data processed successfully!", state="complete", expanded=False)
            st.markdown("<div class='status-container success'>✅ Data processed successfully!</div>", unsafe_allow_html=True)

            st.write("### Final Expense Table")
            lines = category_table.strip().split("\n")[2:]  

            categories = []
            amounts = []

            for line in lines:
                parts = re.split(r'\s*\|\s*', line.strip('|'))  
                category = parts[0].strip()
                try:
                    amount = float(parts[1].strip().replace(',', ''))  
                    if amount > 0:  # Ignore zero values
                        categories.append(category)
                        amounts.append(amount)
                except ValueError:
                    st.error(f"Invalid number in row: {line}")
                    st.stop()

            # Pie Chart & Data Table Side by Side
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("### 📊 Expense Breakdown")
                fig, ax = plt.subplots(figsize=(6, 6))
                wedges, texts, autotexts = ax.pie(
                    amounts, labels=categories, autopct='%1.1f%%', startangle=140,
                    textprops={'fontsize': 12, 'weight': 'bold'}, wedgeprops={'edgecolor': 'black'}
                )
                ax.set_title("Expense Breakdown", fontsize=16, fontweight="bold")

                for text in texts:
                    text.set_color("#333")
                for autotext in autotexts:
                    autotext.set_color("darkred")

                st.pyplot(fig)
                st.session_state['pie_chart'] = fig

            # Display Data Table
            with col2:
                st.markdown("### 📜 Parsed Data")
                st.dataframe({"Category": categories, "Amount": amounts}, hide_index=True, use_container_width=True)
                st.session_state['cat_chart'] = {"Category": categories, "Amount": amounts}
        

else:
    st.write("loading ...")
