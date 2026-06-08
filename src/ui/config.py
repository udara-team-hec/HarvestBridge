LOCATIONS = {
    "Nigeria": {
        "currency": "NGN",
        "states": {
            "Kano": {
                "Kano City": "Kano, Nigeria",
                "Wudil":     "Wudil, Kano, Nigeria",
                "Gwarzo":    "Gwarzo, Kano, Nigeria",
            },
            "Lagos": {
                "Lagos Market": "Lagos, Nigeria",
                "Badagry":      "Badagry, Lagos, Nigeria",
            },
            "Kaduna": {
                "Kaduna City": "Kaduna, Nigeria",
                "Zaria":       "Zaria, Kaduna, Nigeria",
                "Saminaka":    "Saminaka, Kaduna, Nigeria",
            },
            "Katsina": {
                "Katsina City": "Katsina, Nigeria",
                "Dandume":      "Dandume, Katsina, Nigeria",
                "Daura":        "Daura, Katsina, Nigeria",
            },
            "Borno": {
                "Maiduguri": "Maiduguri, Nigeria",
                "Biu":       "Biu, Borno, Nigeria",
                "Damboa":    "Damboa, Borno, Nigeria",
            },
            "Yobe": {
                "Damaturu": "Damaturu, Nigeria",
                "Potiskum": "Potiskum, Yobe, Nigeria",
                "Gashua":   "Gashua, Yobe, Nigeria",
            },
            "Adamawa": {
                "Jimeta":  "Jimeta, Adamawa, Nigeria",
                "Mubi":    "Mubi, Adamawa, Nigeria",
                "Michika": "Michika, Adamawa, Nigeria",
            },
            "Oyo": {
                "Ibadan": "Ibadan, Nigeria",
            },
            "Abia": {
                "Aba": "Aba, Nigeria",
            },
            "Gombe": {
                "Gombe City": "Gombe, Nigeria",
            },
            "Sokoto": {
                "Illela":      "Illela, Sokoto, Nigeria",
                "Sokoto City": "Sokoto, Nigeria",
            },
        }
    },
    "Ethiopia": {
        "currency": "ETB",
        "states": {
            "Amhara": {
                "Bahir Dar":    "Bahir Dar, Ethiopia",
                "Gondar":       "Gondar, Ethiopia",
                "Dessie":       "Dessie, Ethiopia",
                "Debre Birhan": "Debre Birhan, Ethiopia",
            },
            "Oromia": {
                "Jimma":  "Jimma, Ethiopia",
                "Adama":  "Adama, Ethiopia",
                "Assela": "Assela, Ethiopia",
                "Chiro":  "Chiro, Ethiopia",
            },
            "Addis Ababa": {
                "Addis Ababa": "Addis Ababa, Ethiopia",
            },
            "SNNPR": {
                "Hawassa":    "Hawassa, Ethiopia",
                "Arba Minch": "Arba Minch, Ethiopia",
            },
            "Tigray": {
                "Mekelle": "Mekelle, Ethiopia",
                "Axum":    "Axum, Ethiopia",
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