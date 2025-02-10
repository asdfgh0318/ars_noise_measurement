from dataclasses import dataclass


CRLF = '\r\n'
COL_SEPARATOR = '\t'
FFT_TOP_FREQ = 21996.1

@dataclass
class NorsonicReportData:
    profile: list[dict[str, str]]
    glob_funcs: dict[str, str]
    glob_fft: dict[float, float]


def parse_report_table(table: str):
    _, head_cols, *rows = table.split(CRLF)
    cols = head_cols.split(COL_SEPARATOR)

    def parse_row(row: str):
        vals = row.split(COL_SEPARATOR)
        if len(vals) != len(cols):
            print(vals)
            print(cols)
            print(len(cols))
            print(len(vals))
            raise ValueError('NorParser: Invalid row read')
        return {cols[i]: vals[i] for i in range(len(cols))}

    return [parse_row(r) for r in rows if len(r) > 0]

def parse_glob(table: str) -> tuple[dict[str, str], dict[float, float]]:
    _, head_cols, row = table.split(CRLF)
    cols = head_cols.split(COL_SEPARATOR) [:-1]
    vals = row.split(COL_SEPARATOR)
    functions = {cols[i]: vals[i] for i in range(len(cols))}

    fft_vals = list(map(float, vals[len(cols):]))
    fft_points = len(fft_vals)
    fft_freqs = [FFT_TOP_FREQ * (i+1)/(fft_points + 1) for i in range(fft_points)]
    fft = {freq: val for freq, val in zip(fft_freqs, fft_vals)}

    return functions, fft


def parse_report(report: bytes):
    *header, glob, prof = report.decode().split(2*CRLF)
    t_prof = parse_report_table(prof)
    t_glob, fft = parse_glob(glob)
    # t_glob = parse_report_table(glob)
    # return t_glob, t_prof
    return NorsonicReportData(t_prof, t_glob, fft)
    # return t_prof


if __name__ == '__main__':
    FNAME = '/home/Downloads/VIP 688 2025-02-05 13-40-36.txt'
    CRLF = '\n'
    with open(FNAME, 'rb') as f:
        rb = f.read()
        global ret
        ret = parse_report(rb)

