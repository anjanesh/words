class SQLIterator:

    """
    row_start : offset - Starting row (First row is normally indexed 0)
    row_count : limit  - Number of Rows to fetch

    count     : Total number of rows using LIMIT
    total     : Total number of rows without using LIMIT

    LIMIT row_start, row_count
    Example : LIMIT 10, 20
    """
    def __init__(self, row_start = 0, row_count = 10):
        self.rows = None
        self.rows_iterator = None

        self.row_start = row_start
        self.row_count = row_count

        self.count = -1
        self.total = -1
        self.row_end = -1 # row_end = row_start + min(row_count, count)
