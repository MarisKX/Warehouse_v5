
def letter_to_number(letters):
    letters = letters.lower()
    let_dict = {
        "a": 2,
        "b": 2,
        "c": 2,
        "d": 3,
        "e": 3,
        "f": 3,
        "g": 4,
        "h": 4,
        "i": 4,
        "j": 5,
        "k": 5,
        "l": 5,
        "m": 6,
        "n": 6,
        "o": 6,
        "p": 7,
        "q": 7,
        "r": 7,
        "s": 7,
        "t": 8,
        "u": 8,
        "v": 8,
        "w": 9,
        "x": 9,
        "y": 9,
        "z": 9,
    }
    letter1 = letters[0]
    number1 = let_dict[letter1]

    letter2 = letters[1]
    number2 = let_dict[letter2]

    letter3 = letters[2]
    number3 = let_dict[letter3]

    letter4 = letters[3]
    number4 = let_dict[letter4]

    number = f"" + str(number1) + str(number2) + str(number3) + str(number4) + ""
    end_number = int(number)
    return end_number
