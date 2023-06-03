from display_settings import DisplaySettings

def reversing_row_column_indexer(irow: int, icol: int, settings: DisplaySettings) -> int:
    '''
    Converts a row and column index into a neopixel index,
    each row reverses the order of the column indicies.  This is
    because the LED matrix is laid out in line that folds back on itself
    each row, ex:
    9 8 7 6 5
    0 1 2 3 4
    0 1 2 3 4
    :param irow:
    :param icol:
    :return:
    '''
    adjusted_icol = icol if irow % 2 == 0 else (settings.num_neo_cols - 1) - icol
    # print(f'irow: {irow} icol: {icol} adjusted_icol: {adjusted_icol}')
    return (irow * settings.num_neo_cols) + adjusted_icol

def flip_column_order_indexer(irow: int, icol: int, settings: DisplaySettings) -> int:
    '''
    Used for NeoPixel Featherwing
    Flips the column ordering.  Useful when the left side of the display should be the right
    :param irow:
    :param icol:
    :return:
    '''
    adjusted_icol = (settings.num_neo_cols - 1) - icol
    # print(f'irow: {irow} icol: {icol} adjusted_icol: {adjusted_icol}')
    return (irow * settings.num_neo_cols) + adjusted_icol

def standard_indexer(irow: int, icol: int, settings: DisplaySettings) -> int:
    '''
    Flips the column ordering.  Useful when the left side of the display should be the right
    :param irow:
    :param icol:
    :return:
    '''
    # print(f'irow: {irow} icol: {icol} adjusted_icol: {adjusted_icol}')
    return (irow * settings.num_neo_cols) + icol

def rows_are_columns_indexer(irow: int, icol: int, settings: DisplaySettings) -> int:
    '''
    Flips the column ordering.  Useful when the left side of the display should be the right
    :param irow:
    :param icol:
    :return:
    '''
    # print(f'irow: {irow} icol: {icol} adjusted_icol: {adjusted_icol}')
    return (icol * settings.num_neo_rows) + irow

def rows_are_columns_with_alternating_column_order_indexer(irow: int, icol: int, settings: DisplaySettings) -> int:
    '''
    Flips the column ordering.  Useful when the left side of the display should be the right
    :param irow:
    :param icol:
    :return:
    '''
    assert(isinstance(irow, int))
    assert(isinstance(icol, int))
    #adjusted_icol = (settings.num_neo_cols - 1) - icol
    # print(f'irow: {irow} icol: {icol} adjusted_icol: {adjusted_icol}')
    adjusted_irow = irow if icol % 2 == 0 else (settings.num_neo_rows - 1) - irow
    i = (icol * settings.num_neo_rows) + adjusted_irow
    #print(f'{irow}, {icol}, adjusted {adjusted_irow} -> {i}')
    return i

def rows_are_columns_with_alternating_reversed_column_order_indexer(irow: int, icol: int, settings: DisplaySettings) -> int:
    '''
    Flips the column ordering.  Useful when the left side of the display should be the right
    :param irow:
    :param icol:
    :return:
    '''
    assert(isinstance(irow, int))
    assert(isinstance(icol, int))
    #adjusted_icol = (settings.num_neo_cols - 1) - icol
    # print(f'irow: {irow} icol: {icol} adjusted_icol: {adjusted_icol}')
    adjusted_irow = irow if icol % 2 == 1 else (settings.num_neo_rows - 1) - irow
    i = (((settings.num_cols - 1) - icol) * settings.num_neo_rows) + adjusted_irow
    #print(f'{irow}, {icol}, adjusted {adjusted_irow} -> {i}')
    return i

def columns_are_rows_with_alternating_column_order_indexer(irow: int, icol: int, settings: DisplaySettings) -> int:
    '''
    Flips the column ordering.  Useful when the left side of the display should be the right
    :param irow:
    :param icol:
    :return:
    '''
    assert(isinstance(irow, int))
    assert(isinstance(icol, int))
    #adjusted_icol = (settings.num_neo_cols - 1) - icol
    # print(f'irow: {irow} icol: {icol} adjusted_icol: {adjusted_icol}')
    adjusted_icol = icol if irow % 2 == 0 else (settings.num_neo_cols - 1) - icol
    i = (irow * settings.num_neo_cols) + adjusted_icol
    #print(f'{irow}, {icol}, adjusted {adjusted_irow} -> {i}')
    return i
