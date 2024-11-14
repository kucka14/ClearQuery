from copy import deepcopy


def clean_data_string(data_string, collection_names, input_collection_name):
    # if the string is an explicit value, just return
    if data_string[:2] != '->':
        return data_string
    # user will not explicitly reference collections, so add this
    for collection_name in collection_names:
        data_string = data_string.replace(collection_name, f'collections.{collection_name}')
    # user will not explicitly add [i] for input_collection, so add this
    if f'{input_collection_name}[' not in data_string:
        data_string = data_string.replace(input_collection_name, f'{input_collection_name}[i]')
    # TODO somehow convert dot notation to bracket notation


def create_execute_plan(include_clauses, ktv_table, group_by_dict, collection_names, input_collection_name):

    # TODO expand ->ALLKEYS and ->ALLVALUES into multiple ktv_tuples

    # TODO create an ordered list of ktv_tuples, as lists for now
    
    variables = {}

    # TODO for k and v values of ktv_tuples, clean and replace variables

    # TODO clean include clauses, replace  variables, and split pre and post group
    
    return ktv_tuples, pre_group_include_clauses, post_group_include_clauses


def eval_data_string(data_string, collections, i):
    if data_string[:2] != '->': # explicit values should not be evaluated
        return data_string[2:]
    try:                
        data = eval(data_string)
    except KeyError:
        # TODO if up against list, try to make list of matches within list, else raise
        raise
    return data


def cast(value, type):
    # TODO cast given value to the given type (given as string)
    if type == 'string':
        pass
    elif type == 'number':
        pass
    elif type == 'list':
        pass
    elif type == 'dict':
        pass
    return value


def evaluate_include_clauses(object, include_clauses):
    # TODO .any(), .all(), .match(), etc
    # need to be able to match multiple conditions to a single object in an array (but any of the objects)
    # but also be able to match when some combination of the objects in the array meet the multiple conditions
    
    for include_clause in include_clauses:
        # TODO if object doesn't match clause, return False
        pass
    return True


def group_collection(collection, group_by):
    return collection


def filter_after_grouping(collection, post_group_include_clauses):
    return collection


def sort_collection(collection, sort_by):
    return collection


def create_collection(create_info, collections):

    # extract info from the create_info dict
    input_collection_name = create_info['input_collection']
    input_collection = collections[input_collection_name]
    subcollections = create_info['subcollections']
    group_by = create_info['group_by']

    # get executable order of steps for adding data and filtering
    ktv_tuples, pre_group_include_clauses, post_group_include_clauses = \
        create_execute_plan(
            create_info['include_clauses'],
            create_info['ktv_table'],
            group_by,
            collections.keys(),
            input_collection_name
        )

    collection = [] # this is the new collection being created
    for i in range(len(input_collection)):

        output_objects = [{}] # one input object could create 1+ output objects

        # partially cleaned ktv_tuples (key, type, value)
        for ktv_tuple in ktv_tuples:

            # get the actual key value from existing data
            output_key = eval_data_string(ktv_tuple[0], collections, i)
            if not isinstance(output_key, str):
                raise # keys should always be strings

            output_type = ktv_tuple[1]
            if not isinstance(output_type, str):
                raise # types should always be strings

            # get the actual value value from existing data
            output_value = eval_data_string(ktv_tuple[2], collections, i)
            
            # catch cases for which the output_value should be expanded to multiple rows
            if isinstance(output_value, list) and not isinstance(output_type, list):
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
                    output_object[output_key] = cast(output_value, output_type)
        
        # test the output objects against include_clauses, then add to collection
        for output_object in output_objects:
            if evaluate_include_clauses(output_object, pre_group_include_clauses):
                collection.append(output_object)

    collection = group_collection(collection, group_by)

    collection = filter_after_grouping(collection, post_group_include_clauses)

    collection = sort_collection(collection, create_info['sort_by'])

    return create_info.get('output_name'), collection