import matplotlib.pyplot as plt
import numpy as np


def make_plot(pulse_data):
    for j in range(5):
        buff = pulse_data[j]
        if buff['is_pulse'] == 1:
            signal = buff['signal']
            pulse_th = buff['pulse_th']
            resid_th = buff['resid_th']
            record_dt = buff['dt']

            np_len = len(signal)
            time = np.arange(record_dt, record_dt * (np_len + 1), record_dt)

            fig, axs = plt.subplots(3, 1, figsize=(8, 8))

            axs[0].plot(time, signal, '-k')
            axs[0].legend(['Original ground motion'])
            axs[0].set_xticklabels([])
            yl = [-max(abs(axs[0].get_ylim())), max(abs(axs[0].get_ylim()))]
            axs[0].set_ylim(yl)

            axs[1].plot(time, pulse_th, '-r')
            axs[1].legend(['Extracted pulse'])
            axs[1].set_ylabel('Velocity [cm/s]')
            axs[1].set_xticklabels([])
            axs[1].set_ylim(yl)

            axs[2].plot(time, resid_th, '-k')
            axs[2].legend(['Residual ground motion'])
            axs[2].set_xlabel('Time [s]')
            axs[2].set_ylim(yl)

            plt.tight_layout()
            plt.show()
            break
