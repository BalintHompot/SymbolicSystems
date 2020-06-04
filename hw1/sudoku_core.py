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

    from pysat.formula import CNF
    from pysat.solvers import MinisatGH

    ## constraint id is calculated as follows: concatenate row num, col num and value   

    solver = MinisatGH()
    ## GENERAL SUDOKU RULES
    formula = CNF()
    
    ## adding: one position can't take two values
    
    for rowInd in range(k*k):
        for colInd in range(k*k):
            for valOne in range(k*k-1):
                for valTwo in range(valOne+1, k*k):
                    formula.append([-int(pad_str(rowInd+1) + pad_str(colInd+1) + pad_str(valOne+1)), -int(pad_str(rowInd+1) + pad_str(colInd+1) + pad_str(valTwo+1))])
    
    ## adding: row rules
    for rowInd in range(k*k):
        for possible_value in range(k*k):
            ## adding that one should be true
            formula.append([int(pad_str(rowInd+1) + pad_str(colInd+1) + pad_str(possible_value+1)) for colInd in range(k*k)])
            ## adding that two cannot be true
            for colIndOne in range(k*k-1):
                for colIndTwo in range(colIndOne+1, k*k):
                    formula.append([-int(pad_str(rowInd+1) + pad_str(colIndOne+1) + pad_str(possible_value+1)), -int(pad_str(rowInd+1) + pad_str(colIndTwo+1) + pad_str(possible_value+1))])
    
    ## adding: col rules
    for colInd in range(k*k):
        for possible_value in range(k*k):
            ## adding that one should be true
            formula.append([int(pad_str(rowInd+1) + pad_str(colInd+1) + pad_str(possible_value+1)) for rowInd in range(k*k)])
            ## adding that two cannot be true
            for rowIndOne in range(k*k-1):
                for rowIndTwo in range(rowIndOne+1, k*k):
                    formula.append([-int(pad_str(rowIndOne+1) + pad_str(colInd+1) + pad_str(possible_value+1)), -int(pad_str(rowIndTwo+1) + pad_str(colInd+1) + pad_str(possible_value+1))])
    
    ## adding: box rules
    for rowStart in range(0,k*k,k):
        for colStart in range(0,k*k,k):
            ## looping inside box
            for possible_value in range(k*k):

                ## adding that one should be true
                box_ids = []
                for rowInd in range(rowStart, rowStart+k):
                    for colInd in range(colStart, colStart+k):
                        box_ids.append(int(pad_str(rowInd+1) + pad_str(colInd+1) + pad_str(possible_value+1)))
                formula.append(box_ids)

                ## adding that two cannot be true
                for rowIndOne in range(rowStart, rowStart+k):
                    for colIndOne in range(colStart, colStart+k):
                        for rowIndTwo in range(rowIndOne, rowStart+k):
                            for colIndTwo in range(colIndOne, colStart+k):
                                if not (rowIndOne == rowIndTwo and colIndOne == colIndTwo):
                                    formula.append([-int(pad_str(rowIndOne+1) + pad_str(colIndOne+1) + pad_str(possible_value+1)), -int(pad_str(rowIndTwo+1) + pad_str(colIndTwo+1) + pad_str(possible_value+1))])
    
    ## Adding the input values as literals
    for rowInd in range(k*k):
        for colInd in range(k*k):
            if sudoku[rowInd][colInd] != 0:
                formula.append([int(pad_str(rowInd+1) + pad_str(colInd+1) + pad_str(sudoku[rowInd][colInd]))])
                

    ## calling the solver
    solver.append_formula(formula)
    answer = solver.solve()
    if not answer:
        return None
    else:
        ### reconstruct sudoku from solution
        for lit in solver.get_model():
            if lit > 0:
                lit_split = [int(x) for x in str(lit)]
                ## appending leading zero if needed, since int conversion removes it
                if len(lit_split) < 6:
                    lit_split = [0] + lit_split
                print(lit_split)

                sudoku[10*lit_split[0] + lit_split[1]-1][10 * lit_split[2] + lit_split[3] -1] = 10 * lit_split[4] + lit_split[5] 
        return sudoku

def pad_str(i):

    s = str(i)
    if len(s) < 2:
        s = "0" + s
    return s

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
