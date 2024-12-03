import xmltodict
import os
import pandas as pd
from pprint import pprint

def extract_details_from_dict(xml_dict):
    extracted_file_path = ""
    extracted_file_name = ""
    extracted_table_name = ""

    # Navigate the dictionary to extract details
    engine_node = xml_dict.get("EngineNodeSet", {}).get("EngineNode", {})
    if not engine_node:
        return None, None, None

    # Extract the file path from the first property with "cmd"
    properties = engine_node.get("properties", {}).get("property", [])
    if not isinstance(properties, list):
        properties = [properties]  # Ensure it's a list for uniform processing

    for prop in properties:
        if "cmd" in prop.get("@name", ""):
            extracted_file_path = prop.get("#text", "").strip()
            if extracted_file_path:
                extracted_file_name = os.path.basename(extracted_file_path.split()[0])
            break

    # Extract the table name
    for prop in properties:
        if prop.get("@name") in ["CMDL_TABLE_NAME", "MKT_TABLE_NAME"]:
            extracted_table_name = prop.get("#text", "").strip()
            break

    return extracted_file_path, extracted_file_name, extracted_table_name


def process_xml_files_in_directory(directory_path, output_excel):
    data = []

    for file_name in os.listdir(directory_path):
        if file_name.endswith(".xml"):
            file_path = os.path.join(directory_path, file_name)

            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    xml_dict = xmltodict.parse(file.read())
                    extracted_file_path, extracted_file_name, extracted_table_name = extract_details_from_dict(xml_dict)

                    if extracted_file_path and extracted_file_name and extracted_table_name:
                        data.append({
                            "XML File Name": file_name,
                            "Extracted File Path": extracted_file_path,
                            "Extracted File Name": extracted_file_name,
                            "Extracted Table Name": extracted_table_name,
                        })

                except Exception as e:
                    print(f"Error processing file {file_name}: {e}")

    if data:
        df = pd.DataFrame(data)
        df.to_excel(output_excel, index=False)
        print(f"Data successfully written to {output_excel}")
    else:
        print("No data extracted.")

# Directory containing XML files
directory_path = "/path/to/xml/files"  # Replace with your XML files directory
output_excel = "extracted_details.xlsx"

process_xml_files_in_directory(directory_path, output_excel)
