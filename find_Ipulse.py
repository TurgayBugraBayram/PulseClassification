def find_Ipulse(pulseData):
    isPulse = 0
    for j in range(5):
        buff = pulseData[j]
        if buff['is_pulse'] == 1:
            isPulse = 1
    return isPulse
