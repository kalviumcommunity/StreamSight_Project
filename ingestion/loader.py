import pandas as pd

import pandas as pd

excel_file = "../data/engagement.xlsx"

excel = pd.ExcelFile(excel_file)

print("Available Excel sheets:")
print(excel.sheet_names)

# CSV Loader

def ingest_csv(filepath, delimiter=",", encoding="utf-8"):

    try:

        df = pd.read_csv(
            filepath,
            delimiter=delimiter,
            encoding=encoding
        )

        print("CSV loaded successfully")

        return df


    except UnicodeDecodeError:

        print(
            f"Encoding error. Try latin-1 or cp1252"
        )

        raise




# JSON Loader

def ingest_json(filepath, nested=False):

    import json

    # Read JSON file directly
    with open(filepath, "r") as file:
        data = json.load(file)


    if nested:

        df = pd.json_normalize(data)

        print("Nested JSON flattened")

    else:

        df = pd.DataFrame(data)


    return df




# Excel Loader

def ingest_excel(filepath, sheet_name):

    df = pd.read_excel(
        filepath,
        sheet_name=sheet_name
    )

    print(
        "Excel loaded successfully"
    )


    return df




# Ingestion Report

def document_ingestion(df, source):

    print("\n-----------")
    print("INGESTION REPORT")
    print("-----------")

    print(
        "Source:",
        source
    )


    print(
        "Rows:",
        df.shape[0]
    )


    print(
        "Columns:",
        df.shape[1]
    )


    print("\nColumn Types")

    print(
        df.dtypes
    )


    print("\nSample Data")

    print(
        df.head(3)
    )





# Testing

if __name__ == "__main__":


    csv_df = ingest_csv(
        "../data/engagement_data.csv",
        delimiter=",",
        encoding="utf-8"
    )


    document_ingestion(
        csv_df,
        "engagement_data.csv"
    )



    json_df = ingest_json(
        "../data/engagement.json",
        nested=True
    )


    document_ingestion(
        json_df,
        "engagement.json"
    )



    excel_df = ingest_excel(
        "../data/engagement.xlsx",
        sheet_name="Engagement_Data"
    )


    document_ingestion(
        excel_df,
        "engagement.xlsx"
    )