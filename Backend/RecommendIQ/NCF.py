import pandas as pd
import numpy as np
import re
from sklearn.metrics.pairwise import cosine_similarity

#Get the CSV files

menu_file = "./RecommendIQ/Menu.csv"
ratings_file = "./RecommendIQ/User_Data.csv"
# menu_file = "Menu.csv"
# ratings_file = "User_Data.csv"
menu_df = pd.read_csv(menu_file)
ratings_df = pd.read_csv(ratings_file)

#get prices
def extract_price(price_str):
    match = re.search(r"\d+(\.\d+)?", str(price_str))  #first non "$"
    return float(match.group()) if match else None

menu_df["Price"] = menu_df["Price"].apply(extract_price)


#get average
average_ratings = ratings_df.groupby("Item_ID")["Rating"].mean().reset_index()
average_ratings.rename(columns={"Rating": "Average_Rating"}, inplace=True)
menu_df = menu_df.merge(average_ratings, on="Item_ID", how="left")  #Mege with menu
menu_df["Average_Rating"] = menu_df["Average_Rating"].fillna(0)


#user-item matrix
user_item_matrix = ratings_df.pivot(index="User_ID", \
                                    columns="Item_ID", \
                                    values="Rating").fillna(0)

#Transpose
item_similarity = cosine_similarity(user_item_matrix.T)

#Load to df
item_similarity_df = pd.DataFrame(item_similarity, index=user_item_matrix.columns, columns=user_item_matrix.columns)

def get_recommendations(item_name, top_n=5):
    item_row = menu_df[menu_df["Item_Name"].str.lower() == item_name.lower()]
    
    
    
    if item_row.empty:
        print(f"Item '{item_name}' not found in menu.")
        return
    

    item_id = item_row.iloc[0]["Item_ID"]

    similar_items = item_similarity_df[item_id].sort_values(ascending=False)[1:top_n+1].index

    recommendations = menu_df[menu_df["Item_ID"].isin(similar_items)][["Item_Name", "Category", "Price", "Average_Rating"]]
    recommendations.sort_values(by="Average_Rating", ascending=False, inplace=True) 

    print(f"\nRecommended items similar to '{item_name}':\n")
    print(recommendations.to_string(index=False))

    return recommendations.to_dict(orient='records')



#for FTESTING PURPOSES
def main():
    while True:
        user_input = input("Enter an item name to get recommendations: ")
        if user_input.lower() == "exit":
            break
        get_recommendations(user_input)

if __name__ == "__main__":
    main()