import numpy as np
from parseAT2 import parse_at2
from classification_algo import classification_algo
from find_Ipulse import find_Ipulse
from find_Tp import find_Tp
from make_plot import make_plot


def main():
    filename1 = 'example_1.AT2'
    filename2 = 'example_2.AT2'

    print('Starting computations')

    A1, dt, NPTS, errCode = parse_at2(filename1)
    signal1 = np.cumsum(A1) * dt * 981

    A2, dt2, NPTS2, errCode = parse_at2(filename2)
    signal2 = np.cumsum(A2) * dt2 * 981

    if errCode == -1:
        print('File not found')
        return

    if abs(NPTS - NPTS2) > 20:
        print('NPTS1 ~= NPTS2')
        return

    if NPTS != NPTS2:
        if NPTS < NPTS2:
            A2 = A2[:len(A1)]
            signal2 = signal2[:len(signal1)]
        else:
            A1 = A1[:len(A2)]
            signal1 = signal1[:len(signal2)]

    if dt != dt2:
        print('dt1 ~= dt2')
        return

    if len(A1) == len(A2):
        pulse_data, rotAngles, selectedCol, selectedRow = classification_algo(signal1, signal2, dt)

        np.savez('classification_result.npz', pulse_data=pulse_data, rotAngles=rotAngles, selectedCol=selectedCol,
                 selectedRow=selectedRow)


    else:
        print('Length of A1 and A2 differ, even though NPTS are same')
        return

    Ipulse = find_Ipulse(pulse_data)
    Tp = find_Tp(pulse_data)
    make_plot(pulse_data)


if __name__ == "__main__":
    main()
