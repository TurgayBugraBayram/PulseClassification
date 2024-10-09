import numpy as np
import pywt

def cont_wavelet_trans(signal, dt, scales, wname):
    time = np.arange(dt, len(signal) * dt + dt, dt)

    # cwt_coefs= pywt.dwt(signal, 'db4')
    # cwt_coefs= pywt.dwt(scales, 'db4')
    cwt_coefs, _ = pywt.cwt(signal, scales, wname, dt)

    return cwt_coefs
