from flask import Flask, request, abort
from flask.wrappers import Response
from database_config import *
import mysql.connector
import hashlib

app = Flask(__name__)

def passwd_encrypt(passwd):
    passwd = passwd+SALT
    return hashlib.sha256(passwd.encode()).hexdigest()

def connect_to_database():
    database = mysql.connector.connect(host=DB_SERVER, user=DB_USER, password=DB_PASSWD, database=DB_NAME, charset='utf8')
    if database.is_connected:
        return database
    else:
        return None

def select_from_db(query):
    db = connect_to_database()
    if db==None:
        abort(500)

    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def delete_from_db(query , params):
    db = connect_to_database()
    if db==None:
        abort(500)

    cursor = db.cursor()
    try:
        cursor.execute(query, params)
        db.commit()
        return True
    except Exception as e:
        return False
    finally:
        cursor.close()
        db.close()

def insert_to_db(query , params , multiple=False):
    db = connect_to_database()
    if db==None:
        abort(500)
    cursor = db.cursor()

    try:
        if multiple:
            cursor.executemany(query, params)
        else:
            cursor.execute(query , params)
        
        db.commit()
        return True
    except :
        return False
    finally:
        cursor.close()
        db.close()



@app.route('/get_shop_info' , methods=['GET'])
def get_shop_info():
    id = request.args.get('shop_id', None)

    if id==None :
        abort(400)
    
    query = f"SELECT * FROM {TABLE_SHOP} WHERE {TABLE_SHOP_ID}={id}"

    result = select_from_db(query)
    if len(result) == 1:
        (id, name, address, latitude, longitude, phone, site, description, id_seller, id_category) = result[0]
        return {"find":True , "shop":{"id":id, "name":name, "address":address, "latitude":latitude, "longitude":longitude, "id_seller":id_seller, "id_category":id_category, "site":site , "description":description, "phone":phone}}
    else :
        return {"find":False , "shop":{}}
        
@app.route('/get_shop_discount' , methods=['GET'])
def get_shop_discount():
    id = request.args.get('shop_id', None)

    if id==None :
        abort(400)
    
    query = f"SELECT * FROM {TABLE_DISCOUNT} WHERE {TABLE_DISCOUNT_ID_SHOP}={id}"

    result = select_from_db(query)
    if len(result) == 1:
        (id_shop, name, amount) = result[0]
        return {"find":True , "discount":{"id_shop":id_shop, "name":name, "amount":amount}}
    else :
        return {"find":False , "discount":{}}

@app.route('/check_user_has_discount' , methods=['GET'])
def check_user_has_discount():
    id_user = request.args.get('user_id', None)
    id_shop = request.args.get('shop_id', None)

    if id_user==None or id_shop==None: 
        abort(400)
    
    query = f"SELECT * FROM {TABLE_DISCOUNT_USER} WHERE {TABLE_DISCOUNT_USER_ID_DISCOUNT}={id_shop} AND {TABLE_DISCOUNT_USER_ID_USER}={id_user}"

    result = select_from_db(query)
    if len(result) == 1:
        return {"discount_enable":True}
    else :
        return {"discount_enable":False}


@app.route('/user_discount_list' , methods=['GET'])
def user_discount_list():
    id_user = request.args.get('user_id', None)

    if id_user==None: 
        abort(400)
    

    query = f'''SELECT {TABLE_DISCOUNT}.{TABLE_DISCOUNT_ID_SHOP}, {TABLE_DISCOUNT}.{TABLE_DISCOUNT_NAME} , {TABLE_DISCOUNT}.{TABLE_DISCOUNT_AMOUNT} , {TABLE_SHOP}.{TABLE_SHOP_ID},
{TABLE_SHOP}.{TABLE_SHOP_NAME} , {TABLE_SHOP}.{TABLE_SHOP_ADDRESS} , {TABLE_SHOP}.{TABLE_SHOP_LATITUDE} , {TABLE_SHOP}.{TABLE_SHOP_LONGITUDE} , {TABLE_SHOP}.{TABLE_SHOP_PHONE} , {TABLE_SHOP}.{TABLE_SHOP_SITE} , {TABLE_SHOP}.{TABLE_SHOP_DESCRIPTION} , {TABLE_SHOP}.{TABLE_SHOP_ID_SELLER} , {TABLE_SHOP}.{TABLE_SHOP_ID_CATEGORY}  
FROM {TABLE_DISCOUNT_USER} JOIN {TABLE_DISCOUNT} ON {TABLE_DISCOUNT_USER}.{TABLE_DISCOUNT_USER_ID_DISCOUNT} = {TABLE_DISCOUNT}.{TABLE_DISCOUNT_ID_SHOP} JOIN {TABLE_SHOP} ON {TABLE_SHOP}.{TABLE_SHOP_ID} = {TABLE_DISCOUNT}.{TABLE_DISCOUNT_ID_SHOP} WHERE {TABLE_DISCOUNT_USER}.{TABLE_MESSAGE_ID_USER} = {id_user}'''


    result = select_from_db(query)
    response = []
    for i in result :
        (id_shop, name, amount , id, name, address, latitude, longitude, phone, site, description, id_seller, id_category) = i
        response.append( {"discount":{"id_shop":id_shop, "name":name, "amount":amount} , 
                          "shop":{"id":id, "name":name, "address":address, "latitude":latitude, "longitude":longitude, "id_seller":id_seller, "id_category":id_category, "site":site , "description":description, "phone":phone}
                         } 
                        )
    return {"discounts":response}


@app.route('/get_seller_info' , methods=['GET'])
def get_seller_info():
    id = request.args.get('seller_id', None)

    if id==None :
        abort(400)

    query = f"SELECT * FROM {TABLE_SELLER} WHERE {TABLE_SELLER_ID}={id}"
    result = select_from_db(query)
        
    if len(result) == 1:
        (id, name, last_name, phone, *_) = result[0]
        return {"find":True , "seller":{"id":id, "name":name, "last_name":last_name , "phone":phone}}
    else:
        return {"find":False , "seller":{}}

@app.route('/get_user_info' , methods=['GET'])
def get_user_info():
    id = request.args.get('user_id', None)

    if id==None :
        abort(400)
    
    query = f"SELECT * FROM {TABLE_USER} WHERE {TABLE_USER_ID}={id}"
    result = select_from_db(query)
        
    if len(result) == 1:
        (id, name, last_name, phone, *_) = result[0]
        return {"find":True , "user":{"id":id, "name":name, "last_name":last_name , "phone":phone}}
    else:
        return {"find":False , "user":{}}

@app.route('/shop_get_message' , methods=['GET'])
def shop_get_message():
    id = request.args.get('shop_id', None)

    if id==None :
        abort(400)
    
    query = f"SELECT * FROM {TABLE_MESSAGE} WHERE {TABLE_MESSAGE_ID_SHOP}={id}"
    result = select_from_db(query)
        
    if len(result) == 0:
        return {"find":False , "messages":[]}
    else:
        messages = []
        for item in result:
            text = item[2]
            messages.append({"text":text}) 
        return {"find":True , "messages":messages}

@app.route('/check_user_has_shop' , methods=['GET'])
def check_user_has_shop():
    id = request.args.get('seller_id', None)

    if id==None :
        abort(400)
    
    query = f"SELECT * FROM {TABLE_SHOP} WHERE {TABLE_SHOP_ID_SELLER}={id}"
    result = select_from_db(query)
        
    if len(result) == 1:
        (id, name, address, latitude, longitude, phone, site, description, id_seller, id_category , city) = result[0]
        return {"find":True , "shop":{"id":id, "name":name, "address":address, "latitude":latitude, "longitude":longitude, "id_seller":id_seller, "id_category":id_category, "site":site , "description":description, "phone":phone}}
    else:
        return {"find":False , "shop":{}}

@app.route('/user_get_shop_message' , methods=['GET'])
def user_get_shop_message():
    id_shop = request.args.get('shop_id', None)
    id_user = request.args.get('user_id', None)

    if id_shop==None or id_user==None:
        abort(400)
    
    query = f"SELECT * FROM {TABLE_MESSAGE} WHERE {TABLE_MESSAGE_ID_SHOP}={id_shop} AND {TABLE_MESSAGE_ID_USER}={id_user}"
    result = select_from_db(query)
        
    if len(result) == 1:
        id_user, id_shop, text = result[0]
        return {"find":True , "message":{"id_user":id_user , "id_shop":id_shop , "text":text }}
    else:
        return {"find":False , "message":{}}

@app.route('/get_shop_badge' , methods=['GET'])
def get_shop_badge():
    id_shop = request.args.get('shop_id', None)

    if id_shop==None:
        abort(400)

    query = f"SELECT {TABLE_BADGE_NAME},{TABLE_BADGE_CATEGORY} FROM {TABLE_SHOP_BADGE} INNER JOIN {TABLE_BADGE} ON {TABLE_BADGE}.{TABLE_BADGE_ID}={TABLE_SHOP_BADGE}.{TABLE_SHOP_BADGE_ID_BADGE} WHERE {TABLE_SHOP_BADGE_ID_SHOP}={id_shop}"
    result = select_from_db(query)
        
    badges = []
    for item in result:    
        name, category = item
        b = {"name":name , "category":category}
        badges.append(b)

    return {"badges":badges}

@app.route('/login_user' , methods=['GET'])
def login_user():
    phone = request.args.get('phone', None)
    passwd = request.args.get('passwd', None)

    if phone==None or passwd==None:
        abort(400)
    
    passwd = passwd_encrypt(passwd)

    query = f"SELECT * FROM {TABLE_USER} WHERE {TABLE_USER_PHONE}={phone}"
    result = select_from_db(query)
        
    if len(result) == 1 and passwd == result[0][4]: 
        id = result[0][0]
        return {"login":True , "user_id":id}
    else:
        return {"login":False , "user_id":-1}

@app.route('/login_seller' , methods=['GET'])
def login_seller():
    phone = request.args.get('phone', None)
    passwd = request.args.get('passwd', None)

    if phone==None or passwd==None:
        abort(400)
    
    passwd = passwd_encrypt(passwd)

    query = f"SELECT * FROM {TABLE_SELLER} WHERE {TABLE_SELLER_PHONE}={phone}"
    result = select_from_db(query)
    
    if len(result) == 1 and passwd == result[0][4]: 
        id = result[0][0]
        return {"login":True , "seller_id":id}
    else:
        return {"login":False , "seller_id":-1}

@app.route('/get_category_question' , methods=['GET'])
def get_category_question():
    id_category = request.args.get('category_id', None)

    if id_category==None :
        abort(400)
    
    query = f"SELECT {TABLE_QUESTION_CATEGORY_ID_QUESTION},{TABLE_QUESTION_CONTENT} FROM {TABLE_QUESTION} JOIN {TABLE_QUESTION_CATEGORY} ON {TABLE_QUESTION}.{TABLE_QUESTION_ID}={TABLE_QUESTION_CATEGORY_ID_QUESTION} WHERE {TABLE_QUESTION_CATEGORY_ID_CATEGORY}={id_category}"
    result = select_from_db(query)
        
    if len(result) == 0:
        return {"find":False , "questions":[]}
    else:
        ans = []
        for item in result:
            id_question,content = item
            ans.append({"id_question":id_question , "content":content})

        return {"find":True , "questions":ans}

@app.route('/check_user_ans_question' , methods=['GET'])
def check_user_ans_question():
    id_user = request.args.get('id_user', None)
    id_shop = request.args.get('id_shop', None)

    if id_user==None or id_shop==None :
        abort(400)

    cmd = f"SELECT * FROM {TABLE_USER_QUESTION} WHERE {TABLE_USER_QUESTION_ID_SHOP} = {id_shop} AND {TABLE_USER_QUESTION_ID_USER} = {id_user}"

    select_result = select_from_db(cmd)

    if len(select_result) > 0:
        return {"answered":True}
    else:
        return {"answered":False}

@app.route('/get_categories_list' , methods=['GET'])
def get_categories_list():

    query = f"SELECT * FROM {TABLE_CATEGORY}"
    result = select_from_db(query)
        
    categories = []
    for item in result:    
        id, name = item
        b = {"id":id , "name":name}
        categories.append(b)

    return {"categories":categories}

@app.route('/get_category_criteria' , methods=['GET'])
def get_category_criteria():
    id_category = request.args.get('category_id', None)

    if id_category==None:
        abort(400)

    query = f'''SELECT DISTINCT {TABLE_CRITERIA}.{TABLE_CRITERIA_ID} , {TABLE_CRITERIA}.{TABLE_CRITERIA_NAME} FROM {TABLE_CRITERIA} JOIN {TABLE_QUESTION} ON {TABLE_QUESTION}.{TABLE_QUESTION_CRITERIA} = {TABLE_CRITERIA}.{TABLE_CRITERIA_ID} JOIN {TABLE_QUESTION_CATEGORY} ON {TABLE_QUESTION}.{TABLE_QUESTION_ID} = {TABLE_QUESTION_CATEGORY}.{TABLE_QUESTION_CATEGORY_ID_QUESTION} AND {TABLE_QUESTION_CATEGORY}.{TABLE_QUESTION_CATEGORY_ID_CATEGORY} = {id_category}'''
    result = select_from_db(query)

    resp = []
    for i in result:
        resp.append({"id":i[0] , "name":i[1]})


    return {"criterias":resp}

@app.route('/get_statistic' , methods=['GET'])
def get_statistic():
    id_shop = request.args.get('shop_id', None)

    if id_shop==None:
        abort(400)

    query = f"SELECT SUM({TABLE_USER_QUESTION}.{TABLE_USER_QUESTION_SCORE}) as sum , {TABLE_CRITERIA}.{TABLE_CRITERIA_NAME} FROM {TABLE_USER_QUESTION} JOIN {TABLE_QUESTION} ON {TABLE_USER_QUESTION}.{TABLE_USER_QUESTION_ID_QUESTION} = {TABLE_QUESTION}.{TABLE_QUESTION_ID} JOIN {TABLE_CRITERIA} ON {TABLE_CRITERIA}.{TABLE_CRITERIA_ID} = {TABLE_QUESTION}.{TABLE_QUESTION_CRITERIA} WHERE {TABLE_USER_QUESTION}.{TABLE_USER_QUESTION_ID_SHOP} = {id_shop} GROUP BY {TABLE_CRITERIA}.{TABLE_CRITERIA_NAME}"
    result = select_from_db(query)

    resp = []
    for i in result:
        resp.append( { "name":i[1], "amount":float(i[0]) } )

    return {"statistic":resp}

@app.route('/search_shop' , methods=['GET'])
def search_shop():
    id_category = request.args.get('category_id', None)
    id_criteria = request.args.get('criteria_id', None)
    city = request.args.get('city', None)
    name = request.args.get('shop_name', None)
    
    if id_category==None or id_criteria==None or city==None: 
        abort(400)

    if name == None:
        query = f'''SELECT {TABLE_CATEGORY}.{TABLE_CATEGORY_NAME} as cat_name , {TABLE_SHOP}.{TABLE_SHOP_ID} as shop_id , {TABLE_SHOP}.{TABLE_SHOP_NAME} as shop_name , {TABLE_SHOP}.{TABLE_SHOP_ADDRESS} as shop_address , {TABLE_SHOP}.{TABLE_SHOP_LATITUDE} as shop_latitude , {TABLE_SHOP}.{TABLE_SHOP_LONGITUDE} as shop_longitude , {TABLE_SHOP}.{TABLE_SHOP_PHONE} as shop_phone , {TABLE_SHOP}.{TABLE_SHOP_SITE} as shop_site, {TABLE_SHOP}.{TABLE_SHOP_DESCRIPTION} as shop_description , {TABLE_SHOP}.{TABLE_SHOP_ID_SELLER} as shop_id_seller  , {TABLE_SHOP}.{TABLE_SHOP_ID_CATEGORY} as shop_id_category , SUM({TABLE_USER_QUESTION}.{TABLE_USER_QUESTION_SCORE}) as uscore , {TABLE_QUESTION}.{TABLE_QUESTION_CRITERIA} as qcriteria FROM {TABLE_SHOP} JOIN {TABLE_CATEGORY} ON {TABLE_SHOP}.{TABLE_SHOP_ID_CATEGORY} = {TABLE_CATEGORY}.{TABLE_CATEGORY_ID}  JOIN {TABLE_USER_QUESTION} ON {TABLE_USER_QUESTION}.{TABLE_USER_QUESTION_ID_SHOP} = {TABLE_SHOP}.{TABLE_SHOP_ID}  JOIN {TABLE_QUESTION} ON {TABLE_USER_QUESTION}.{TABLE_USER_QUESTION_ID_QUESTION} = {TABLE_QUESTION}.{TABLE_QUESTION_ID} WHERE {TABLE_QUESTION}.{TABLE_QUESTION_CRITERIA} = {id_criteria} AND {TABLE_CATEGORY}.{TABLE_CATEGORY_ID} = {id_category} AND {TABLE_SHOP}.{TABLE_SHOP_CITY} = '{city}' GROUP BY {TABLE_QUESTION_CRITERIA} , shop_id ORDER BY uscore DESC'''
    else:
        query = f'''SELECT {TABLE_CATEGORY}.{TABLE_CATEGORY_NAME} as cat_name , {TABLE_SHOP}.{TABLE_SHOP_ID} as shop_id , {TABLE_SHOP}.{TABLE_SHOP_NAME} as shop_name , {TABLE_SHOP}.{TABLE_SHOP_ADDRESS} as shop_address , {TABLE_SHOP}.{TABLE_SHOP_LATITUDE} as shop_latitude , {TABLE_SHOP}.{TABLE_SHOP_LONGITUDE} as shop_longitude , {TABLE_SHOP}.{TABLE_SHOP_PHONE} as shop_phone , {TABLE_SHOP}.{TABLE_SHOP_SITE} as shop_site, {TABLE_SHOP}.{TABLE_SHOP_DESCRIPTION} as shop_description , {TABLE_SHOP}.{TABLE_SHOP_ID_SELLER} as shop_id_seller  , {TABLE_SHOP}.{TABLE_SHOP_ID_CATEGORY} as shop_id_category , SUM({TABLE_USER_QUESTION}.{TABLE_USER_QUESTION_SCORE}) as uscore , {TABLE_QUESTION}.{TABLE_QUESTION_CRITERIA} as qcriteria FROM {TABLE_SHOP} JOIN {TABLE_CATEGORY} ON {TABLE_SHOP}.{TABLE_SHOP_ID_CATEGORY} = {TABLE_CATEGORY}.{TABLE_CATEGORY_ID}  JOIN {TABLE_USER_QUESTION} ON {TABLE_USER_QUESTION}.{TABLE_USER_QUESTION_ID_SHOP} = {TABLE_SHOP}.{TABLE_SHOP_ID}  JOIN {TABLE_QUESTION} ON {TABLE_USER_QUESTION}.{TABLE_USER_QUESTION_ID_QUESTION} = {TABLE_QUESTION}.{TABLE_QUESTION_ID} WHERE {TABLE_QUESTION}.{TABLE_QUESTION_CRITERIA} = {id_criteria} AND {TABLE_CATEGORY}.{TABLE_CATEGORY_ID} = {id_category} AND {TABLE_SHOP}.{TABLE_SHOP_CITY} = '{city}' AND {TABLE_SHOP}.{TABLE_SHOP_NAME} LIKE '%{name}%' GROUP BY {TABLE_QUESTION_CRITERIA} , shop_id ORDER BY uscore DESC'''

    print(">>>>"+query)
    result = select_from_db(query)

    if len(result) == 0:    
        if name==None: 
            query = f'''SELECT {TABLE_CATEGORY}.{TABLE_CATEGORY_NAME} as cat_name , {TABLE_SHOP}.{TABLE_SHOP_ID} as shop_id ,{TABLE_SHOP}.{TABLE_SHOP_NAME} as shop_name ,{TABLE_SHOP}.{TABLE_SHOP_ADDRESS} as shop_address , {TABLE_SHOP}.{TABLE_SHOP_LATITUDE} as shop_latitude , {TABLE_SHOP}.{TABLE_SHOP_LONGITUDE} as shop_longitude , {TABLE_SHOP}.{TABLE_SHOP_PHONE} as shop_phone , {TABLE_SHOP}.{TABLE_SHOP_SITE} as shop_site,{TABLE_SHOP}.{TABLE_SHOP_DESCRIPTION} as shop_description , {TABLE_SHOP}.{TABLE_SHOP_ID_SELLER} as shop_id_seller  , {TABLE_SHOP}.{TABLE_SHOP_ID_CATEGORY} as shop_id_category FROM {TABLE_SHOP} JOIN {TABLE_CATEGORY} ON {TABLE_SHOP}.{TABLE_SHOP_ID_CATEGORY} = {TABLE_CATEGORY}.{TABLE_CATEGORY_ID} WHERE {TABLE_CATEGORY}.{TABLE_CATEGORY_ID} = {id_category} AND {TABLE_SHOP}.{TABLE_SHOP_CITY} = '{city}' GROUP BY shop_id'''
        else:
            query = f'''SELECT {TABLE_CATEGORY}.{TABLE_CATEGORY_NAME} as cat_name , {TABLE_SHOP}.{TABLE_SHOP_ID} as shop_id , {TABLE_SHOP}.{TABLE_SHOP_NAME} as shop_name , {TABLE_SHOP}.{TABLE_SHOP_ADDRESS} as shop_address , {TABLE_SHOP}.{TABLE_SHOP_LATITUDE} as shop_latitude , {TABLE_SHOP}.{TABLE_SHOP_LONGITUDE} as shop_longitude , {TABLE_SHOP}.{TABLE_SHOP_PHONE} as shop_phone , {TABLE_SHOP}.{TABLE_SHOP_SITE} as shop_site, {TABLE_SHOP}.{TABLE_SHOP_DESCRIPTION} as shop_description , {TABLE_SHOP}.{TABLE_SHOP_ID_SELLER} as shop_id_seller  , {TABLE_SHOP}.{TABLE_SHOP_ID_CATEGORY} as shop_id_category FROM {TABLE_SHOP} JOIN {TABLE_CATEGORY} ON {TABLE_SHOP}.{TABLE_SHOP_ID_CATEGORY} = {TABLE_CATEGORY}.{TABLE_CATEGORY_ID}  WHERE {TABLE_CATEGORY}.{TABLE_CATEGORY_ID} = {id_category} AND {TABLE_SHOP}.{TABLE_SHOP_CITY} = '{city}' AND {TABLE_SHOP}.{TABLE_SHOP_NAME} LIKE '%{name}%' GROUP BY shop_id'''
        print("<<<<<"+query)       
        result = select_from_db(query)
        resp = []
        for i in result:
            cat_name, id, name, address, latitude, longitude, phone, site, description, id_seller, id_category = i
            resp.append({"id":id, "name":name, "address":address, "latitude":latitude, "longitude":longitude, "id_seller":id_seller, "id_category":id_category, "site":site , "description":description, "phone":phone})
        return {"shop_list":resp}

    else:        
        resp = []
        for i in result:
            cat_name, id, name, address, latitude, longitude, phone, site, description, id_seller, id_category , uscore, qcriteria= i
            resp.append({"id":id, "name":name, "address":address, "latitude":latitude, "longitude":longitude, "id_seller":id_seller, "id_category":id_category, "site":site , "description":description, "phone":phone})
        return {"shop_list":resp}



@app.route('/delete_discount' , methods=['GET'])
def delete_discount():
    id_shop = request.args.get('id_shop', None)

    if id_shop==None:
        abort(400)

    query = f"SELECT * FROM {TABLE_DISCOUNT} WHERE {TABLE_DISCOUNT_ID_SHOP}={id_shop}"
    select_result = select_from_db(query)
    if len(select_result) == 0:
        exists = False
    else:
        exists = True

    query = f"DELETE FROM {TABLE_DISCOUNT} WHERE {TABLE_DISCOUNT_ID_SHOP}=%s"
    params = (id_shop,)

    delete_result = delete_from_db(query , params)
    
    if delete_result:
        query = f"SELECT * FROM {TABLE_DISCOUNT} WHERE {TABLE_DISCOUNT_ID_SHOP}={id_shop}"
        select_result = select_from_db(query)
        if len(select_result) == 0 and exists:
            return {"discount_deleted":True}
        else:
            return {"discount_deleted":False}    
    else:
        return {"discount_deleted":False}

@app.route('/delete_seller' , methods=['GET'])
def delete_seller():
    id = request.args.get('id_seller', None)

    if id==None:
        abort(400)

    cmd = f"SELECT * FROM {TABLE_SELLER} WHERE {TABLE_SELLER_ID}={id}"
    select_result = select_from_db(cmd)
    if len(select_result) == 0:
        exist=False
    else:
        exist=True

    cmd = f"DELETE FROM {TABLE_SELLER} WHERE {TABLE_SELLER_ID}=%s"
    params = (id,)

    delete_result = delete_from_db(cmd , params)
    if delete_result :
        cmd = f"SELECT * FROM {TABLE_SELLER} WHERE {TABLE_SELLER_ID}={id}"
        select_result = select_from_db(cmd)
        if len(select_result) == 0 and exist:
            return {"seller_deleted":True}
        else :
            return {"seller_deleted":False}        
    else:
        return {"seller_deleted":False}        
    
@app.route('/delete_user' , methods=['GET'])
def delete_user():
    id = request.args.get('id_user', None)

    if id==None:
        abort(400)

    cmd = f"SELECT * FROM {TABLE_USER} WHERE {TABLE_USER_ID}={id}"
    select_result = select_from_db(cmd)
    if len(select_result) == 0:
        exist = False
    else:
        exist = True

    cmd = f"DELETE FROM {TABLE_USER} WHERE {TABLE_USER_ID}=%s"
    params = (id,)

    delete_result = delete_from_db(cmd , params)
    if delete_result :
        cmd = f"SELECT * FROM {TABLE_USER} WHERE {TABLE_USER_ID}={id}"
        select_result = select_from_db(cmd)
        if len(select_result) == 0 and exist:
            return {"user_deleted":True}
        else:
            return {"user_deleted":False}        
    else:
        return {"user_deleted":False}

@app.route('/delete_shop' , methods=['GET'])
def delete_shop():
    id = request.args.get('id_shop', None)

    if id==None:
        abort(400)

    cmd = f"SELECT * FROM {TABLE_SHOP} WHERE {TABLE_SHOP_ID}={id}"
    select_result = select_from_db(cmd)
    if len(select_result) == 0:
        exist = False
    else:
        exist = True

    cmd = f"DELETE FROM {TABLE_SHOP} WHERE {TABLE_SHOP_ID}=%s"
    params = (id,)

    delete_result = delete_from_db(cmd , params)
    if delete_result :
        cmd = f"SELECT * FROM {TABLE_SHOP} WHERE {TABLE_SHOP_ID}={id}"
        select_result = select_from_db(cmd)
        if len(select_result) == 0 and exist:
            return {"shop_deleted":True}
        else:
            return {"shop_deleted":False}        
    else:
        return {"shop_deleted":False}

@app.route('/user_used_discount_code' , methods=['GET'])
def user_used_discount_code():
    shop_id = request.args.get('id_shop', None)
    user_id = request.args.get('id_user', None)

    if shop_id==None or user_id==None:
        abort(400)

    cmd = f"SELECT * FROM {TABLE_DISCOUNT_USER} WHERE {TABLE_DISCOUNT_USER_ID_USER}={user_id} AND {TABLE_DISCOUNT_USER_ID_DISCOUNT}={shop_id}"
    select_result = select_from_db(cmd)
    if len(select_result) == 0:
        exist = False
    else:
        exist = True
    
    cmd = f"DELETE FROM {TABLE_DISCOUNT_USER} WHERE {TABLE_DISCOUNT_USER_ID_USER}=%s AND {TABLE_DISCOUNT_USER_ID_DISCOUNT}=%s"
    params = (user_id, shop_id)

    delete_result = delete_from_db(cmd , params)
    
    if delete_result :
        cmd = f"SELECT * FROM {TABLE_DISCOUNT_USER} WHERE {TABLE_DISCOUNT_USER_ID_USER}={user_id} AND {TABLE_DISCOUNT_USER_ID_DISCOUNT}={shop_id}"
        select_result = select_from_db(cmd)

        if len(select_result) == 0 and exist:
            return {"user_discount_deleted":True}
        else:
            return {"user_discount_deleted":False}        
    else:
        return {"user_discount_deleted":False}



@app.route('/register_seller' , methods=['GET'])
def registar_seller():
    name = request.args.get('name', None)
    last_name = request.args.get('last_name', None)
    phone = request.args.get('phone', None)
    passwd = request.args.get('passwd', None)

    if name==None or last_name==None or phone==None or passwd==None:
        abort(400)

    #TODO: chek phone is valid

    passwd = passwd_encrypt(passwd)

    cmd = f"INSERT INTO {TABLE_SELLER} ({TABLE_SELLER_NAME}, {TABLE_SELLER_LAST_NAME}, {TABLE_SELLER_PHONE}, {TABLE_SELLER_PASSWD}) VALUES (%s, %s, %s, %s)"
    params = (name, last_name, phone, passwd)


    insert_result = insert_to_db(cmd , params)
    if insert_result:
        cmd = f"SELECT * FROM {TABLE_SELLER} WHERE {TABLE_SELLER_PHONE}={phone}"
        select_result = select_from_db(cmd)
        if len(select_result) == 1:
            id,name,last_name,phone,*_ = select_result[0]
            return {"status_register":True , "seller":{"id":id, "name":name , "last_name":last_name , "phone":phone}}
        else:
            return {"status_register":False , "seller":{}}
    else:
        return {"status_register":False , "seller":{}}   

@app.route('/register_shop' , methods=['GET'])
def registar_shop():
    name = request.args.get('name', None)
    address = request.args.get('address', None)
    latitude = request.args.get('latitude', None)
    longitude = request.args.get('longitude', None)
    id_seller = request.args.get('id_seller', None)
    id_category = request.args.get('id_category', None)
    city = request.args.get('city', None)
    #optional 
    site = request.args.get('site', None)
    description = request.args.get('description', None)
    phone = request.args.get('phone', None)

    if name==None or address==None or latitude==None or longitude==None or id_seller==None or id_category==None or city==None:
        abort(400)

    cmd = f"INSERT INTO {TABLE_SHOP} ({TABLE_SHOP_NAME}, {TABLE_SHOP_ADDRESS}, {TABLE_SHOP_LATITUDE}, {TABLE_SHOP_LONGITUDE}, {TABLE_SHOP_ID_SELLER}, {TABLE_SHOP_ID_CATEGORY}, {TABLE_SHOP_SITE}, {TABLE_SHOP_DESCRIPTION}, {TABLE_SHOP_PHONE} , {TABLE_SHOP_CITY}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    params = (name, address, latitude, longitude, id_seller, id_category, site, description, phone , city)
    
    insert_result = insert_to_db(cmd , params)
    if insert_result :
        cmd = f"SELECT * FROM {TABLE_SHOP} WHERE {TABLE_SHOP_ID_SELLER}={id_seller}"
        select_result = select_from_db(cmd)
        if len(select_result) == 1:
            id, name, address, latitude, longitude, phone, site, description, id_seller, id_category , city = select_result[0]
            return {"status_register":True , "shop":{"id":id, "name":name, "address":address, "latitude":latitude, "longitude":longitude, "id_seller":id_seller, "id_category":id_category, "site":site , "description":description, "phone":phone}}
        else:
            return {"status_register":False , "shop":{}}
    else:
        return {"status_register":False , "shop":{}}

@app.route('/register_user' , methods=['GET'])
def registar_user():
    name = request.args.get('name', None)
    last_name = request.args.get('last_name', None)
    phone = request.args.get('phone', None)
    passwd = request.args.get('passwd', None)

    if name==None or last_name==None or phone==None or passwd==None:
        abort(400)

    #TODO: chek phone is valid
     
    passwd = passwd_encrypt(passwd)

    cmd = f"INSERT INTO {TABLE_USER} ({TABLE_USER_NAME}, {TABLE_USER_LAST_NAME}, {TABLE_USER_PHONE}, {TABLE_USER_PASSWD}) VALUES (%s, %s, %s, %s)"
    params = (name, last_name, phone, passwd)

    insert_result = insert_to_db(cmd , params)
    if insert_result:
        cmd = f"SELECT * FROM {TABLE_USER} WHERE {TABLE_USER_PHONE}={phone}"
        select_result = select_from_db(cmd)
        if len(select_result) == 1:
            id, name, last_name, phone, *_ = select_result[0]
            return {"status_register":True , "user":{"id":id, "name":name , "last_name":last_name , "phone":phone}}
        else:
            return {"status_register":False , "user":{}}
    else:
        return {"status_register":False , "user":{}}

@app.route('/register_discount' , methods=['GET'])
def registar_discount():
    name = request.args.get('name', None)
    amount = request.args.get('amount', None)
    id_shop = request.args.get('id_shop', None)

    if name==None or amount==None or id_shop==None:
        abort(400)

    cmd = f"INSERT INTO {TABLE_DISCOUNT} ({TABLE_DISCOUNT_ID_SHOP}, {TABLE_DISCOUNT_NAME}, {TABLE_DISCOUNT_AMOUNT}) VALUES (%s, %s, %s)"
    params = (id_shop, name, amount)

    insert_result = insert_to_db(cmd, params)
    if insert_result:
        cmd = f"SELECT * FROM {TABLE_DISCOUNT} WHERE {TABLE_DISCOUNT_ID_SHOP}={id_shop}"
        select_result = select_from_db(cmd)
        if len(select_result) == 1:
            id_shop,name,amount = select_result[0]
            return {"status_register":True, "discount":{"id_shop":id_shop ,"name":name , "amount":amount }}
        else:
            return {"status_register":False, "discount":{}}
    else:
        return {"status_register":False, "discount":{}}

@app.route('/register_user_discount' , methods=['GET'])
def registar_user_discount():
    userId = request.args.get('id_user', None)
    discountId = request.args.get('id_discount', None)

    if userId==None or discountId==None:
        abort(400)

    cmd = f"INSERT INTO {TABLE_DISCOUNT_USER} ({TABLE_DISCOUNT_USER_ID_USER}, {TABLE_DISCOUNT_USER_ID_DISCOUNT}) VALUES (%s, %s)"
    params = (userId, discountId)

    insert_result = insert_to_db(cmd, params)
    if insert_result:
        return {"discount_register":True}
    else:
        return {"discount_register":False}

@app.route('/register_user_message' , methods=['GET'])
def registar_user_message():
    id_user = request.args.get('id_user', None)
    id_shop = request.args.get('id_shop', None)
    text = request.args.get('text', None)

    if id_user==None or id_shop==None or text==None:
        abort(400)

    cmd = f"INSERT INTO {TABLE_MESSAGE} ({TABLE_MESSAGE_ID_USER}, {TABLE_MESSAGE_ID_SHOP}, {TABLE_MESSAGE_TEXT}) VALUES (%s, %s, %s)"
    params = (id_user, id_shop, text)

    insert_result = insert_to_db(cmd, params)
    if insert_result:
        cmd = f"SELECT * FROM {TABLE_MESSAGE} WHERE {TABLE_MESSAGE_ID_SHOP}={id_shop} AND {TABLE_MESSAGE_ID_USER}={id_user}"
        select_result = select_from_db(cmd)
        if len(select_result) == 1:
            id_user,id_shop,text = select_result[0]
            return {"message_register":True, "message":{"id_user":id_user ,"id_shop":id_shop , "text":text }}
        else:
            return {"message_register":False, "message":{}}
    else:
        return {"message_register":False, "message":{}}

@app.route('/submit_question' , methods=['GET'])
def submit_question():
    id_user = request.args.get('id_user', None)
    id_shop = request.args.get('id_shop', None)

    if id_user==None or id_shop==None :
        abort(400)

    question_answer = dict(request.args.items())
    question_answer.pop('id_user')
    question_answer.pop('id_shop')

    values = []
    for id_question,score in question_answer.items():
        values.append((id_user,id_shop,id_question,score))

    cmd = f"INSERT INTO {TABLE_USER_QUESTION} ({TABLE_USER_QUESTION_ID_USER}, {TABLE_USER_QUESTION_ID_SHOP}, {TABLE_USER_QUESTION_ID_QUESTION}, {TABLE_USER_QUESTION_SCORE}) VALUES (%s, %s, %s, %s)"

    insert_result = insert_to_db(cmd, values , True)
    if insert_result:
        return {"registered":True}
    else:
        return {"registered":False}

@app.route('/user_answered_question' , methods=['GET'])
def get_user_answered_question():
    id_user = request.args.get('id_user', None)
    id_shop = request.args.get('id_shop', None)

    if id_user==None or id_shop==None :
        abort(400)

    cmd = f'''SELECT {TABLE_QUESTION}.{TABLE_QUESTION_ID} , {TABLE_QUESTION}.{TABLE_QUESTION_CONTENT}, {TABLE_USER_QUESTION}.{TABLE_USER_QUESTION_SCORE} FROM {TABLE_USER_QUESTION} 
JOIN {TABLE_USER} ON {TABLE_USER}.{TABLE_USER_ID} = {TABLE_USER_QUESTION}.{TABLE_USER_QUESTION_ID_USER} 
JOIN {TABLE_QUESTION} ON {TABLE_USER_QUESTION}.{TABLE_USER_QUESTION_ID_QUESTION} = {TABLE_QUESTION}.{TABLE_QUESTION_ID} 
WHERE {TABLE_USER_QUESTION}.{TABLE_USER_QUESTION_ID_SHOP}={id_shop} AND {TABLE_USER_QUESTION}.{TABLE_USER_QUESTION_ID_USER} ={id_user}'''
    
    ans = select_from_db(cmd)
    result = []
    for item in ans : 
        id_question,content, score = item
        result.append({"id_question":id_question , "content":content , "score":score})
    
    return {"result":result}

@app.route('/delete_user_survey' , methods=['GET'])
def delete_user_survey():
    id_user = request.args.get('id_user', None)
    id_shop = request.args.get('id_shop', None)

    if id_user==None or id_shop==None :
        abort(400)

    cmd = f"DELETE FROM {TABLE_MESSAGE} WHERE {TABLE_MESSAGE}.{TABLE_MESSAGE_ID_USER}=%s AND {TABLE_MESSAGE}.{TABLE_MESSAGE_ID_SHOP}=%s"
    params = (id_user, id_shop)
    message_result = delete_from_db(cmd , params)

    cmd = f"DELETE FROM {TABLE_USER_QUESTION} WHERE {TABLE_USER_QUESTION}.{TABLE_USER_QUESTION_ID_USER}=%s AND {TABLE_USER_QUESTION}.{TABLE_USER_QUESTION_ID_SHOP}=%s"
    params = (id_user, id_shop)
    user_question_result=delete_from_db(cmd , params)
    if((message_result == True) and (user_question_result == True)) :
        return {"result":True}
    else:
        return {"result":False}

if __name__ == "__main__":
    app.run("localhost" , 5000 , True)