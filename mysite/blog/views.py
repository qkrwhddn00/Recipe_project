import json
import os
import re

import pymysql
import requests
from django.conf import settings
from django.contrib import messages
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from dotenv import load_dotenv

from blog import query_sql as q
from blog import stable_diffusion as sd


def mysql_rdb_conn():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        database="RECIPE",
        port=3306,
    )


def mypage(request):
    return render(request, "blog/mypage.html")


def home_view(request):
    return render(request, "blog/home.html")


def main_view(request):
    return render(request, "blog/main.html")


def signup_view(request):
    return render(request, "blog/signup.html")


def recommend(request):
    return render(request, "blog/recommend.html")


def result(request):
    return render(request, "blog/result.html")


def signup(request):
    if request.method == "POST":
        nickname = request.POST["nickname"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm-password"]

        try:
            with mysql_rdb_conn() as conn:
                with conn.cursor() as curs:
                    curs.execute(q.select_nickname_from_users(), (nickname,))
                    if curs.fetchone():
                        messages.error(request, "이미 사용 중인 닉네임입니다.")
                        return redirect("signup")

                    if "@" not in email:
                        messages.error(request, "올바른 이메일 형식을 입력해 주세요.")
                        return redirect("signup")

                    if password != confirm_password:
                        messages.error(request, "비밀번호가 일치하지 않습니다.")
                        return redirect("signup")

                    user_id = nickname
                    regi_data = (user_id, nickname, email, password)
                    curs.execute(q.mem_register(), regi_data)
                    conn.commit()

                    messages.success(request, "회원가입이 완료되었습니다.")
                    return redirect("home")

        except Exception as e:
            messages.error(request, f"Unexpected error: {e}")
            return redirect("signup")

    return render(request, "blog/signup.html")


def login(request):
    if request.method == "POST":
        nickname = request.POST["nickname"]
        password = request.POST["password"]

        settings.GLOBAL_NICKNAME = nickname

        if not nickname:
            messages.error(request, "닉네임을 입력해 주세요.")
            return redirect("home")

        if not password:
            messages.error(request, "비밀번호를 입력해 주세요.")
            return redirect("home")

        try:
            with mysql_rdb_conn() as conn:
                with conn.cursor() as curs:
                    curs.execute(q.select_nickname_from_users(), (nickname,))
                    if curs.fetchone() is None:
                        messages.error(request, "아이디가 존재하지 않습니다.")
                        return redirect("home")

                    curs.execute(q.select_password_from_users(), (nickname,))
                    row = curs.fetchone()
                    db_password = row[0] if row else None

                    if db_password is None or password != db_password:
                        messages.error(request, "비밀번호가 틀립니다.")
                        return redirect("home")

                    messages.success(request, "로그인이 완료되었습니다.")
                    return redirect("main")

        except Exception as e:
            messages.error(request, f"Unexpected error: {e}")
            return redirect("home")

    return render(request, "home")


def guest_login(request):
    if request.method == "POST":
        settings.GLOBAL_NICKNAME = "게스트"
        return redirect("main")
    return render(request, "home")


def get_gpt_response(request):
    load_dotenv()
    gpt_api_key = os.getenv("GPT_API_KEY")
    gpt_api_url = os.getenv("GPT_API_URL")

    ingredient_input = ""
    if request.method == "POST":
        ingredient_input = request.POST.get("ingredientInput", "").replace("{", "{{").replace("}", "}}")

    gpt_response = None
    api_error = ""
    dish_type, dish_name, recipe_steps, image_url, keyword = "", "", [], "", ""

    prompt = f"""
    당신은 요리 추천과 레시피 작성을 도와주는 AI 셰프입니다.
    사용자가 제공한 재료를 바탕으로 가장 잘 어울리는 요리를 추천하고, 자세한 조리 단계를 작성해 주세요.
    출력은 반드시 JSON 형식만 반환하세요.

    입력 재료:
    {ingredient_input}

    출력 형식:
    {{
        "dish_type": "한식/중식/일식/양식/디저트 중 하나",
        "dish_name": "추천 요리 이름",
        "recipe_steps": ["조리 단계 1", "조리 단계 2", "조리 단계 3", "조리 단계 4", "조리 단계 5"],
        "keyword": "image generation prompt in English"
    }}
    """

    if request.method == "POST":
        headers = {
            "Authorization": f"Bearer {gpt_api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
        }

        try:
            response = requests.post(gpt_api_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            gpt_response = response.json()["choices"][0]["message"]["content"].strip()
            print("Raw GPT response:", gpt_response)

            json_match = re.search(r"\{.*\}", gpt_response, re.DOTALL)
            if not json_match:
                raise ValueError("JSON block not found in GPT response")

            parsed_response = json.loads(json_match.group(0))
            dish_type = parsed_response.get("dish_type", "")
            dish_name = parsed_response.get("dish_name", "")
            recipe_steps = parsed_response.get("recipe_steps", [])
            keyword = parsed_response.get("keyword", "")

            image_url = sd.generate_image(dish_name, keyword) if dish_name else ""
            recipe_steps = [re.sub(r"^\d+\.\s*", "", step) for step in recipe_steps]

            if settings.GLOBAL_NICKNAME != "게스트":
                inset_list_data = json.dumps(recipe_steps, ensure_ascii=False)
                with mysql_rdb_conn() as conn:
                    with conn.cursor() as curs:
                        query = """
                        INSERT INTO userlist (nickname, recom_rec_name, list, image_url, prompt, keyword)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        curs.execute(
                            query,
                            (
                                settings.GLOBAL_NICKNAME,
                                dish_name,
                                inset_list_data,
                                image_url,
                                ingredient_input,
                                keyword,
                            ),
                        )
                        conn.commit()
            else:
                messages.error(request, "게스트는 마이페이지 접근이 불가능합니다.")

        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON parsing error: {e}")
            print("Raw GPT response:", gpt_response)
            dish_type, dish_name, recipe_steps, image_url, keyword = "", "", [], "", ""
            api_error = "AI 응답 형식을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요."

        except requests.exceptions.RequestException as e:
            status_code = getattr(getattr(e, "response", None), "status_code", None)
            response_text = getattr(getattr(e, "response", None), "text", "")
            error_payload = {}

            try:
                if getattr(e, "response", None) is not None:
                    error_payload = e.response.json()
            except ValueError:
                error_payload = {}

            error_type = error_payload.get("error", {}).get("type", "")
            error_message = error_payload.get("error", {}).get("message", "")

            print(f"OpenAI API request failed: status={status_code}, type={error_type}, message={error_message}")
            if response_text:
                print(f"OpenAI API raw response: {response_text}")

            if status_code == 429:
                if error_type == "insufficient_quota":
                    api_error = "OpenAI API 사용 한도 또는 크레딧이 부족합니다. 결제/Usage를 확인해 주세요."
                else:
                    api_error = "요청이 너무 많아 잠시 제한되었습니다. 잠시 후 다시 시도해 주세요."
            elif status_code == 401:
                api_error = "OpenAI API 키가 올바르지 않습니다. .env 설정을 확인해 주세요."
            elif status_code == 403:
                api_error = "OpenAI API 접근이 거부되었습니다. 계정 또는 권한 설정을 확인해 주세요."
            else:
                api_error = "OpenAI API 요청 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."

            messages.error(request, api_error)

    return render(
        request,
        "blog/result.html",
        {
            "ingredientInput": ingredient_input,
            "dish_type": dish_type,
            "dish_name": dish_name,
            "recipe_steps": recipe_steps,
            "image_url": image_url,
            "prompt": prompt,
            "keyword": keyword,
            "api_error": api_error,
        },
    )


def result_by_type(request):
    if request.method == "POST":
        request.POST.get("{{recipe.rec_name}}")
    settings.GLOBAL_SELECT_TYPE = request.POST["name"]
    return render(request, "blog/home.html")


def ko_food(request, category):
    with connection.cursor() as cursor:
        sql, params = q.select_ko_from_recipes(category)
        cursor.execute(sql, params)
        results = cursor.fetchall()

    recipes = [
        {
            "rec_id": row[0],
            "rec_name": row[1],
            "rec_descrip": row[2],
            "rec_detail": row[3],
            "rec_img": f"{row[4]}" if row[4] else None,
        }
        for row in results
    ]

    return render(request, "blog/koreanfood.html", {"recipes": recipes, "category": category})


def recipe_detail(request, rec_id):
    if request.method == "POST":
        rec_id = request.POST.get("rec_id")
        print(f"POST request received, rec_id: {rec_id}")

        if rec_id:
            recipe = get_object_or_404("rec_id")
            return render(request, "recipe_detail.html", {"recipe": recipe})
        return render(request, "recipe_detail.html", {"error": "레시피 ID가 없습니다."})

    if rec_id:
        try:
            rec_id = int(rec_id)

            with mysql_rdb_conn() as conn:
                with conn.cursor() as curs:
                    curs.execute(q.select_foodname_by_id(), (rec_id,))
                    rec_name = curs.fetchone()

                    curs.execute(q.select_descrip_by_id(), (rec_id,))
                    rec_descrip = curs.fetchone()

                    curs.execute(q.select_img_by_id(), (rec_id,))
                    rec_img = curs.fetchone()

                    curs.execute(q.find_steps(), (rec_id,))
                    rec_detail = curs.fetchall()

                    curs.execute(q.find_number(), (rec_id,))
                    rec_number = curs.fetchone()

                    rec_number = int(rec_number[0]) if rec_number else 0
                    rec_detail_list = [row[0] for row in rec_detail] if rec_detail else ["상세 정보 없음"]

                    if rec_name:
                        return render(
                            request,
                            "recipe_detail.html",
                            {
                                "rec_name": rec_name[0] if rec_name else "정보 없음",
                                "rec_descrip": rec_descrip[0] if rec_descrip else "설명 없음",
                                "rec_img": rec_img[0] if rec_img else None,
                                "rec_detail": rec_detail_list,
                            },
                        )

                    messages.error(request, "레시피를 찾을 수 없습니다.")
                    print("레시피를 찾을 수 없습니다.")
                    return redirect("main")

        except ValueError:
            messages.error(request, "잘못된 레시피 ID 형식입니다.")
            print("잘못된 레시피 ID 형식입니다.")
            return redirect("main")

        except Exception as e:
            messages.error(request, f"Unexpected error: {e}")
            print(f"Unexpected error: {e}")
            return redirect("main")

    messages.error(request, "잘못된 요청입니다.")
    print("잘못된 요청입니다.")
    return redirect("main")


def user_list_view(request):
    with connection.cursor() as cursor:
        sql = """
            SELECT * FROM userlist where nickname = %s
        """
        cursor.execute(sql, (settings.GLOBAL_NICKNAME,))
        results = cursor.fetchall()

    users = [
        {
            "id": row[0],
            "nickname": row[1],
            "recom_rec_name": row[2],
            "list": row[3],
            "image_url": row[4],
            "prompt": row[5],
        }
        for row in results
    ]
    print("users:", users)
    return render(request, "blog/mypage.html", {"users": users})


def delete_selected_recipes(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            selected_ids = data.get("selected_ids", [])

            if not selected_ids:
                return JsonResponse({"status": "error", "message": "삭제할 레시피를 선택하세요!"})

            selected_ids = [int(item) for item in selected_ids if str(item).isdigit()]

            with connection.cursor() as cursor:
                format_strings = ",".join(["%s"] * len(selected_ids))
                sql = f"DELETE FROM userlist WHERE id IN ({format_strings})"
                cursor.execute(sql, selected_ids)

            return JsonResponse({"status": "success", "message": "선택한 레시피 삭제 완료!"})

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "잘못된 JSON 데이터"}, status=400)

    return JsonResponse({"status": "error", "message": "잘못된 요청"}, status=400)


def delete_all_recipes(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            if data.get("action") != "delete_all":
                return JsonResponse({"status": "error", "message": "잘못된 요청"}, status=400)

            with connection.cursor() as cursor:
                sql = """DELETE FROM userlist WHERE nickname = %s"""
                cursor.execute(sql, settings.GLOBAL_NICKNAME)

            return JsonResponse({"status": "success", "message": "전체 레시피 삭제 완료!"})

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "잘못된 JSON 데이터"}, status=400)

    return JsonResponse({"status": "error", "message": "잘못된 요청"}, status=400)
