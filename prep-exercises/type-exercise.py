def double(value):
    return value * 2

def second(value):
    return value[1]

def half(value):
    return value / 2

def main():
    print(second(22))
    print(second(0x16))
    print(second("hello"))
    print(second("22"))


if __name__ == "__main__":
    main()
