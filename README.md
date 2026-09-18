# 국내 여행지 추천 프로그램

## 1. 프로그램 소개

사용자가 여행 날짜를 입력하면 국내 여행지를 추천하고,  
추천된 지역의 맛집을 검색한 뒤 최종 여행 리포트를 생성하는 Python 프로그램입니다.

이 프로그램은 두 종류의 API를 연동하여 동작합니다.

- Codyssey OpenAI 호환 API
  - 국내 여행지 추천
  - 최종 여행 리포트 생성
- Kakao Local API
  - 추천 지역의 맛집 검색

프로그램은 CLI(Command Line Interface) 방식으로 실행합니다.

---

## 2. 주요 기능

1. CLI에서 여행 날짜 입력
2. 입력한 날짜 형식 검증
3. LLM API를 이용한 국내 여행지 추천
4. 추천 결과를 JSON 형식으로 변환
5. 추천된 지역명을 Kakao Local API의 검색어로 활용
6. 추천 지역의 맛집 최대 5곳 검색
7. 추천 정보, 맛집 정보, 오류 정보를 JSON으로 저장
8. 최종 여행 리포트를 Markdown 파일로 저장
9. API 오류 및 검색 결과 없음 상태 처리
10. LLM JSON 파싱 실패 시 1회 재요청
11. 같은 날짜로 여러 번 실행해도 기존 결과를 삭제하지 않고 보관
12. 가장 최근 실행 결과에는 `_final` 표시
13. 같은 날짜로 다시 실행할 경우 이전 추천 지역을 확인하여 가능한 한 다른 지역을 추천

---

## 3. 실행 방법

터미널에서 프로젝트 폴더로 이동한 뒤 다음 명령어를 실행합니다.

```bash
python3 travel_planner.py --date "2026-10-15"
```

또는 다음 형식도 사용할 수 있습니다.

```bash
python3 travel_planner.py -date "2026-10-15"
```

`-date`, `--date` 두 옵션 모두 같은 기능을 합니다.

날짜는 반드시 아래 형식으로 입력해야 합니다.

```text
YYYY-MM-DD
```

예:

```bash
python3 travel_planner.py --date "2026-12-25"
```

잘못된 날짜를 입력하면 프로그램은 오류 메시지와 사용 방법을 출력한 뒤 종료합니다.

예:

```bash
python3 travel_planner.py --date "2026-99-99"
```

---

## 4. 필요한 Python 패키지

다음 패키지가 필요합니다.

```bash
pip3 install requests python-dotenv
```

### 사용 모듈

- `argparse`
  - CLI에서 날짜 옵션을 입력받기 위해 사용합니다.

- `os`
  - 환경변수 확인, 폴더 생성, 파일 존재 여부 확인 등에 사용합니다.

- `requests`
  - 외부 API에 HTTP 요청을 보내기 위해 사용합니다.

- `json`
  - LLM 응답을 JSON으로 변환하고 결과 파일을 저장하기 위해 사용합니다.

- `datetime`
  - 사용자가 입력한 날짜가 실제 날짜 형식인지 검사하기 위해 사용합니다.

- `python-dotenv`
  - `.env` 파일에 저장된 API 키를 환경변수로 불러오기 위해 사용합니다.

---

## 5. API 키 설정 방법

프로젝트 폴더에 `.env` 파일을 생성합니다.

`.env` 파일 안에는 다음 형식으로 API 키를 입력합니다.

```text
OPENAI_API_KEY=발급받은_OpenAI_호환_API_키
KAKAO_REST_API_KEY=발급받은_Kakao_REST_API_키
```

이 프로젝트에서는 Codyssey에서 발급받은 OpenAI 호환 API 키를 사용합니다.

Kakao API는 Kakao Developers에서 발급받은 REST API 키를 사용합니다.

API 키가 설정되지 않은 경우 프로그램은 설정 방법을 출력한 뒤 즉시 종료합니다.

예:

```text
OpenAI API 키가 설정되지 않았습니다.
.env 파일에 OPENAI_API_KEY를 설정해주세요.
```

또는:

```text
Kakao API 키가 설정되지 않았습니다.
.env 파일에 KAKAO_REST_API_KEY를 설정해주세요.
```

---

## 6. API 키 보안

API 키는 Python 코드에 직접 작성하지 않습니다.

API 키는 `.env` 파일에 저장하고 환경변수로 불러옵니다.

`.gitignore` 파일에는 다음 내용을 포함합니다.

```text
.env
```

이를 통해 `.env` 파일이 Git 저장소에 포함되지 않도록 합니다.

API 키가 다음 위치에 노출되지 않도록 주의해야 합니다.

- GitHub 저장소
- README.md
- 실행 로그
- JSON 결과 파일
- Markdown 결과 파일
- 화면 캡처
- 제출용 ZIP 파일

제출용 프로젝트에는 실제 `.env` 파일을 포함하지 않습니다.

---

## 7. 프로그램 실행 흐름

프로그램은 다음 순서로 실행됩니다.

```text
사용자가 여행 날짜 입력
        ↓
날짜 형식 검증
        ↓
API 키 존재 여부 확인
        ↓
기존 같은 날짜의 결과 파일 확인
        ↓
이전 추천 지역 확인
        ↓
LLM API로 여행 지역 추천
        ↓
LLM 결과를 JSON으로 파싱
        ↓
recommended_city 추출
        ↓
Kakao Local API로 맛집 검색
        ↓
추천 정보 + 맛집 정보 + errors 저장
        ↓
LLM API로 최종 Markdown 리포트 생성
        ↓
결과 파일 저장
```

예를 들어 LLM이 다음과 같이 추천한 경우:

```json
{
  "recommended_city": "속초"
}
```

프로그램은 `recommended_city` 값을 사용하여 Kakao API에 다음과 같은 검색어를 전달합니다.

```text
속초 맛집
```

즉, 첫 번째 API의 출력 결과를 두 번째 API의 입력으로 사용하는 구조입니다.

---

## 8. 이전 추천 지역 중복 방지

같은 날짜로 프로그램을 여러 번 실행하면 LLM이 비슷한 지역을 반복해서 추천할 수 있습니다.

이를 줄이기 위해 프로그램은 기존 `results/` 폴더의 JSON 파일에서 이전에 추천된 도시를 확인합니다.

예를 들어 같은 날짜의 이전 결과가 다음과 같다면:

```text
경주
강릉
제주
```

다음 LLM 요청에는 이전 추천 도시 정보를 함께 전달합니다.

```text
같은 날짜의 이전 실행에서 이미 추천된 지역:
경주, 강릉, 제주

가능하면 위의 이전 추천 지역과 겹치지 않는 다른 지역을 추천해주세요.
```

이를 통해 날짜와 계절을 고려하면서도 가능한 한 다양한 국내 여행지를 추천하도록 구성했습니다.

---

## 9. LLM 여행지 추천 JSON 구조

LLM은 반드시 JSON으로 파싱할 수 있는 결과를 생성하도록 프롬프트를 작성했습니다.

최소 구조는 다음과 같습니다.

```json
{
  "recommended_city": "속초",
  "weather": "10월 중순의 일반적인 날씨 요약",
  "events": [
    "설악산 단풍철 산행",
    "지역 가을 행사"
  ],
  "reason": "가을 여행에 적합한 이유를 2~4문장으로 작성합니다."
}
```

필수 필드는 다음과 같습니다.

- `recommended_city`
  - 문자열
  - 추천 도시 또는 지역 이름

- `weather`
  - 문자열
  - 해당 시기의 일반적인 날씨 설명

- `events`
  - 문자열 배열
  - 행사 또는 축제 후보 1~3개

- `reason`
  - 문자열
  - 추천 이유 2~4문장

`recommended_city`에는 관광지 설명이나 괄호를 넣지 않고 도시 또는 지역 이름만 출력하도록 프롬프트를 설정했습니다.

예:

```text
속초
강릉
경주
제주
```

---

## 10. Kakao Local 맛집 검색

LLM이 추천한 `recommended_city` 값을 이용하여 Kakao Local API에 맛집을 검색합니다.

예:

```text
recommended_city: 속초
```

검색어:

```text
속초 맛집
```

검색 결과는 최대 5곳까지 사용합니다.

맛집 데이터는 다음 구조로 변환합니다.

```json
{
  "name": "맛집 이름",
  "address": "주소",
  "category": "음식점 > 한식",
  "url": "Kakao 장소 URL",
  "x": 128.000000,
  "y": 38.000000
}
```

각 필드의 의미는 다음과 같습니다.

- `name`
  - 장소 이름

- `address`
  - 장소 주소

- `category`
  - 장소 카테고리

- `url`
  - Kakao 장소 상세 페이지 URL

- `x`
  - 경도 좌표값

- `y`
  - 위도 좌표값

---

## 11. 결과 파일 저장 방식

프로그램 실행이 완료되면 `results/` 폴더에 결과가 저장됩니다.

같은 날짜로 여러 번 실행해도 기존 파일을 덮어쓰지 않습니다.

가장 최근 실행 결과에는 `_final`이 붙습니다.

### 첫 번째 실행

```text
results/
├── 2026-10-15_raw_final.json
└── 2026-10-15_travel_plan_final.md
```

### 두 번째 실행

기존 최신 결과는 일반 파일로 변경되고, 새 결과가 `_final` 파일이 됩니다.

```text
results/
├── 2026-10-15_raw.json
├── 2026-10-15_raw(1)_final.json
├── 2026-10-15_travel_plan.md
└── 2026-10-15_travel_plan(1)_final.md
```

### 세 번째 실행

```text
results/
├── 2026-10-15_raw.json
├── 2026-10-15_raw(1).json
├── 2026-10-15_raw(2)_final.json
├── 2026-10-15_travel_plan.md
├── 2026-10-15_travel_plan(1).md
└── 2026-10-15_travel_plan(2)_final.md
```

따라서 `_final`이 붙은 파일을 확인하면 가장 최근 실행 결과를 쉽게 찾을 수 있습니다.

---

## 12. 원본 JSON 파일

원본 JSON에는 최소한 다음 데이터가 포함됩니다.

```text
recommendation
restaurants
errors
```

예:

```json
{
  "recommendation": {
    "recommended_city": "속초",
    "weather": "10월 중순의 전형적인 가을 날씨",
    "events": [
      "설악산 단풍철 산행",
      "속초 지역 가을 행사"
    ],
    "reason": "설악산의 단풍과 동해를 함께 즐기기 좋은 시기입니다."
  },
  "restaurants": [
    {
      "name": "맛집 이름",
      "address": "강원특별자치도 속초시 ...",
      "category": "음식점 > 한식",
      "url": "http://place.map.kakao.com/...",
      "x": 128.000000,
      "y": 38.000000
    }
  ],
  "errors": []
}
```

정상 실행에서는 일반적으로:

```json
"errors": []
```

형태가 됩니다.

오류가 발생한 경우에는 `errors` 배열 안에 오류 정보가 저장됩니다.

---

## 13. 최종 Markdown 리포트

최종 리포트에는 다음 항목이 포함됩니다.

```markdown
# YYYY-MM-DD 국내 여행 추천 리포트

## 추천 지역

## 추천 이유

## 날씨 요약

## 행사/축제

## 맛집 추천

## 1일 일정 제안

## 오류 요약(errors)
```

1일 일정은 다음과 같이 구분합니다.

```text
오전
오후
저녁
```

맛집 검색 결과가 정상적으로 존재하는 경우 최대 5곳의 정보를 표시합니다.

검색 결과가 0건인 경우에는 다음과 같이 표시합니다.

```text
데이터 없음
```

---

## 14. 에러 처리

프로그램은 API 호출 및 데이터 처리 과정에서 발생할 수 있는 오류를 `try-except`로 처리합니다.

### 14-1. API 키 미설정

API 키가 없으면 즉시 프로그램을 종료합니다.

예:

```text
OpenAI API 키가 설정되지 않았습니다.
.env 파일에 OPENAI_API_KEY를 설정해주세요.
```

---

### 14-2. Kakao 검색 결과 0건

검색 결과가 없더라도 프로그램을 종료하지 않습니다.

맛집 결과는 빈 배열로 처리합니다.

```json
"restaurants": []
```

그리고 `errors`에 다음과 같은 내용을 저장합니다.

```json
{
  "step": "place_search",
  "type": "EMPTY_RESULT",
  "message": "0 results for query=지역명 맛집"
}
```

최종 리포트의 맛집 부분에는 `데이터 없음`이라고 표시하고 리포트 생성을 계속합니다.

---

### 14-3. Kakao API 요청 실패

네트워크 또는 인증 오류가 발생하면 오류 정보를 `errors`에 저장합니다.

예:

```json
{
  "step": "place_search",
  "type": "AUTH_ERROR",
  "message": "HTTP 403"
}
```

맛집 목록은 빈 리스트로 처리하고 최종 리포트 생성은 계속 진행합니다.

---

### 14-4. LLM JSON 파싱 실패

LLM이 정상적인 JSON을 반환하지 않는 경우 한 번 다시 요청합니다.

재요청 프롬프트에서는 필수 키만 포함한 JSON을 다시 출력하도록 요청합니다.

필수 키:

```text
recommended_city
weather
events
reason
```

재시도 후에도 JSON 변환에 실패하면 다음 오류를 기록합니다.

```json
{
  "step": "travel_recommendation",
  "type": "JSON_PARSE_ERROR",
  "message": "JSON parsing failed after retry"
}
```

---

### 14-5. LLM API 요청 실패

인증, 네트워크, 쿼터 등의 오류를 구분하여 기록합니다.

인증 오류 예:

```json
{
  "step": "travel_recommendation",
  "type": "AUTH_ERROR",
  "message": "HTTP 401"
}
```

쿼터 오류 예:

```json
{
  "step": "travel_recommendation",
  "type": "QUOTA_ERROR",
  "message": "HTTP 429"
}
```

---

## 15. 사용 API

### Codyssey OpenAI 호환 API

Base URL:

```text
https://copa.codyssey.kr/v1
```

사용 엔드포인트:

```text
https://copa.codyssey.kr/v1/chat/completions
```

사용 모델:

```text
gpt-5-mini
```

HTTP 요청 방식:

```text
POST
```

사용 목적:

- 국내 여행지 추천
- 최종 Markdown 여행 리포트 생성

---

### Kakao Local API

사용 기능:

```text
키워드 장소 검색
```

사용 엔드포인트:

```text
https://dapi.kakao.com/v2/local/search/keyword.json
```

HTTP 요청 방식:

```text
GET
```

인증 방식:

```text
Authorization: KakaoAK REST_API_KEY
```

사용 목적:

- `recommended_city + " 맛집"` 형태의 키워드 검색
- 최대 5개의 장소 데이터 확보

---

## 16. REST API 요청/응답 구조

이 프로그램에서는 두 가지 HTTP 메서드를 사용합니다.

### GET

Kakao Local API의 장소 검색에 사용합니다.

```text
프로그램
→ GET 요청
→ Kakao Local API
→ JSON 응답
→ Python에서 필요한 장소 데이터 추출
```

GET은 주로 서버에서 데이터를 조회할 때 사용합니다.

### POST

LLM API 호출에 사용합니다.

```text
프로그램
→ JSON 데이터와 함께 POST 요청
→ LLM API
→ 생성된 응답
→ Python에서 JSON 또는 Markdown으로 처리
```

POST는 서버에 데이터를 전달하여 새로운 결과를 생성하거나 처리하도록 요청할 때 사용합니다.

---

## 17. 프로젝트 파일 구조

제출용 프로젝트의 기본 구조는 다음과 같습니다.

```text
travel-planner-git/
├── results/
│   ├── 2026-10-15_raw.json
│   ├── 2026-10-15_raw(1).json
│   ├── 2026-10-15_raw(2)_final.json
│   ├── 2026-10-15_travel_plan.md
│   ├── 2026-10-15_travel_plan(1).md
│   └── 2026-10-15_travel_plan(2)_final.md
├── .gitignore
├── README.md
└── travel_planner.py
```

제출용 폴더에는 실제 API 키가 들어 있는 `.env` 파일을 포함하지 않습니다.

각 파일의 역할은 다음과 같습니다.

- `travel_planner.py`
  - 프로그램 실행 코드

- `.gitignore`
  - Git 저장소에 포함하지 않을 파일 설정

- `README.md`
  - 프로그램 설명, 실행 방법, 오류 처리, 결과물 설명

- `results/`
  - 실행 결과 JSON 및 Markdown 파일 저장

---

## 18. 필수 요구사항 체크리스트

| 구분 | 요구사항 | 현재 상태 | 판정 |
|---|---|---|---|
| 최종 결과물 | CLI Python 프로그램 | `travel_planner.py` 구현 | ✅ |
| 최종 결과물 | 진행 로그 출력 | 여행지 추천, 맛집 검색, 최종 리포트 생성 과정 출력 | ✅ |
| 최종 결과물 | 결과 저장 경로 안내 | JSON 및 Markdown 저장 경로 출력 | ✅ |
| 최종 결과물 | 원본 JSON 1개 이상 | `results/`에 JSON 결과 파일 저장 | ✅ |
| 최종 결과물 | 최종 Markdown 리포트 | `results/`에 Markdown 리포트 저장 | ✅ |
| 최종 결과물 | README.md | 프로그램 설명 및 사용법 작성 | ✅ |
| CLI | argparse 사용 | `argparse.ArgumentParser()` 사용 | ✅ |
| CLI | 날짜 필수 입력 | `required=True` 적용 | ✅ |
| CLI | 날짜 형식 검증 | `datetime.strptime()` 사용 | ✅ |
| CLI | --date 옵션 | `--date` 지원 | ✅ |
| CLI | -date 옵션 | `-date`도 함께 지원 | ✅ |
| LLM | 날짜를 입력으로 추천 | 입력 날짜를 LLM 프롬프트에 전달 | ✅ |
| LLM | JSON 형식 출력 프롬프트 | JSON만 출력하도록 프롬프트 작성 | ✅ |
| LLM | recommended_city | 문자열 필드 구현 | ✅ |
| LLM | weather | 문자열 필드 구현 | ✅ |
| LLM | events 배열 | 문자열 배열 구현 | ✅ |
| LLM | reason | 문자열 필드 구현 | ✅ |
| 장소 API | Kakao Local 사용 | Kakao Local 키워드 검색 API 사용 | ✅ |
| 장소 API | recommended_city를 검색 입력으로 사용 | `recommendation["recommended_city"]` 사용 | ✅ |
| 맛집 | 최대 5곳 검색 | `size=5` 설정 | ✅ |
| 맛집 | name/address/category/url/x/y | 모든 필드 저장 | ✅ |
| 0건 처리 | 프로그램 계속 실행 | 빈 리스트 반환 후 리포트 생성 계속 | ✅ |
| 0건 처리 | errors에 EMPTY_RESULT | `EMPTY_RESULT` 오류 기록 | ✅ |
| 최종 리포트 | 추천 지역/이유 | 포함 | ✅ |
| 최종 리포트 | 날씨 | 포함 | ✅ |
| 최종 리포트 | 행사/축제 | 포함 | ✅ |
| 최종 리포트 | 맛집 | 포함 | ✅ |
| 최종 리포트 | 0건이면 데이터 없음 | 프롬프트에서 데이터 없음 처리 | ✅ |
| 최종 리포트 | 오전/오후/저녁 일정 | 1일 일정에 포함 | ✅ |
| 에러 처리 | try-except | API 및 JSON 처리에 사용 | ✅ |
| 에러 처리 | API 키 없으면 즉시 종료 | 설정 안내 후 `SystemExit` | ✅ |
| 에러 처리 | Kakao 실패 시 계속 진행 | 빈 맛집 목록으로 처리 | ✅ |
| 에러 처리 | LLM JSON 실패 시 1회 재요청 | 재요청 로직 구현 | ✅ |
| errors | 내부 오류 목록 관리 | `errors = []` 사용 | ✅ |
| 보안 | .env에서 키 읽음 | `load_dotenv()`와 `os.getenv()` 사용 | ✅ |
| 보안 | 코드에 키 직접 작성 안 함 | API 키 하드코딩 없음 | ✅ |
| 보안 | .gitignore에 .env | `.env` 등록 | ✅ |
| 보안 | 제출물에 실제 키 미포함 | 제출용 폴더에 `.env` 제외 | ✅ |
| 결과 저장 | results/ 생성 | `os.makedirs()`로 자동 생성 | ✅ |
| 결과 저장 | 추천+맛집+errors JSON | 세 데이터 모두 저장 | ✅ |
| 결과 저장 | 최종 .md 저장 | Markdown 파일 저장 | ✅ |

---

## 19. 현재 결과 데이터 체크

### JSON 결과

현재 원본 JSON에는 다음 데이터가 포함됩니다.

```text
recommended_city ✅
weather ✅
events ✅
reason ✅
errors ✅
restaurants ✅
```

예를 들어 정상 실행 결과에서는:

```text
추천 지역 존재 ✅
맛집 5곳 존재 ✅
errors 빈 배열 ✅
```

형태로 저장됩니다.

---

### Markdown 리포트

최종 Markdown 리포트에는 다음 항목이 포함됩니다.

```text
추천 지역 ✅
추천 이유 ✅
날씨 ✅
행사/축제 ✅
맛집 섹션 ✅
맛집 0건 → 데이터 없음 ✅
1일 일정 ✅
오전/오후/저녁 ✅
errors 섹션 ✅
```

---

### README

README에는 다음 내용이 포함됩니다.

```text
프로그램 개요 ✅
실행 방법 ✅
API 키 설정 방법 ✅
결과물 확인 방법 ✅
API 키 보안 주의 ✅
사용 API 설명 ✅
오류 처리 설명 ✅
결과 파일 구조 ✅
필수 요구사항 체크리스트 ✅
```

---

## 20. 보너스 과제

보너스 과제는 선택 사항이므로 필수 제출 조건에는 포함되지 않습니다.

```text
복수 지역 추천 ❌
결과 캐싱 ❌
```

### 복수 지역 추천

현재 프로그램은 실행 한 번당 하나의 지역을 추천합니다.

```text
recommended_city: string
```

따라서 복수 지역 추천 기능은 구현하지 않았습니다.

### 결과 캐싱

현재 프로그램은 같은 날짜로 실행해도 API를 다시 호출합니다.

기존 결과를 API 호출 없이 그대로 재사용하는 캐싱 기능은 구현하지 않았습니다.

대신 기존 실행 결과는 삭제하지 않고 번호를 붙여 보관합니다.

이 기능은 결과 캐싱과는 별개의 기능입니다.

---

## 21. 최종 보안 확인

GitHub 또는 제출용 ZIP을 만들기 전에 다음 사항을 확인합니다.

```text
.env 파일 없음 ✅
Python 코드에 API 키 없음 ✅
README에 실제 API 키 없음 ✅
결과 JSON에 API 키 없음 ✅
결과 Markdown에 API 키 없음 ✅
.gitignore에 .env 등록 ✅
```

Git을 사용하는 경우 다음 명령어로 확인할 수 있습니다.

```bash
git status
```

숨김 파일을 포함하여 프로젝트 폴더를 확인하려면 macOS 터미널에서 다음 명령어를 사용할 수 있습니다.

```bash
ls -la
```

`.env`가 제출용 폴더에 나타나지 않으면 됩니다.

---

## 22. 실행 예시

```bash
python3 travel_planner.py --date "2026-10-15"
```

실행 과정은 다음과 같은 형태로 표시됩니다.

```text
입력한 날짜: 2026-10-15
OpenAI API 키 확인 완료
Kakao API 키 확인 완료

[1/3] 여행지 추천 생성 중...
추천 지역: 속초

[OpenAI 추천 결과]
{
  "recommended_city": "속초",
  "weather": "...",
  "events": [
    "...",
    "..."
  ],
  "reason": "..."
}

[카카오 맛집 검색]
검색 결과: 5 곳

원본 JSON 저장 완료: results/2026-10-15_raw(2)_final.json

[3/3] 최종 리포트 생성 중...
리포트 생성 완료

최종 리포트 저장 완료:
results/2026-10-15_travel_plan(2)_final.md
```

가장 최근 실행 결과는 `_final` 파일을 확인하면 됩니다.