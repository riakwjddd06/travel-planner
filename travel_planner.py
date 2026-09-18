import argparse
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()


def search_restaurants(city, kakao_api_key, errors):
    print("\n[카카오 맛집 검색]")

    url = "https://dapi.kakao.com/v2/local/search/keyword.json"

    headers = {
        "Authorization": f"KakaoAK {kakao_api_key}"
    }

    params = {
        "query": f"{city} 맛집",
        "size": 5
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=5
        )

        response.raise_for_status()

        data = response.json()
        places = data["documents"]

        if len(places) == 0:
            errors.append({
                "step": "place_search",
                "type": "EMPTY_RESULT",
                "message": f"0 results for query={city} 맛집"
        })

        restaurants = []

        for place in places:
            restaurant = {
             "name": place["place_name"],
             "address": place["address_name"],
             "category": place["category_name"],
             "url": place["place_url"],
             "x": float(place["x"]),
             "y": float(place["y"])
            }

            restaurants.append(restaurant)
    

        print("검색 결과:", len(places), "곳")

        for index, restaurant in enumerate(restaurants, start=1):
            print()
            print(index, ".", restaurant["name"])
            print("주소:", restaurant["address"])
            print("카테고리:", restaurant["category"])

        return restaurants

    except requests.exceptions.RequestException as e:
      print("카카오 API 요청 실패:", e)

      error_type = "REQUEST_ERROR"
      message = str(e)

      if e.response is not None:
          print("카카오 오류 내용:", e.response.text)

          if e.response.status_code in [401, 403]:
             error_type = "AUTH_ERROR"
             message = f"HTTP {e.response.status_code}"

      errors.append({
         "step": "place_search",
         "type": error_type,
         "message": message
      })

      return []

def get_previous_recommended_cities(date):
    previous_cities = []

    if not os.path.exists("results"):
        return previous_cities

    for filename in os.listdir("results"):
        if not filename.startswith(f"{date}_raw"):
            continue

        if not filename.endswith(".json"):
            continue

        file_path = os.path.join("results", filename)

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            recommendation = data.get("recommendation")

            if recommendation:
                city = recommendation.get("recommended_city")

                if city and city not in previous_cities:
                    previous_cities.append(city)

        except (json.JSONDecodeError, OSError):
            continue

    return previous_cities

def get_travel_recommendation(date, openai_api_key, errors):
    print("\n[1/3] 여행지 추천 생성 중...")

    previous_cities = get_previous_recommended_cities(date)

    url = "https://copa.codyssey.kr/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }

    if previous_cities:
        previous_city_text = ", ".join(previous_cities)
    else:
        previous_city_text = "없음"

    prompt = f"""
여행 날짜는 {date}입니다.

이 날짜에 국내에서 여행하기 좋은 지역 1곳을 추천해주세요.

같은 날짜의 이전 실행에서 이미 추천된 지역:
{previous_city_text}

가능하면 위의 이전 추천 지역과 겹치지 않는 다른 지역을 추천해주세요.
단, 여행 날짜와 계절을 고려했을 때 적절한 국내 여행지여야 합니다.

반드시 아래 형식의 JSON만 출력하세요.
설명문, 마크다운, ```json 같은 표시는 절대 넣지 마세요.

{{
    "recommended_city": "도시 이름",
    "weather": "해당 시기의 일반적인 날씨 요약",
    "events": ["행사 또는 축제 후보 1", "행사 또는 축제 후보 2"],
    "reason": "추천 이유를 2~4문장으로 작성"
}}

조건:
- recommended_city는 문자열
- recommended_city에는 반드시 도시 또는 지역 이름만 작성
- 관광지 이름, 괄호, 부가 설명을 넣지 말 것
- 예: "속초", "강릉", "경주", "제주"
- weather는 문자열
- events는 문자열 배열이며 1~3개
- reason은 문자열
"""

    body = {
        "model": "gpt-5-mini",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()
        result_text = data["choices"][0]["message"]["content"]

        try:
            recommendation = json.loads(result_text)

        except json.JSONDecodeError:
            print("JSON 파싱 실패 - 1회 재시도합니다.")

            retry_prompt = f"""
아래 응답을 설명 없이 올바른 JSON 형식으로만 다시 출력해주세요.

반드시 다음 필수 키를 포함하세요.

- recommended_city: string
- weather: string
- events: array of string
- reason: string

기존 응답:
{result_text}
"""

            retry_body = {
                "model": "gpt-5-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": retry_prompt
                    }
                ]
            }

            retry_response = requests.post(
                url,
                headers=headers,
                json=retry_body,
                timeout=30
            )

            retry_response.raise_for_status()

            retry_data = retry_response.json()
            retry_text = retry_data["choices"][0]["message"]["content"]

            recommendation = json.loads(retry_text)

        print("추천 지역:", recommendation["recommended_city"])

        return recommendation

    except requests.exceptions.RequestException as e:
        print("OpenAI API 요청 실패:", e)

        error_type = "REQUEST_ERROR"
        message = str(e)

        if e.response is not None:
            print("API 오류 내용:", e.response.text)

            if e.response.status_code in [401, 403]:
                error_type = "AUTH_ERROR"
                message = f"HTTP {e.response.status_code}"

            elif e.response.status_code == 429:
                error_type = "QUOTA_ERROR"
                message = "HTTP 429"

        errors.append({
            "step": "travel_recommendation",
            "type": error_type,
            "message": message
        })

        return None

    except json.JSONDecodeError as e:
        print("재시도 후에도 JSON 파싱 실패:", e)

        errors.append({
            "step": "travel_recommendation",
            "type": "JSON_PARSE_ERROR",
            "message": "JSON parsing failed after retry"
        })

        return None

def archive_previous_final(date):
    os.makedirs("results", exist_ok=True)

    # 첫 실행에서 만들어지는 final 파일
    raw_first_final = f"results/{date}_raw_final.json"
    report_first_final = f"results/{date}_travel_plan_final.md"

    # 첫 번째 final 파일이 있으면 일반 파일로 변경
    if os.path.exists(raw_first_final) or os.path.exists(report_first_final):

        if os.path.exists(raw_first_final):
            os.rename(
                raw_first_final,
                f"results/{date}_raw.json"
            )

        if os.path.exists(report_first_final):
            os.rename(
                report_first_final,
                f"results/{date}_travel_plan.md"
            )

        return

    # 두 번째 실행 이후의 numbered final 파일 확인
    count = 1

    while True:
        raw_normal = f"results/{date}_raw({count}).json"
        report_normal = f"results/{date}_travel_plan({count}).md"

        raw_final = f"results/{date}_raw({count})_final.json"
        report_final = f"results/{date}_travel_plan({count})_final.md"

        # final 파일을 찾은 경우 일반 기록으로 변경
        if os.path.exists(raw_final) or os.path.exists(report_final):

            if os.path.exists(raw_final):
                os.rename(
                    raw_final,
                    raw_normal
                )

            if os.path.exists(report_final):
                os.rename(
                    report_final,
                    report_normal
                )

            return

        # 일반 파일도 없고 final 파일도 없으면
        # 더 이상 찾을 파일이 없으므로 반복 종료
        if (
            not os.path.exists(raw_normal)
            and not os.path.exists(report_normal)
        ):
            return

        count += 1


def get_next_run_number(date):
    # 번호 없는 과거 파일이 없으면 첫 실행
    raw_base = f"results/{date}_raw.json"
    report_base = f"results/{date}_travel_plan.md"

    raw_first_final = f"results/{date}_raw_final.json"
    report_first_final = f"results/{date}_travel_plan_final.md"

    if (
        not os.path.exists(raw_base)
        and not os.path.exists(report_base)
        and not os.path.exists(raw_first_final)
        and not os.path.exists(report_first_final)
    ):
        return 0

    count = 1

    while True:
        raw_normal = f"results/{date}_raw({count}).json"
        raw_final = f"results/{date}_raw({count})_final.json"

        report_normal = f"results/{date}_travel_plan({count}).md"
        report_final = f"results/{date}_travel_plan({count})_final.md"

        if (
            not os.path.exists(raw_normal)
            and not os.path.exists(raw_final)
            and not os.path.exists(report_normal)
            and not os.path.exists(report_final)
        ):
            return count

        count += 1

def save_raw_json(
    date,
    recommendation,
    restaurants,
    errors,
    run_number
):
    os.makedirs("results", exist_ok=True)

    result_data = {
        "recommendation": recommendation,
        "restaurants": restaurants,
        "errors": errors
    }

    if run_number == 0:
        file_path = f"results/{date}_raw_final.json"
    else:
        file_path = f"results/{date}_raw({run_number})_final.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            result_data,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\n원본 JSON 저장 완료:", file_path)

    return file_path

def generate_final_report(date, recommendation, restaurants, errors, openai_api_key):
    print("\n[3/3] 최종 리포트 생성 중...")

    url = "https://copa.codyssey.kr/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }

    restaurant_text = json.dumps(
        restaurants,
        ensure_ascii=False,
        indent=2
    )

    error_text = json.dumps(
        errors,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
여행 날짜는 {date}입니다.

아래 여행 추천 정보와 맛집 검색 결과를 바탕으로
국내 여행 추천 리포트를 Markdown 형식으로 작성해주세요.

[여행 추천 정보]
{json.dumps(recommendation, ensure_ascii=False, indent=2)}

[맛집 검색 결과]
{restaurant_text}

[오류 목록]
{error_text}

반드시 아래 항목을 포함하세요.

# {date} 국내 여행 추천 리포트

## 추천 지역

## 추천 이유

## 날씨 요약

## 행사/축제

## 맛집 추천

## 1일 일정 제안

## 오류 요약(errors)

조건:
- 맛집이 0곳이면 "데이터 없음"이라고 작성
- 오전 / 오후 / 저녁으로 나눠 1일 일정을 제안
- 오류 목록이 비어 있으면 "없음"이라고 작성
- Markdown 텍스트만 출력
"""

    body = {
        "model": "gpt-5-mini",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()
        report = data["choices"][0]["message"]["content"]

        print("리포트 생성 완료")

        return report

    except requests.exceptions.RequestException as e:
        print("최종 리포트 생성 실패:", e)

        if e.response is not None:
            print("API 오류 내용:", e.response.text)

        return None

def save_markdown_report(date, report, run_number):
    if run_number == 0:
        file_path = f"results/{date}_travel_plan_final.md"
    else:
        file_path = (
            f"results/{date}_travel_plan({run_number})_final.md"
        )

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(report)

    print("최종 리포트 저장 완료:", file_path)

    return file_path

parser = argparse.ArgumentParser(
    description="국내 여행지 추천 프로그램"
)

parser.add_argument(
    "-date",
    "--date",
    required=True,
    help="여행 날짜를 YYYY-MM-DD 형식으로 입력하세요."
)

args = parser.parse_args()


try:
    datetime.strptime(args.date, "%Y-%m-%d")
    print("입력한 날짜:", args.date)

except ValueError:
    parser.error("날짜는 YYYY-MM-DD 형식으로 입력해주세요.")


openai_api_key = os.getenv("OPENAI_API_KEY")
kakao_api_key = os.getenv("KAKAO_REST_API_KEY")


if not openai_api_key:
    print("OpenAI API 키가 설정되지 않았습니다.")
    print(".env 파일에 OPENAI_API_KEY를 설정해주세요.")
    raise SystemExit(1)

print("OpenAI API 키 확인 완료")


if not kakao_api_key:
    print("Kakao API 키가 설정되지 않았습니다.")
    print(".env 파일에 KAKAO_REST_API_KEY를 설정해주세요.")
    raise SystemExit(1)

print("Kakao API 키 확인 완료")

archive_previous_final(args.date)
run_number = get_next_run_number(args.date)

errors = []

recommendation = get_travel_recommendation(
    args.date,
    openai_api_key,
    errors
)

if recommendation:
    print("\n[OpenAI 추천 결과]")
    print(json.dumps(
        recommendation,
        ensure_ascii=False,
        indent=2
    ))

    city = recommendation["recommended_city"]
    restaurants = search_restaurants(
      city,
      kakao_api_key,
      errors
    )

    save_raw_json(
       args.date,
       recommendation,
       restaurants,
       errors,
       run_number
    )

    report = generate_final_report(
        args.date,
        recommendation,
        restaurants,
        errors,
        openai_api_key
    )

    if report:
        save_markdown_report(
          args.date,
          report,
          run_number
        )