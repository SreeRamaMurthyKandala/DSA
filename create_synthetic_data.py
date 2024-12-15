import os
from datetime import datetime
import random

# Function to create directories and files
def create_directory_structure():
    base_dir = "repo"
    sub_dir = os.path.join(base_dir, "jethro-metadata")

    # Create base directories
    os.makedirs(sub_dir, exist_ok=True)
    
    # Create e1, e2, e3 directories
    for subfolder in ["e1", "e2", "e3"]:
        os.makedirs(os.path.join(sub_dir, subfolder), exist_ok=True)

    # Create 10 subfolders in e3
    e3_dir = os.path.join(sub_dir, "e3")
    usecases = [f"usecase_{i+1}" for i in range(10)]
    
    for usecase in usecases:
        usecase_dir = os.path.join(e3_dir, usecase)
        os.makedirs(usecase_dir, exist_ok=True)

        # Create two text files in each usecase folder
        create_usecase_files(usecase_dir)

import random
import os
from datetime import datetime

def create_usecase_files(directory):
    date_str = datetime.now().strftime("%Y%m%d")
    table_count = random.randint(3, 10)  # Random number of tables (1 to 5)
    table_names = [f"table_{random.randint(1, 100)}" for _ in range(table_count)]
    schema_name = f"schema_{random.randint(1, 300)}"  # Dynamic schema name

    # Generate synthetic content for tables.ddl file
    ddl_statements = []
    for table_name in table_names:
        col_count = random.randint(2, 5)  # Random number of columns per table
        cols = []
        for i in range(col_count):
            col_type = random.choice(["STRING", "INT", "FLOAT", "BOOLEAN", "TIMESTAMP", "DATE", "CHAR", "VARCHAR(255)"])
            cols.append(f"col_{random.randint(1, 100)} {col_type}")
        ddl_statements.append(f"use {schema_name};\nCREATE TABLE {table_name} ({', '.join(cols)});\n;")
    
    ddl_content = "\n".join(ddl_statements)

    ddl_filename = f"tables.ddl_{date_str}.txt"
    with open(os.path.join(directory, ddl_filename), "w") as ddl_file:
        ddl_file.write(ddl_content)

    # Generate synthetic content for tables_metadata_info file
    metadata_content = (
        "ID | Schema Name | Table Name    | Column Name | Rows   | Partitions| Columns-MB  | Indexes-MB  | Keys-MB  | Guki-MB  | Table Type \n"
    )
    metadata_content += "-------------------------------------------------------------------------------------------------------------------------------------\n"
    row_count = random.randint(2, 6)  # Random number of metadata rows (2 to 6)
    for i in range(row_count):
        table_name = table_names[random.randint(0, table_count - 1)]
        metadata_content += (
            f"{i + 1:<3}| {schema_name:<13}| {table_name:<13}| col_{random.randint(1, 100):<11}| "
            f"{random.randint(1000, 100000):<7}| {random.randint(1, 50):<10}| {random.uniform(0.1, 10.0):<11.2f}| "
            f"{random.uniform(0.01, 1.0):<11.2f}| {random.uniform(0.01, 1.0):<8.2f}| {random.uniform(0.01, 1.0):<8.2f}| Managed  \n"
        )

    metadata_content += "-------------------------------------------------------------------------------------------------------------------------------------\n"
    metadata_content += "Total query time: " + str(random.randint(1, 500)) + "\n\n"
    metadata_content += "Row count: " + str(row_count)

    metadata_filename = "tables_metadata_info.txt"
    with open(os.path.join(directory, metadata_filename), "w") as metadata_file:
        metadata_file.write(metadata_content)



# Execute the function
if __name__ == "__main__":
    create_directory_structure()
    print("Directory structure and files created successfully!")