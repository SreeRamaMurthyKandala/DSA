import os
import re
import pandas as pd
from openpyxl import Workbook

def extract_ddl_info(ddl_file_path):
    """
    Extract schema name, table name, query type, and query length from a DDL file.
    """
    with open(ddl_file_path, 'r') as file:
        content = file.read()

    # Extract queries with schema and table names
    queries = re.findall(r'use\s+(\w+);\nCREATE\s+TABLE\s+(\w+).*?;', content, re.DOTALL | re.IGNORECASE)

    data = []
    for schema, table_name in queries:
        # Extract the entire query for length
        query_match = re.search(r'(CREATE\s+TABLE\s+\w+.*?;)', content, re.IGNORECASE)
        if query_match:
            query = query_match.group(1)
            query_length = len(query)
            data.append({
                'schema_name': schema.lower(),       # Standardize to lowercase
                'table_name': table_name.lower(),   # Standardize to lowercase
                'type_of_query': 'CREATE',          # Since we're only handling CREATE TABLE
                'no_of_queries': 1,
                'query_length': query_length
            })

    return pd.DataFrame(data)

def extract_metadata_info(metadata_file_path):
    """
    Extract table metadata from a metadata info file.

    Args:
        metadata_file_path (str): The path to the metadata info text file.

    Returns:
        pd.DataFrame: A DataFrame containing the extracted metadata.
    """
    with open(metadata_file_path, 'r') as file:
        lines = file.readlines()

    table_data = []
    inside_table = False
    header_skipped = False

    for line in lines:
        line = line.strip()
        
        # Detect the start or end of the table by lines starting with '-'
        if line.startswith('---'):
            inside_table = not inside_table  # Toggle the state
            if inside_table:
                header_skipped = False  # Reset header flag when a new table starts
            continue  # Skip the border lines

        if inside_table:
            # Skip the header row
            if not header_skipped:
                header_skipped = True
                continue

            # Process data rows that start with a number followed by '|'
            if re.match(r'^\d+\s*\|', line):
                # Split the line by '|' and strip spaces
                columns = [col.strip() for col in line.split('|')]
                
                # Ensure the line has the expected number of columns
                if len(columns) == 11:
                    table_data.append({
                        'id': columns[0],
                        'schema_name': columns[1].lower(),   # Standardize to lowercase
                        'table_name': columns[2].lower(),    # Standardize to lowercase
                        'column_name': columns[3],
                        'rows': columns[4],
                        'partitions': columns[5],
                        'columns_mb': columns[6],
                        'indexes_mb': columns[7],
                        'keys_mb': columns[8],
                        'guki_mb': columns[9],
                        'table_type': columns[10]
                    })

    # Convert the list of dictionaries to a DataFrame
    metadata_df = pd.DataFrame(table_data)

    # Convert data types for numerical columns
    numerical_columns = ['id', 'rows', 'partitions', 'columns_mb', 'indexes_mb', 'keys_mb', 'guki_mb']
    for col in numerical_columns:
        if col in metadata_df.columns:
            metadata_df[col] = pd.to_numeric(metadata_df[col], errors='coerce')

    return metadata_df

def process_repo(repo_path, output_file):
    """
    Process the repository to parse the data and create an Excel file.
    """
    all_data = []

    for root, dirs, files in os.walk(repo_path):
        # Extract usecase_name only if the current directory is a usecase folder
        # Assuming usecase folders are named 'usecase_x'
        usecase_name = os.path.basename(root)
        if not usecase_name.startswith('usecase_'):
            continue  # Skip non-usecase folders

        ddl_file = None
        metadata_file = None

        # Identify the required files in the current directory
        for file in files:
            if file.startswith("tables.ddl_"):
                ddl_file = os.path.join(root, file)
            elif file == "tables_metadata_info.txt":
                metadata_file = os.path.join(root, file)

        # If both files are found, process them
        if ddl_file and metadata_file:
            ddl_df = extract_ddl_info(ddl_file)
            metadata_df = extract_metadata_info(metadata_file)
            
            # Debugging prints (optional)
            print(f"Processing {usecase_name}:")
            print("DDL DataFrame:")
            print(ddl_df)
            print("Metadata DataFrame:")
            print(metadata_df)
            print("-" * 50)
            
            # Merge on schema_name and table_name (case insensitive)
            if not ddl_df.empty and not metadata_df.empty:
                merged_df = pd.merge(
                    ddl_df, 
                    metadata_df, 
                    on=['schema_name', 'table_name'], 
                    how='inner',
                    suffixes=('_ddl', '_meta')
                )
                if not merged_df.empty:
                    merged_df.insert(0, 'usecase_name', usecase_name)  # Add usecase name
                    all_data.append(merged_df)

    # Combine all data and write to Excel
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_excel(output_file, index=False)
        print(f"Data successfully written to {output_file}")
    else:
        print("No data found in the repository.")

if __name__ == "__main__":
    # Replace with your actual repository path
    repo_path = r"C:\Users\satya\Downloads\schema parser\repo\jethro-metadata\e3"
    output_file = "schema_analysis.xlsx"
    process_repo(repo_path, output_file)