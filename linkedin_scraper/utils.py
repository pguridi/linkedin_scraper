import csv


def get_rows_from_csv(fname):
    for row in read_csv(fname):
        yield row


def read_csv(fname):
    with open(fname) as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            yield row[0]


def write_csv(fname, header, data):
    with open(fname, "w") as f:
        writer = csv.writer(f)

        writer.writerow(header)
        writer.writerows(data)
