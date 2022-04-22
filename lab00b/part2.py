import json

def ex1():
    fi = open("lab02/Resources/states.json")
    data = json.load(fi)
    fi.close()
    print(type(data))
    print(data)

if __name__ == "__main__":
    ex1()
