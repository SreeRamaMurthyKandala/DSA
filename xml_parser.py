import os
import xml.etree.ElementTree as ET
import pandas as pd

def extract_details_from_xml(file_path):
    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()
        namespace = {"ns": "http://idnprod.ipc.us.aexp.com/schema/engine-node-1.0"}  # Define namespace

        # Initialize variables
        extracted_file_path = ""
        extracted_file_name = ""
        extracted_table_name = ""

        # Extract file path from the first <property name="&lt;cmd&gt;">
        cmd_property = root.find(".//ns:property[@name='&lt;cmd&gt;']", namespace)
        if cmd_property is not None:
            extracted_file_path = cmd_property.text.strip()
            extracted_file_name = os.path.basename(extracted_file_path.split()[0])  # Extract file name

        # Extract table name from CMDL_TABLE_NAME or MKT_TABLE_NAME
        table_property = root.find(".//ns:property[@name='CMDL_TABLE_NAME']", namespace)
        if table_property is None:
            table_property = root.find(".//ns:property[@name='MKT_TABLE_NAME']", namespace)
        
        if table_property is not None:
            extracted_table_name = table_property.text.strip()

        return extracted_file_path, extracted_file_name, extracted_table_name

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None, None, None


def process_xml_files_in_directory(directory_path, output_excel):
    # List to store extracted details
    data = []

    # Iterate over all files in the directory
    for file_name in os.listdir(directory_path):
        if file_name.endswith(".xml"):
            file_path = os.path.join(directory_path, file_name)
            extracted_file_path, extracted_file_name, extracted_table_name = extract_details_from_xml(file_path)
            
            if extracted_file_path and extracted_file_name and extracted_table_name:
                data.append({
                    "XML File Name": file_name,
                    "Extracted File Path": extracted_file_path,
                    "Extracted File Name": extracted_file_name,
                    "Extracted Table Name": extracted_table_name,
                })

    # Create a DataFrame and save to Excel
    if data:
        df = pd.DataFrame(data)
        df.to_excel(output_excel, index=False)
        print(f"Data successfully written to {output_excel}")
    else:
        print("No data extracted.")


# Directory path containing XML files and output Excel file path
directory_path = "/path/to/xml/files"  # Replace with your directory path
output_excel = "extracted_details.xlsx"  # Output Excel file name

# Process XML files and generate the Excel
process_xml_files_in_directory(directory_path, output_excel)
