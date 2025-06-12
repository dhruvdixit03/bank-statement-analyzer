from langchain_ollama import OllamaLLM
import os
import re
from concurrent.futures import ThreadPoolExecutor

class BankStatementAnalyzer:
    def __init__(self, summary_model = "gemma2:9b", reasoning_model = "phi4"):
        self.summary_llm = OllamaLLM(model=summary_model, num_ctx = 4096)
        self.reasoning_llm = OllamaLLM(model=reasoning_model, num_ctx = 8192)
        
    def get_sorted_files(self, folder_path):
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        files.sort(key=lambda x: [int(num) if num.isdigit() else num for num in re.split(r'(\d+)', x)])
        return files
    
    def analyze_tables(self, folder_path, output_file):
        files = self.get_sorted_files(folder_path)
        # ans = []
        tables = []
        
        for cur_file in files:
            with open(cur_file, "r", encoding="utf-8") as file:
                markdown_content = file.read()
                tables.append((cur_file, markdown_content))
        
        # Define LLM processing function
        def process_table(file_data):
            cur_file, markdown_content = file_data
            prompt = (
                "Imagine you are a bank statement analyzer. "
                "I have given you a table from a bank statement. "
                "Summarize the transactions in this table. Identify income, debt, spending habits, "
                "and concerning transactions."
                "Include amounts for each section as evidence."
                "Don't make it too long and only have the important details. No fluff."
            )
            response = self.summary_llm.invoke(f"{prompt}\n\n{markdown_content}")
            print("ONE:")
            print(response, '\n\n\n\n')
            return f"File: {cur_file}\n{response}\n\n"

        # Run LLM calls in parallel
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(process_table, tables))
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as out_file:
            out_file.writelines(results)
        
        return output_file
    
    
    def generate_final_summary(self, output_file):
        with open(output_file, "r", encoding="utf-8") as out_file:
            final_summary = out_file.read()
        
        final_prompt = '''
Imagine you are a bank statement analyzer. I have provided you with summaries of tables from a bank statement. Based on this information, I need you to give me an in-depth analysis of whether this person should receive a loan. Your analysis should include the following:

1. **Income Stability**:
    - Analyze the consistency and frequency of income deposits.
    - Identify any irregularities or fluctuations in income.

2. **Debt-to-Income Ratio (DTI)**:
   - Calculate the DTI ratio using the formula: (Total Monthly Debt Payments / Monthly Income) * 100.
    - Only include debt payments (e.g., loans, credit card payments) in the calculation, not daily expenses.
    - Interpret the DTI ratio (e.g., < 20% is excellent, 20-35% is manageable, > 35% is risky).

3. **Spending Habits**:
    - Analyze recurring expenses (e.g., rent, utilities, subscriptions).
    - Identify discretionary spending (e.g., entertainment, dining out).
    - Look for patterns of overspending or financial mismanagement.

4. **Overall Financial Health**:
    - Check for red flags such as overdrafts, insufficient funds, or late payments.
    - Evaluate the consistency of deposits and expenses.
    - Assess the individual's ability to save or invest.

5. **Conclusion**:
    - Based on the above analysis, provide a clear recommendation (Yes or No) on whether the loan should be approved.
    - Justify your recommendation with specific insights from the data.

Here is the bank statement summary:
\n\n''' + final_summary
        return self.reasoning_llm.invoke(final_prompt)
    
    
