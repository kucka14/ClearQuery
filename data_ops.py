import json

def load_data(load_info, collections):
    for collection_name, path in load_info:
        with open(path, 'r') as f:
            collection = json.load(f)
        collections[collection_name] = collection


def delete_data(delete_info, collections):
    pass


def write_data(write_info, collections):
    pass