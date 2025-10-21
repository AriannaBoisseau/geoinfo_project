# libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import scipy as sp

def plot_clock_offsets(all_data):
    fig, ax = plt.subplots(figsize=(10,6))
    ax.set(xlabel='Seconds in a day', ylabel='Clock-offset', title = "Clock offsets")
    ax.plot(all_data['time'], all_data['clock_offset'], '-', color='blue')
    plt.show() # uncomment to show the plot

def plot_satellite_trajectory(gdf, world):
    fig, ax = plt.subplots (figsize = (15,15))
    world.plot(ax=ax)
    ax.set(xlabel='Longitude', ylabel='Latitude', title='Satellite daily trajectory')
    gdf.plot(ax = ax, marker='o', color='red')
    plt.show() 

def plot_visibility(t_hours, visibility):
    fig, ax = plt.subplots(figsize=(10,6))
    ax.set(xlabel='Hours from the first message from the satellite', ylabel='Visibility', title='Satellite Visibility')
    ax.plot(t_hours, visibility, '-', color='blue')
    ax.axhline(0, color='red', linestyle='--')
    ax.set_ylim(-0.5, 1.5)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Not Visible', 'Visible'])
    plt.show()

def plot_satellite_trajectory_with_visibility(world, gdf, all_data, latitude_T, longitude_T):
    fig, ax = plt.subplots(figsize=(15, 15))
    ax.set(xlabel='Longitude', ylabel='Latitude', title='Satellite daily trajectory')
    world.plot(ax=ax)

    # Plot the ground track with visibility indication
    visible_points = gdf[all_data['visibility'] == 1]
    not_visible_points = gdf[all_data['visibility'] == 0]

    visible_points.plot(ax=ax, marker='o', color='green', label='Visible', markersize=5)
    not_visible_points.plot(ax=ax, marker='o', color='red', label='Not visible', markersize=5)

    # Add Toamasina coordinates in orange
    ax.plot(longitude_T, latitude_T, 'o', color='orange', markersize=10, label='Toamasina')

    # Add legend
    ax.legend()

    plt.show()

def plot_satellite_distance(t_hours, all_data, t_visible_hours, satellite_distances_visible, avg_satellite_distance):
    # Plot both
    plt.figure(figsize=(12, 6))
    plt.plot(t_hours, all_data['distance'], 'r-', label='Not visible')  # red line for full distance
    plt.plot(t_visible_hours, satellite_distances_visible, 'g-', linewidth=2, label='Visible')  # green overlay
    plt.xlabel("Time [hours]")
    plt.ylabel("Distance from Earth's Center [m]")
    plt.title(f"Satellite Distance Over Time with Visibility - Average distance: {avg_satellite_distance} [m]")
    plt.xlim(0, 24)
    plt.grid(True)
    plt.legend()
    plt.show()

def plot_elevation(all_data, min_elevation, elevations):
    plt.figure(figsize=(12, 6))
    plt.plot(np.array(all_data['time'])/3600, elevations, '-', color='blue', linewidth=1)
    plt.axhline(y=min_elevation, color='r', linestyle='--', label=f'Min elevation ({min_elevation}°)')
    plt.fill_between(np.array(all_data['time'])/3600, min_elevation, 90, where=np.array(elevations)>=min_elevation,
                    alpha=0.3, color='green', label='Visible')
    plt.xlabel('Time (hours)')
    plt.ylabel('Elevation angle (degrees)')
    plt.title('Satellite Elevation Angle from Toamasina')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.xlim(0, 24)
    plt.show()

def plot_distance_from_user(all_data):
    plt.figure(figsize=(12, 6))
    plt.plot(np.array(all_data['time'])/3600, all_data['distance'], '-', color='blue', linewidth=1)
    plt.xlabel('Time (hours)')
    plt.ylabel('Distance (km)')
    plt.title('Satellite distance from user in Tomasina')
    plt.show()

def plot_observations(observations):
    plt.figure(figsize=(12, 6))
    plt.plot(range(53491, 79963, 1), observations, '-', color='blue', linewidth=1)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Distance (m)')
    plt.title('Satellite distance from user only for visible epoch')
    plt.show()

def plot_differences(differences):
    plt.figure(figsize=(12, 6))
    plt.plot(range(53491, 79962, 1), differences, '-', color='blue', linewidth=1)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Distance (m)')
    plt.title('Differences between consecutive epochs')
    plt.show()