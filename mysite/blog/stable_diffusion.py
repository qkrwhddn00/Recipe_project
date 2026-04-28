import os
import torch
from PIL import Image
from diffusers import StableDiffusionPipeline
import pymysql
from django.conf import settings

# 파스타면 1인분, 계란, 베이컨

def mysql_rdb_conn():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        database="RECIPE",
        port=3306
    )

# Stable Diffusion 모델 로드
MODEL_PATH = "runwayml/stable-diffusion-v1-5"
device = "cuda" if torch.cuda.is_available() else "cpu"

pipe = StableDiffusionPipeline.from_pretrained(MODEL_PATH)
pipe.to(device)

# 이미지 저장 폴더 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 현재 스크립트 경로
STATIC_IMAGE_PATH = os.path.join(BASE_DIR, "..", "blog", "static", "generated")
# os.makedirs(STATIC_IMAGE_PATH, exist_ok=True)


def generate_image(prompt: str,keyword: str):
    """Stable Diffusion을 실행하여 음식 이미지를 생성하고 저장하여 URL 반환"""
    print(f"🔹 Stable Diffusion 실행: {prompt}")
    
    promptgen = keyword


    print(f"📌 최종 프롬프트: {promptgen}")


    # 이미지 생성 시도
    try:
        with mysql_rdb_conn() as conn:
            with conn.cursor() as curs:
                sql = """select recom_rec_name from userlist where recom_rec_name = %s and nickname = %s"""
                data = (prompt, settings.GLOBAL_NICKNAME)
                curs.execute(sql, data)
                res = curs.fetchone()
                if not res:
                    # image = pipe(f"high-quality, realistic photo of {promptgen} plated on a table").images[0]
                    image = pipe(promptgen).images[0]
                    print("이미지 생성 완료")
                        # 이미지 파일명 설정 (공백 제거)
                    image_filename = f"{prompt.replace(', ', '_').replace(' ', '')}.png"
                    image_path = os.path.join(STATIC_IMAGE_PATH, image_filename)
                    image_url = f"{image_filename}"
                    print(f" 저장될 이미지 경로: {image_path}")  
                    try:
                        image.save(image_path)
                        print(f"이미지 저장 완료: {image_path}")
                    except Exception as e:
                        print(f"이미지 저장 오류: {e}")
                        return None  # 저장 실패 시 None 반환
                else:
                    print("이미지 있음 !")
                    image_filename = f"{prompt.replace(', ', '_').replace(' ', '')}.png"
                    image_path = os.path.join(STATIC_IMAGE_PATH, image_filename)
                    image_url = f"{image_filename}"
    except Exception as e:
        print(f"Stable Diffusion 오류 발생: {e}")
        return None  # 오류 발생 시 None 반환

    return image_url  # 웹에서 접근 가능한 URL 반환