import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from orbitdeterminator.doppler.utils.constants import *
from orbitdeterminator.doppler.utils.utils import *

from mpl_toolkits.mplot3d import Axes3D

def plot_sphere(ax, d:np.ndarray, n:np.ndarray) -> None:
    """ Plots a sphere on a given axes object.

    Args:
        ax (matplotlib.axes): axes to plot on
        d (float): sphere diameter
        n (float): grid resolution
    """
    
    u = np.linspace(0, np.pi, n)
    v = np.linspace(0, 2 * np.pi, n)

    x = d * np.outer(np.sin(u), np.sin(v))
    y = d * np.outer(np.sin(u), np.cos(v))
    z = d * np.outer(np.cos(u), np.ones_like(v))

    ax.plot_wireframe(x, y, z, alpha=0.2, linewidth=1, color='gray')

def plot_earth(ax, d:np.ndarray, filename:str, angle=0):
    """ Plots Earth.
        Source: https://stackoverflow.com/questions/53074908/map-an-image-onto-a-sphere-and-plot-3d-trajectories
    """
    img = plt.imread(filename)

    # define a grid matching the map size, subsample along with pixels
    u = np.linspace(0, np.pi, img.shape[0])
    v = np.linspace(0+angle, 2*np.pi+angle, img.shape[1])

    count = 180 # keep 180 points along theta and phi
    u_idx = np.linspace(0, img.shape[0] - 1, count).round().astype(int)
    v_idx = np.linspace(0, img.shape[1] - 1, count).round().astype(int)
    u, v = u[u_idx], v[v_idx]
    img = img[np.ix_(u_idx, v_idx)]

    u,v = np.meshgrid(u, v)

    # sphere
    x = d * np.sin(u) * np.cos(v)
    y = d * np.sin(u) * np.sin(v)
    z = d * np.cos(u)

    # create 3d Axes
    ax.plot_surface(x.T, y.T, z.T, facecolors=img/255, cstride=1, rstride=1) # we've already pruned ourselves

    # make the plot more spherical
    #ax.axis('scaled')

def plot_example_3d(x_sat_orbdyn_stm:np.ndarray, x_obs_multiple:np.ndarray, title=None):
    """ Plots a sphere, site position and satellite trajectory.

    Args:
        x_sat_orbdyn_stm (np.array): satellite trajectory array.
        x_obs_multiple (np.array): observer positions.
    """

    font = {'size': 16}
    matplotlib.rc('font', **font)

    fig = plt.figure(figsize=(14,14))
    ax1 = fig.add_subplot(111, projection='3d')

    # Dimension fix
    if len(x_obs_multiple.shape) == 2:
        x_obs_multiple = np.expand_dims(x_obs_multiple)
    
    #plot_sphere(ax1, d=R_EQ, n=40)

    s = []      # Scatter instances
    l = []      # Legends

    for i in range(x_obs_multiple.shape[2]):
        # TODO: Check first argument
        ss = ax1.scatter(x_obs_multiple[0,:,i], x_obs_multiple[1,:,i], x_obs_multiple[2,:,i], marker='.', s=4)
        st = ax1.scatter(x_obs_multiple[0,0,i], x_obs_multiple[1,0,i], x_obs_multiple[2,0,i], c=ss.get_facecolors())
        s.append(st)
        l.append(f"Observer {i}")

    ax1.set_xlabel("x ECI (m)", fontsize=16, labelpad=10)
    ax1.set_ylabel("y ECI (m)", fontsize=16, labelpad=10)
    ax1.set_zlabel("z ECI (m)", fontsize=16, labelpad=10)

    s4 = ax1.scatter(x_sat_orbdyn_stm[0,0], x_sat_orbdyn_stm[1,0], x_sat_orbdyn_stm[2,0], c='k')
    ax1.scatter(x_sat_orbdyn_stm[0,:], x_sat_orbdyn_stm[1,:], x_sat_orbdyn_stm[2,:], marker='.', c='k', s=1)
    s.append(s4)
    l.append('Satellite')

    if title is not None:
        ax1.title.set_text('Scenario example')
        
    ax1.legend((s), (l), loc=2, bbox_to_anchor=(0.15,0.9))

    return fig

def plot_range_range_rate(x_sat_orbdyn_stm:np.ndarray, x_obs_multiple:np.ndarray, t_sec: np.array):
    """ Plots range and range relative to the station

    Args:
        x_sat_orbdyn_stm (np.ndarray): satellite trajectory array.
        x_obs_multiple (np.ndarray): observer positions.
        t_sec (np.ndarray): array of timesteps.
    """

    if len(x_obs_multiple.shape) == 2:
        x_obs_multiple = np.expand_dims(x_obs_multiple)

    fig = plt.figure(figsize=(14,14))

    n_obs = x_obs_multiple.shape[2]

    for i in range(n_obs):
        r, rr = range_range_rate(x_sat_orbdyn_stm, x_obs_multiple[:,:,i])

        ax1 = fig.add_subplot(n_obs, 2, i*2+1)
        ax1.plot(t_sec, r)
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Range (m)')
        ax1.grid(':')
        ax1.title.set_text('Station 1 - Range')

        ax2 = fig.add_subplot(n_obs, 2, i*2+2)
        ax2.plot(t_sec, rr)
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Range rate (m/s)')
        ax2.grid(':')
        ax2.title.set_text('Station 1 - Range Rate')

    fig.subplots_adjust(hspace=0.3)

    return fig

def plot_pos_vel_norms(x_sat:np.ndarray, t_sec: np.array):
    """ Plots range and range relative to the station

    Args:
        x_sat_orbdyn_stm (np.ndarray): satellite trajectory array.
        x_obs_multiple (np.ndarray): observer positions.
        t_sec (np.ndarray): array of timesteps.
    """

    r = np.linalg.norm(x_sat[0:3,], axis=0)     # Norm of the position
    v = np.linalg.norm(x_sat[3:6,], axis=0)     # Norm of the velocity

    fig = plt.figure(figsize=(14,7))

    ax1 = fig.add_subplot(1, 2, 1)
    ax1.plot(t_sec, r)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Satellite position norm (m)')
    ax1.grid(':')
    ax1.title.set_text('Position Norm')

    ax2 = fig.add_subplot(1, 2, 2)
    ax2.plot(t_sec, v)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Satellite velocity norm (m/s)')
    ax2.grid(':')
    ax2.title.set_text('Velocity Norm')

    fig.subplots_adjust(hspace=0.25)

    return fig

def plot_batch_results(
        x_sat_orbdyn_stm:np.ndarray, 
        x_0r:np.ndarray, 
        x_br:np.ndarray, 
        x_berr:np.ndarray
    ):
    """ Plot relevant converged batch results.

    Args:
        x_sat_orbdyn_stm  (np.ndarray): True satellite position.
        x_0r (np.ndarray): array of random initial sampled positions.
        x_br (np.ndarray): array of batch estimates of initial positions.
        x_berr (np.ndarray): array of errors relative to x_0
    Returns:
        fig
    """

    fig = plt.figure(figsize=(14,14))
    ax1 = fig.add_subplot(111, projection='3d')

    font = {'size': 16}
    matplotlib.rc('font', **font)

    plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0))

    # Groundtruth
    ax1.scatter(x_sat_orbdyn_stm[0,0], x_sat_orbdyn_stm[1,0], x_sat_orbdyn_stm[2,0], s=10, marker='x', c = 'r')

    x_berr_norm = np.linalg.norm(x_berr, axis=0)
    norm_mask = x_berr_norm < 5000

    traj = ax1.plot(x_sat_orbdyn_stm[0,:4], x_sat_orbdyn_stm[1,:4], x_sat_orbdyn_stm[2,:4], c='k')
    traj_proxy = ax1.scatter(x_sat_orbdyn_stm[0,0], x_sat_orbdyn_stm[1,0], x_sat_orbdyn_stm[2,0], c='k', s=10)

    # Batch results
    for i in range(x_0r.shape[1]):
        if x_berr_norm[i] < 100000:
            s1 = ax1.scatter(x_0r[0, i], x_0r[1, i], x_0r[2, i], c='b', s=40, marker='x')
            s2 = ax1.scatter(x_br[0, i], x_br[1, i], x_br[2, i], c='r', s=20)

    ax1.set_xlabel("x ECI (m)", fontsize=16, labelpad=15)
    ax1.set_ylabel("y ECI (m)", fontsize=16, labelpad=15)
    ax1.set_zlabel("z ECI (m)", fontsize=16, labelpad=15)

    s1_proxy = ax1.scatter(x_0r[0, 0], x_0r[1, 0], x_0r[2, 0], c='b', s=40, marker='x')
    s2_proxy = ax1.scatter(x_br[0, 1], x_br[1, 1], x_br[2, 1], c='r', s=20)

    ax1.legend((traj_proxy, s1_proxy, s2_proxy), 
        ('Groundtruth trajectory', 'Pre-batch positions', 'Post-batch positions'),
        loc=2, bbox_to_anchor=(0.15,0.9))

    return fig

def plot_tdoa(tdoa:np.ndarray, tof:np.ndarray, t_sec:np.ndarray, title=None):
    """ Plot TDoA measurements.

    Args:
        tdoa (np.ndarray): time differential of arrival array (n_obs, n).
        tof (np.ndarray): time of flight array (n_obs, n).
        t_sec (np.ndarray): time array, seconds (n,).
    Returns:
        fig ():
    """
    fig = plt.figure(figsize=(14,7))

    font = {'size': 16}
    matplotlib.rc('font', **font)

    if title is not None:
        fig.suptitle(title)

    # Reference station time of flight
    ax = fig.add_subplot(2, 2, 1)
    
    ax.plot(t_sec, tof[0,:])
    ax.set_xlabel('Time (s)', fontsize=16, labelpad=10)
    ax.set_ylabel('Time of flight (s)', fontsize=16, labelpad=10)
    ax.grid(':')
    ax.title.set_text(f"Station 0 ToF")
    plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0))

    # Time differential of arrival for the rest of three stations
    for i in range(tdoa.shape[0]-1):
        ax = fig.add_subplot(2, 2, i+2)
        ax.plot(t_sec, tdoa[i+1,:])
        ax.set_xlabel('Time (s)', fontsize=16, labelpad=10)
        ax.set_ylabel('Time differential (s)', fontsize=16, labelpad=10)
        ax.grid(':')
        ax.title.set_text(f"Station {i+1}-0 TDoA")
        plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0))

    fig.subplots_adjust(hspace=0.5)

    return fig

def plot_tdoa_results(p_sat:np.ndarray, x_obs:np.ndarray, x_sat:np.ndarray=None, angle=None):
    """ Plot results of TDoA multilateration.

    Args:
        p_sat (np.ndarray): multilaterated satellite position (3, n).
        x_obs (np.ndarray): observer positions (6, n, n_obs).
        x_sat (np.ndarray): groundtruth satellite position (6, n).
    Returns:
        fig ():
    """ 
    x_obs_mean = np.mean(x_obs,axis=2)

    font = {'size': 16}
    matplotlib.rc('font', **font)

    txtp, txtn = 1.002, 0.998    # Temporary variables - text location

    fig = plt.figure(figsize=(10,10))

    ax = fig.add_subplot(111, projection='3d')
    ax.title.set_text("TDoA Example")
    #plot_sphere(ax, d=R_EQ, n=40)

    # Observer
    obs = ax.scatter(x_obs[0,0,:], x_obs[1,0,:], x_obs[2,0,:], c='b')
    for j in range(x_obs.shape[2]):
        ax.text(x_obs[0,0,j]*txtp, x_obs[1,0,j]*txtp, x_obs[2,0,j]*txtp, f"Obs_1 {j}",c='k',fontsize=10)
        ax.scatter(x_obs[0,:,:], x_obs[1,:,:], x_obs[2,:,:], marker='.', s=0.5, c='b')

    # # Mean observer position
    # ax.scatter(x_obs_mean[0, :], x_obs_mean[1, :], x_obs_mean[2, :], marker='.', s=1, alpha=0.1)
    # ax.text(x_obs_mean[0, 0]*txtn, x_obs_mean[1, 0]*txtn, x_obs_mean[2, 0]*txtn, f"Observer (mean)")

    if x_sat is not None:
        # Satellite
        sat = ax.scatter(x_sat[0,:], x_sat[1,:], x_sat[2,:])
        sat_0 = ax.scatter(x_sat[0,0], x_sat[1,0], x_sat[2,0], marker='x')
        ax.text(x_sat[0,0]*txtp, x_sat[1,0]*txtp, x_sat[2,0]*txtp, "Satellite")

    # Result trajectory
    ax.scatter(p_sat[0,:], p_sat[1,:], p_sat[2,:],alpha=0.4,s=0.5,c='k')
    res = ax.scatter(p_sat[0,0], p_sat[1,0], p_sat[2,0],c='k')

    o = ax.scatter(0,0,0,c='teal')

    # Temp legend workaround
    if x_sat is not None:
        ax.legend([res, sat, sat_0, obs, o],["Result Trajectory", "Groundtruth", "Start", "Observers", "Origin"], loc=2, bbox_to_anchor=(0.15,0.9))
    else:
        ax.legend([res, obs, o],["Result Trajectory", "Observers", "Origin"], loc=2, bbox_to_anchor=(0.15,0.9))

    ax.ticklabel_format(axis="x", style="sci", scilimits=(0,0))
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
    ax.ticklabel_format(axis="z", style="sci", scilimits=(0,0))

    ax.set_xlabel("x ECI (m)", fontsize=16, labelpad=15)
    ax.set_ylabel("y ECI (m)", fontsize=16, labelpad=15)
    ax.set_zlabel("z ECI (m)", fontsize=16, labelpad=15)

    if angle is not None:
        ax.view_init(angle[0], angle[1])

    return fig

def plot_tdoa_errors(p_sat, x_sat, title=None):
    """ Plots TDoA multilateration errors compared to groundtruth trajectory.

    Args:
        p_sat (np.ndarray): multilaterated satellite position (3, n).
        x_sat (np.ndarray): groundtruth satellite position (6, n).
    Returns:
        fig ():
    """
    tdoa_error = x_sat[0:3,:] - p_sat[0:3,:]

    fig = plt.figure(figsize=(14,7))

    plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0))

    font = {'size': 16}
    matplotlib.rc('font', **font)

    ax = fig.add_subplot(111)
    ax.grid(':')

    if title is not None:
        ax.title.set_text(title)

    xx = ax.plot(tdoa_error[0,:], linewidth=1)
    yy = ax.plot(tdoa_error[1,:], linewidth=1)
    zz = ax.plot(tdoa_error[2,:], linewidth=1)

    ax.set_xlabel("Time (seconds)", fontsize=16, labelpad=10)
    ax.set_ylabel("Error (m)", fontsize=16, labelpad=10)

    ax.legend(["x","y","z"],loc=0)

    return fig

def plot_tdoa_hg_errors(x_sat, t_sec, x_sat_hg, w):
    """ Plots TDoA multilateration errors compared to groundtruth trajectory.

    Args:
        x_sat (np.ndarray): groundtruth satellite state vector (6, n).
        t_sec (np.ndarray): time array (n,).
        x_sat_hg (np.ndarray): estimated satellite state vector (TDoA+Herrick-Gibbs).
        w (np.ndarray): estimated window size.
    Returns:
        fig ():
    """

    t_sat_hg = t_sec[w:-w]
    diff = x_sat[:,w:-w] - x_sat_hg

    fig = plt.figure(figsize=(14,7))

    ax_1 = fig.add_subplot(1,2,1)
    xx = ax_1.plot(t_sat_hg, diff[0,:], linewidth=1)
    yy = ax_1.plot(t_sat_hg, diff[1,:], linewidth=1)
    zz = ax_1.plot(t_sat_hg, diff[2,:], linewidth=1)

    ax_1.grid(':')
    ax_1.legend(["x","y","z"],loc=0)
    ax_1.set_xlabel("Time (seconds)")
    ax_1.set_ylabel("Error (m)")
    ax_1.title.set_text("Position Error, TDoA + Herrick-Gibbs")

    ax_2 = fig.add_subplot(1,2,2)
    v_xx = ax_2.plot(t_sat_hg, diff[3,:], linewidth=1)
    v_yy = ax_2.plot(t_sat_hg, diff[4,:], linewidth=1)
    v_zz = ax_2.plot(t_sat_hg, diff[5,:], linewidth=1)

    ax_2.grid(':')
    ax_2.legend(["x","y","z"], loc=0)
    ax_2.set_xlabel("Time (seconds)")
    ax_2.set_ylabel("Error (m/s)")
    ax_2.title.set_text("Velocity Error, TDoA + Herrick-Gibbs")

    return fig

def save_images(x_sat, x_obs, t_sec=None, prefix="", path=""):
    """ Auxiliary function to save the images.

    Args:
        x_sat (np.ndarray): satellite state vectors (6,n).
        x_obs (np.ndarray): observer state vectors (6,n,n_ons).
        t_sec (np.ndarray): time array (n,).
        prefix (str): filename prefix.
        path (str): save path.
    Returns:
        None
    """

    fig_1 = plot_example_3d(x_sat, x_obs)
    fig_1.savefig(os.path.join(path, f"{prefix}_scenario"))

    fig_2 = plot_range_range_rate(x_sat, x_obs, t_sec)
    fig_2.savefig(os.path.join(path, f"{prefix}_range_range_rate"))

def save_images_batch_results(x_sat, x_0r, x_br, x_berr, prefix="", path=""):
    """ Auxiliary function to save the batch result images.

    Args:
        x_sat (np.ndarray): satellite state vectors (6,n). 
        x_0r  (np.ndarray): vector of pre-batch initial positions (6,n).
        x_br  (np.ndarray): vector if post-batch estimated initial positions (6,n).
        x_berr(np.ndarray): vector of errors (6,n).
        prefix (str): filename prefix.
        path (str): save path.
    Returns:
        None
    """

    fig_3 = plot_batch_results(x_sat, x_0r, x_br, x_berr)
    fig_3.savefig(os.path.join(path, f"{prefix}_range_range_rate"))