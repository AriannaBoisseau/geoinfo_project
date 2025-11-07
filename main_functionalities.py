import json

from functions import *

with open('default_parameters.json', 'r') as file:
    param = json.load(file)

satellite_df, satellite_matrix = computing_satellite_data(param)

visibility_df = compute_visibility_df(satellite_df, param['ground_station_latitude'], param['ground_station_longitude'], param['minimum_elevation_angle'])

distances = []
elevations = []
azimuths = []

# for i, t_i in enumerate(satellite_df['time']):
#     elev, azim, dist = compute_elevation_azimuth(satellite_matrix[i], geod2Cart(param['ground_station_latitude'], param['ground_station_longitude'], param['ground_station_altitude']), param['ground_station_latitude'], param['ground_station_longitude'])
#     elevations.append(elev)
#     azimuths.append(azim)
#     distances.append(dist / 1000)  # Convert to km