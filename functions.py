import math as m
import numpy as np
import pandas as pd
import pyproj as pp
import scipy as sp

from almanac_constants import AlmanacConstants as ac

def compute_clock_offset(t):
    clock_offsets = []
    
    for t_i in t:
        clock_offsets.append(ac.dt0 + ac.dt1 * t_i + ac.dt2 * t_i**2)

    return clock_offsets

def ecc_anomaly(M):
    E = M

    max_iter = 12

    i = 1
    dE = 1

    while ((dE > 1e-12) and (i < max_iter)):
        E_tmp = E
        E = M + ac.e * np.sin(E)
        dE = np.mod(E - E_tmp, 2 * np.pi)
        i = i + 1

    if (i == max_iter):
        print('WARNING: Eccentric anomaly does not converge.\n')

    E = np.mod(E, 2 * np.pi)

    return E

def compute_ITRF_satellite_position(t):
    coord_ORS = []
    coord_ITRF = []

    # compute mean motion
    n = m.sqrt(ac.GMe / ac.a**3)

    for t_i in t:
        # compute mean anomaly
        M = ac.M0 + n * t_i

        # compute eccentric anomaly
        eta = ecc_anomaly(M)

        # Compute psi
        psi = m.atan2((m.sqrt(1 - ac.e**2) * m.sin(eta)), (m.cos(eta) - ac.e))

        # Compute radius r
        r = (ac.a * (1 - ac.e**2)) / (1 + (ac.e * m.cos(psi)))

        # Compute the coordinates of the satellite in ORS and store it in coord_ORS
        xORS = r * m.cos(psi)
        yORS = r * m.sin(psi)
        zORS = 0
        coord_ORS.append(np.array([[xORS], [yORS], [zORS]]))
        # Compute rotation angles omega, i, OMEGA
        omega = ac.w0 + (ac.wdot * t_i)
        i = ac.i0 + (ac.idot * t_i)
        OMEGA = ac.Omega0 + ((ac.Omegadot - ac.OmegaEdot) * t_i)
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

def compute_ITRF_rover(latitude, longitude, height):
    crsIN = pp.CRS.from_epsg(4326)
    crsOUT = pp.CRS.from_epsg(4978)

    trf = pp.Transformer.from_crs(crsIN, crsOUT, always_xy=True)

    coord_ITRF = trf.transform(longitude, latitude, height)

    return np.array([[coord_ITRF[0]], [coord_ITRF[1]], [coord_ITRF[2]]])

def itrf_to_geodetic(df_ITRF):
    """
    Given a DataFrames with ITRF coordinates [X, Y, Z] in meters,
    return three DataFrames: latitude, longitude, and height.

    Parameters:
    - df_ITRF: DataFrame with columns ['X', 'Y', 'Z']

    Returns:
    - lat_df: DataFrame with column ['latitude']
    - lon_df: DataFrame with column ['longitude']
    - h_df: DataFrame with column ['height']
    """
    # Create transformer from ITRF (ECEF XYZ) to WGS84 geographic (lat/lon/height)
    transformer = pp.Transformer.from_crs("EPSG:4978", "EPSG:4326", always_xy=True)

    X = df_ITRF['X'].values
    Y = df_ITRF['Y'].values
    Z = df_ITRF['Z'].values

    # Perform the transformation
    lon, lat, h = transformer.transform(X, Y, Z)

    # Create separate output DataFrames
    lat_df = pd.DataFrame(lat, columns=['latitude'])
    lon_df = pd.DataFrame(lon, columns=['longitude'])
    h_df = pd.DataFrame(h, columns=['height'])

    return lat_df, lon_df, h_df

def computing_satellite_data(param):
    satellite_data = pd.DataFrame()
    satellite_data['time'] = list(range(0, param['epochs'], 1))
    satellite_data['integer_ambiguity'] = np.full(param['epochs'], param['integer_ambiguity'])
    np.random.seed(42) 
    satellite_data['noise'] = np.random.normal(param['clock_offset_mean'], param['clock_offset_std'], param['epochs'])
    satellite_data['clock_offset'] = compute_clock_offset(satellite_data['time'])
    coord_ITRF_list = compute_ITRF_satellite_position(satellite_data['time'])
    ITRF_matrix = np.concatenate(coord_ITRF_list).reshape(-1, 3)
    satellite_data['x_cart'] = ITRF_matrix[:, 0]
    satellite_data['y_cart'] = ITRF_matrix[:, 1]
    satellite_data['z_cart'] = ITRF_matrix[:, 2]
    X_coords, Y_coords, Z_coords = ITRF_matrix.T
    df_ITRF = pd.DataFrame({
        'X': X_coords,
        'Y': Y_coords,
        'Z': Z_coords
    })
    lat_df, lon_df, h_df = itrf_to_geodetic(df_ITRF)

    satellite_data['lat'] = lat_df['latitude']
    satellite_data['long'] = lon_df['longitude']
    satellite_data['height'] = h_df['height']

    return satellite_data, ITRF_matrix

def compute_visibility_df(satellite_df, gs_lat, gs_lon, gs_alt):
    """
    Compute visibility DataFrame for the satellite from a ground station.

    Parameters:
    - satellite_df: DataFrame with satellite data including 'lat', 'long', 'height'
    - gs_lat: Latitude of the ground station in degrees
    - gs_lon: Longitude of the ground station in degrees
    - gs_alt: Altitude of the ground station in meters

    Returns:
    - satellite_df: original DataFrame with a 'visibility' column (True/False) added
    """
    latitude_T = gs_lat
    longitude_T = gs_lon
    height_T = gs_alt

    observer_coords = (latitude_T, longitude_T, height_T)

    latitudes = satellite_df['lat'].values
    longitudes = satellite_df['long'].values
    heights = satellite_df['height'].values

    visibility = []

    for lat, lon, h in zip(latitudes, longitudes, heights):
        sat_coords = (lat, lon, h) 
        visibility.append(is_satellite_visible(sat_coords, observer_coords))
    satellite_df['visibility'] = visibility

    return satellite_df

def compute_observations(df, lambda_val, lat, lon, ionoparams, frequency, f1):
    """
    Compute the observation based on the given frequency.

    Parameters:
    - df: DataFrame with satellite data including 'clock_offset', 'integer_ambiguity', 'noise', 'distance'
    - lambda_val: Wavelength in meters 
    - TODO !!!!!!!!

    Returns:
    - observations: DataFrame with columns 'epoch', 'phase'
    """

    ionospheric_correction = iono_phase_correction(lat, lon, df['azimuth'], df['elevation'], df['time'], ionoparams, frequency, f1)

    observations = pd.DataFrame(columns=['epoch', 'phase'])
    observations['epoch'] = df['time']
    observations['phase'] = df['distance'] * 1000 + df['clock_offset'] * sp.constants.speed_of_light + df['noise'] + df['integer_ambiguity'] * lambda_val + ionospheric_correction

    return observations

def compute_wavelength(fun_freq, f_mult):
    """
    Compute the wavelength based on the frequency multiplier.
    
    Parameters:
    - fun_freq: Fundamental frequency in Hz (e.g., 10.23e6 Hz)
    - f_mult: Frequency multiplier (e.g., 154 for L1, 120 for L2)
    
    Returns:
    - wavelength: Wavelength in meters
    """
    frequency = fun_freq * f_mult
    c = sp.constants.speed_of_light
    wavelength = c / frequency
    return wavelength

def iono_phase_correction(lat, lon, az, el, time, ionoparams, frequency, f1):
    """
    Compute ionospheric phase correction using Klobuchar model for multiple observations.
    
    Parameters
    ----------
    lat : float
        Receiver latitude in degrees
    lon : float
        Receiver longitude in degrees
    az : pandas.Series or array-like
        Satellite azimuth in degrees
    el : pandas.Series or array-like
        Satellite elevation in degrees
    time : pandas.Series or array-like
        Time in seconds from midnight
    ionoparams : list or array
        Ionospheric parameters [alpha0, alpha1, alpha2, alpha3, beta0, beta1, beta2, beta3]
    frequency : float 
        value in Hz
    f1 : float
        reference frequency in Hz (Klobuchar model is defined for L1)

    Returns
    -------
    phase_correction : pandas.Series or array
        Ionospheric phase correction in meters (to be SUBTRACTED from phase measurement)
    
    Notes
    -----
    - The phase correction has OPPOSITE sign compared to pseudorange correction
    - The correction is frequency-dependent
    - For L1: phase_correction = -pseudorange_correction
    - For other frequencies: scaled by (f/f1)^2
    """
    
    # Convert time from seconds since midnight to GPS time of the week
    # Date: 2016-11-28
    # GPS epoch started on January 6, 1980
    from datetime import datetime, timedelta
    
    # GPS epoch
    gps_epoch = datetime(1980, 1, 6)
    
    # Target date: 2016-11-28
    target_date = datetime(2016, 11, 28)
    
    # Calculate days since GPS epoch
    days_since_gps_epoch = (target_date - gps_epoch).days
    
    # Calculate day of week (0 = Sunday, 6 = Saturday)
    day_of_week = days_since_gps_epoch % 7
    
    # Convert to GPS time of the week in seconds
    # GPS time of week = (day_of_week * 86400) + seconds_since_midnight
    gps_time_of_week = (day_of_week * 86400) + time
    
    # Ionospheric parameters
    a0, a1, a2, a3, b0, b1, b2, b3 = ionoparams
    
    # Elevation from 0 to 90 degrees
    el = np.abs(el)
    
    # Conversion to semicircles
    lat_sc = lat / 180
    lon_sc = lon / 180
    az_sc = az / 180
    el_sc = el / 180
    
    # Earth-centered angle (elevation angle)
    psi = (0.0137 / (el_sc + 0.11)) - 0.022
    
    # Geodetic latitude of the ionospheric pierce point
    phi = lat_sc + psi * np.cos(az_sc * np.pi)
    
    # Limit latitude to ±76 degrees (±0.416 semicircles) - vectorized operations
    phi = np.where(phi > 0.416, 0.416, phi)
    phi = np.where(phi < -0.416, -0.416, phi)
    
    # Geodetic longitude of the ionospheric pierce point
    lambda_ = lon_sc + (psi * np.sin(az_sc * np.pi)) / np.cos(phi * np.pi)
    
    # Geomagnetic latitude of the ionospheric pierce point
    phi_m = phi + 0.064 * np.cos((lambda_ - 1.617) * np.pi)

    # Local time at the ionospheric pierce point (seconds)
    # Use GPS time of the week instead of the original time
    t = lambda_ * 43200 + gps_time_of_week
    
    # Ensure time is within [0, 86400) seconds - vectorized operations
    t = np.where(t >= 86400, t - 86400, t)
    t = np.where(t < 0, t + 86400, t)
    
    # Slant factor (obliquity factor)
    F = 1 + 16 * (0.53 - el_sc) ** 3
    
    # Amplitude of the cosine curve (seconds)
    A = a0 + a1 * phi_m + a2 * phi_m**2 + a3 * phi_m**3
    A = np.where(A < 0, 0, A)
    
    # Period of the cosine curve (seconds)
    P = b0 + b1 * phi_m + b2 * phi_m**2 + b3 * phi_m**3
    P = np.where(P < 72000, 72000, P)
    
    # Phase of the cosine curve (radians)
    X = (2 * np.pi * (t - 50400)) / P
    
    # Ionospheric time delay (seconds) for L1 - vectorized operations
    T_iono = np.where(np.abs(X) < 1.57, 
                      F * (5e-9 + A * (1 - X**2/2 + X**4/24)),
                      F * 5e-9)
    
    # Convert to distance (pseudorange correction in meters)
    pseudorange_correction = sp.constants.speed_of_light * T_iono
    
    # Compute phase correction (opposite sign, frequency dependent)
    # Phase advancement = -pseudorange delay * (f/f1)^2
    frequency_factor = (frequency / f1) ** 2
    phase_correction = -pseudorange_correction * frequency_factor
    
    return phase_correction

def cycle_slip_generator(frequency, number, epochs):
    '''
    Compute when and how long will the cycle slip be

    Input: 
    - Frequency: L1, L2 GNSS frequency
    - Number: Number of cycle slips   
    - Epochs: Time 

    Return: List of (start_epoch, slip_magnitude) tuples 
    '''

    if frequency.upper() == "L1" :
        wavelength = compute_wavelength(10.23e6, 154)
    elif frequency.upper() == "L2":
        wavelength = compute_wavelength(10.23e6, 120)

    number = 1 # To test 

    # Generate random epochs where the cycle slip starts
    slip_start = np.sort(np.random.uniform(0, epochs, number))

    # Generate random magnitude for the event
    slip_cycles = np.random.randint(1, 1000, number)

    # Convert to phase offset in meters
    slip_offsets = slip_cycles * wavelength

    # Return as list of (start_time, magnitude) tuples for easy application
    cycle_slips = [(slip_start[i], slip_offsets[i]) for i in range(number)]
    
    return cycle_slips

