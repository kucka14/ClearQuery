from data_ops import load_data, delete_data, write_data
from join_ops import join_data
from create_ops import create_collection
import test_operations


def perform_operation(operation, collections):
    if operation['type'] == 'load':
        load_data(operation, collections)
    elif operation['type'] == 'delete':
        delete_data(operation, collections)
    elif operation['type'] == 'write':
        write_data(operation, collections)
    elif operation['type'] == 'join':
        join_data(operation, collections)
    elif operation['type'] == 'create_collection':
        collection_name, collection = create_collection(operation, collections)
        collections[collection_name] = collection

if __name__ == '__main__':

    collections = {}

    for operation in test_operations.operations_list:
        perform_operation(operation, collections)