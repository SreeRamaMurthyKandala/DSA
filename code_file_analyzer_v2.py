import os
import re
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment
import ast
import pandas as pd

# Function to extract cron expression from the code
def extract_cron_expression(code):
    cron_pattern = r'(\d{1,2} \d{1,2} \d{1,2} \d{1,2} \d{1,2} \S+)'
    cron_expression = re.findall(cron_pattern, code)
    return cron_expression[0] if cron_expression else "N/A"

# Function to extract SQL queries from the code
def extract_sql_queries(code):
    sql_pattern = r'(SELECT.*?;|INSERT INTO.*?;|UPDATE.*?;|DELETE FROM.*?;)'
    sql_queries = re.findall(sql_pattern, code, re.DOTALL)
    return sql_queries

# Function to extract table names (input/output) from SQL queries
def extract_table_names(sql_queries):
    table_names = []
    for query in sql_queries:
        # Extract table names from common SQL commands
        tables = re.findall(r'FROM (\w+)|INTO (\w+)|JOIN (\w+)', query)
        for table in tables:
            table_names.extend([t for t in table if t])
    return table_names

# Function to extract the character length of SQL queries
def extract_query_length(sql_queries):
    return sum(len(query) for query in sql_queries)

# Function to extract dependencies (import statements and external functions)
def extract_dependencies(code):
    imports = re.findall(r'^\s*(import|from)\s+([a-zA-Z0-9_]+)', code, re.MULTILINE)
    functions = re.findall(r'^\s*def\s+([a-zA-Z0-9_]+)\s*\(', code, re.MULTILINE)
    return {
        "imports": [imp[1] for imp in imports],
        "functions": functions
    }

# Function to categorize code complexity based on extracted info
def categorize_complexity(cron_expression, sql_queries, dependencies):
    # Heuristic based on extracted info (you can adjust this logic as per your requirement)
    complexity = "Low"
    if cron_expression != "N/A":
        complexity = "Medium"
    if len(sql_queries) > 3:
        complexity = "High"
    if len(dependencies["imports"]) > 5 or len(dependencies["functions"]) > 5:
        complexity = "Very High"
    return complexity

# Function to extract all necessary information from a Python file
def extract_code_info(file_path):
    with open(file_path, 'r') as file:
        code = file.read()

    # Extract necessary information
    cron_expression = extract_cron_expression(code)
    sql_queries = extract_sql_queries(code)
    table_names = extract_table_names(sql_queries)
    query_length = extract_query_length(sql_queries)
    dependencies = extract_dependencies(code)
    complexity = categorize_complexity(cron_expression, sql_queries, dependencies)

    # Extract additional information
    function_calls = extract_function_calls(code)
    docstrings = extract_docstrings(code)
    loops = extract_loops(code)
    conditions = extract_conditions(code)
    lines_of_code = len(code.splitlines())
    class_count = len(re.findall(r'class\s+[A-Za-z_][A-Za-z0-9_]*', code))
    function_count = len(re.findall(r'^\s*def\s+', code))
    query_count = len(sql_queries)

    # Assuming you have placeholders for purpose, triggers, sources, and sinks
    purpose = "Unknown"
    triggers = "Unknown"
    sources = "Unknown"
    sinks = "Unknown"

    return {
        "file_name": os.path.basename(file_path),
        "type": "Python",  # Set based on file type
        "lines_of_code": lines_of_code,
        "class_count": class_count,
        "function_count": function_count,
        "query_count": query_count,
        "purpose": purpose,
        "dependencies": dependencies,
        "triggers": triggers,
        "sources": sources,
        "sinks": sinks,
        "imports": dependencies["imports"],
        "function_names": ", ".join(dependencies["functions"]),
        "class_names": ", ".join(re.findall(r'class\s+([A-Za-z_][A-Za-z0-9_]*)', code)),
        "cron_expression": cron_expression,
        "sql_queries": sql_queries,
        "table_names": table_names,
        "query_length": query_length,
        "complexity": complexity
    }

# Function to write the extracted data to an Excel file
def write_to_excel(data, output_filename):
    wb = Workbook()
    ws = wb.active
    ws.title = "Code Analysis"

    # Headers for the Excel file, including the new columns
    headers = [
        "file_name", "type", "lines_of_code", "class_count", "function_count", "query_count",
        "purpose", "dependencies", "triggers", "sources", "sinks", "imports", "function_names", "class_names", 
        "cron_expression", "sql_queries", "input/output_table_names", "query_length", "complexity"
    ]
    ws.append(headers)

    # Write data to Excel
    for item in data:
        ws.append([
            item["file_name"],
            item["type"],
            item["lines_of_code"],
            item["class_count"],
            item["function_count"],
            item["query_count"],
            item["purpose"],
            f"Imports: {', '.join(item['dependencies']['imports'])}\nFunctions: {', '.join(item['dependencies']['functions'])}",
            item["triggers"],
            item["sources"],
            item["sinks"],
            ", ".join(item["imports"]),
            item["function_names"],
            item["class_names"],
            item["cron_expression"],
            "\n".join(item["sql_queries"]),
            ", ".join(item["table_names"]),
            item["query_length"],
            item["complexity"]
        ])

    # Apply styles and formatting
    for col in range(1, len(headers) + 1):
        column = chr(64 + col)  # Convert to column letter (e.g., A, B, C, ...)
        ws.column_dimensions[column].auto_size = True

    # Bold headers
    for cell in ws[1]:
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.font = openpyxl.styles.Font(bold=True)

    # Save the workbook
    wb.save(output_filename)

# Function to extract function calls from the code
def extract_function_calls(code):
    # Find all function calls (e.g., foo(), bar())
    return re.findall(r'(\w+)\s*\(', code)

# Function to extract docstrings from the code
def extract_docstrings(code):
    # Extract all docstrings in the code (both single and multi-line)
    return re.findall(r'"""(.*?)"""', code, re.DOTALL)

# Function to extract loops from the code
def extract_loops(code):
    # Extract loop structures (for and while loops)
    return re.findall(r'(for|while)\s+\w+', code)

# Function to extract conditions (if statements)
def extract_conditions(code):
    # Extract if condition statements
    return re.findall(r'if\s+.*:', code)

# Main function to analyze files in a directory
def analyze_directory(directory, output_filename):
    data = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):  # You can add more file types if needed
                file_path = os.path.join(root, file)
                code_info = extract_code_info(file_path)
                data.append(code_info)

    write_to_excel(data, output_filename)

# Example Usage
directory_to_analyze = r"C:\Users\sree.rama.m.kandala\Downloads\code_file_analyzer\test"
output_excel_file = "code_analysis_output.xlsx"
analyze_directory(directory_to_analyze, output_excel_file)
