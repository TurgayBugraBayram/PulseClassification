def find_Tp(pulse_data):
    Tp = -999
    for j in range(5):
        buff = pulse_data[j]
        if buff['is_pulse'] == 1:
            Tp = buff['Tp']
            return Tp
    return Tp
