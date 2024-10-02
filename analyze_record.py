import numpy as np
import pywt


def analyze_record(signal, dt, col, row, scales, wname):
    num_coefs = 10

    num_scales = len(scales)
    scales = scales[max(0, row - 1):min(num_scales, row + 1)]

    cwt_coefs, _ = pywt.cwt(signal, scales, wname)
    z = np.abs(cwt_coefs[:, col])
    row = np.argmax(z)
    pulse_scale = scales[row]

    time = np.arange(dt, len(signal) * dt + dt, dt)
    wtype = pywt.wavelist()  # bir sürü type var sıkıntı olabilir burası
    iter = 4

    if wname == 'db4':
        psi, xval = pywt.Wavelet(wname).wavefun(iter)
    elif wname == 'sym4':
        psi, xval = pywt.Wavelet(wname).wavefun(iter)
    elif wname == 'coif4':
        psi, xval = pywt.Wavelet(wname).wavefun(iter)
    elif wname == 'bior4.4':
        psi, xval = pywt.Wavelet(wname).wavefun(iter)
    elif wname == 'rbio4.4':
        psi, xval = pywt.Wavelet(wname).wavefun(iter)
    else:
        raise ValueError(f"Unsupported wavelet: {wname}")

    resid_th = signal.copy()
    pulse_th = np.zeros_like(signal)

    for i in range(num_coefs):
        coefs, _, col, Tp = fn_extract_one_wavelet(resid_th, dt, pulse_scale, col[0])

        basis = xval * pulse_scale
        basis += (col[0] - np.median(basis))
        basis *= dt
        y_vals = psi * coefs / np.sqrt(pulse_scale)
        delta = basis[1] - basis[0]
        num_pads = np.ceil((max(time) - max(basis)) / delta)

        # hesaplar sorunlu olabilir
        final_basis = np.concatenate([np.arange(0, basis[0] - 1e-5, delta), basis,
                                      np.arange(max(basis) + delta, max(basis) + delta * num_pads, delta)])
        final_yvals = np.concatenate([np.zeros_like(np.arange(0, basis[0] - 1e-5, delta)),
                                      y_vals,
                                      np.zeros(num_pads)])
        pulse_th += np.interp(time, final_basis, final_yvals)
        pulse_th[(np.isnan(pulse_th))] = 0
        resid_th = signal - pulse_th

    signal_E = np.cumsum(signal ** 2) / np.sum(signal ** 2) * 100
    pulse_E = np.cumsum(pulse_th ** 2) / np.sum(pulse_th ** 2) * 100
    index = np.where(pulse_E <= 5)[0]
    lateTime = signal_E[index[-1]]

    late = lateTime >= 17

    pulse_data = {}
    pulse_data['dwt_orig'] = np.sum(np.abs(pywt.wavedec(signal, wname)))
    pulse_data['dwt_resid'] = np.sum(np.abs(pywt.wavedec(resid_th, wname)))
    pulse_data['dwt_squared_orig'] = np.sum(np.abs(pywt.wavedec(signal, wname)) ** 2)
    pulse_data['dwt_squared_resid'] = np.sum(np.abs(pywt.wavedec(resid_th, wname)) ** 2)

    PGV = np.max(np.abs(signal))
    PGV_resid = np.max(np.abs(resid_th))
    pgvRatio = PGV_resid / PGV
    energyRatio = pulse_data['dwt_squared_resid'] / pulse_data['dwt_squared_orig']
    pc = 0.63 * pgvRatio + 0.777 * energyRatio
    P = (pc - 1.208421) / 0.2462717
    V = (PGV - 11.58861) / 18.88015
    pulse_indicator = (-7.817 -
                       0.5679 * P ** 2 -
                       0.1516 * V ** 2 -
                       3.0253 * P -
                       1.7396 * V -
                       2.7156 * P * V)

    is_pulse = (pulse_indicator > 0) and not late

    pulse_data['dt'] = dt
    pulse_data['num_pts'] = len(signal)
    pulse_data['Tp'] = Tp
    pulse_data['wavelet_name'] = wname
    pulse_data['pulse_scale'] = pulse_scale
    pulse_data['rows'] = col
    pulse_data['coefs'] = coefs
    pulse_data['PGV'] = PGV
    pulse_data['PGV_resid'] = PGV_resid
    pulse_data['delta_energy_t'] = delta
    pulse_data['late'] = late
    pulse_data['pulse_indicator'] = pulse_indicator
    pulse_data['is_pulse'] = is_pulse
    pulse_data['signal'] = signal
    pulse_data['pulse_th'] = pulse_th
    pulse_data['resid_th'] = resid_th

    return pulse_data


def fn_extract_one_wavelet(signal, dt, pulse_scale, pulse_row):
    Tp_min = 0.25  #
    Tp_max = 15
    row_range = 10 / 25
    wname = 'db4'

    scales = pulse_scale
    row_indices = range(max(0, pulse_row - np.ceil(scales * row_range)),
                        min(len(signal), pulse_row + np.ceil(scales * row_range)))

    cwt_coefs, _ = pywt.cwt(signal, scales, wname)

    z = np.max(np.abs(cwt_coefs[0, row_indices]))
    row = 1
    col = np.argmax(z == np.abs(cwt_coefs[0, :]))

    coef = cwt_coefs[row, col]

    Tp = 1.0 / pywt.scale2frequency(pulse_scale, wname, dt)  # ????

    return coef, pulse_scale, col, Tp
