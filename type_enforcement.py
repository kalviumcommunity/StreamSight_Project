import pandas as pd


def enforce_types(df):

    print("\n===== TYPE ENFORCEMENT =====")

    # -----------------------------
    # 1. Date: String → Datetime
    # -----------------------------

    print("Converting transaction_date...")

    try:

        df["transaction_date"] = pd.to_datetime(
            df["transaction_date"],
            format="%Y-%m-%d"
        )

        print("✓ transaction_date converted to datetime")

    except ValueError as error:

        print(
            f"✗ Date conversion failed: {error}"
        )

        raise


    # -----------------------------
    # 2. Currency: String → Float
    # -----------------------------

    print("Converting amount...")

    try:

        df["amount"] = (
            df["amount"]
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
        )

        df["amount"] = pd.to_numeric(
            df["amount"],
            errors="raise"
        )

        print("✓ amount converted to float")

    except (ValueError, TypeError) as error:

        print(
            f"✗ Amount conversion failed: {error}"
        )

        raise


    # -----------------------------
    # 3. Integer → Boolean
    # -----------------------------

    print("Converting is_active...")

    try:

        df["is_active"] = df["is_active"].map({
            0: False,
            1: True
        })
        if df["is_active"].isna().any():
         raise ValueError("is_active contains values other than 0 or 1")


        print("✓ is_active converted to boolean")

    except Exception as error:

        print(
            f"✗ Boolean conversion failed: {error}"
        )

        raise


    return df


def show_type_report(df):

    print("\n===== TYPE REPORT =====")

    print(df.dtypes)

    print("\nSample data:")

    print(df.head())


if __name__ == "__main__":

    # Load raw engagement data
    df = pd.read_csv(
        "data/engagement_data.csv"
    )

    print("Original data types:")

    print(df.dtypes)


    # Enforce correct types
    df = enforce_types(df)


    # Display final result
    show_type_report(df)