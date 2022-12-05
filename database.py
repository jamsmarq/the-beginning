import pymongo

def setup_database():
    CONNECTION_STRING = "mongodb+srv://jamsmarq:jUKNFaKrMghuQZ@the-beginning.mzrodrd.mongodb.net/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(CONNECTION_STRING)

    return client['the_beginning']

def get_module_data(module: str):
    database = setup_database().bot_modules

    return database.find_one({"module": module})

def set_module_data(module: str, item: str):
    database = get_module_data(module)

    database.update_one()