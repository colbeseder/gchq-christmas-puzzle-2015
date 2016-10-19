"""
Solver for GCHQ Christmas Card Puzzle 2015
"""

from itertools import combinations
from data import * ## rows_data, columns_data

MAX_RUNS = 25 # Don't want to leave it running all day

UNKNOWN = 0 # Or blank
FILLED  = 1
EMPTY   = 2

symbols = {}
symbols[UNKNOWN] = "?"
symbols[FILLED] = "X" #"\u25a0"
symbols[EMPTY] = "."

row_length = 25

## Used for calculating easier rows first
max_free = 2


## Display the table
def paint(table):
    complete = True # for now
    for row in table:
        complete = complete and (UNKNOWN not in row)
        paint_row(row)
    if not complete:
        print("\nWARNING: Table not complete\n")

def paint_row(row):
    result = ""
    for i in range(row_length):
        if len(row) <= i:
            result += symbols[UNKNOWN]
            continue
        cell = row[i]
        if cell == FILLED:
            result += symbols[FILLED]
        elif cell == EMPTY:
            result += symbols[EMPTY]
        else:
            result += symbols[UNKNOWN]
    print("|%s|"%result)

# "freedom" is the number of unfilled squares that can be moved around
def get_full_freedom(data):
    full = len(data) -1 + sum(data)
    return row_length - full

def new_row():
    return [UNKNOWN] * row_length

def combine(opt1, opt2):
    #Known squares take precedence
    row = new_row()
    for i in range(row_length):
        if opt1[i] == UNKNOWN:
            row[i] = opt2[i]
        elif opt2[i] == UNKNOWN:
            row[i] = opt1[i]
        elif opt1[i] != opt2[i]:
            #Conflict
            return None
        else:
            row[i] = opt1[i]
    return row

## Do two rows disagree on a "known" square
def rows_conflict(opt1, opt2):
    for i in range(row_length):
        if opt1[i] != UNKNOWN and opt2[i] != UNKNOWN and opt1[i] != opt2[i]:
            return True
    return None

## If all possible options agree on the state of a square
## Then we can be confident in that state
def find_confident_squares(opt1, opt2):
    found = False # Did we learn anything new?
    row = opt1[:]
    #Unknown takes precedence
    for i in range(row_length):
        if opt1[i] != opt2[i] or opt2[i] == UNKNOWN or opt1[i] == UNKNOWN:
            row[i] = UNKNOWN
        elif opt1[i] == opt2[i]:
            #Good. Keep this
            found = True
    if not found:
        return None
    else:
        return row

def attempt_row(data, current):
    if is_row_complete(current):
        #Nothing to do
        return None
    
    ## This is the performance bottleneck
    ## It would be better to only generate combos that
    ## Do not conflict with current known row
    combos = brute_force_combos(data)
    if not combos:
        return None

    first_run = True
    for c in combos:
        if rows_conflict(c, current):
            #Combo not valid - doesn't match reality
            continue
        if first_run:
			# This is to ignore squares we already know.
			# So we can exit if we're not learning anything
            res = clear_known_squares(current, c[:])
            first_run = False
            #continue #No previous options to compare against
        res = find_confident_squares(res, c)
        if not res:
            ## Nothing new found on this run
            return None
    return combine(res, current)

def clear_known_squares(current, combo):
    for i in range(len(current)):
        if current[i] != UNKNOWN:
            combo[i] = UNKNOWN
    return combo

def balls_in_boxes(n, m):# balls, boxes
    for c in combinations(range(n + m - 1), m - 1):
        yield tuple(b - a - 1 for a, b in zip((-1,) + c, c + (n + m - 1,)))

def brute_force_combos(data):
    # "freedom" is the number of unfilled squares that can be moved around
    freedom = get_full_freedom(data)

    if freedom > max_free and (row_length - freedom) > max_free:
		# Leave more complex rows for later
        return None

    if freedom == 0:
        return [single_space(data)]

    num_of_buckets = len(data) + 1
    ## Minimum buckets [0, 1, 1, ... 1, 0]
    buckets = [0]
    while len(buckets) < num_of_buckets:
        buckets.append(1)
    buckets[len(buckets) -1] = 0

    combos = []

    for trial_buckets in balls_in_boxes(freedom, num_of_buckets):
        combined_buckets = buckets[:]
        for i in range(num_of_buckets):
            combined_buckets[i] += trial_buckets[i]
            combos.append(interleave([0] + data, combined_buckets))
    return combos

def was_changed(before, after):
    for i in range(len(before)):
        if before[i] != after[i]:
            return True
    return False

def interleave(black, white):
    row = new_row()
    i = 0
    for yy in range(len(black)):
        b = black[yy]
        w = white[yy]
        for j in range(b):
            row[i] = FILLED
            i += 1
        for j in range(w):
            row[i] = EMPTY
            i += 1
    while i < row_length:
        row[i] = EMPTY
        i += 1
    return row

## return column of data as a single list (as a row would be)
def get_column(table, idx):
    col = []
    for i in range(row_length):
        if idx >= len(table[i]):
            col.append(UNKNOWN)
        else:
            col.append(table[i][idx])
    return col

def get_row(table, idx):
    row = table[idx]
    while (len(row) < row_length):
        row.append(UNKNOWN)
    return row

def set_cell(table, row, col, val):
    table[row][col] = val

def set_col(table, col, data):
    for i in range(row_length):
        x = data[i]
        table[i][col] = x

def single_space(data):
    row = []
    for d in data:
        for j in range(d):
            row.append(FILLED)
        if len(row) < row_length:
            row.append(EMPTY)
    return row

def is_row_complete(row):
    return not (UNKNOWN in row)

## setup table
table = [ [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [] ]

table[3]  = [UNKNOWN, UNKNOWN, UNKNOWN, FILLED, FILLED, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, FILLED, FILLED, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, FILLED]
table[8]  = [UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, FILLED, FILLED, UNKNOWN, UNKNOWN, FILLED, UNKNOWN, UNKNOWN, UNKNOWN, FILLED,  FILLED, UNKNOWN, UNKNOWN, FILLED]
table[16] = [UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, FILLED, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, FILLED, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, FILLED, UNKNOWN, UNKNOWN, UNKNOWN, FILLED]
table[21] = [UNKNOWN, UNKNOWN, UNKNOWN, FILLED, FILLED, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, FILLED, FILLED, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, FILLED, UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, FILLED, FILLED]

for i in range(row_length):
    table[i] = get_row(table, i)
## Table is now ready

import time
start_time = time.time()

for runs in range(MAX_RUNS):
    touched = False
    #print("Run: %d"%runs)

	# Attempt Rows
    for i in range(row_length):
        res = attempt_row(rows_data[i], table[i])
        if res:
            if was_changed(table[i], res):
                touched = True
            table[i] = res

	# Attempt columns
    for i in range(row_length):
        res = attempt_row(columns_data[i], get_column(table, i))
        if res:
            if was_changed(get_column(table, i), res):
                touched = True
            set_col(table, i, res)

    max_free += 3
    #if not touched:
    #    break

print("")
print("--- %s seconds ---" % (time.time() - start_time))
print("")

paint(table)

input()