import pandas as pd

# Read the orders CSV file
# df = pd.read_csv('data/orders.csv')
df = pd.read_csv('data/listings.csv')


# Calculate total amount spent by each customer
# total_spent = (
#     df.groupby('customer_id')['amount']
#       .sum()
#       .reset_index(name='total_amount_spent')
# )
print("First 5 rows from listings.csv:\n")
print("Filter datasset to neighborhood equal to Albany Park")
albany_park_df = df[df['neighbourhood'] == 'Albany Park']
print(albany_park_df.head(5))
print(f"\nNumber of rows: {albany_park_df.shape[0]}")
# print(df.head(5))
print("Average price by neighborhood:")
average_price_by_neighborhood = df.groupby('neighbourhood')['price'].mean()
# average_price_by_neighborhood = albany_park_df['price'].mean()
print(average_price_by_neighborhood)
print("Sort the average price by neighborhood in descending order:")
sorted_average_price = average_price_by_neighborhood.sort_values(ascending=False)
print(sorted_average_price)
# Save the average price by neighborhood to a new CSV file
output_path = 'data/average_price_by_neighborhood.csv'
sorted_average_price.to_csv(output_path, index=True)
print(f"\nSaved average price by neighborhood to: {output_path}")