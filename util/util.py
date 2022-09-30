import configparser


def get_value_from_config(file, section, key):
    config = configparser.ConfigParser()
    config.read(file)
    return config.get(section, key)


def in_range(left, num, right):
    return left <= num and num <= right


def get_in_range(left, num, right):
    if num < left:
        return left
    if num > right:
        return right
    return num