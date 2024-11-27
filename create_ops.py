from copy import deepcopy
import re


def create_execute_plan(ktv_table, input_collection):

    # expand ->ALLKEYS and ->ALLVALUES into multiple ktv_tuples
    ktv_tuples = []
    for row in ktv_table:
        if row[0] == '->ALLKEYS' and row[2] == '->ALLVALUES':
            for key, value in input_collection.items():
                ktv_tuples.append((key, row[1], value, row[3]))
        elif row[0] == '->ALLKEYS':
            for key in input_collection.keys():
                ktv_tuples.append((key, row[1], row[2], row[3]))
        elif row[2] == '->ALLVALUES':
            for value in input_collection.values():
                ktv_tuples.append((row[0], row[1], value, row[3]))
        else:
            ktv_tuples.append(row)

    # create an ordered list of ktv_tuples
    ktv_variables = set()
    ordered_ktv_tuples = []
    while len(ktv_tuples) > 0:
        i = 0
        while i < len(ktv_tuples):
            ktv_tuple = ktv_tuples[i]
            variables_in_key = set([variable[2:-1] for variable in re.findall(r'\${.*?}', ktv_tuple[0])])
            variables_in_value = set([variable[2:-1] for variable in re.findall(r'\${.*?}', ktv_tuple[2])])
            if variables_in_key.issubset(ktv_variables) and variables_in_value.issubset(ktv_variables):
                ordered_ktv_tuples.append(ktv_tuples.pop(i))
                ktv_variables.add(ktv_tuple[0])
            else:
                i += 1
                                                                                        
    return ktv_tuples


def eval_istring(istring, i):
    istring = istring[1:-1].replace(' ', '')
    if istring[1] == '+':
        return i + int(istring[2:])
    elif istring[1] == '-':
        return i - int(istring[2:])
    else:
        return i
    

def sub_ktv_variables(data_string, ktv_variables):
    for key, value in ktv_variables.items():
        if f'${key}$' in data_string:
            data_string = data_string.replace(f'${key}$', value)
    return data_string


def eval_data_substring(data_string, root_object, i=None):

    data_steps = data_string.split('.')

    # start with a one-object list, could be expanded
    current_groups = [root_object]
    j = 0
    while j < len(data_steps):
        data_step = data_steps[j]
        if data_step[0] == '{' and data_step[-1] == '}': # if is python lambda expression
            new_groups = []
            altered_data_step = f'lambda ab9c750a5a4ffa5dd71ea36ce72fb51f: {data_step[1:-1]}'.replace('this', 'ab9c750a5a4ffa5dd71ea36ce72fb51f')
            for ab9c750a5a4ffa5dd71ea36ce72fb51f in current_groups:
                new_groups.append(eval(altered_data_step))
            j += 1
        elif isinstance(current_groups[0], list):
            if data_step[0] == '(i': # if list index is given, get that object for each group
                new_groups = [current_group[eval_istring(data_step, i)] for current_group in current_groups]
                j += 1
            else: # flatten the list of lists, but don't advance a step
                new_groups = [] 
                for current_group in current_groups:
                    for item in current_group:
                        new_groups.append(item)
        elif isinstance(current_groups[0], dict):
            new_groups = [current_group[data_step] for current_group in current_groups]
            j += 1
        current_groups = new_groups 
    
    if len(current_groups) == 1:
        return current_groups[0]
    else:
        return current_groups


def get_outer_bracket_indices(data_string):
    level = 0
    index_couplets = []
    for i in range(len(data_string)):
        if data_string[i] == '{':
            if level == 0:
                opening_index = i
            level -= 1
        if data_string[i] == '}':
            level += 1
            if level == 0:
                index_couplets.append((opening_index, i))
    return index_couplets


def eval_data_string(data_string, collections, i, input_collection_name, ktv_variables):

    if not isinstance(data_string, str):
        return data_string
    
    data_string = sub_ktv_variables(data_string, ktv_variables)
    
    bracket_couplets = get_outer_bracket_indices(data_string)
    if len(bracket_couplets) == 0:
        new_data_string = data_string
    else:
        new_data_string = data_string[0:bracket_couplets[0][0]]
        for i in range(len(bracket_couplets)):

            data_substring = data_string[bracket_couplets[i][0]+1:bracket_couplets[i][1]]

            # user may not explicitly add .(i) for input_collection, so add this
            if f'{input_collection_name}.(' not in data_substring:
                data_substring = data_substring.replace(input_collection_name, f'{input_collection_name}.(i)')

            new_data_string += str(eval_data_substring(data_substring, collections, i))
            if i == len(bracket_couplets) - 1:
                new_data_string += data_string[bracket_couplets[-1][1]+1:]
            else:
                new_data_string += data_string[bracket_couplets[i][1]+1:bracket_couplets[i+1][0]]

    try:
        new_data = eval(new_data_string)
    except:
        pass
    return new_data


def cast(value, type):
    # cast given value to the given type (given as string)
    if type == 'string':
        value = str(value)
    elif type == 'number':
        value = float(value)
    elif type == 'list':
        value = list(value)
    elif type == 'dict':
        value = dict(value)
    return value


def evaluate_include_clause(target_object, include_clause, ktv_variables):

    include_clause = sub_ktv_variables(include_clause, ktv_variables)
    include_clause_list = include_clause.split()

    new_include_clause_list = []
    for subclause in include_clause_list:
        if subclause == 'and' or subclause == 'or' or subclause == '(' or subclause == ')':
            new_include_clause_list.append(subclause)
        else:
            data_string = re.sub(r'\.(matchAny|matchAll|match)\(.*$', '', subclause)
            subtarget = eval_data_substring(data_string, target_object, i=None)
            subclause_verdict = None
            if '.matchAny(' in subclause:
                if not isinstance(subtarget, list):
                    raise
                match_expression = subclause.split('.matchAny(')[1][:-1]
                match_expression = match_expression.replace('this', 'ab9c750a5a4ffa5dd71ea36ce72fb51f')
                subclause_verdict = False
                for ab9c750a5a4ffa5dd71ea36ce72fb51f in subtarget:
                    if eval(match_expression):
                        subclause_verdict = True
                        break
            elif '.matchAll(' in subclause:
                if not isinstance(subtarget, list):
                    raise
                match_expression = subclause.split('.matchAll(')[1][:-1]
                match_expression = match_expression.replace('this', 'ab9c750a5a4ffa5dd71ea36ce72fb51f')
                subclause = True
                for ab9c750a5a4ffa5dd71ea36ce72fb51f in subtarget:
                    if not eval(match_expression):
                        subclause_verdict = False
            elif '.match(' in subclause:
                match_expression = subclause.split('.match(')[1][:-1]
                match_expression = match_expression.replace('this', 'ab9c750a5a4ffa5dd71ea36ce72fb51f')
                ab9c750a5a4ffa5dd71ea36ce72fb51f = subtarget
                subclause_verdict = eval(match_expression)

            if subclause_verdict:
                new_include_clause_list.append('True')
            else:
                new_include_clause_list.append('False')

    new_include_clause = ' '.join(new_include_clause_list)

    return eval(new_include_clause)


def group_collection(collection, group_by):


    return collection, ktv_variables


def filter_after_grouping(collection, post_group_include_clauses, ktv_variables):
    return collection


def sort_collection(collection, sort_by):




    return collection


def create_collection(create_info, collections):

    # extract info from the create_info dict
    input_collection_name = create_info['input_collection']
    input_collection = collections[input_collection_name]
    subcollections = create_info['subcollections']
    pre_group_include_clause = create_info['include_clauses'][0]

    # get executable order of steps for adding data and filtering
    ktv_tuples = create_execute_plan(create_info['ktv_table'], input_collection)

    collection = [] # this is the new collection being created
    for i in range(len(input_collection)):

        output_objects = [{}] # one input object could create 1+ output objects

        ktv_variables = {}

        # partially cleaned ktv_tuples (key, type, value, isoutput)
        for ktv_tuple in ktv_tuples:

            # get the actual key value from existing data
            output_key = eval_data_string(ktv_tuple[0], collections, i, input_collection_name, ktv_variables)
            if not isinstance(output_key, str):
                raise # keys should always be strings

            output_type = ktv_tuple[1]
            if not isinstance(output_type, str):
                raise # types should always be strings

            # get the actual value value from existing data
            output_value = eval_data_string(ktv_tuple[2], collections, i, input_collection_name, ktv_variables)
            
            # catch cases for which the output_value should be expanded to multiple rows
            if isinstance(output_value, list) and output_type != 'list':
                # if expansion has not been made yet...
                if len(output_objects) == 1 and len(output_value) > 1:
                    new_output_objects = [deepcopy(output_objects[0]) for _ in range(len(output_value))]
                    output_objects = new_output_objects
                # something is wrong with this or a previous expansion
                if len(output_objects) != len(output_value):
                    raise
                # add list items to the expanded output
                for j in range(len(output_objects)):
                    output_objects[j][output_key] = cast(output_value[j], output_type)

            # if the string was a keyword for a subcollection
            elif isinstance(output_value, str) and output_value in subcollections:
                # make recursive call to create the subcollection, name is not necessary
                subcollection_name, subcollection = create_collection(subcollections[output_value], collections)
                for output_object in output_objects:
                    output_object[output_key] = subcollection

            # otherwise just add the key, value pair to output
            else:
                for output_object in output_objects:
                    if ktv_tuple[3]:
                        output_object[output_key] = cast(output_value, output_type)
        
        # test the output objects against include_clauses, then add to collection
        for output_object in output_objects:
            if evaluate_include_clause(output_object, pre_group_include_clause, ktv_variables):
                collection.append(output_object)

    # need to create new ktv_varialbes
    collection, ktv_variables = group_collection(collection, create_info['group_by'])

    collection = filter_after_grouping(collection, create_info['include_clauses'][1], ktv_variables)

    collection = sort_collection(collection, create_info['sort_by'])

    return create_info.get('output_name'), collection