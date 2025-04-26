from flask import Flask, jsonify, request, abort, make_response
from flask_cors import CORS, cross_origin
from Player import player
from ast import literal_eval
from os import path
import random
from functools import wraps

app = Flask(__name__)
CORS(app, supports_credentials=True)
path_file_name = './users.json'


# עטיפת פונקציה לבדיקת חיבור משתמש באמצעות עוגיות
def check_is_login(func):
    @wraps(func)  # שימור מטא-נתונים של הפונקציה המקורית
    def wrapper(*args, **kwargs):
        # בדיקת קיום עוגייה בשם 'user_id'
        if request.cookies.get('user_id') == None:
            return abort(403)  # משתמש לא מחובר - גישת HTTP 403
        return func(*args, **kwargs)  # קריאה לפונקציה אם המשתמש מחובר

    return wrapper


# פונקציה לבדיקת תקינות תעודת זהות
def check_id(id):
    if len(id) != 9:  # אורך שגוי
        return False
    sum = 0  # סכום ספרות מחושב
    i1 = 1  # משקל חישוב לספרה
    check = int(id[-1])  # ספרת ביקורת
    id = id[0:-1]  # הסרת ספרת הביקורת
    for i in id:
        try:
            int(i)
        except ValueError:
            return False
        num = i1 * int(i)  # הכפלה במשקל
        while num >= 1:  # חישוב ספרות המספר
            sum += num % 10
            num -= num % 10
            num /= 10

        i1 = 1 if i1 == 2 else 2  # שינוי המשקל
    # בדיקה אם ספרת הביקורת תואמת
    return check == 10 - sum % 10 or check == 0 == sum % 10

# פונקציה לבדיקה אם השם מכיל רק אותיות
def check_name(name):
    # בדיקת כל התווים בשם
    for char in name:
        if char.isalpha():
            continue
        else:
            return False
    return True

# פונקציה לבדוק אם שחקן קיים לפי תעודת זהות
def exists_player(id):
    if path.exists(path_file_name):# בדיקה אם קובץ המשתמשים קיים
        with open(path_file_name, 'r', encoding="UTF-8") as f:
            list1 = f.readlines()
            for l in list1:
                l1 = l.removesuffix('\n')
                player = literal_eval(l1)# המרת מחרוזת לאובייקט
                if player['id'] == id:# בדיקת התאמה לתעודת זהות
                    return player
    return False


@cross_origin(app, supports_credentials=True)
@app.route('/login', methods=["GET"])
def login():
    user = request.json# קריאת נתוני המשתמש
    res = check_id(user['id'])# בדיקת תקינות תעודת זהות
    if (res == False):
        return abort(400)
    if path.exists(path_file_name): # בדיקה אם קובץ המשתמשים קיים
        with open(path_file_name, 'r', encoding="UTF-8") as f:
            list1 = f.readlines()
            for l in list1:
                if l != '\n':
                    l1 = l.removesuffix('\n')
                    try:
                        player = literal_eval(l1)# המרת מחרוזת לאובייקט
                    except:
                        return abort(500)
                    # אימות שם משתמש וסיסמה
                    if player['id'] == user['id'] and player['password'] == user['password']:
                        response = make_response(jsonify({"message": f"Hello {player['name']}!"}))
                        # הגדרת עוגיות עם נתוני המשתמש
                        response.set_cookie('user_name', player['name'], max_age=600, httponly=True)
                        response.set_cookie('user_id', player['id'], max_age=600, httponly=True)
                        return response
    return abort(405)# משתמש לא נמצא


# נקודת קצה לרישום משתמש חדש
@cross_origin(app, supports_credentials=True)
@app.route('/register', methods=["POST"])
def register():
    user = request.json  # קריאת נתוני המשתמש
    res = check_id(user['id'])  # בדיקת תקינות תעודת זהות
    if res == False:  # אם התעודה לא תקינה
        return abort(400)  # החזרה עם שגיאה 400
    res = check_name(user['name'])  # בדיקת תקינות שם
    if res == False:  # אם השם לא תקין
        return abort(400)  # החזרה עם שגיאה 400
    if exists_player(user['id']) == False:  # בדיקה אם המשתמש לא קיים
        new_player = player(user['name'], user['id'], user['password'])  # יצירת שחקן חדש
        with open(path_file_name, 'a',encoding="UTF-8") as f:
            f.write("\n" + str(new_player))  # הוספת המשתמש לקובץ
        response = make_response(jsonify({"message": f"Hello {new_player.name}!"}))  # תגובה עם הודעה
        response.set_cookie('user_name', new_player.name, max_age=600, httponly=True)  # הגדרת עוגייה לשם
        response.set_cookie('user_id', new_player.id, max_age=600, httponly=True)  # הגדרת עוגייה לתעודת הזהות
        return response
    return abort(403)  # החזרה עם שגיאה אם המשתמש כבר קיים


# נקודת קצה לשליפת מילה אקראית למשחק
@cross_origin(app, supports_credentials=True)
@app.route('/word', methods=["GET"])
@check_is_login  # בדיקה אם המשתמש מחובר
def take_word():
    num = request.json['num']  # שליפת פרמטר מספר המילה מהבקשה
    num1 = request.json['lan']  # שליפת פרמטר שפת המילה מהבקשה
    if num1 == 1:  # אם השפה היא אנגלית
        path1 = './words.txt'  # הגדרת מסלול לקובץ המילים באנגלית
        if num is not None:  # בדיקה אם המספר לא ריק
            with open(path1, 'r') as fi:  # פתיחת קובץ המילים באנגלית
                words = fi.readlines()  # קריאת כל המילים בקובץ
                random.shuffle(words)  # ערבוב המילים
                return jsonify(words[num % len(words)])  # החזרת מילה לפי המספר שנשלח
        else:
            return abort(400)  # החזרה עם שגיאה אם המספר חסר
    else:  # אם השפה היא עברית
        path1 = './hebrew.txt'  # הגדרת מסלול לקובץ המילים בעברית
        if num is not None:  # בדיקה אם המספר לא ריק
            with open(path1, 'r', encoding="UTF-8") as fi:  # פתיחת קובץ המילים בעברית
                words = fi.readlines()  # קריאת כל המילים בקובץ
                random.shuffle(words)  # ערבוב המילים
                return jsonify(words[num % len(words)])  # החזרת מילה לפי המספר שנשלח
        else:
            return abort(400)  # החזרה עם שגיאה אם המספר חסר

# נקודת קצה להוספת משחק להיסטוריית המשתמש
@cross_origin(app, supports_credentials=True)
@app.route('/add_game', methods=["POST"])
@check_is_login  # בדיקה אם המשתמש מחובר
def add_game():
    if path.exists(path_file_name):  # בדיקה אם קובץ המשתמשים קיים
        with open(path_file_name, 'r+', encoding="UTF-8") as fi:  # פתיחת הקובץ לקריאה וכתיבה
            lines = fi.readlines()  # קריאת כל השורות בקובץ
            for index, value in enumerate(lines):  # מעבר על כל שורה
                l1 = value.removesuffix('\n')  # הסרת תו שורה חדשה
                player1 = literal_eval(l1)  # המרת מחרוזת לאובייקט שחקן
                if player1['id'] == request.cookies.get('user_id'):  # חיפוש השחקן לפי תעודת זהות
                    player1['sum_games'] += 1  # עדכון מספר המשחקים
                    if request.json['success'] == True:  # אם המשחק הסתיים בהצלחה
                        player1['sum_wins'] += 1  # עדכון מספר הניצחונות
                    player1['last_words'].append(request.json['word'].removesuffix('\n'))  # הוספת המילה האחרונה
                    player1['last_words'] = list(set(player1['last_words']))  # הסרת כפילויות מהמילים האחרונות
                    lines[index] = str(player1) + "\n"  # עדכון השורה בקובץ
                    break  # יציאה מהלולאה לאחר עדכון השחקן
            fi.seek(0)  # חזרה לתחילת הקובץ
            fi.truncate()  # מחיקת תוכן הקובץ
            fi.writelines(lines)  # כתיבת השורות המעודכנות לקובץ
    return jsonify("good")  # החזרת תגובה לאחר סיום העדכון

# נקודת קצה להצגת היסטוריית משחקים של המשתמש
@cross_origin(app, supports_credentials=True)
@app.route('/history', methods=["GET"])
# @check_is_login  # ניתן להפעיל אם נדרשת בדיקת התחברות
def history():
    with open(path_file_name, 'r', encoding="UTF-8") as f:  # פתיחת קובץ המשתמשים לקריאה
        lines = f.readlines()  # קריאת כל השורות בקובץ
        for value in lines:  # מעבר על כל שורה
            l1 = value.removesuffix('\n')  # הסרת תו שורה חדשה
            player1 = literal_eval(l1)  # המרת מחרוזת לאובייקט שחקן
            if player1['id'] == request.cookies.get('user_id'):  # בדיקת תעודת זהות מול העוגייה
                return jsonify(player1)  # החזרת היסטוריית השחקן בפורמט JSON
    return abort(405)  # אם השחקן לא נמצא, החזרה עם שגיאה 405

# נקודת קצה להתנתקות המשתמש
@cross_origin(app, supports_credentials=True)
@app.route('/logout', methods=["GET"])
def log_out():
    response = make_response()  # יצירת תגובה ריקה
    response.set_cookie('user_name', "", max_age=0, httponly=True, secure=False)  # מחיקת עוגייה לשם המשתמש
    return response  # החזרת תגובה לאחר התנתקות

# הפעלת השרת
if __name__ == "__main__":
    app.run(debug=True)  # הרצת השרת במצב debug