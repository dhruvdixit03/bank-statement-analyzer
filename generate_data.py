import os
import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

fake = Faker()

categories = {
    "Deposits": ["Salary", "Business Revenue", "Refund"],
    "Fixed Expenses": ["Rent", "Utilities", "Loan Payment", "Insurance"],
    "Variable Expenses": ["Groceries", "Dining", "Shopping", "Travel"],
    "Debt Payments": ["Credit Card Payment", "Other Loan"]
}

output_folder = "synthetic_statements"
os.makedirs(output_folder, exist_ok=True)

def generate_transactions(num_transactions=100, start_date="2023-01-01", end_date="2023-12-31"):
    transactions = []
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    for month in range(1, 13):
        salary_date = datetime(2023, month, 1) + timedelta(days=random.randint(0, 5))
        rent_date = datetime(2023, month, 5) + timedelta(days=random.randint(0, 3))
        loan_date = datetime(2023, month, 15) + timedelta(days=random.randint(0, 3))

        transactions.append([salary_date.strftime("%Y-%m-%d"), "Salary", round(random.uniform(3000, 7000), 2), "Deposits"])
        transactions.append([rent_date.strftime("%Y-%m-%d"), "Rent Payment", round(random.uniform(800, 2500), 2) * -1, "Fixed Expenses"])
        transactions.append([loan_date.strftime("%Y-%m-%d"), "Loan Payment", round(random.uniform(200, 800), 2) * -1, "Debt Payments"])

    for _ in range(num_transactions):
        date = start + timedelta(days=random.randint(0, (end - start).days))
        category = random.choice(list(categories.keys()))
        description = random.choice(categories[category])

        # Assign transaction amounts based on category
        if category == "Deposits":
            amount = round(random.uniform(50, 7000), 2)
        elif category == "Fixed Expenses":
            amount = round(random.uniform(50, 3000), 2) * -1
        elif category == "Variable Expenses":
            amount = round(random.uniform(10, 500), 2) * -1
        elif category == "Debt Payments":
            amount = round(random.uniform(100, 1500), 2) * -1

        transactions.append([date.strftime("%Y-%m-%d"), description, amount, category])

    anomaly_dates = [start + timedelta(days=random.randint(0, (end - start).days)) for _ in range(3)]
    for date in anomaly_dates:
        transactions.append([date.strftime("%Y-%m-%d"), "Emergency Expense", round(random.uniform(5000, 10000), 2) * -1, "Anomalies"])

    return transactions

def generate_pdf(df, filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []

    data = [["Date", "Description", "Amount", "Category"]] + df.values.tolist()

    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)
    elements.append(table)

    doc.build(elements)

for i in range(1, 11):
    df = pd.DataFrame(generate_transactions(), columns=["Date", "Description", "Amount", "Category"])
    df.sort_values("Date", inplace=True)
    csv_filename = os.path.join(output_folder, f"bank_statement_{i}.csv")
    pdf_filename = os.path.join(output_folder, f"bank_statement_{i}.pdf")
    df.to_csv(csv_filename, index=False)
    generate_pdf(df, pdf_filename)
    print(f"Generated: {csv_filename} and {pdf_filename}")

print("\n10 synthetic bank statements saved in 'synthetic_statements' folder!")
