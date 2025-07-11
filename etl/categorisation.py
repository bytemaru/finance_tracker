import pandas as pd

# load data

df = pd.read_csv("/Users/mariapogorelova/WebstormProjects/finance_tracker/data/raw/Export20250628115905.csv",
                 skiprows=5)
print(df.head())


def filtering(data):
    filtered = data[((data["Amount"] < 0) & ~data["Payee"].str.contains("MB TRANSFER", case=False, na=False)) | ~data["Payee"].str.contains("MB TRANSFER", case=False, na=False) & (data["Amount"] > 0) & (data["Payee"] != "D/C FROM 0")]
    return filtered


# data enrichment
def categorise(desc):
    if "UBER* TRIPUBER.COM" in desc:
        return "Taxi"
    elif "UBER* EATSUBER.COM" in desc:
        return "Food delivery (uber eats)"
    elif "HELL PIZZA" in desc:
        return "Food delivery"
    elif "Net Speed Data Ltd" in desc:
        return "Internet"
    elif "MILKRUNFavona" in desc:
        return "Food delivery (groceries)"
    elif "Tinakori Rd" in desc:
        return "Rent"
    elif "NEW WORLD" in desc:
        return "Groceries"
    elif "WOOLWORTHS" in desc:
        return "Groceries"
    elif "FRESH CHOICE" in desc:
        return "Groceries"
    elif "WHITCOULLS" in desc:
        return "Stationery"
    elif "UNITY BOOKSWELLINGTON" in desc:
        return "Stationery"
    elif "Campus BooksLimited Wellington" in desc:
        return "Stationery"
    elif "SPARK PAY MONTHLY" in desc:
        return "Mobile"
    elif "GRAMMARLY" in desc:
        return "Subscriptions"
    elif "OPENAI *CHATGPT SUBSCR" in desc:
        return "Subscriptions"
    elif "WAXNLASERLOWER HUTT" in desc:
        return "Beauty"
    elif "CHEMIST WAREHOUSE" in desc:
        return "Home & Hygiene"
    elif "COCA-COLA" in desc:
        return "Vending"
    elif "PUSH DEVELOPMENTS LOWER HUTT" in desc:
        return "Vending"
    elif "THE LAB" in desc:
        return "Coffee"
    elif "Crazy RabbitCafe Wellington" in desc:
        return "Breakfast out"
    elif "Hataitai HotBread S Wellington" in desc:
        return "Breakfast out"
    elif "SPLENDID PHOTO WELLINGTON" in desc:
        return "Photography"
    return "Other"


filtered_data = filtering(df).copy()
filtered_data["Category"] = filtered_data["Payee"].apply(categorise)
filtered_data.to_csv("/Users/mariapogorelova/WebstormProjects/finance_tracker/data/processed/transactions_cleaned.csv", index=False)