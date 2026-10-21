import concurrent.futures


def paint_quadrant(matrix, start_row, end_row, start_col, end_col, color):
    for i in range(start_row, end_row):
        for j in range(start_col, end_col):
            matrix[i][j] = color


def divide_and_paint(matrix, colors):
    mid_row = len(matrix) // 2
    mid_col = len(matrix[0]) // 2
    rows = len(matrix)
    cols = len(matrix[0])
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(paint_quadrant, matrix, 0, mid_row, 0, mid_col, colors[0]),
            executor.submit(paint_quadrant, matrix, 0, mid_row, mid_col, cols, colors[1]),
            executor.submit(paint_quadrant, matrix, mid_row, rows, 0, mid_col, colors[2]),
            executor.submit(paint_quadrant, matrix, mid_row, rows, mid_col, cols, colors[3]),
        ]
        for future in concurrent.futures.as_completed(futures):
            future.result()
