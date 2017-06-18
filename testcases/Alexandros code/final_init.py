'''
Created by Alexandros Kazantzidis
Date 03/06/17
'''


from math import *
import numpy as np
import pandas as pd
pd.set_option('display.width', 1000)
import matplotlib.pylab as plt
import matplotlib as mpl

import orbit_fit
import kep_state
import rkf78
import golay_filter
import read_data
import tripple_moving_average

def mainf(datafile, window):
    '''This function takes as an input a .csv data file with satellite positional data in the format of
    (Time, x, y, z) and uses them alone with Savitzky - Golay filtering that needs a window input, Lambert's 
    solution for the preliminary orbit determination problem and Kalman filters to produce a final keplerian elements 
    set of the orbit that these inital data set produce

    Args:
        datafile(csv file) =  format (Time, x, y, z)
        window(int) = number for the window of the Savintzky - Golay filter
                      its better to select it as the len(data)/3 and it needs to be an odd number

    Returns:
        kep_final(numpy array) = a 6x1 numpy array containing the final estimated keplerian elements of the orbit 
        format (a (km), e (float number), i (degrees), ω (degrees), Ω (degrees), v (degress))
    '''

    my_data = read_data.load_data(datafile)
    my_data = tripple_moving_average.generate_filtered_data(my_data, 3)
    my_data_filt = golay_filter.golay(my_data, window)

    kep = orbit_fit.create_kep(my_data_filt)
    kep_final = orbit_fit.kalman(kep)
    kep_final = np.transpose(kep_final)

    state = kep_state.Kep_state(kep_final)

    ## setting some inputs for the Runge Kutta numerical integration to run and find different state vectors for various
    ## time intervals
    keep_state = np.zeros((6, 20))
    ti = 0.0
    tf = 100.0
    t_hold = np.zeros((20, 1))
    x = state
    h = 1.0
    tetol = 1e-04
    for i in range(0, 20):

        keep_state[:, i] = np.ravel(rkf78.rkf78(6, ti, tf, h, tetol, x))
        t_hold[i, 0] = tf
        tf = tf + 100


    positions = keep_state[0:3, :]

    print("Diplaying the differences between the initial data set and the data set filtered with Savitzky - "
          "Golay filter")
    ## Find the differences between the initial - after golay filter data

    dif = np.zeros((len(my_data), 4))
    dif[:, 1:4] = my_data[:, 1:4] - my_data_filt[:, 1:4]
    dif[:, 0] = my_data[:, 0]
    df = pd.DataFrame(dif)
    df = df.rename(columns={0: 'Time (sec)', 1: 'x (km)', 2: 'y (km)', 3: 'z (km)'})
    print(df)

    print(' ')

    print(' ')
    print('Displaying the keplerian elements final computation given by the use of the filtered data set, Lamberts '
          'solution and Kalman filtering')

    ## Give the keplerian elements after the lamberts - kalman solution

    df2 = pd.DataFrame(kep_final)
    df2 = df2.rename(index={0: 'Semi major axis (km)', 1: 'Eccentricity (float number)', 2: 'Inclination (degrees)',
                            3: 'Argument of perigee (degrees)', 4: 'Right ascension of the ascending node (degrees)',
                            5: 'True anomally (degrees)'})
    df2 = df2.rename(columns={0: 'Final Results'})
    print(df2)


    # Plot the final graph

    mpl.rcParams['legend.fontsize'] = 10
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    ax.plot(my_data[:, 1], my_data[:, 2], my_data[:, 3], ".", label='Initial data ')
    ax.plot(my_data_filt[:, 1], my_data_filt[:, 2], my_data_filt[:, 3], "k", linestyle='-', label='Filtered data with Savitzky - Golay filter')
    ax.plot(positions[0, :], positions[1, :], positions[2, :], "r-", label='Orbit after Lamberts - Kalman')
    ax.legend()
    ax.can_zoom()
    ax.set_xlabel('x (km)')
    ax.set_ylabel('y (km)')
    ax.set_zlabel('z (km)')
    plt.show()

    ## Compute and plot the absolute value of position and velocity vector of the final orbit

    r = np.zeros((20, 1))
    v = np.zeros((20, 1))
    for i in range(0, 20):
        r[i, 0] = (keep_state[0, i] ** 2 + keep_state[1, i] ** 2 + keep_state[2, i] ** 2) ** (0.5)
        v[i, 0] = (keep_state[3, i] ** 2 + keep_state[4, i] ** 2 + keep_state[5, i] ** 2) ** (0.5)


    fig, ax1 = plt.subplots()

    ax1.plot(t_hold, r, "b", label='Absolute value of position vector r')
    ax1.legend(bbox_to_anchor=(1, 1.15))
    ax1.set_xlabel('Time (sec)')
    ax1.set_ylabel('|r| (km)')
    ax1.tick_params('y', colors='b')

    ax2 = ax1.twinx()
    ax2.plot(t_hold, v, "r", label='Absolute value of velocity vector v')
    ax2.legend(bbox_to_anchor=(1, 1.05))
    ax2.set_ylabel('|v| (km/s)', color='r')
    ax2.tick_params('y', colors='r')

    plt.show()

    return kep_final


if __name__ == "__main__":

    kep = mainf('orbit.csv', 61)
