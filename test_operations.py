
# input data paths
load_operation_1 = {
    'type': 'load',
    'laureates': '/data/laureates.json',
    'prizes': '/data/prizes.json'
}

# delete collection from memory
delete_operation_1 = {
    'type': 'delete'
}

# write collection to disk
write_operation_1 = {
    'type': 'write'
}

# joins
join_operation_2 = {
    'type': 'join',
},

# output collection1
create_collection_operation_1 = {
    'type': 'create_collection'
},

# output collection2
create_collection_operation_2 = {
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

operations_list = [
    load_operation_1,
    create_collection_operation_2
]
