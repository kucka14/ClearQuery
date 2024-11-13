import json
from copy import deepcopy

input = [

    # input data paths
    {
        'type': 'load',
        'laureates': '/data/laureates.json',
        'prizes': '/data/prizes.json'
    },

    # joins
    {
        'type': 'join',
    },

    # output collection1
    {
        'type': 'create_collection'
    },

    # output collection2
    {
        'type': 'create_collection',
        'output_name': '',
        'input_collection': '',
        'include_clauses': (

        ),
        'ktv_table': (
            ('', '', ''),
            ('', '', '')
        ),
        'sort_by': (),

        # this will match ktv_table keys to aggregation conditions
        'group_by': {
            
        },
        'subcollections': {
            'subcollection1': {
                'iterates_over': '',
                'input_collection': '',
                'include_clauses': (

                ),
                'ktv_table': (
                    ('', '', ''),
                    ('', '', '')
                ),
                'sort_by': (),
                'group_by': {

                }
            } 
        }
    }

]


def load_data(input_data_dict, collections):
    for collection_name, path in input_data_dict:
        with open(path, 'r') as f:
            collection = json.load(f)
        collections[collection_name] = collection
    return collections


def perform_joins(join_dict, collections):
    # perform the joins specified in the join_dict
    # add new datasets to existing datasets in collections
    pass


def create_execute_plan(include_clauses, ktv_table, group_by_dict, input_collection_name):
    # create an ordered list of include clauses and ktv tuples
    # ALLKEYS and ALLVALUES will be expanded in multiple ktv_tuples
    pass


def evaluate_include_clause(include_clause, object):
    pass


def sort_collection(collection, sort_by):
    # sort the given collection by the keys in sort_by tuple
    # return a new sorted collection
    return collection


def group_collection(collection, group_by):
    return collection


def filter_after_grouping(collection, post_group_include_clauses):
    return collection


def parse_data_string(data_string, collections, i):
    for collection_name in collections.keys():
        data_string = data_string.replace(collection_name, f'collections.{collection_name}')
        if f'{collection_name}[' not in data_string:
            data_string = data_string.replace(collection_name, f'{collection_name}[{i}]')
    try:                
        data = eval(data_string)
    except NameError:
        data = data_string
    except KeyError:
        raise
    return data


def cast(value, type):
    # casts given value to the given type (given as string)
    return value

def create_collection(cs, collections):

    input_collection_name = cs['input_collection']

    input_collection = collections[input_collection_name]

    subcollections = cs['subcollections']

    group_by = cs['group_by']

    execute_plan, post_group_include_clauses = create_execute_plan(cs['include_clauses'], cs['ktv_table'], group_by, input_collection_name)

    collection = []
    for i in range(len(input_collection)):

        output_objects = [{}]
        for execute_step in execute_plan:
            if execute_step[0] == 'include_clause':
                include_clause = execute_step[1]
                if not evaluate_include_clause(include_clause, output_object):
                    continue
            elif execute_step[0] == 'ktv_tuple':

                ktv_tuple = execute_step[1]

                output_key = parse_data_string(ktv_tuple[0], collections, i)
                if not isinstance(output_key, str):
                    raise
                output_type = ktv_tuple[1]
                if not isinstance(output_type, str):
                    raise
                output_value = parse_data_string(ktv_tuple[2], collections, i)
                if isinstance(output_value, list) and not isinstance(output_type, list):
                    if len(output_objects) == 1 and len(output_value) > 1:
                        new_output_objects = [deepcopy(output_objects[0]) for _ in range(len(output_value))]
                        output_objects = new_output_objects
                    if len(output_objects) != len(output_value):
                        raise
                    for j in range(len(output_objects)):
                        output_objects[j][output_key] = cast(output_value[j], output_type)
                elif isinstance(output_value, str) and output_value in subcollections:
                    for output_object in output_objects:
                        None, output_object[output_key] = create_collection(subcollections[output_value], collections)
                else:
                    for output_object in output_objects:
                        output_object[output_key] = cast(output_value, output_type)

        for output_object in output_objects:
            collection.append(output_object)

    collection = group_collection(collection, group_by)

    collection = filter_after_grouping(collection, post_group_include_clauses)

    collection = sort_collection(collection, cs['sort_by'])

    return cs.get('output_name'), collection


if __name__ == '__main__':

    collections = {}

    for operation in input:

        if operation['type'] == 'load':
            load_data(operation, collections)
        elif operation['type'] == 'join':
            perform_joins(operation, collections)
        elif operation['type'] == 'create_collection':
            collection_name, collection = create_collection(operation, collections)
            # store the newly created collection in the collections dict
            collections[collection_name] = collection