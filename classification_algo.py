from cont_wavelet_trans import cont_wavelet_trans
import numpy as np
from analyze_record import analyze_record
import pywt

def classification_algo(signal1, signal2, dt):
    pulse_datas = [None] * 5
    rotAngles = [None] * 5
    selectedCol = [None] * 5
    selectedRow = [None] * 5

    wname = "db4"
    # in cwt we can use ['cgau1', 'cgau2', 'cgau3', 'cgau4', 'cgau5', 'cgau6', 'cgau7', 'cgau8', 'cmor', 'fbsp', 'gaus1', 'gaus2', 'gaus3', 'gaus4', 'gaus5', 'gaus6', 'gaus7', 'gaus8', 'mexh', 'morl', 'shan']
    TpMin = 0.25
    TpMax = 15
    numScales = 50
    scaleMin = np.floor(np.floor(TpMin / 1.4 / dt))
    scaleStep = np.ceil(np.ceil((TpMax / 1.4 / dt - scaleMin) / numScales))
    scaleMax = scaleMin + numScales * scaleStep
    scales = np.arange(scaleMin, scaleMax + scaleStep, scaleStep)

    test = pywt.scale2frequency(wname, scales)/dt # module scale2fr fonskiyonu kullanılmış

    coefs1 = np.array(cont_wavelet_trans(signal1, dt, scales, wname))
    coefs2 = np.array(cont_wavelet_trans(signal2, dt, scales, wname))

    maxCoefs = (coefs1 ** 2 + coefs2 ** 2)

    for i in range(5):
        maxCoef = np.max(maxCoefs)
        col = np.where(maxCoefs == maxCoef)
        row = np.where(np.max(maxCoefs, axis=1) == maxCoef)

        maxDir = np.arctan(coefs2[row[0][0], col[0][0]] / coefs1[row[0][0], col[0][0]])
        signal = signal1 * np.cos(maxDir) + signal2 * np.sin(maxDir)

        pulse_data = analyze_record(signal, dt, col[0][0], row[0][0], scales, wname)
        pulseScale = scales[row[0][0]]

        pulse_datas[i] = pulse_data
        rotAngles[i] = maxDir
        selectedCol[i] = col[0][0]
        selectedRow[i] = row[0][0]

        blockMin = col[0][0] - 10 / 25 * pulseScale
        blockMax = col[0][0] + 10 / 25 * pulseScale
        idx = np.where((np.arange(1, len(signal1) + 1) > blockMin) &
                       (np.arange(1, len(signal1) + 1) < blockMax))
        maxCoefs[:, idx] = 0

    return pulse_datas, rotAngles, selectedCol, selectedRow
