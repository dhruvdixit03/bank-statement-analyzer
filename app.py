import streamlit as st
from bank_statement_parser import BankStatementParser
from bank_statement_analyzer import BankStatementAnalyzer
import os
import pandas as pd
import shutil
from contextlib import contextmanager



st.set_page_config(page_title="Bank Statement Analyzer", layout="wide")


def cleanup_temp_directories():
    """Clean up any existing temporary directories."""
    temp_dirs = ['temp', 'temp/tables']
    for dir_path in temp_dirs:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
            except Exception as e:
                print(f"Error cleaning up {dir_path}: {e}")

@contextmanager
def temporary_directory():
    """Create a temporary directory and clean it up when done."""
    os.makedirs("temp", exist_ok=True)
    os.makedirs("temp/tables", exist_ok=True)
    try:
        yield "temp"
    finally:
        cleanup_temp_directories()

def parse_markdown_table(markdown_text):
    lines = markdown_text.strip().split('\n')
    headers = [col.strip() for col in lines[0].split('|')[1:-1]]
    data_lines = lines[2:]
    data = [[cell.strip() for cell in line.split('|')[1:-1]] for line in data_lines if len(line.split('|')[1:-1]) == len(headers)]
    return pd.DataFrame(data, columns=headers)

# Initialize session state variables
for key, default_value in {
    'processed': False,
    'file_uploaded': False,
    'tables': [],
    'final_summary': "",
    'chat_messages': [{'role': "bot", 'content': "Hello, welcome to chat!"}],
    'waiting_for_response': False  # Prevents flickering & ensures first message works
}.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

st.title("📊 Bank Statement Analyzer")

uploaded_file = st.file_uploader("Upload Bank Statement (PDF)", type=["pdf"])

if uploaded_file and not st.session_state['processed']:
    st.session_state['processed'] = True  # Prevent re-processing
    st.session_state['file_uploaded'] = True
    with st.spinner('Processing your file...'):
        with temporary_directory() as temp_dir:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            parser = BankStatementParser(api_key="input-your-key")
            tables = parser.parse_statement(file_path, os.path.join(temp_dir, "tables"))

            analyzer = BankStatementAnalyzer()
            output_file = analyzer.analyze_tables(os.path.join(temp_dir, "tables"), os.path.join(temp_dir, "result.txt"))
            with open(output_file, "r", encoding="utf-8") as out_file:
                st.session_state['chat_file'] = out_file.read()
            final_summary = analyzer.generate_final_summary(output_file)

            st.session_state['tables'] = tables
            st.session_state['final_summary'] = final_summary  

if st.session_state['tables']:
    with st.expander("📄 Extracted Tables", expanded=False):
        for i, table in enumerate(st.session_state['tables'], 1):
            st.subheader(f"Table {i}")
            df = parse_markdown_table(table)
            st.dataframe(df, use_container_width=True)

if st.session_state['final_summary']:
    with st.expander("📊 AI Summary & Loan Decision", expanded=False):
        st.write(st.session_state['final_summary'])