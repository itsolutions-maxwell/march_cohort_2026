from pathlib import Path
import pandas as pd # used for data manipulation and analysis, especially for working with tabular data like CSV files


def display_first_five_rows():
    csv_path = Path(__file__).parent / "data" / "listings.csv"
    df = pd.read_csv(csv_path) # Extract the data from the csv file and store it in a dataframe
    def get_no_of_bed(room_type):
        if room_type == "Private room":
            return 1
        elif room_type == "Entire home/apt":
            return 2
        else:
            return 0

    df["no_of_bed"] = df["room_type"].apply(get_no_of_bed)

    print("First 5 rows from listings.csv:\n")
    print(df.head(5))
    rows, columns = df.shape
    print(f"\nNumber of rows: {rows}")
    print(f"Number of columns: {columns}")

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    avg_price_by_bed = df[df["no_of_bed"].isin([1, 2])].groupby("no_of_bed")["price"].mean()
    #print(avg_price_by_bed.head())  # Display the average price by no_of_bed
    avg_price_1_bed = avg_price_by_bed.get(1, 0)
    avg_price_2_bed = avg_price_by_bed.get(2, 0)

    print("\nAverage price by no_of_bed:")
    print(f"1 bed: {avg_price_1_bed:.2f}")
    print(f"2 bed: {avg_price_2_bed:.2f}")

    report_df = pd.DataFrame(
        {
            "no_of_bed": [1, 2],
            "avg_price": [avg_price_1_bed, avg_price_2_bed],
        }
    )
    output_path = Path(__file__).parent / "avg_price_report.csv"
    report_df.to_csv(output_path, index=False)
    print(f"\nSaved report to: {output_path}")


if __name__ == "__main__":
    display_first_five_rows()
