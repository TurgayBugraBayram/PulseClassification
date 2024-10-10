def parseASC(filename):
    try:
        with open(filename, 'r') as file_in:
            lines = file_in.readlines()

            #1-based index
            dt_line = lines[28].strip()
            dt = float(dt_line.split(":")[1].strip())

            #row 30
            npts_line = lines[29].strip()
            NPTS = int(npts_line.split(":")[1].strip())

            #row 65
            Acc = []
            for line in lines[64:]:
                values = line.strip().split()
                Acc.extend([float(val) / 981 for val in values])  # çevirme

        errCode = 0
    except FileNotFoundError:
        Acc, dt, NPTS, errCode = -1, -1, -1, -1
    except ValueError as e:
        print(f"Error parsing the file: {e}")
        Acc, dt, NPTS, errCode = -1, -1, -1, -1

    return Acc, dt, NPTS, errCode


#test
if __name__ == "__main__":
    print(parseASC("asc/20230206011732_3116_mp_Acc_E.asc"))
    print(parseASC("asc/20230206011732_3116_mp_Acc_N.asc"))