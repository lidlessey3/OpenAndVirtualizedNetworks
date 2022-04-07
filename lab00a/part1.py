def ex1() :
    a = int(input("Enter a number: "))
    b = int(input("Enter a second number: "))

    sum = a * b

    print("Thei product is ")
    print(sum)

    if sum > 1000:
        print("Their sum is ")
        print(a + b)

def ex2() :
    prev=None
    for num in range(-10, 20):
        if prev != None:
            print(prev + num)
        prev = num

def ex3(list) :
    if list[0] == list[-1]:
        print("yay")
    else:
        print("nay")

def ex4(list) :
    for num in list:
        if num % 5 == 0:
            print(num)

def ex5(string, sub):
    count = 0
    eos = False
    while not eos:
        tmp = string.find(sub)
        if tmp == -1:
            eos = True
        else:
            count += 1
            string=string[tmp+len(sub):]
    print(sub + " was found a total of " + str(count) + " times.")


if __name__ == "__main__":
    ex5("Emma is a good developer. Emma is also a writer", "Emma")
