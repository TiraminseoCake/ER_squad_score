import random
import requests
import pprint
import time

# API Key and Base URL configuration
API_KEY = "LeG377Fnji3o0uCQqF5Ue5EaAGRnN6vM9hJWCcOq"
BASE_URL = "https://open-api.bser.io/v1"
HEADERS = {"x-api-key": API_KEY}

# 글로벌 데이터
global_combination_data = {}
processed_user_ids = set()  # 중복 방지용

def get_users_in_tier():
    url = f"{BASE_URL}/rank/top/27/3"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    return [user["userNum"] for user in data["topRanks"]]

def get_random_user_id():
    users = get_users_in_tier()
    if not users:
        return None
    return random.choice(users)

def get_recent_match_record(user_num):
    """
    특정 유저의 가장 최근 스쿼드 모드 전적 하나를 가져옵니다.
    """
    url = f"{BASE_URL}/user/games/{user_num}"
    response = requests.get(url, headers=HEADERS)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTPError: {e}")
        print(f"Response Content: {response.content.decode()}")
        return None

    data = response.json()

    # 스쿼드 모드 (mode=3) 전적 검색
    for match in data["userGames"]:
        if match["matchingTeamMode"] == 3:  # 스쿼드 모드 확인
            return match["gameId"]

    # 스쿼드 모드 전적이 없는 경우
    return None



def GetGameDetail(gameid):
    url = f"{BASE_URL}/games/{gameid}"
    delay = 1
    while True:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 429:
            print(f"429 Too Many Requests. {delay}초 대기 중...")
            time.sleep(delay)
            delay = min(delay * 2, 10)  # 최대 10초 대기
            continue
        response.raise_for_status()
        return response.json()

def calculate_team_scores(match_record):
    rank_points = {1: 10, 2: 7, 3: 5, 4: 2, 5: 1, 6: 0, 7: 0, 8: 0}
    combination_data = {}
    team_data = {}

    for player in match_record["userGames"]:
        team_id = player["teamNumber"]
        character_name = player["characterNum"]
        rank = player["gameRank"]
        kills = player["teamKill"]

        if team_id not in team_data:
            team_data[team_id] = {"rank": rank, "kills": kills, "characters": []}
        team_data[team_id]["characters"].append(character_name)

    for team in team_data.values():
        characters = tuple(sorted(team["characters"]))
        rank = team["rank"]
        kills = team["kills"]
        score = rank_points.get(rank, 0) + kills*2

        if characters not in combination_data:
            combination_data[characters] = {"total_score": 0, "count": 0}
        combination_data[characters]["total_score"] += score
        combination_data[characters]["count"] += 1

    return combination_data

def update_global_combination_data(new_data):
    global global_combination_data

    for characters, scores in new_data.items():
        if characters not in global_combination_data:
            global_combination_data[characters] = {"total_score": 0, "count": 0}
        global_combination_data[characters]["total_score"] += scores["total_score"]
        global_combination_data[characters]["count"] += scores["count"]

def GetUserNum(nickName: str):
    url = f"{BASE_URL}/user/nickname?query={nickName}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()["user"]["userNum"]

def main():
    global processed_user_ids

    first_nickName = input("첫 번째 유저 닉네임을 입력하세요: ")
    current_user_num = GetUserNum(first_nickName)

    if not current_user_num:
        print("첫 번째 유저 정보를 가져올 수 없습니다.")
        return

    processed_user_ids.add(current_user_num)

    iterations = 100  # 반복 횟수
    for _ in range(iterations):
        try:
            # 현재 유저의 최근 게임 데이터 가져오기
            recent_match = get_recent_match_record(current_user_num)
            game_data = GetGameDetail(recent_match)
            team_scores = calculate_team_scores(game_data)
            update_global_combination_data(team_scores)

            # 현재 게임 데이터에서 랜덤 유저 선택 (본인 제외, 중복 제외)
            user_ids_in_game = [
                player["userNum"]
                for player in game_data["userGames"]
                if player["userNum"] != current_user_num and player["userNum"] not in processed_user_ids
            ]

            if user_ids_in_game:
                current_user_num = random.choice(user_ids_in_game)
                processed_user_ids.add(current_user_num)
            else:
                # 다음 유저를 선택할 수 없으면 티어에서 새로운 유저 추출
                print("게임에서 유효한 유저를 찾을 수 없습니다. 티어에서 새로운 유저를 선택합니다.")
                current_user_num = get_random_user_id()
                if current_user_num in processed_user_ids:
                    continue  # 이미 처리된 유저라면 무시
                processed_user_ids.add(current_user_num)
            print(current_user_num)     
        except Exception as e:
            print(f"오류 발생: {e}")
            break

        time.sleep(2)  # API 호출 제한 방지

    # 최종 글로벌 데이터 출력
    print("글로벌 조합 점수 데이터:")
    pprint.pprint(global_combination_data)

if __name__ == "__main__":
    main()