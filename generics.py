import csv
from collections import deque


def write_to_csv(filepath: str, data: list):
    with open(filepath, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)


def get_last_n_rows_csv(file_path, n):
    """
    Retrieves the last 'n' rows from a CSV file.

    Args:
        file_path (str): The path to the CSV file.
        n (int): The number of rows to retrieve from the end.

    Returns:
        list: A list of lists, where each inner list represents a row
              from the last 'n' rows of the CSV file.
    """
    with open(file_path, 'r', newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        last_rows = deque(csv_reader, maxlen=n)  # keep only last n rows
    return list(last_rows)
