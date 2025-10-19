import math as m
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import scipy as sp

def compute_clock_offset(t, dt0, dt1, dt2):
    clock_offsets = []
    
    for t_i in t:
        clock_offsets.append(dt0 + dt1 * t_i + dt2 * t_i**2)

    return clock_offsets

def ecc_anomaly(M, e):
    E = M

    max_iter = 12

    i = 1
    dE = 1

    while ((dE > 1e-12) and (i < max_iter)):
        E_tmp = E
        E = M + e * np.sin(E)
        dE = np.mod(E - E_tmp, 2 * np.pi)
        i = i + 1

    if (i == max_iter):
        print('WARNING: Eccentric anomaly does not converge.\n')

    E = np.mod(E, 2 * np.pi)

    return E

def compute_ITRF_satellite_position(GMe, a, e, M0, Omega0, OmegaEdot, Omegadot, i0, idot, w0, wdot, t):
    coord_ORS = []
    coord_ITRF = []

    # compute mean motion
    n = m.sqrt(GMe / a**3)

    for t_i in t:
        # compute mean anomaly
        M = M0 + n * t_i

        # compute eccentric anomaly
        eta = ecc_anomaly(M, e)

        # Compute psi
        psi = m.atan2((m.sqrt(1 - e**2) * m.sin(eta)), (m.cos(eta) - e))

        # Compute radius r
        r = (a * (1 - e**2)) / (1 + (e * m.cos(psi)))

        # Compute the coordinates of the satellite in ORS and store it in coord_ORS
        xORS = r * m.cos(psi)
        yORS = r * m.sin(psi)
        zORS = 0
        coord_ORS.append(np.array([[xORS], [yORS], [zORS]]))
        # Compute rotation angles omega, i, OMEGA
        omega = w0 + (wdot * t_i)
        i = i0 + (idot * t_i)
        OMEGA = Omega0 + ((Omegadot - OmegaEdot) * t_i)
        # Compute the rotation matrices required to transform from ORS to ITRF
        # R(-omega(t))
        Romega = np.array([[np.cos(-omega), np.sin(-omega), 0], [-np.sin(-omega), np.cos(-omega), 0], [0, 0, 1]])
        # R(i(t)) # la matrice di rotazione è fatta già per angoli negativi (non c'è bisogno di usare -i)
        Ri = np.array([[1, 0, 0], [0, np.cos(i), -np.sin(i)], [0, np.sin(i), np.cos(i)]])
        # R(-OMEGA(t))
        RO = np.array([[np.cos(-OMEGA), np.sin(-OMEGA), 0], [-np.sin(-OMEGA), np.cos(OMEGA), 0], [0, 0, 1,]])
        # Final rotation matrix R
        R = np.dot(np.dot(RO, Ri), Romega)
        # Compute the coordinates of the satellites in ITRF and store it in coord_ITRF
        coord_ITRF.append(np.dot(R, coord_ORS[t_i]))

    return coord_ITRF

def cart2Geod(P_cart):
    x, y, z = P_cart[0], P_cart[1], P_cart[2]
    a = 6378137
    e = 0.0818191908426215
    e2 = e*e
    b = a*(np.sqrt(1 - e2))
    eb2 = (a*a - b*b)/(b*b)
    # radius computation
    r = np.sqrt(x*x + y*y)
    # longitude
    lon = np.arctan2(y, x)
    # latitude
    psi = np.arctan2(z, (r*np.sqrt(1-e2)))
    lat = np.arctan2((z+eb2*b*np.power(np.sin(psi), 3)), (r - e2*a*np.power(np.cos(psi), 3)))
    N = a/np.sqrt(1 - e2*np.power(np.sin(lat), 2))
    h = r/(np.cos(lat)) - N
    lon = lon*180/np.pi
    lat = lat*180/np.pi
    return np.matrix(f'{lat}; {lon}; {h}')

def is_satellite_visible(sat_coords, observer_coords):
    """
    Check if the satellite is visible from a given observer's location.

    Parameters:
    sat_coords (tuple): Satellite's geodetic coordinates (latitude, longitude, height) in degrees and meters.
    observer_coords (tuple): Observer's geodetic coordinates (latitude, longitude, height) in degrees and meters.

    Returns:
    bool: True if the satellite is visible, False otherwise.
    """
    # Unpack coordinates
    sat_lat, sat_lon, sat_height = sat_coords
    obs_lat, obs_lon, obs_height = observer_coords

    # Convert degrees to radians
    sat_lat, sat_lon = np.radians(sat_lat), np.radians(sat_lon)
    obs_lat, obs_lon = np.radians(obs_lat), np.radians(obs_lon)

    # Earth's radius (approximate)
    R = 6378137  # meters

    # Observer's position in ECEF (Earth-Centered, Earth-Fixed)
    x_obs = (R + obs_height) * np.cos(obs_lat) * np.cos(obs_lon)
    y_obs = (R + obs_height) * np.cos(obs_lat) * np.sin(obs_lon)
    z_obs = (R + obs_height) * np.sin(obs_lat)

    # Satellite's position in ECEF
    x_sat = (R + sat_height) * np.cos(sat_lat) * np.cos(sat_lon)
    y_sat = (R + sat_height) * np.cos(sat_lat) * np.sin(sat_lon)
    z_sat = (R + sat_height) * np.sin(sat_lat)

    # Vector from observer to satellite
    vec_sat = np.array([x_sat - x_obs, y_sat - y_obs, z_sat - z_obs])

    # Observer's zenith vector
    vec_zenith = np.array([x_obs, y_obs, z_obs])

    # Normalize vectors
    vec_sat_norm = vec_sat / np.linalg.norm(vec_sat)
    vec_zenith_norm = vec_zenith / np.linalg.norm(vec_zenith)

    # Flatten the vectors to ensure compatibility for dot product
    vec_sat_norm = vec_sat_norm.flatten()
    vec_zenith_norm = vec_zenith_norm.flatten()

    # Compute elevation angle
    elevation_angle = np.arcsin(np.dot(vec_sat_norm, vec_zenith_norm))

    # Convert elevation angle to degrees
    elevation_angle_deg = np.degrees(elevation_angle)

    # Satellite is visible if elevation angle is greater than 0
    return elevation_angle_deg > 0

def geod2Cart(lat, lon, h):
    """Convert geodetic coordinates to Cartesian ITRF"""
    lat_rad = np.deg2rad(lat)
    lon_rad = np.deg2rad(lon)

    a = 6378137
    e = 0.0818191908426215
    e2 = e * e

    N = a / np.sqrt(1 - e2 * np.sin(lat_rad)**2)

    X = (N + h) * np.cos(lat_rad) * np.cos(lon_rad)
    Y = (N + h) * np.cos(lat_rad) * np.sin(lon_rad)
    Z = (N * (1 - e2) + h) * np.sin(lat_rad)

    return np.array([[X], [Y], [Z]])

def compute_elevation_azimuth(sat_cart, user_cart, user_lat, user_lon):
    """
    Compute elevation and azimuth angles from user to satellite

    Parameters:
    - sat_cart: Satellite position in ITRF [X, Y, Z]
    - user_cart: User position in ITRF [X, Y, Z]
    - user_lat, user_lon: User geodetic coordinates in degrees

    Returns:
    - elevation: Elevation angle in degrees
    - azimuth: Azimuth angle in degrees
    - distance: Distance in meters
    """
    # Vector from user to satellite
    dx = sat_cart - user_cart

    # Convert to local ENU (East-North-Up) coordinates
    lat_rad = np.deg2rad(user_lat)
    lon_rad = np.deg2rad(user_lon)

    # Rotation matrix from ITRF to ENU
    R_enu = np.array([
        [-np.sin(lon_rad), np.cos(lon_rad), 0],
        [-np.sin(lat_rad)*np.cos(lon_rad), -np.sin(lat_rad)*np.sin(lon_rad), np.cos(lat_rad)],
        [np.cos(lat_rad)*np.cos(lon_rad), np.cos(lat_rad)*np.sin(lon_rad), np.sin(lat_rad)]
    ])

    # Transform vector to ENU
    dxyz_enu = np.dot(R_enu, dx)

    E = dxyz_enu[0, 0]
    N = dxyz_enu[1, 0]
    U = dxyz_enu[2, 0]

    # Calculate distance
    distance = np.sqrt(E**2 + N**2 + U**2)

    # Calculate elevation angle
    elevation = np.rad2deg(np.arcsin(U / distance))

    # Calculate azimuth angle
    azimuth = np.rad2deg(np.arctan2(E, N))
    if azimuth < 0:
        azimuth += 360

    return elevation, azimuth, distance