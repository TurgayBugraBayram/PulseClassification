import os


def parse_at2(filename):
    if not os.path.exists(filename):
        return -1, -1, -1, -1

    with open(filename, 'r') as file_in:
        # Skip first three lines
        for _ in range(3):
            next(file_in)

        # Read NPTS and DT from the fourth line
        line = next(file_in)
        parts = line.split(',')
        NPTS = int(parts[0].split('=')[1].strip())
        record_dt = float(parts[1].split('=')[1].split()[0].strip())

        # Skip the next line
        next(file_in)

        # Read acceleration data
        Acc = []
        for line in file_in:
            Acc.extend([float(x) for x in line.split()])

    return Acc, record_dt, NPTS, 0

