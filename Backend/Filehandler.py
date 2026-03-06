import json

def write_to_json(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)


def read_json():
    with open("data.json", "r") as f:
        test = json.load(f)
        print(test)
    return test

def add_json(data):
    old_data = read_json()
    data.update(old_data)
    write_to_json(data)


if __name__ == "__main__":
    data = {
        "name2":"Albin"
        
        }
    add_json(data)
