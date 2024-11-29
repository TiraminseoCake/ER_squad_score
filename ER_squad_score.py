import random
import requests
import pprint
import time
import json
# API Key and Base URL configuration
API_KEY = "LeG377Fnji3o0uCQqF5Ue5EaAGRnN6vM9hJWCcOq"
BASE_URL = "https://open-api.bser.io/v1"
HEADERS = {"x-api-key": API_KEY}


def get_users_in_tier():
    """
    특정 티어(in 1000)의 유저 ID 목록을 가져옵니다.
    - 현재 시즌, 스쿼드 모드 (mode=3)에서 티어에 해당하는 유저를 필터링.
    """
    url = f"{BASE_URL}/rank/top/27/3"  
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


def calculate_team_scores(match_record):
    """
    단일 게임 데이터에서 팀별 캐릭터 조합의 점수를 계산하고 저장합니다.
    - 각 조합별로 등수 점수와 킬 점수를 반영합니다.
    """
    # 점수 기준 (등수에 따른 점수)
    rank_points = {1: 10, 2: 7, 3: 5, 4: 2, 5: 1,6: 0, 7: 0, 8: 0}
    combination_data = {}

    # 각 팀의 데이터를 처리
    
    for player in match_record["userGames"]:
        team_id = player["teamNumber"]
        character_name = player["characterNum"]
        rank = player["gameRank"]
        kills = player["teamKill"]

        # 팀별로 캐릭터 조합 구성
        if team_id not in combination_data:
            combination_data[team_id] = {
                "rank": rank,
                "kills": kills,
                "characters": []
            }
        
        combination_data[team_id]["characters"].append(character_name)

    # 조합별 점수 계산;
    team_scores = {}
    for team in combination_data.values():
        # 캐릭터 조합 정렬
        characters = tuple(sorted(team["characters"]))
        rank = team["rank"]
        kills = team["kills"]

        # 조합 점수 계산
        score = rank_points.get(rank, 0) + kills

        # 조합 점수 반영
        if characters not in team_scores:
            team_scores[characters] = {"total_score": 0, "count": 0}

        team_scores[characters]["total_score"] += score
        team_scores[characters]["count"] += 1

    return team_scores

def GetUserStats(userNum, seasonId=27):
    response_userStats = requests.get(f"{BASE_URL}v1/user/stats/{userNum}/{seasonId}", headers=HEADERS)
    return response_userStats.json()


def GetGameDetail(gameid):
    response_gamedetail = requests.get(f"{BASE_URL}v1/games/{gameid}",headers=HEADERS)
    return response_gamedetail.json()


def ExportJson(js, fileName="temp",printjs=False):
    file_path= f"{fileName}.json"
    if printjs:pprint(js)
    file = open(file_path,"w")
    file.write(json.dumps(js, indent="\t"))
    print(file_path)
    time.sleep(1)
    
    
    
def main():
    # Step 1: Get a random user ID
    random_user_id = get_random_user_id()
    if not random_user_id:
        return

    print(f"랜덤 유저 ID: {random_user_id}")
    
 
    
    match_records = get_match_records(random_user_id)
    a=calculate_team_scores(match_records)
    pprint.pprint(a)




if __name__ == "__main__":
    main()