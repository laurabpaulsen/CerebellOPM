import mne
import matplotlib.pyplot as plt

from config import EEG_sensors, cap_ch_names

def plot_eeg_sensor_positions():
    info = mne.create_info(sfreq = 1, ch_names = cap_ch_names)
    info.set_channel_types({name: "eeg" for name in cap_ch_names})

    info.set_montage("easycap-M1")

    info.plot_sensors(show_names = EEG_sensors)

    plt.savefig("EEG-sensor-positions.png")

def plot_depth_measurement_opm():
    pass

if __name__ in "__main__":
    plot_eeg_sensor_positions()
    plot_depth_measurement_opm

