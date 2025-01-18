import streamlit as st
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
import os
from calendar import month_name

# Load environment variables
load_dotenv()

st.title("Yearly Expense Visualization App")

# Introduction to the app
st.header("Welcome to the Yearly Expense Visualization App!")
st.markdown("""
This app helps you analyze and visualize your yearly spending, providing insights into your expenses across various categories, people, and payment modes.

### Features:
- Get an overview of your total expenses for the year.
- Visualize your spending across categories, months, or individuals.
- Track trends, identify the highest spenders, and gain insights into your spending patterns.
- Query custom SQL to fetch specific data from your database.

Use the buttons below to explore the available queries and visualize your data.
""")

# All 20 queries
queries = {
    "1. Total expenses of the year-2024": """
        SELECT SUM(Amount) AS Total_Expenses 
        FROM yearly_expenses;
    """,
    "2. Monthly Total Expenses": """
        SELECT MONTH(Date) AS Month, SUM(Amount) AS Amount 
        FROM yearly_expenses 
        GROUP BY MONTH(Date) 
        ORDER BY Month;
    """,
    "3. Total Expenses Grouped by Category for 2024": """
        SELECT Category, SUM(Amount) AS Amount 
        FROM yearly_expenses 
        GROUP BY Category 
        ORDER BY Amount DESC;
    """,
    "4. Total Expenses Grouped by Payment Mode": """
        SELECT Payment_Mode, SUM(Amount) AS Amount 
        FROM yearly_expenses 
        GROUP BY Payment_Mode 
        ORDER BY Amount DESC;
    """,
    "5. Average Spending per Category": """
        SELECT Category, AVG(Amount) AS Amount 
        FROM yearly_expenses 
        GROUP BY Category 
        ORDER BY Amount DESC;
    """,
    "6. Total expenses per person": """
        SELECT Name, SUM(Amount) AS Amount 
        FROM yearly_expenses 
        GROUP BY Name 
        ORDER BY Amount DESC;
    """,
    "7. Average expense amount by category": """
        SELECT Category, AVG(Amount) AS Amount 
        FROM yearly_expenses 
        GROUP BY Category 
        ORDER BY Amount DESC;
    """,
    "8. Days with the highest total spending": """
        SELECT Date, SUM(Amount) AS Amount 
        FROM yearly_expenses 
        GROUP BY Date 
        ORDER BY Amount DESC 
        LIMIT 5;
    """,
    "11. Total spending on Groceries": """
        SELECT SUM(Amount) AS Grocery
        FROM yearly_expenses 
        WHERE Category = 'Groceries';
    """,
    "12. Total expenses by Balu and Cynthia": """
        SELECT SUM(Amount) AS Total_Expense
        FROM yearly_expenses
        WHERE Name IN ('Balu', 'Cynthia');
    """,
    "13. Most frequently used payment mode": """
        SELECT Payment_Mode, COUNT(*) AS Frequency 
        FROM yearly_expenses 
        GROUP BY Payment_Mode 
        ORDER BY Frequency DESC 
        LIMIT 1;
    """,
    "14. Total spending by description": """
        SELECT Description, SUM(Amount) AS Amount 
        FROM yearly_expenses 
        GROUP BY Description 
        ORDER BY Amount DESC;
    """,
    "15. Category-Wise Expenses per Person": """
        SELECT Name, Category, SUM(Amount) AS Total_Amount 
        FROM yearly_expenses 
        GROUP BY Name, Category 
        ORDER BY Name, Total_Amount DESC;
    """,
    "16. Daily Average spending": """
        SELECT AVG(Amount) AS Amount
        FROM (
            SELECT DATE(Date) AS Day, SUM(Amount) AS Amount
            FROM yearly_expenses
            GROUP BY DATE(Date)
        ) AS SubQuery;
    """,
    "17. Total spending per person": """
        SELECT Name, SUM(Amount) AS Amount
        FROM yearly_expenses
        GROUP BY Name
        ORDER BY Amount DESC;
    """,
    "18. Person with the highest spending": """
        SELECT Name, SUM(Amount) AS Amount
        FROM yearly_expenses
        GROUP BY Name
        ORDER BY Amount DESC
        LIMIT 1;
    """,
    "19. Person with the lowest spending": """
        SELECT Name, SUM(Amount) AS Amount
        FROM yearly_expenses
        GROUP BY Name
        ORDER BY Amount ASC
        LIMIT 1;
    """,
    "20. Category-wise highest spender": """
        SELECT 
            e1.Category, 
            e1.Name, 
            SUM(e1.Amount) AS Amount
        FROM yearly_expenses e1
        JOIN (
            SELECT Category, MAX(SUM_Amount) AS Max_Spending
            FROM (
                SELECT Category, Name, SUM(Amount) AS SUM_Amount
                FROM yearly_expenses
                GROUP BY Category, Name
            ) AS SubQuery
            GROUP BY Category
        ) e2
        ON e1.Category = e2.Category AND e1.Name = (
            SELECT Name 
            FROM yearly_expenses
            WHERE Category = e2.Category
            GROUP BY Name
            HAVING SUM(Amount) = e2.Max_Spending
        )
        GROUP BY e1.Category, e1.Name;
    """
}

# Sidebar: Query selection
st.sidebar.header("Query Options")
query_names = list(queries.keys()) + ["Custom Query"]
selected_query = st.sidebar.radio("Choose a Query", query_names)

if selected_query == "Custom Query":
    query = st.sidebar.text_area("Enter your SQL query:")
else:
    query = queries[selected_query]

# Database connection
def get_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "Manoj@1146"),
            database=os.getenv("DB_NAME", "sqlpython1"),
        )
        return connection
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# Fetch data
def fetch_data(query):
    try:
        connection = get_connection()
        if connection is None:
            return None
        df = pd.read_sql_query(query, connection)
        connection.close()
        return df
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None

# Main logic
if query:
    data = fetch_data(query)
    if data is not None and not data.empty:
        st.subheader("Query Results")

        # Add ₹ symbol to Amount columns
        if "Amount" in data.columns:
            data["Amount"] = data["Amount"].apply(lambda x: f"₹{x:,.2f}")
        if "Total_Amount" in data.columns:
            data["Total_Amount"] = data["Total_Amount"].apply(lambda x: f"₹{x:,.2f}")
        if "Total_Expenses" in data.columns:
            data["Total_Expenses"] = data["Total_Expenses"].apply(lambda x: f"₹{x:,.2f}")
        st.write(data)

        # Visualization logic
        if "Month" in data.columns:
            data["Month"] = data["Month"].apply(lambda x: month_name[x])
            fig, ax = plt.subplots()
            sns.barplot(x="Month", y="Amount", data=data, ax=ax, palette="viridis")
            ax.set_title("Monthly Spending")
            ax.set_xlabel("Month")
            ax.set_ylabel("Spending (₹)")
            st.pyplot(fig)
        elif "Category" in data.columns:
            fig, ax = plt.subplots()
            sns.barplot(x="Amount", y="Category", data=data, ax=ax, palette="Blues_r")
            ax.set_title("Spending by Category")
            ax.set_xlabel("Spending (₹)")
            ax.set_ylabel("Category")
            st.pyplot(fig)
        elif "Name" in data.columns:
            fig, ax = plt.subplots()
            sns.barplot(x="Amount", y="Name", data=data, ax=ax, palette="Greens_r")
            ax.set_title("Spending Per Person")
            ax.set_xlabel("Spending (₹)")
            ax.set_ylabel("Name")
            st.pyplot(fig)
        else:
            st.info("No predefined visualization available for this query.")
    else:
        st.warning("No data returned by the query. Please check your query or database.")
