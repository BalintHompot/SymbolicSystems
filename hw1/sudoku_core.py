from copy import deepcopy

###
### Propagation function to be used in the recursive sudoku solver
###

def propagate(sudoku_possible_values, k):
    ### approach: simply removing values that are solved/guessed from the other's domains in row, col and box

    sudoku_possible_values_copy = deepcopy(sudoku_possible_values)
    for rowInd in range(k*k):
        for colInd in range(k*k):
            ### checking for single value
            if len(sudoku_possible_values[rowInd][colInd]) == 1:
                to_remove = sudoku_possible_values[rowInd][colInd][0]
                #removing from row, col and box values
                sudoku_possible_values_copy = remove_value(sudoku_possible_values_copy, rowInd, colInd, to_remove, k)

    return sudoku_possible_values_copy

def remove_value(sudoku_possible_values, rowInd, colInd, to_remove, k):
    #removing from row
    for colInd_other in range(k*k):
        if colInd_other != colInd:
            try:
                sudoku_possible_values[rowInd][colInd_other].remove(to_remove)
            except ValueError:
                pass
    ## removing from column
    for rowInd_other in range(k*k):
        if rowInd_other != rowInd:
            try:
                sudoku_possible_values[rowInd_other][colInd].remove(to_remove)
            except ValueError:
                pass
    
    ##removing from box
    start_row = rowInd - (rowInd % k)
    start_col = colInd - (colInd % k)
    for colInd_other in range(start_col, start_col+k):
        for rowInd_other in range(start_row, start_row+k):
            if not (colInd_other == colInd and rowInd_other == rowInd):
                try:
                    sudoku_possible_values[rowInd_other][colInd_other].remove(to_remove)
                except ValueError:
                    pass

    return sudoku_possible_values

###
### Solver that uses SAT encoding
###
def solve_sudoku_SAT(sudoku,k):
    return None;

###
### Solver that uses CSP encoding
###
def solve_sudoku_CSP(sudoku,k):
    return None;

###
### Solver that uses ASP encoding
###
def solve_sudoku_ASP(sudoku,k):
    return None;

###
### Solver that uses ILP encoding
###
def solve_sudoku_ILP(sudoku,k):
    return None;
