import os
import json
from datetime import datetime
import pandas as pd
import chardet


# 1. Check file exists

def validate_file_exists(filepath):

    if not os.path.exists(filepath):
        return False, f"File not found: {filepath}"

    if os.path.getsize(filepath) == 0:
        return False, "File is empty"

    return True, "File exists and contains data"



# 2. Check file format

def validate_file_format(filepath):

    allowed = ["csv", "json"]

    extension = filepath.split(".")[-1].lower()

    if extension not in allowed:
        return False, f"Unsupported format: {extension}"

    return True, f"Format valid: {extension}"



# 3. Check schema

def validate_schema(df, expected_columns):

    missing = set(expected_columns) - set(df.columns)

    extra = set(df.columns) - set(expected_columns)


    if missing or extra:

        message = []

        if missing:
            message.append(
                f"Missing columns: {missing}"
            )

        if extra:
            message.append(
                f"Extra columns: {extra}"
            )

        return False, " | ".join(message)


    return True, "Schema valid"



# 4. Detect encoding

def detect_encoding(filepath):

    with open(filepath,"rb") as file:

        result = chardet.detect(
            file.read(10000)
        )


    encoding = result["encoding"]
    confidence = result["confidence"]


    return (
        True,
        f"Detected encoding: {encoding} ({confidence:.0%})"
    )



# 5. Capture statistics

def capture_stats(filepath, df):

    return {

        "rows": len(df),

        "columns": len(df.columns),

        "file_size_MB":
        round(
            os.path.getsize(filepath)/(1024*1024),
            2
        )
    }



# Generate complete report

def generate_report(filepath):

    expected_columns = [

        "user_id",
        "video_id",
        "watch_duration",
        "pause_count",
        "completion_rate",
        "timestamp"

    ]


    report = {

        "time":
        datetime.now().isoformat(),

        "file":
        filepath,

        "checks": {}

    }


    # File check

    status,msg = validate_file_exists(filepath)

    report["checks"]["file"] = msg


    if not status:
        return report



    # Format check

    status,msg = validate_file_format(filepath)

    report["checks"]["format"] = msg


    if not status:
        return report



    # Load data

    df = pd.read_csv(filepath)



    # Schema check

    status,msg = validate_schema(
        df,
        expected_columns
    )


    report["checks"]["schema"] = msg



    # Encoding

    status,msg = detect_encoding(filepath)

    report["checks"]["encoding"] = msg



    # Statistics

    report["statistics"] = capture_stats(
        filepath,
        df
    )


    return report




if __name__ == "__main__":


    result = generate_report(
        "../data/engagement_data.csv"
    )


    with open(
        "report.json",
        "w"
    ) as file:

        json.dump(
            result,
            file,
            indent=4
        )


    print("Validation completed")