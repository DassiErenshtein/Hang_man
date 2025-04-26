from ast import literal_eval
from requests import session
session = session()
class hang_man:
    def __init__(self):
        self.basic_url = "http://127.0.0.1:5000"
        self.cookie = None
        self.user = {}
        self.hang_man = ["x-------x",
                         """ x-------x
|
|
|
|
|""",
"""x-------x
|       |
|       0
|
|
|""",
"""x-------x
|       |
|       0
|       |
|
|""",
"""x-------x
|       |
|       0
|      /|\ 
|
|""",
r"""x-------x
|       |
|       0
|      /|\ 
|      /
|""",
r"""x-------x
|       |
|       0
|      /|\ 
|      / \ 
|"""]
        self.english_letters={}
        self.hebrew_letters = {}
        self.letters()
    def letters(self):
        self.hebrew_letters = {
            'א': False, 'ב': False, 'ג': False, 'ד': False, 'ה': False,
            'ו': False, 'ז': False, 'ח': False, 'ט': False, 'י': False,
            'כ': False, 'ך': False, 'ל': False, 'מ': False, 'ם': False,
            'נ': False, 'ן': False, 'ס': False, 'ע': False, 'פ': False,
            'ף': False, 'צ': False, 'ץ': False, 'ק': False, 'ר': False,
            'ש': False, 'ת': False
        }
        self.english_letters = {
            'a': False, 'b': False, 'c': False, 'd': False, 'e': False,
            'f': False, 'g': False, 'h': False, 'i': False, 'j': False,
            'k': False, 'l': False, 'm': False, 'n': False, 'o': False,
            'p': False, 'q': False, 'r': False, 's': False, 't': False,
            'u': False, 'v': False, 'w': False, 'x': False, 'y': False,
            'z': False

        }
    def register(self):
        while True:
            response = session.post(f"{self.basic_url}/register",
                                    json={'name': input("input your name"), 'id': input("input id"), 'password': input("input password")})
            if response.status_code == 200:
                print(literal_eval(response.text)['message'])
                break
            elif (response.status_code == 400):
                print("invalid variables, try again")
            else:
                print("id exists!!")
    # פונקציה להתחברות
    def login(self):
        #כל עוד ההתחברות לא תקינה, מעביר לREGISTER או שאם יש שגיאה ממשיך
        while True:
            #קריאת שרת של התחברות
            login = session.get(f"{self.basic_url}/login", json={'id': input("input id"), 'password': input("input password")})
            if login.status_code == 200:
                print(literal_eval(login.text)['message'])
                break
            #אם הערכים לא תקינים
            elif (login.status_code == 400):
                print("you didnot fill good variables, try again")
                continue
            #שגיאה במהלך הקריאה בשרת (בקריאה מהקובץ)
            elif (login.status_code == 500):
                print("something wrong, please try again!")
            else:
                print("you need to register")
                self.register()
                break
    #התחלת המשחק
    def start_game(self):
        num1 = self.check_is_number("""choose language:
                                        1- english
                                        2- hebrew""")
        while num1 != 1 and num1 != 2:
            num1 = self.check_is_number("choose language:"
                                        "1- english"
                                        "2- hebrew")
        my_characters = self.english_letters
        if num1 == 2:
            my_characters = self.hebrew_letters
        num = self.check_is_number("input which number that you want... (it won't less your options...😋)")
        word = session.get(f"{self.basic_url}/word",json={'num': num, 'lan': num1})

        while word.status_code == 403:
            print("you need to login")
            self.login()
            word = session.get(f"{self.basic_url}/word",
                               json={'num': num})
        if word.status_code == 500:
            print("something wrong, try again!")
            return
        word = word.json()
        i = 0
        encrypted_word = []
        for i1 in range(len(word) - 1):
            if word[i1] == " ":
                encrypted_word.append(" ")
            else:
                encrypted_word.append("_")
        while True:
            if i == len(self.hang_man):
                break
            print("".join(encrypted_word))
            print(self.hang_man[i])
            letter = input(f"input a letter, You have {len(self.hang_man) - i} times to tap!")
            while True:
                isaletter=self.is_a_letter(letter)
                if(isaletter == True and letter in my_characters and my_characters[letter]==False):
                    break
                if isaletter == False:
                    letter = input(f"Please enter a valid value!")
                    continue
                if letter in my_characters:
                    pass
                else:
                    letter = input(f"change the language!")
                    continue
                if my_characters[letter]==True:
                    letter = input(f"You have already chosen this letter!")
                    continue
            my_characters[letter]=True
            if letter in word:
                for i1 in range(len(word)):
                    if word[i1] == letter:
                        encrypted_word[i1] = letter
            else:
                i += 1
            if "_" in encrypted_word:
                continue
            else:
                break
        self.letters()
        if i == len(self.hang_man):
            a = session.post(f"{self.basic_url}/add_game", json={'success': False, 'word': word})
            while a.status_code != 200:
                print("you need to login!")
                self.login()
                a = session.post(f"{self.basic_url}/add_game",json={'success': False, 'word': word})
            if a.status_code == 200:
                print(f"you failed, try again! the word is: {''.join(word)}")
        else:
            a = session.post(f"{self.basic_url}/add_game", json={'success': True, 'word': word})
            while a.status_code == 403:
                print("you need to login!")
                self.login()
                a = session.post(f"{self.basic_url}/add_game", json={'success': True, 'word': word})
            if a.status_code == 200:
                print("you are a winner!! wow! you did it...!!👑👑👑🏆🎖")
            else:
                print("you have a problem, your game doesn't wrriten. sorry...🤔")
    #הפונקציה מקבלת הודעה, ומציגה אותה כל עוד הINPUT עדיין לא מספר ומחזירה את המספר שהתקבל
    def check_is_number(self, message):
        num = 0
        while True:
            try:
                #מציגה את ההודעה
                num = int(input(message))
            except ValueError:
                print("you need to input just a number!")
                continue
            break
        return num

    def game(self):
        print(fr"""
          _    _
         | |  | |
         | |__| | __ _ _ __   __ _ _ __ ___   __ _ _ __
         |  __  |/ _' | '_ \ / _' | '_ ' _ \ / _' | '_ \
         | |  | | (_| | | | | (_| | | | | | | (_| | | | |
         |_|  |_|\__,_|_| |_|\__, |_| |_| |_|\__,_|_| |_|
                        __/ |
                       |___/
        """)
        while True:
            num = self.check_is_number("""what do you want to do:
                                    1- login
                                    2- register
                                    """)
            if num==1:
                self.login()
                break
            elif num==2:
                self.register()
                break
            else:
                print("Invalid value")
        while True:
            num = self.check_is_number("""what do you want to do:
                        1- start game
                        2- history
                        3- logout
                        """)
            if num == 1:
                self.start_game()
            if num == 2:
                self.history()
            if num == 3:
                session.get(f"{self.basic_url}/logout")
                print("you logged out")
                self.login()
            else:
                print("Invalid value")
    def history(self):
        response = session.get(f"{self.basic_url}/history")
        if response.status_code == 200:
            last = response.json()
            print("last words: " + ", ".join(last['last_words']))
            print("sum games: " + str(last['sum_games']))
            print("sum wins : " + str(last['sum_wins']))

        elif response.status_code==403:
            print("you need to login!!")
            self.login()
            self.history()
        else:
            print("error, try again!")

    def is_a_letter(self, letter):
        if (len(letter) != 1):
            return False
        return letter.isalpha()
if __name__ == "__main__":
    mygame = hang_man()
    mygame.game()