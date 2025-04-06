import pandas as pd
import argparse

def parse_spending_csv(csv_path: str):
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    df["Category"] = df["Category"].fillna("Uncategorized").astype(str).str.strip()

    # Filter out refunds or income
    df = df[df["Amount"] > 0]

    # Exclude non-spending categories
    exclude_categories = ["Transfers", "Credit Card Payment"]
    df = df[~df["Category"].isin(exclude_categories)]

    print("\n🔍 Categorizing spending...\n")

    # Group and print each matched transaction
    for _, row in df.iterrows():
        print(f"✅ Matched '{row['Name']}' → {row['Category']} (+${row['Amount']:.2f})")

    # Summarize totals by category
    summary = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)

    print("\n📊 Spending Summary:")
    for category, total in summary.items():
        print(f"{category:25}: ${total:,.2f}")

    return summary.to_dict()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse and summarize variable spending from Rocket Money CSV.")
    parser.add_argument("csv_file", help="Path to spending CSV")
    args = parser.parse_args()

    parse_spending_csv(args.csv_file)
