import random
import requests
import pprint

# API Key and Base URL configuration
API_KEY = "LeG377Fnji3o0uCQqF5Ue5EaAGRnN6vM9hJWCcOq"
BASE_URL = "https://open-api.bser.io/v1"
HEADERS = {"x-api-key": API_KEY}


def get_users_in_tier():
    """
    특정 티어의 유저 ID 목록을 가져옵니다.
    - 현재 시즌, 스쿼드 모드 (mode=3)에서 티어에 해당하는 유저를 필터링.
    """
    url = f"{BASE_URL}/rank/top/27/3"  # 시즌 1, 스쿼드 모드
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    
    # 입력한 티어에 해당하는 유저만 필터링
    users_in_tier = [user["userNum"] for user in data["topRanks"] ]
    return users_in_tier


def get_random_user_id():
    """
    특정 티어에서 무작위로 유저 ID를 선택합니다.
    """
    users = get_users_in_tier()
    if not users:
        print(f"티어 {tier_name}에 해당하는 유저가 없습니다.")
        return None
    return random.choice(users)


def get_match_records(user_num, next=None):
    """
    특정 유저의 전적 기록을 가져옵니다. 페이징 처리가 가능합니다.
    """
    if next is None:
        url = f"{BASE_URL}/user/games/{user_num}"
    else:
        url = f"{BASE_URL}/user/games/{user_num}?next={next}"
    
    response = requests.get(url, headers=HEADERS)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTPError: {e}")
        print(f"Response Content: {response.content.decode()}")
        return None
    
    data = response.json()
    return data


def extract_team_rank_and_kills_with_combinations(match_records):
    """
    유저 전적 데이터를 기반으로 캐릭터 조합별 등수와 킬 수를 누적 저장합니다.
    - 같은 캐릭터 조합이라면 다른 팀이라도 데이터를 누적합니다.
    """
    combination_data = {}
    for match in match_records.get("games", []):
        # 게임 데이터에서 팀별로 그룹화
        team_data = {}
        for player in match["players"]:
            team_id = player["teamId"]
            character_name = player["characterName"]
            rank = player["rank"]
            kills = player["teamKill"]

            # 팀별로 캐릭터 조합 구성
            if team_id not in team_data:
                team_data[team_id] = {"rank": rank, "kills": kills, "characters": []}

            team_data[team_id]["characters"].append(character_name)

        # 조합별로 데이터 저장
        for team in team_data.values():
            characters = tuple(sorted(team["characters"]))  # 캐릭터 이름 정렬
            rank = team["rank"]
            kills = team["kills"]

            # 조합 데이터 초기화 또는 업데이트
            if characters not in combination_data:
                combination_data[characters] = {"rank_sum": 0, "count": 0, "kills_sum": 0}

            combination_data[characters]["rank_sum"] += rank
            combination_data[characters]["count"] += 1
            combination_data[characters]["kills_sum"] += kills

    return combination_data


def main():
    # Step 1: Get a random user ID
    random_user_id = get_random_user_id()
    if not random_user_id:
        return
    
    print(f"랜덤 유저 ID: {random_user_id}")

    # Step 2: Get match records for the selected user
    match_records = get_match_records(random_user_id)
    #if not match_records.get("games"):
        #print("해당 유저의 전적 기록이 없습니다.")
       #return

    # Step 3: Extract combination data
    combination_data = extract_team_rank_and_kills_with_combinations(match_records)

    # Step 4: Output results
    print("캐릭터 조합 데이터 (등수와 킬 수):")
    for characters, data in combination_data.items():
        avg_rank = data["rank_sum"] / data["count"]
        avg_kills = data["kills_sum"] / data["count"]
        print(f"조합: {characters}, 평균 등수: {avg_rank:.2f}, 평균 킬: {avg_kills:.2f}")


if __name__ == "__main__":
    main()