# Bank Statement Analysis with AI

## Overview
This project is an AI-powered system designed to analyze bank statements and extract meaningful insights. It leverages LlamaParse for transaction extraction while providing a user-friendly frontend for financial data visualization and insights generation.

## Features
- **Automated Data Extraction**: Parses bank statements and extracts transaction details.
- **ML-Based Table Recognition**: Uses AI to extract tables from scanned or digital statements.
- **Summarization & Insights**: Provides key financial metrics, spending trends, and income analysis.
- **Interactive UI**: Built with Streamlit for a clean and aesthetic presentation.

## Tech Stack
- **Backend**: Python, Pandas
- **Frontend**: Streamlit 
- **Machine Learning**: LlamaParse, Ollama (phi4, gemma2, mistral)

## Installation & Setup
### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/bank-statement-analysis.git
cd bank-statement-analysis
```
### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
### 3. Run the Application
```bash
streamlit run app.py
```

## Usage
1. **Upload a Bank Statement (PDF).**
2. **AI extracts and categorizes transactions automatically.**
3. **View financial insights through an interactive dashboard.**
4. **Chat with PDF**
5. **Make sure to update the Ollama models to your own local models for customizaility.**

