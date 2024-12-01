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

def get_users_in_tier():
    """
    티어 내 유저 ID 목록 가져오기.
    """
    url = f"{BASE_URL}/rank/top/27/3"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    return [user["userNum"] for user in data["topRanks"]]

def get_recent_matches(user_num):
    """
    특정 유저의 최근 전적 목록 (최대 10개) 가져오기.
    """
    url = f"{BASE_URL}/user/games/{user_num}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    return data["userGames"][:10]  # 최대 10개 전적 반환

def get_game_detail(gameid):
    """
    게임 세부 정보 가져오기.
    """
    url = f"{BASE_URL}/games/{gameid}"
    delay = 1
    while True:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 429:
            print(f"429 Too Many Requests. {delay}초 대기 중...")
            time.sleep(delay)
            delay = min(delay * 2, 10)
            continue
        response.raise_for_status()
        return response.json()

def calculate_team_scores(match_record):
    """
    게임 데이터에서 팀별 캐릭터 조합 점수 계산.
    조합 내 캐릭터 개수가 3개가 아니면 스킵.
    """
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
        # 스킵 조건: 캐릭터 개수가 3개가 아닌 경우
        if len(team["characters"]) != 3:
            continue

        characters = tuple(sorted(team["characters"]))
        rank = team["rank"]
        kills = team["kills"]
        score = rank_points.get(rank, 0) + kills * 2

        if characters not in combination_data:
            combination_data[characters] = {"scores": []}
        combination_data[characters]["scores"].append(score)

    return combination_data

def update_global_combination_data(new_data):
    """
    새로운 조합 점수 데이터를 글로벌 데이터에 병합.
    """
    global global_combination_data

    for characters, scores in new_data.items():
        if characters not in global_combination_data:
            global_combination_data[characters] = {"scores": []}
        global_combination_data[characters]["scores"].extend(scores["scores"])

def get_user_num(nickName: str):
    """
    닉네임으로 유저 번호 가져오기.
    """
    url = f"{BASE_URL}/user/nickname?query={nickName}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()["user"]["userNum"]

def main():
    global global_combination_data

    # 첫 번째 유저의 닉네임 입력
    first_nickName = input("첫 번째 유저 닉네임을 입력하세요: ")
    first_user_num = get_user_num(first_nickName)

    if not first_user_num:
        print("첫 번째 유저 정보를 가져올 수 없습니다.")
        return

    # 첫 번째 유저의 첫 번째 전적
    first_matches = get_recent_matches(first_user_num)
    if not first_matches:
        print("첫 번째 유저의 전적을 가져올 수 없습니다.")
        return
    first_match = first_matches[0]  # 첫 번째 전적
    game_data = get_game_detail(first_match["gameId"])
    team_scores = calculate_team_scores(game_data)
    update_global_combination_data(team_scores)

    # 반복적으로 티어 내 유저 선택 및 전적 처리
    iterations = 2000
    users_in_tier = get_users_in_tier()
    for _ in range(iterations):
        try:
            # 티어 내 유저 랜덤 선택
            random_user = random.choice(users_in_tier)
            matches = get_recent_matches(random_user)

            if not matches:
                print(f"유저 {random_user}의 전적이 없습니다. 다음 유저를 선택합니다.")
                continue

            # 최근 전적 10개 중 랜덤 선택
            random_match = random.choice(matches)
            game_data = get_game_detail(random_match["gameId"])
            team_scores = calculate_team_scores(game_data)
            update_global_combination_data(team_scores)

            print(f"유저 {random_user}의 전적 처리 완료.")

        except Exception as e:
            print(f"오류 발생: {e}")
            break

        time.sleep(2)  # API 호출 제한 방지

    # 최종 글로벌 데이터 출력
    print("글로벌 조합 점수 데이터:")
    pprint.pprint(global_combination_data)

if __name__ == "__main__":
    main()