"""Cicle slip simulation

Created by Arianna & Edoardo

"""
# libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import scipy as sp
import json

# import functions
from functions import *
from plots import *

print('Importing default parameters and initializing variables ...'.ljust(80), end='', flush=True)
with open('default_parameters.json', 'r') as file:
    param = json.load(file)

# dataframe containing all values, exported as a csv at the end of the processing
all_data = pd.DataFrame(columns=['time', 'x_cart', 'y_cart', 'z_cart', 'lat', 'long', 'height', 'clock_offset', 'integer_ambiguity', 'noise', 'visibility', 'distance'])

# integer ambiguity
all_data['integer_ambiguity'] = np.full(param['epochs'], param['integer_ambiguity'])

# gaussian noise
np.random.seed(42) # for reproducibility
all_data['noise'] = np.random.normal(0, param['clock_offset_std'], param['epochs'])

# lambda (widelane)
lambda_wl = 0.5

# Create a list containing all the epochs
all_data['time'] = list(range(0, param['epochs'], 1))

print('done.')
"""
Clock offset computation
"""
print("Computing clock offsets...".ljust(80), end='', flush=True)
all_data['clock_offset'] = compute_clock_offset(
    all_data['time'],
    param['dt0'],
    param['dt1'],
    param['dt2']
)

plot_clock_offsets(all_data)

print('done.')
"""
Satellite position computation in Cartesian ITRF coordinates [X, Y, Z]
"""
print("Computing satellite positions...".ljust(80), end='', flush=True)
coord_ITRF = compute_ITRF_satellite_position(all_data['time'], param)

all_data['x_cart'] = [x[0, 0] for x in coord_ITRF]
all_data['y_cart'] = [x[1, 0] for x in coord_ITRF]
all_data['z_cart'] = [x[2, 0] for x in coord_ITRF]

print('done.')
"""
Conversion from global cartesian coordinates to geodetic coordinates (latitude, longitude, height)
"""
print("Converting Cartesian coordinates to Geodetic coordinates...".ljust(80), end='', flush=True)
coord_geod = []

coord_ITRF_len = len(coord_ITRF)
for v in range(coord_ITRF_len):
    coord_geod.append(cart2Geod(coord_ITRF[v]))

# Create 3 lists containing the values of Latitude, Longitude and Height
lats = []
longs = []
heights = []
for v in range (len(coord_geod)):
    lats.append(coord_geod[v][0])
    longs.append(coord_geod[v][1])
    heights.append(coord_geod[v][2])

all_data['lat'] = [float(lat.item()) if isinstance(lat, np.ndarray) else float(lat) for lat in lats]
all_data['long'] = [float(lon.item()) if isinstance(lon, np.ndarray) else float(lon) for lon in longs]
all_data['height'] = [float(hgt.item()) if isinstance(hgt, np.ndarray) else float(hgt) for hgt in heights]

print('done.')
"""
Plotting groundtrack of the satellite
"""
print("Plotting satellite trajectory with basemap...".ljust(80), end='', flush=True)
# Realize a dataframe containing satellite coordinates
df = pd.DataFrame()
df['time'] = all_data['time']
df['lat'] = lats
df['lon'] = longs

# Transform the DataFrame in a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs = 3857)

# Load the basemap
world = gpd.read_file('world/world.shp')

plot_satellite_trajectory(gdf, world)

print('done.')
"""
Cheching observability period for a ground station located in Toamasina (Madagascar)
"""
print("Cheching observability period in Toamasina...".ljust(80), end='', flush=True)

latitude_T = param['ground_station_latitude']
longitude_T = param['ground_station_longitude']
height_T = param['ground_station_altitude']

observer_coords = (latitude_T, longitude_T, height_T)

# Check visibility for each time step
visibility = []
for i in range(len(coord_geod)):
    sat_coords = (coord_geod[i][0], coord_geod[i][1], coord_geod[i][2])
    visibility.append(is_satellite_visible(sat_coords, observer_coords))

all_data['visibility'] = visibility

# Convert time from seconds to hours
t_hours = [time / 3600 for time in all_data['time']]

plot_visibility(t_hours, visibility)

plot_satellite_trajectory_with_visibility(world, gdf, all_data, latitude_T, longitude_T)

print('done.')

"""Plotting elevation for visible timewindow"""
print("Plotting elevation for visible timewindow...".ljust(80), end='', flush=True)

# Convert user location to Cartesian
user_cart = geod2Cart(latitude_T, longitude_T, height_T)

# Find visibility periods (continuous segments above minimum elevation)

min_elevation = param['minimum_elevation_angle']

visibility_periods = []
visible_times = []
elevations = []
azimuths = []
distances = []
visible_elevations = []

for i, t_i in enumerate(all_data['time']):
    elev, azim, dist = compute_elevation_azimuth(coord_ITRF[i], user_cart, latitude_T, longitude_T)
    elevations.append(elev)
    azimuths.append(azim)
    distances.append(dist / 1000)  # Convert to km

    # Check if satellite is visible
    if elev >= min_elevation:
        visible_times.append(t_i)
        visible_elevations.append(elev)

all_data['distance'] = distances

t_step = 1  # seconds

if visible_times:
    period_start = visible_times[0]
    period_end = visible_times[0]

    for i in range(1, len(visible_times)):
        if visible_times[i] - visible_times[i-1] <= t_step:
            period_end = visible_times[i]
        else:
            visibility_periods.append((period_start, period_end))
            period_start = visible_times[i]
            period_end = visible_times[i]

    visibility_periods.append((period_start, period_end))

# Print visibility summary
print(f"\n{'='*60}")
print(f"SATELLITE VISIBILITY ANALYSIS")
print(f"{'='*60}")
# print(f"Location: Toamasina, Madagascar")
print(f"Coordinates: {latitude_T:.4f}°, {longitude_T:.4f}°")
print(f"\nNumber of visibility periods: {len(visibility_periods)}")
print(f"Total visible time: {len(visible_times)} seconds ({len(visible_times)/3600:.2f} hours)")
print(f"\nVisibility periods:")
print(f"{'Start (HH:MM:SS)':<20} {'End (HH:MM:SS)':<20} {'Duration (min)':<15}")
print(f"{'-'*60}")

for start, end in visibility_periods:
    start_hms = f"{start//3600:02d}:{(start%3600)//60:02d}:{start%60:02d}"
    end_hms = f"{end//3600:02d}:{(end%3600)//60:02d}:{end%60:02d}"
    duration = (end - start) / 60
    print(f"{start_hms:<20} {end_hms:<20} {duration:<15.1f}")

plot_elevation(all_data, min_elevation, elevations)

plot_distance_from_user(all_data)

# find min and max of all_data['distance'] and index of it
min_distance = min(all_data['distance'])
max_distance = max(all_data['distance'])

min_index = all_data['distance'].idxmin()
max_index = all_data['distance'].idxmax()

print(f"Min distance: {min_distance} at time {min_index} seconds")
print(f"Max distance: {max_distance} at time {max_index} seconds")

print(f"\n{'='*60}")

"""Computing distance between satellite and ground station over time"""

print("Computing distance between satellite and ground station over time...".ljust(80), end='', flush=True)

# Extract visible portions
satellite_distances_visible = []
t_visible_hours = []

for i in range(len(visibility)):
    if visibility[i]:
        satellite_distances_visible.append(all_data['distance'][i])
        t_visible_hours.append(t_hours[i])

avg_satellite_distance = np.mean(satellite_distances_visible)

print('done.')

"""Exporting dataframes and observations to csv"""
print("Exporting dataframes and observations to csv...".ljust(80), end='', flush=True)

# export all_data as csv
all_data.to_csv('output/all_data.csv', index=False)

# filter dataframe and only keep rows with all_data['visible'] == True
visible_epoch = all_data[all_data['visibility'] == True]

visible_epoch.to_csv('output/visible_epoch.csv', index=False)

# distance(km) * 1000 + clock_offset * c + noise + integer_ambiguity * lambda_wl
observations = pd.DataFrame(columns=['phase'])

observations['phase'] = visible_epoch['distance'] * 1000 + visible_epoch['clock_offset'] * sp.constants.speed_of_light + visible_epoch['noise'] + visible_epoch['integer_ambiguity'] * lambda_wl

observations.to_csv('output/observations.csv', index=False)

# array from dataframe
observations = observations['phase'].to_numpy()

# plot observations
plot_observations(observations)

differences = np.zeros(len(observations) - 1)

for i in range(1, len(observations)):
  differences[i-1] = observations[i-1] - observations[i]

# export csv of differences
np.savetxt('output/differences.csv', differences, delimiter=',')

# plot differences
# plot_differences(differences)

print('done.')