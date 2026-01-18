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

    alpha = [param['alpha0'], param['alpha1'], param['alpha2'], param['alpha3']]
    beta = [param['beta0'], param['beta1'], param['beta2'], param['beta3']]

    # alpha = [0.7451*10**(-8),  0.1490*10**(-7),  -0.5960*10**(-7), -0.1192*10**(-6)]
    # beta = [0.9216*10**5,  0.1311*10**6, -0.6554*10**5, -0.5243*10**6]

    L1 = compute_observations(filtered_df, f1, param['ground_station_latitude'], param['ground_station_longitude'], alpha+beta, param['fundamental_frequency'] * param['frequency_multiplier_L1'], param['fundamental_frequency'] * param['frequency_multiplier_L1']) 
    L2 = compute_observations(filtered_df, f2, param['ground_station_latitude'], param['ground_station_longitude'], alpha+beta, param['fundamental_frequency'] * param['frequency_multiplier_L2'], param['fundamental_frequency'] * param['frequency_multiplier_L1'])

    L1.to_csv('output/L1_observations.csv', index=False)
    L2.to_csv('output/L2_observations.csv', index=False)

    return L1, L2