

import pandas as pd
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import plotly.express as px


def haversine_distance(pos1, pos2):
    return geodesic(pos1, pos2).kilometers

def detect_proximity(data, distance_threshold):
    proximity_events = []

    # Group data by minute to avoid unnecessary comparisons
    data['rounded_time'] = data['timestamp'].dt.floor('min')
    grouped = data.groupby('rounded_time')

    for time, group in grouped:
        vessels = group.reset_index(drop=True)
        for i in range(len(vessels)):
            vessel1 = vessels.loc[i]
            for j in range(i + 1, len(vessels)):
                vessel2 = vessels.loc[j]
                if vessel1['mmsi'] != vessel2['mmsi']:
                    distance = haversine_distance(
                        (vessel1['lat'], vessel1['lon']),
                        (vessel2['lat'], vessel2['lon'])
                    )
                    if distance <= distance_threshold:
                        proximity_events.append({
                            'timestamp': time,
                            'mmsi_1': vessel1['mmsi'],
                            'mmsi_2': vessel2['mmsi'],
                            'distance_km': round(distance, 3)
                        })

    return pd.DataFrame(proximity_events)


data = pd.read_csv('sample_data.csv')
data['timestamp'] = pd.to_datetime(data['timestamp'])
data['lat'] = data['lat'].astype(float)
data['lon'] = data['lon'].astype(float)


distance_threshold = 1 # in kilometers
proximity_df = detect_proximity(data, distance_threshold)

print("Proximity Events:")
print(proximity_df.head())


def plot_proximity_matplot(events_df):
    plt.figure(figsize=(8, 5))
    for _, row in events_df.iterrows():
        plt.plot([row['timestamp'], row['timestamp']], [row['mmsi_1'], row['mmsi_2']], 'bo-')
    plt.xlabel('Timestamp')
    plt.ylabel('MMSI')
    plt.title('Vessel Proximity Events')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_proximity_plotly(events_df):
    fig = px.scatter(events_df, x='timestamp', y='mmsi_1',
                     color='mmsi_2', hover_data=['distance_km'],
                     title='Interactive Vessel Proximity Events',
                     labels={'timestamp': 'Time', 'mmsi_1': 'Vessel', 'mmsi_2': 'Near Vessel'})
    fig.show()


plot_proximity_matplot(proximity_df)




