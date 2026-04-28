# users 테이블 관련
def mem_register():
    sql = """INSERT INTO users(user_id, nickname, email, password)
    VALUES (%s, %s, %s, %s)"""
    return sql


def select_nickname_from_users():
    sql = """
    SELECT nickname from users where nickname = %s
    """
    return sql


def select_password_from_users():
    sql = """
    SELECT password from users where nickname = %s
    """
    return sql


def select_ko_from_recipes(category):
    sql = """
    SELECT rec_id, rec_name, rec_descrip, rec_detail, rec_img FROM recipes WHERE rec_type = %s
    """
    return sql, [category]


# recipes 테이블 관련 - 음식이름으로
def select_foodname_by_id():  # 음식의 이름별로 음식 카테고리리
    sql = """ 
    SELECT rec_name from recipes where rec_id = %s
    """
    return sql


def select_descrip_by_id():  # 음식의 이름별로 음식 설명 조회
    sql = """ 
    SELECT rec_descrip from recipes where rec_id = %s
    """
    return sql


def select_img_by_id():  # 음식의 이름별로 음식 사진 조회
    sql = """ 
    SELECT rec_img from recipes where rec_id = %s
    """
    return sql


# user_list 관련
def insert_list_recom():
    sql = """
    INSERT INTO userlist (nickname,recom_rec_name,list) VALUES (%s,%s,%s)
    """
    return sql


def find_steps():
    sql = """
    select step_description from recipe_steps where rec_id = %s
    """
    return sql


def find_number():
    sql = """
    select step_number from recipe_steps where rec_id = %s
    """
    return sql
