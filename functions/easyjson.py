import json
import os


def into_json(keys, value, file):
    """
    Update/Save values of existing json file.
    Cannot be used with multi level indexes(ex: ['index_1']['index_2'])
    :param keys: Key of the json dictionary. If accessing more than 1 indexes deep,
                should be split with dot(.)
    :param value: Value of the key
    :param file: json file
    :return:
    """
    if os.path.exists(file):
        main_dict = json.load(open(file))
        indexes = keys.split('.')
        if len(indexes) > 4:
            print('Can only handle 4 level deep indexes.')
            return

        if len(indexes) == 1:
            main_dict[indexes[0]] = value
        elif len(indexes) == 2:
            main_dict[indexes[0]][indexes[1]] = value
        elif len(indexes) == 3:
            main_dict[indexes[0]][indexes[1]][indexes[2]] = value
        elif len(indexes) == 4:
            main_dict[indexes[0]][indexes[1]][indexes[2]][indexes[3]] = value

        with open(file, 'w') as f:
            json.dump(main_dict, f, indent=3)

    else:
        raise FileNotFoundError


def from_json(keys, file):
    """
    Return the value of the specified key from a json file.
    Cannot be used with multi level indexes(ex: ['index_1']['index_2'])
    :param keys: Key of the json dictionary. If accessing more than 1 indexes deep,
                should be split with dot(.)
    :param file: json file.
    :return:
    """
    if os.path.exists(file):
        indexes = keys.split('.')
        if len(indexes) > 4:
            print('Can only handle 4 level deep indexes.')
            return

        with open(file) as json_file:
            main_dict = json.load(json_file)
            if len(indexes) == 1:
                val = main_dict[indexes[0]]
            if len(indexes) == 2:
                val = main_dict[indexes[0]][indexes[1]]
            if len(indexes) == 3:
                val = main_dict[indexes[0]][indexes[1]][indexes[2]]
            if len(indexes) == 4:
                val = main_dict[indexes[0]][indexes[1]][indexes[2]][indexes[3]]
        return val

    else:
        raise FileNotFoundError


# user_3 = {
#     "Name": "Michael",
#     "Age": 20
# }
# into_json("Users.User_1.Name", "Sahan", "test.json")
# print(from_json("Users.User_1.Name", 'test.json'))
