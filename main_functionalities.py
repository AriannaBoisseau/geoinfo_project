import json

from functions import *

def run_simulation():

    with open('default_parameters.json', 'r') as file:
        param = json.load(file)

    satellite_df, satellite_matrix = computing_satellite_data(param)

    visibility_df = compute_visibility_df(satellite_df, param['ground_station_latitude'], param['ground_station_longitude'], param['minimum_elevation_angle'])

    distances = []
    elevations = []
    azimuths = []

    for i, t_i in enumerate(satellite_df['time']):
        elev, azim, dist = compute_elevation_azimuth(satellite_matrix[i], geod2Cart(param['ground_station_latitude'], param['ground_station_longitude'], param['ground_station_altitude']), param['ground_station_latitude'], param['ground_station_longitude'])
        elevations.append(elev)
        azimuths.append(azim)
        distances.append(dist / 1000)  # Convert to km

    satellite_df['distance'] = distances
    satellite_df['elevation'] = elevations
    satellite_df['azimuth'] = azimuths

    filtered_df = visibility_df[visibility_df['visibility'] == True]

    f1 = compute_wavelength(param['fundamental_frequency'], param['frequency_multiplier_L1'])
    f2 = compute_wavelength(param['fundamental_frequency'], param['frequency_multiplier_L2'])

    L1 = compute_observations(filtered_df, f1)
    L2 = compute_observations(filtered_df, f2)

    L1.to_csv('output/L1_observations.csv', index=False)
    L2.to_csv('output/L2_observations.csv', index=False)