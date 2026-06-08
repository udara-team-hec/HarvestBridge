LOCATIONS = {
    "Nigeria": {
        "currency": "NGN",
        "states": {
            "Lagos": {
                "Lagos Island": "Lagos Island, Lagos, NG",
                "Epe":          "Epe, Lagos, NG",
                "Badagry":      "Badagry, Lagos, NG",
                "Ikorodu":      "Ikorodu, Lagos, NG",
            },
            "Kano": {
                "Kano City": "Kano, Kano, NG",
                "Wudil":     "Wudil, Kano, NG",
                "Gwarzo":    "Gwarzo, Kano, NG",
            },
            "Benue": {
                "Makurdi": "Makurdi, Benue, NG",
                "Gboko":   "Gboko, Benue, NG",
                "Otukpo":  "Otukpo, Benue, NG",
            },
            "Ondo": {
                "Akure":      "Akure, Ondo, NG",
                "Ondo Town":  "Ondo, Ondo, NG",
                "Okitipupa":  "Okitipupa, Ondo, NG",
            },
            "Katsina": {
                "Katsina City": "Katsina, Katsina, NG",
                "Daura":        "Daura, Katsina, NG",
            },
            "Kaduna": {
                "Kaduna City": "Kaduna, Kaduna, NG",
                "Zaria":       "Zaria, Kaduna, NG",
            },
            "Rivers": {
                "Port Harcourt": "Port Harcourt, Rivers, NG",
                "Ahoada":        "Ahoada, Rivers, NG",
            },
            "Abuja": {
                "Gwagwalada": "Gwagwalada, Abuja, NG",
                "Kuje":       "Kuje, Abuja, NG",
            },
        }
    },
    "Ethiopia": {
        "currency": "ETB",
        "states": {
            "Amhara": {
                "Bahir Dar": "Bahir Dar, Amhara, ET",
                "Gondar":    "Gondar, Amhara, ET",
                "Dessie":    "Dessie, Amhara, ET",
            },
            "Oromia": {
                "Jimma":   "Jimma, Oromia, ET",
                "Adama":   "Adama, Oromia, ET",
                "Nekemte": "Nekemte, Oromia, ET",
            },
            "Addis Ababa": {
                "Mercato": "Mercato, Addis Ababa, ET",
                "Kaliti":  "Kaliti, Addis Ababa, ET",
            },
        }
    }
}

CROPS = [
    "Maize", "Cassava", "Gari", "Rice", "Yam",
    "Beans", "Millet", "Sorghum", "Sesame"
]

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