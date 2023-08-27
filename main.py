"""
"""
from datetime import datetime

import folium
import pandas as pd
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim
from percache import Cache

geolocator = Nominatim(user_agent="event_heatmap")

@Cache("coords-cache")
def get_coordinates(location: str) -> tuple[float | None, float | None]:
    """
    Returns (float, float) coordinates of location specified in text.
    Returns (None, None) if not found.
    Result is cached to disk.
    """
    print(f"resolving {location}")
    try:
        if coordinates := geolocator.geocode(location):
            return coordinates.latitude, coordinates.longitude
    except Exception:
        print(ex)
    return None, None


# ההתנתקות
CUTOFF = datetime(2005, 9, 11)


def main():
    """
    Processes a spreadsheet downloaded from Betselem and renamed "civilians.xlsx".
    Soldier deaths can be processed as well. Name their spreadsheet "soldiers.xlsx" and uncomment the appropriate line below.
    Location column should be renamed "location".
    Date of death should be renamed "death".
    Only events since ההתנתקות are processed. Change `CUTOFF` for a different starting date.
    """
    # Read spreadsheet
    df = pd.concat(
        [
            pd.read_excel(path)
            for path in [
                "civilian.xlsx",
                # "soldiers.xlsx",
            ]
        ]
    )
    # Discard events before cutoff
    df = df[df["death"] > CUTOFF]

    # Get locations coordinates
    all_locations = (
        df["location"]
        .apply(get_coordinates)
        .apply(lambda x: (None, None) if x is None else x)
    )
    df["latitude"], df["longitude"] = zip(*all_locations)
    df = df.dropna(subset=["latitude", "longitude"])

    # Create a map centered around the man of the events
    center_latitude = df["latitude"].mean()
    center_longitude = df["longitude"].mean()
    base_map = folium.Map(location=[center_latitude, center_longitude], zoom_start=10)

    # Create a HeatMap layer
    heat_data = df[["latitude", "longitude"]].values.tolist()
    HeatMap(heat_data, radius=20, blur=5).add_to(base_map)

    # Save the map to an HTML file
    output_file = "event_heatmap.html"
    base_map.save(output_file)

    print(f"Heatmap created and saved to '{output_file}'")


if __name__ == "__main__":
    main()
