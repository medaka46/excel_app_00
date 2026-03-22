import pandas as pd

# Sheet 1: Projects
projects = pd.DataFrame({
    "Project Name": ["Tower A", "Tower B", "Office C", "Mall D", "Hotel E",
                     "Tower F", "School G", "Hospital H", "Condo I", "Park J"],
    "Type":         ["Residential", "Residential", "Office", "Commercial", "Hotel",
                     "Residential", "Education", "Medical", "Residential", "Leisure"],
    "Location":     ["Tokyo", "Osaka", "Tokyo", "Nagoya", "Tokyo",
                     "Fukuoka", "Sapporo", "Tokyo", "Osaka", "Kyoto"],
    "Status":       ["Completed", "In Progress", "Completed", "Planned", "In Progress",
                     "Completed", "Completed", "In Progress", "Planned", "Completed"],
    "Year":         [2021, 2024, 2022, 2026, 2023, 2020, 2019, 2025, 2026, 2021],
    "TFA (m2)":     [15000, 22000, 8500, 35000, 12000, 18000, 4500, 9000, 25000, 6000],
    "Cost (Oku)":   [45.0, 72.5, 20.0, 95.0, 38.0, 54.0, 10.5, 28.0, 80.0, 14.0],
    "Floors":       [30, 45, 12, 6, 20, 36, 4, 8, 50, 3],
})

# Sheet 2: Materials
materials = pd.DataFrame({
    "Material":      ["Concrete", "Steel", "Glass", "Aluminum", "Timber",
                      "Brick", "Insulation", "Roofing", "Tile", "Paint"],
    "Category":      ["Structure", "Structure", "Facade", "Facade", "Interior",
                      "Structure", "Envelope", "Envelope", "Finish", "Finish"],
    "Unit":          ["m3", "ton", "m2", "kg", "m3", "piece", "m2", "m2", "m2", "L"],
    "Unit Price":    [25000, 120000, 15000, 800, 60000, 150, 3000, 8000, 5000, 500],
    "CO2 (kg/unit)": [320, 1800, 25, 12, 50, 0.8, 4, 15, 8, 2],
    "Lead Days":     [3, 14, 21, 10, 7, 5, 7, 14, 10, 3],
    "Stock":         ["Available", "On Order", "Available", "Available", "Available",
                      "Available", "Low", "Available", "Available", "Low"],
})

# Sheet 3: Teams
teams = pd.DataFrame({
    "Team":            ["Design", "Structure", "MEP", "Interior", "Landscape",
                        "PM", "BIM", "Facade", "Sustainability", "Cost"],
    "Lead":            ["Tanaka", "Suzuki", "Yamada", "Ito", "Sato",
                        "Kato", "Nakamura", "Kobayashi", "Watanabe", "Abe"],
    "Members":         [8, 6, 10, 5, 4, 3, 7, 4, 3, 5],
    "Department":      ["Architecture", "Engineering", "Engineering", "Architecture", "Architecture",
                        "Management", "Technology", "Engineering", "Sustainability", "Management"],
    "Office":          ["Tokyo", "Tokyo", "Osaka", "Tokyo", "Kyoto",
                        "Tokyo", "Fukuoka", "Tokyo", "Osaka", "Tokyo"],
    "Active Projects": [5, 4, 6, 3, 2, 8, 5, 3, 4, 7],
    "Budget (Oku)":    [12.0, 9.5, 15.0, 7.0, 4.5, 5.0, 8.0, 6.0, 4.0, 5.5],
})

output = "Sample_DB_00.xlsx"
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    projects.to_excel(writer, sheet_name="Projects", index=False)
    materials.to_excel(writer, sheet_name="Materials", index=False)
    teams.to_excel(writer, sheet_name="Teams", index=False)

print(f"Saved: {output}")
