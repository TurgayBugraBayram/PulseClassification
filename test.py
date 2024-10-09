import numpy as np
import matplotlib.pyplot as plt
import pywt
from scipy.integrate import cumulative_trapezoid


def parseAT2(filename):
    try:
        with open(filename, 'r') as file_in:
            for _ in range(3):
                file_in.readline()

            header_line = file_in.readline().strip()
            header_parts = header_line.split(',')

            NPTS_str = header_parts[0].split('=')[1].strip()
            record_dt_str = header_parts[1].split('=')[1].strip().split()[0]

            NPTS = int(NPTS_str)
            record_dt = float(record_dt_str)

            Acc = []
            for line in file_in:
                values = line.strip().split()
                Acc.extend([float(val) for val in values])

        errCode = 0
    except FileNotFoundError:
        Acc, record_dt, NPTS, errCode = -1, -1, -1, -1
    except ValueError as e:
        print(f"Error parsing the file: {e}")
        Acc, record_dt, NPTS, errCode = -1, -1, -1, -1

    return Acc, record_dt, NPTS, errCode


def make_plot(pulseData):
    for j in range(5):
        buff = pulseData[j]
        if buff['is_pulse']:
            signal = buff['signal']
            pulse_th = buff['pulse_th']
            resid_th = buff['resid_th']
            record_dt = buff['dt']

            np_points = len(signal)
            time = np.arange(record_dt, record_dt * np_points + record_dt, record_dt)

            fig, axs = plt.subplots(3, 1, sharex=True, figsize=(10, 8))

            axs[0].plot(time, signal, '-k')
            axs[0].legend(['Original ground motion'])
            yl = [-max(abs(axs[0].get_ylim())), max(abs(axs[0].get_ylim()))]
            axs[0].set_ylim(yl)

            axs[1].plot(time, pulse_th, '-r')
            axs[1].legend(['Extracted pulse'])
            axs[1].set_ylabel('Velocity [cm/s]')
            axs[1].set_ylim(yl)

            axs[2].plot(time, resid_th, '-k')
            axs[2].legend(['Residual ground motion'])
            axs[2].set_xlabel('Time [s]')
            axs[2].set_ylim(yl)

            plt.show()
            break


def find_Tp(pulseData):
    for j in range(5):
        buff = pulseData[j]
        if buff['is_pulse']:
            return buff['Tp']
    return -999


def find_Ipulse(pulseData):
    for j in range(5):
        buff = pulseData[j]
        if buff['is_pulse']:
            return 1
    return 0


def cont_wavelet_trans(signal, dt, scales, wname):
    try:
        coefs, _ = pywt.cwt(signal, scales, wname)
    except ValueError as e:
        print(f"Wavelet error: {e}")
        return None
    return coefs


def analyze_record(signal, dt, col, row, scales, wname):
    num_coefs = 10
    pulse_scale = scales[row]
    cwt_coefs = cont_wavelet_trans(signal, dt, scales[max(1, row - 1):min(len(scales), row + 1)], wname)
    z = np.abs(cwt_coefs[:, col])
    row = np.argmax(z)

    psi, xval = pywt.Wavelet(wname).wavefun(level=4)
    resid_th = signal.copy()
    pulse_th = np.zeros_like(signal)

    for i in range(num_coefs):
        coef, pulse_scale, col, Tp = fn_extract_one_wavelet(resid_th, dt, pulse_scale, col)
        basis = xval * pulse_scale + (col - np.median(xval * pulse_scale))
        delta = np.diff(basis).mean()
        num_pads = int((max(np.arange(len(signal)) * dt) - max(basis)) / delta)

        final_basis = np.concatenate(
            (np.arange(0, min(basis), delta), basis, np.arange(max(basis), max(basis) + num_pads * delta, delta)))
        y_vals = psi * coef / np.sqrt(pulse_scale)
        final_yvals = np.concatenate((np.zeros(len(np.arange(0, min(basis), delta))), y_vals, np.zeros(num_pads)))

        pulse_th += np.interp(np.arange(len(signal)) * dt, final_basis, final_yvals)
        pulse_th[np.isnan(pulse_th)] = 0
        resid_th = signal - pulse_th

    pulse_data = {
        'dt': dt,
        'num_pts': len(signal),
        'Tp': Tp,
        'wavelet_name': wname,
        'pulse_scale': pulse_scale,
        'rows': col,
        'coefs': coef,
        'PGV': max(np.abs(signal)),
        'PGV_resid': max(np.abs(resid_th)),
        'pulse_th': pulse_th,
        'resid_th': resid_th,
        'is_pulse': False
    }
    return pulse_data


def fn_extract_one_wavelet(signal, dt, pulse_scale, pulse_row):
    wname = 'db4'
    scales = [pulse_scale]
    coefs = cont_wavelet_trans(signal, dt, scales, wname)
    col = np.argmax(np.abs(coefs[0, :]))
    coef = coefs[0, col]
    Tp = 1.0 / pywt.scale2frequency(wname, pulse_scale) * dt
    return coef, pulse_scale, col, Tp


def classification_algo(signal1, signal2, dt):
    wname = 'cmor'
    TpMin, TpMax = 0.25, 15
    numScales = 50
    scales = np.arange(TpMin / 1.4 / dt, TpMax / 1.4 / dt, numScales)

    coefs1 = cont_wavelet_trans(signal1, dt, scales, wname)
    coefs2 = cont_wavelet_trans(signal2, dt, scales, wname)
    maxCoefs = coefs1 ** 2 + coefs2 ** 2

    pulse_datas = []
    rotAngles = []
    selectedCol = []
    selectedRow = []

    for i in range(5):
        maxCoef = np.max(maxCoefs)
        col, row = np.unravel_index(np.argmax(maxCoefs), maxCoefs.shape)
        maxDir = np.arctan(coefs2[row, col] / coefs1[row, col])
        signal = signal1 * np.cos(maxDir) + signal2 * np.sin(maxDir)
        pulse_data = analyze_record(signal, dt, col, row, scales, wname)
        pulse_datas.append(pulse_data)
        rotAngles.append(maxDir)
        selectedCol.append(col)
        selectedRow.append(row)

        blockMin, blockMax = col - 10 / 25 * pulse_data['pulse_scale'], col + 10 / 25 * pulse_data['pulse_scale']
        maxCoefs[:, np.logical_and(np.arange(len(signal1)) > blockMin, np.arange(len(signal1)) < blockMax)] = 0

    return pulse_datas, rotAngles, selectedCol, selectedRow

if __name__ == "__main__":
    filename1 = 'example_1.AT2'
    filename2 = 'example_2.AT2'

    A1, dt, NPTS, errCode = parseAT2(filename1)
    if len(A1) > 0:
        signal1 = cumulative_trapezoid(A1, dx=dt, initial=0) * 981
    else:
        print("Error: A1 is empty or invalid.")
    A2, dt2, NPTS2, errCode2 = parseAT2(filename2)
    signal2 = cumulative_trapezoid(A2, dx=dt2, initial=0) * 981

    if errCode == -1:
        print('File not found')
        exit()

    if abs(NPTS - NPTS2) > 20:
        print('NPTS1 != NPTS2')
        exit()

    if NPTS != NPTS2:
        if NPTS < NPTS2:
            A2 = A2[:len(A1)]
            signal2 = signal2[:len(signal1)]
        else:
            A1 = A1[:len(A2)]
            signal1 = signal1[:len(signal2)]

    if dt != dt2:
        print('dt1 != dt2')
        exit()

    if len(A1) == len(A2):
        pulseData, rotAngles, selectedCol, selectedRow = classification_algo(signal1, signal2, dt)
        Ipulse = find_Ipulse(pulseData)
        Tp = find_Tp(pulseData)
        make_plot(pulseData)
    else:
        print('length(A1) != length(A2), even though NPTS are same')
