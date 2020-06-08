from copy import deepcopy

###
### Propagation function to be used in the recursive sudoku solver
###

def propagate(sudoku_possible_values, k):
    ### approach: simply removing values that are solved/guessed from the other's domains in row, col and box

    sudoku_possible_values_copy = deepcopy(sudoku_possible_values)      ## copy so the original is not getting overwritten
    for rowInd in range(k*k):
        for colInd in range(k*k):
            ### checking for solved/guessed cell (number of possible values is 1)
            if len(sudoku_possible_values[rowInd][colInd]) == 1:
                to_remove = sudoku_possible_values[rowInd][colInd][0]
                #removing from row, col and box values
                sudoku_possible_values_copy = remove_value(sudoku_possible_values_copy, rowInd, colInd, to_remove, k)

    return sudoku_possible_values_copy

def remove_value(sudoku_possible_values, rowInd, colInd, to_remove, k):
    ### removing values that are already solved or guessed (=their possible values has only 1 option)
    ## note: skipping cells that's value is under removal, trying to remove in the other cells and catching if value is not present
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

    ### note: this solution assumes that we don't go over 2 digits in the size/numbers (so works up to 9*9 units)

    from pysat.formula import CNF
    from pysat.solvers import MinisatGH

    ## constraint id is calculated as follows: concatenate row num, col num and value, padded two 2 digits   

    solver = MinisatGH()
    formula = CNF()
    
    ## Approach:
    ## We have variables for each possible value in each cell (so rowNum * colNum * potential_values = k*k * k*k * k*k)
    ## for each unit (row, co, box) we add a rule that at least one should be true (a or b or c or ...)
    ## than for each pair in a unit, we add that the two cannot be true at the same time (not a or not b)

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
    from ortools.sat.python import cp_model
    model = cp_model.CpModel()

    ## Approach:
    ## variables stored in a matrix of same format as the sudoku itself
    ## each has the domain 1-k
    ## for each pair in a unit (row, col, box) add a constraint that they cannot be equal
    ## note: pairwise is more efficient than alldif, but for code simplicity box employs alldiff

    ## define variables matrix
    var_matrix = [[0 for j in range(k*k)] for i in range(k*k)]
    for rowInd in range(k*k):
        for colInd in range(k*k):
            var_matrix[rowInd][colInd] = model.NewIntVar(1,k*k,pad_str(rowInd+1) + pad_str(colInd+1))

    ## note: pairwise non-equality constraint is a lot more efficient than alldif
    ## adding: row rules
    for rowInd in range(k*k):
        for colIndOne in range(k*k-1):
            for colIndTwo in range(colIndOne+1, k*k):
                model.Add(var_matrix[rowInd][colIndOne]!=var_matrix[rowInd][colIndTwo])

    ## adding: col rules
    for colInd in range(k*k):
        for rowIndOne in range(k*k-1):
            for rowIndTwo in range(rowIndOne+1, k*k):
                model.Add(var_matrix[rowIndOne][colInd]!=var_matrix[rowIndTwo][colInd])

    ## adding: box rules
    ## here i use alldif for simplicity
    for rowStart in range(0,k*k,k):
        for colStart in range(0,k*k,k):
            box_vars = []
            for rowInd in range(rowStart, rowStart+k):
                for colInd in range(colStart, colStart+k):
                    box_vars.append(var_matrix[rowInd][colInd])
            model.AddAllDifferent(box_vars)

    ## adding input values as constraints
    for rowInd in range(k*k):
        for colInd in range(k*k):
            if sudoku[rowInd][colInd] != 0:
                model.Add(var_matrix[rowInd][colInd] == sudoku[rowInd][colInd])
    ## solving model
    solver = cp_model.CpSolver();
    answer = solver.Solve(model);

    ## reconstructing sudoku
    for rowInd in range(k*k):
        for colInd in range(k*k):
            sudoku[rowInd][colInd] = solver.Value(var_matrix[rowInd][colInd])

    return sudoku;

###
### Solver that uses ASP encoding
###
def solve_sudoku_ASP(sudoku,k):
    import clingo
    asp_code = ""

    ##Approach:
    ## each cells is defined as a cell (with name c<ROW_NUM>_<COL_NUM>)
    ## for every pair in a unit (row, col or box) encode that they are in the same unit
    ## encode that each cells should take exactly one of the k values
    ## add a rule that two cells that are in the same unit cannot have the same value

    ## first: encode cells
    for rowInd in range(k*k):
        for colInd in range(k*k):
            cell_id = "c" + str(rowInd) + "_" + str(colInd)
            asp_code += "cell(" + cell_id + ").\n"
    
    
    ## encode cells sharing row
    for rowInd in range(k*k):
        for colIndOne in range(k*k-1):
            for colIndTwo in range(colIndOne+1, k*k):
                cellOne_id = "c" + str(rowInd)+ "_"  + str(colIndOne)
                cellTwo_id = "c" + str(rowInd)+ "_"  + str(colIndTwo)
                asp_code += "same_unit(" + cellOne_id + "," + cellTwo_id + ").\n"
    
    ## encode cells sharing col
    for colInd in range(k*k):
        for rowIndOne in range(k*k-1):
            for rowIndTwo in range(rowIndOne+1,k*k):
                cellOne_id = "c" + str(rowIndOne)+ "_"  + str(colInd) 
                cellTwo_id = "c" + str(rowIndTwo)+ "_"  + str(colInd) 
                asp_code += "same_unit(" + cellOne_id + "," + cellTwo_id + ").\n"
    
    ## encode cells sharing box
    for rowStart in range(0,k*k,k):
        for colStart in range(0,k*k,k):
            ## looping inside box
            for rowIndOne in range(rowStart, rowStart+k):
                for colIndOne in range(colStart, colStart+k):
                    for rowIndTwo in range(rowStart, rowStart+k):
                        for colIndTwo in range(colStart, colStart+k):
                            if not (rowIndOne == rowIndTwo and colIndOne == colIndTwo):
                                cellOne_id = "c" + str(rowIndOne)+ "_"  + str(colIndOne) 
                                cellTwo_id = "c" + str(rowIndTwo)+ "_"  + str(colIndTwo) 
                                asp_code += "same_unit(" + cellOne_id + "," + cellTwo_id + ").\n"
    
    ## we need to encode that all cells take one of the k values => if not the others, it should be one
    possible_values = range(k*k)
    for possible_value in possible_values:
        only_one_rule = "value(C," + str(possible_value) + ") :- cell(C),"
        for smaller_val in possible_values[0:possible_value]:
            only_one_rule += " not value(C," + str(smaller_val) + "),"
        for bigger_val in possible_values[possible_value+1:]:
            only_one_rule += " not value(C," + str(bigger_val) + "),"
        only_one_rule = only_one_rule[:-1]  ##removing last comma
        asp_code += only_one_rule + ".\n"
    
    ##encode the input values
    for rowInd in range(k*k):
        for colInd in range(k*k):
            if sudoku[rowInd][colInd] != 0:
                asp_code += "value(c" + str(rowInd) + "_" + str(colInd) + "," + str(sudoku[rowInd][colInd]-1) + ") :- .\n"

    ## we only need to add: two cells that share a unit cannot take the same value
    asp_code += ":- same_unit(C1, C2), value(C1, V), value(C2, V)."

    ## solve the model
    control = clingo.Control()
    control.add("base", [], asp_code)
    control.ground([("base", [])])

    control.configuration.solve.models = 1

    ## storing the values obtained by the model
    vals = ""
    with control.solve(yield_=True) as handle:
        for model in handle:
            vals = (model.symbols(atoms=True))

    ## reconstruct sudoku
    if vals:
        for atom in vals:
            atom = str(atom)
            if atom[0] == "v":       ## focus on values
                cell_str = atom.split("c")[1]
                cell_id, val = cell_str.split(",")
                cell_id = cell_id.split("_")
                val = val[:-1]
                sudoku[int(cell_id[0])][int(cell_id[1])] = int(val) + 1
    else:
        sudoku = None
    return sudoku
###
### Solver that uses ILP encoding
###
def solve_sudoku_ILP(sudoku,k):
    import gurobipy as gp
    from gurobipy import GRB
    model = gp.Model()

    ##Approach: vars stored in a tensor of rows by colums by possible values (k*k * k*k * k*k)
    ## the potential values dimension in each cell should sum to 1 (i.e. there is exactly one value assigned to a cell)
    ## the row dimension for any given value should sum to 1 (each row has exactly 1 of each value)
    ## the col dimension for any given value should sum to 1 (each col has exactly 1 of each value)
    ## the box for any value should sum to 1 (each box has exactly 1 of each value)

    ### adding vars in a matrix
    var_matrix = [[0 for j in range(k*k)] for i in range(k*k)]
    for rowInd in range(k*k):
        for colInd in range(k*k):
            var_matrix[rowInd][colInd] = model.addVars(k*k, vtype = 'I', name = str(rowInd)+ "_" + str(colInd))
    

    ## every cell should have one value
    for rowInd in range(k*k):
        for colInd in range(k*k):
            model.addConstr(gp.quicksum([var_matrix[rowInd][colInd][i] for i in range(k*k)]) == 1, "constr_row" + str(rowInd) + "_col" + str(colInd))

    ## adding: row constraints
    for rowInd in range(k*k):
        ## everything should appear once
        for possible_value in range(k*k):
            model.addConstr(gp.quicksum([var_matrix[rowInd][i][possible_value] for i in range(k*k)]) == 1, "constr_row" + str(rowInd) + "_val" + str(possible_value))

    ## adding: col constraints
    for colInd in range(k*k):
        ## everything should appear once
        for possible_value in range(k*k):
            model.addConstr(gp.quicksum([var_matrix[i][colInd][possible_value] for i in range(k*k)]) == 1, "constr_col" + str(colInd) + "_val" + str(possible_value))

    ## addong: box constraints
    for rowStart in range(0,k*k,k):
        for colStart in range(0,k*k,k):
            box_vars = []
            for rowInd in range(rowStart, rowStart+k):
                for colInd in range(colStart, colStart+k):
                    box_vars.append(var_matrix[rowInd][colInd])
            for possible_value in range(k*k):
                model.addConstr(gp.quicksum([box_vars[i][possible_value] for i in range(k*k)]) == 1, "constr_box" + str(rowStart) + str(colStart) + "_val" + str(possible_value))


    ## adding inputs
    for rowInd in range(k*k):
        for colInd in range(k*k):
            if sudoku[rowInd][colInd] != 0:
                model.addConstr(var_matrix[rowInd][colInd][sudoku[rowInd][colInd]-1] == 1, "constr_input_" + str(rowInd) + str(colInd))



    model.optimize();
    ### reconstructing sudoku
    if model.status == GRB.OPTIMAL:
        for v in model.getVars():
            if int(v.x) != 0:
                name_split = v.varName.split("[")
                ind_split = name_split[0].split("_")
                sudoku[int(ind_split[0])][int(ind_split[1])] = int(name_split[1][:-1])+1
    else:
        sudoku = None
    return sudoku