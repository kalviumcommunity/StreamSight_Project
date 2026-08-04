import pandas as pd


def clean_text_column(
        series,
        lowercase=True,
        strip=True,
        remove_special=False,
        mapping=None
):

    result = series.copy()


    # Remove spaces
    if strip:
        result = result.str.strip()


    # Convert to lowercase
    if lowercase:
        result = result.str.lower()


    # Remove special characters
    if remove_special:
        result = result.str.replace(
            '[^a-zA-Z0-9 ]',
            '',
            regex=True
        )


    # Standardize values
    if mapping:
        result = result.map(mapping)


    return result

category_map = {

    "movies": "Movies",

    "series": "Series"

}



segment_map = {

    "b2b": "B2B",

    "b 2 b": "B2B",

    "business-to-business": "B2B"

}

if __name__ == "__main__":


    df = pd.read_csv(
        "data/engagement_data.csv"
    )


    print("Before Cleaning")
    print(df[
        [
            "viewer_name",
            "category",
            "segment",
            "city"
        ]
    ])



    # Clean names

    df["viewer_name"] = clean_text_column(
        df["viewer_name"]
    )



    # Clean category

    df["category"] = clean_text_column(
        df["category"],
        mapping=category_map
    )



    # Clean segment

    df["segment"] = clean_text_column(
        df["segment"],
        mapping=segment_map
    )



    # Clean city

    df["city"] = clean_text_column(
        df["city"],
        remove_special=True
    )



    print("\nAfter Cleaning")

    print(df[
        [
            "viewer_name",
            "category",
            "segment",
            "city"
        ]
    ])