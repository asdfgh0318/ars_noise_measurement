CRLF = '\r\n'
COL_SEPARATOR = '\t'

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
            raise ValueError('NorPaeser: Invalid row read')
        return {cols[i]: vals[i] for i in range(len(cols))}

    return [parse_row(r) for r in rows if len(r) > 0]

def parse_report(report: bytes):
    *header, glob, prof = report.decode().split(2*CRLF)
    t_prof = parse_report_table(prof)
    # t_glob = parse_report_table(glob)
    # return t_glob, t_prof
    return t_prof

