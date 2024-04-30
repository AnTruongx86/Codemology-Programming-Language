from os.path import dirname, join
from textx import metamodel_from_file
import operator

#Create a metamodel and open the example program from the same folder.
this_folder = dirname(__file__)

Codemo_meta = metamodel_from_file(join(this_folder, 'Codemology.tx'))

program = Codemo_meta.model_from_file(join(this_folder, 'Codprogram3.cod'))

#comps dictionary use to translate Codemology's operators into Python's operators
comps = {
    "exceeds" : operator.gt,
    "subceeds" : operator.lt,
    "equals" : operator.eq,
    "unequals" : operator.ne,
    "approaching" : operator.le,  
    "departing" : operator.ge, 
}

#state use to store the program's variables
state = {}

def varmap(targetVar, dict):
    for key in dict: 
        if targetVar == key: 
            return dict[key]
    raise ValueError("Variable not found")

def compare(int1, comp, int2):
    return comps[comp](int1, int2)

# Main function use to intepret the program. 
def interpret(program):
    for statement in program.statements: 
        if statement.__class__.__name__ == "Assignment":
            if statement.value == "Habitable":
                state[statement.name] = True
            elif statement.value == "Non-habitable":
                state[statement.name] = False
            else: 
                state[statement.name] = statement.value 
        
        elif statement.__class__.__name__ == "List": 
            if statement.name in state.keys() and statement.item and statement.listAction: 
                if statement.listAction == 'captures': 
                    if statement.item in state.keys(): 
                        state[statement.name].append(state[statement.item])
                    else: 
                        state[statement.name].append(statement.item)
                elif statement.listAction == "escapes": 
                    if statement.item in state.keys(): 
                        state[statement.name].remove(state[statement.item])
                    else: 
                        state[statement.name].remove(statement.item)
            else: 
                state[statement.name] = []
                for item in statement.items: 
                    if item.value in state.keys(): 
                        state[statement.name].append(state[item.value])
                    else: 
                        state[statement.name].append(item.value)
        
        elif statement.__class__.__name__ == "Print":
            if statement.name: 
                print(state[statement.name])
            else: 
                print(statement.value)
                
        elif statement.__class__.__name__ == "Loop": 
            for i in range(0, statement.orbits, 1):
                loop_program = type('Program', (object,), {'statements': statement.body})
                interpret(loop_program)
            
        elif statement.__class__.__name__ == "Calculation": 
            if statement.operator == "redshifted" and statement.name in state.keys(): 
                state[statement.name] += statement.value
            elif statement.operator == "blueshifted" and statement.name in state.keys():
                state[statement.name] -= statement.value 
                
        elif statement.__class__.__name__ == "IfStmt":
            if statement.op1 in state.keys():     
                temp1 = varmap(statement.op1, state)
            
            if statement.value in state.keys():
                temp2 = varmap(statement.value, state)
            elif statement.value == 'Habitable':
                temp2 = True
            elif statement.value == 'Non-habitable': 
                temp2 = False
            else: 
                temp2 = statement.value

            if statement.comparator in comps.keys() and temp1 and temp2:
                if compare(temp1, statement.comparator, temp2) == True: 
                    if_body = type('Program', (object,), {'statements': statement.body})
                    interpret(if_body)
                elif compare(temp1, statement.comparator, temp2) == False and statement.body2: 
                    else_body = type('Program', (object,), {'statements': statement.body2})
                    interpret(else_body)
            elif temp2 == True or temp2 == False: 
                if compare(temp1, 'equals', temp2) == True: 
                    if_body = type('Program', (object,), {'statements': statement.body})
                    interpret(if_body)
                elif compare(temp1, 'equals', temp2) == False and statement.body2: 
                    else_body = type('Program', (object,), {'statements': statement.body2})
                    interpret(else_body)
            else: 
                print("Error: Invalid If Statement")
                
        elif statement.__class__.__name__ == "Function": 
            state[statement.name] = type('Program', (object,), {'statements': statement.body})
            
        elif statement.__class__.__name__ == "ExFunction": 
            interpret(state[statement.function])
            
        
interpret(program)