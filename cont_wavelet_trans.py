import numpy as np
import pywt


def cont_wavelet_trans(signal, dt, scales, wname):
    time = np.arange(dt, len(signal) * dt + dt, dt)

    cwt_coefs, _ = pywt.cwt(signal, scales, pywt.Wavelet("db4"), dt)

    return cwt_coefs
