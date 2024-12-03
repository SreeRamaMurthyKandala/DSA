import os
import xml.etree.ElementTree as ET
import pandas as pd

def extract_details_from_xml(file_path):
    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Initialize variables
        extracted_file_path = ""
        extracted_file_name = ""
        extracted_table_name = ""

        # Find the first property tag with the cmd pattern and extract the file path
        for prop in root.iter("property"):
            if "cmd" in prop.attrib.get("name", ""):  # Look for cmd in the property name
                extracted_file_path = prop.text.strip()
                if extracted_file_path:
                    extracted_file_name = os.path.basename(extracted_file_path.split()[0])  # Extract file name
                break

        # Find the property for table names (CMDL_TABLE_NAME or MKT_TABLE_NAME)
        for prop in root.iter("property"):
            if prop.attrib.get("name") in ["CMDL_TABLE_NAME", "MKT_TABLE_NAME"]:
                extracted_table_name = prop.text.strip()
                break

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
