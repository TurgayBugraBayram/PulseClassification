import os


def parse_at2(filename):
    if not os.path.exists(filename):
        return -1, -1, -1, -1

    with open(filename, 'r') as file_in:
        for _ in range(3):
            next(file_in)

        line = next(file_in)
        parts = line.split(',')
        NPTS = int(parts[0].split('=')[1].strip())
        print(NPTS)
        record_dt = float(parts[1].split('=')[1].split()[0].strip())

        Acc = []

        for line in file_in:
            Acc.extend([float(x) for x in line.split()])

    return Acc, record_dt, NPTS, 0
