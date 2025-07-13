import pandas as pd

# load data

df = pd.read_csv("/Users/mariapogorelova/WebstormProjects/finance_tracker/data/raw/Export20250712190202.csv",
                 skiprows=6)
print(df.head())


def filtering(data):
    filtered = data[((data["Amount"] < 0) & ~data["Payee"].str.contains("MB TRANSFER", case=False, na=False)) | ~data["Payee"].str.contains("MB TRANSFER", case=False, na=False) & (data["Amount"] > 0) & (data["Payee"] != "D/C FROM 0")]
    return filtered


BUSINESS_CATEGORIES = {
    "Taxi":                         ["uber* trip"],
    "Public transport":            ["snapper"],
    "Food delivery (uber eats)":   ["uber* eat"],
    "Food delivery":               ["hell pizza"],
    "Food delivery (groceries)":   ["milkrunfavona"],
    "Internet":                    ["net speed data ltd"],
    "Hotels":                      ["bkg*hotel"],
    "Eating out":                  ["tj katsu", "picnic cafe", "maki mono", "angry ramen", "subway", "mcdonalds", "1154", "midnight", "le bouillonbel", "st pierres"],
    "Airplane tickets":            ["air new zealand", "air nZ "],
    "Rent":                        ["tinakori rd", "pmt to fc06-0606-0100241-00"],
    "Groceries":                   ["new world", "woolworths", "fresh choice",
                                    "four square", "night'n'day", "moore wilsons", "pak n save", "shelly bay baker"],
    "Stationery":                  ["whitcoulls", "unity books", "campus bookslimited wellington"],
    "Mobile":                      ["spark pay monthly"],
    "Power":                       ["sustainabilitytr"],
    "Subscriptions":               ["grammarly", "openai", "spotify"],
    "Beauty":                      ["waxnlaser", "the body shop", "colleen"],
    "Home & Hygiene":              ["chemist warehouse", "the warehouse", "3 dollar japan", "bunnings", "bbb"],
    "Vending":                     ["coca-cola", "push developments"],
    "Coffee":                      ["the lab"],
    "Breakfast out":               ["crazy rabbitcafe wellington", "hataitai hotbread s wellington"],
    "Photography":                 ["splendid photo"],
    "Pharmacy":                    ["unichem", "after hourspharmacy"],
    "Sport":                       ["vuw recreation"],
    "Shopping":                    ["lululemon", "mecca", "kathmandu", "macpac", "pagani", "area 51", "platypus", "levi", "peter alexander", "the fittingroom", "max fashion", "cotton on"],
}

def categorise(desc):
    desc = str(desc).lower()
    for category, patterns in BUSINESS_CATEGORIES.items():
        if any(pat in desc for pat in patterns):
            return category
    return "Other"


filtered_data = filtering(df).copy()
filtered_data["Category"] = filtered_data["Payee"].apply(categorise)
filtered_data.to_csv("/Users/mariapogorelova/WebstormProjects/finance_tracker/data/processed/transactions_cleaned.csv", index=False)