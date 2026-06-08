LOCATIONS = {
    "Nigeria": {
        "currency": "NGN",
        "states": {
            "Kano": {
                "Kano City":     "Kano, Kano, NG",
                "Wudil":         "Wudil, Kano, NG",
                "Gwarzo":        "Gwarzo, Kano, NG",
            },
            "Lagos": {
                "Lagos Market":  "Lagos, Lagos, NG",
                "Badagry":       "Badagry, Lagos, NG",
            },
            "Kaduna": {
                "Kaduna City":   "Kaduna, Kaduna, NG",
                "Zaria":         "Zaria, Kaduna, NG",
                "Saminaka":      "Saminaka, Kaduna, NG",
            },
            "Katsina": {
                "Katsina City":  "Katsina, Katsina, NG",
                "Dandume":       "Dandume, Katsina, NG",
                "Daura":         "Daura, Katsina, NG",
            },
            "Borno": {
                "Maiduguri":     "Maiduguri, Borno, NG",
                "Biu":           "Biu, Borno, NG",
                "Damboa":        "Damboa, Borno, NG",
            },
            "Yobe": {
                "Damaturu":      "Damaturu, Yobe, NG",
                "Potiskum":      "Potiskum, Yobe, NG",
                "Gashua":        "Gashua, Yobe, NG",
            },
            "Adamawa": {
                "Jimeta":        "Jimeta, Adamawa, NG",
                "Mubi":          "Mubi, Adamawa, NG",
                "Michika":       "Michika, Adamawa, NG",
            },
            "Oyo": {
                "Ibadan":        "Ibadan, Oyo, NG",
            },
            "Abia": {
                "Aba":           "Aba, Abia, NG",
            },
            "Gombe": {
                "Gombe City":    "Gombe, Gombe, NG",
            },
            "Sokoto": {
                "Illela":        "Illela, Sokoto, NG",
                "Sokoto City":   "Sokoto, Sokoto, NG",
            },
        }
    },
    "Ethiopia": {
        "currency": "ETB",
        "states": {
            "Amhara": {
                "Bahir Dar":     "Bahir Dar, Amhara, ET",
                "Gondar":        "Gondar, Amhara, ET",
                "Dessie":        "Dessie, Amhara, ET",
                "Debre Birhan":  "Debre Birhan, Amhara, ET",
            },
            "Oromia": {
                "Jimma":         "Jimma, Oromia, ET",
                "Adama":         "Adama, Oromia, ET",
                "Assela":        "Assela, Oromia, ET",
                "Chiro":         "Chiro, Oromia, ET",
            },
            "Addis Ababa": {
                "Addis Ababa":   "Addis Ababa, ET",
            },
            "SNNPR": {
                "Hawassa":       "Hawassa, SNNPR, ET",
                "Arba Minch":    "Arba Minch, SNNPR, ET",
            },
            "Tigray": {
                "Mekelle":       "Mekelle, Tigray, ET",
                "Axum":          "Axum, Tigray, ET",
            },
        }
    }
}

# Country-aware crop lists — prevents Nigerian farmer selecting Teff
# and Ethiopian farmer selecting Gari
CROPS_BY_COUNTRY = {
    "Nigeria": [
        "Maize", "Gari", "Rice", "Yam",
        "Sorghum", "Millet", "Beans", "Onions",
    ],
    "Ethiopia": [
        "Maize", "Teff", "Sorghum", "Wheat",
    ]
}

STORAGE_TYPES = [
    "None (selling from field)",
    "Traditional open bags",
    "Hermetic bags",
    "Warehouse / silo",
]

STORAGE_MAP = {
    "None (selling from field)": None,
    "Traditional open bags":     "Traditional open bags",
    "Hermetic bags":             "Hermetic bags",
    "Warehouse / silo":          "Warehouse / silo",
}

RISK_COLOURS = {
    "Low":    "🟢",
    "Medium": "🟡",
    "High":   "🔴",
}