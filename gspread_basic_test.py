import gspread
from typing import List

# 아버님이 알려주신 1창고, 2창고 주소와 실제 열쇠 파일 이름 적용 완료!
URL_1 = "https://docs.google.com/spreadsheets/d/1RoPRJhE0l9UekV__h6jVWzMLwoYhoZ7UDP0_KW4J9DA/edit?gid=0#gid=0"
URL_2 = "https://docs.google.com/spreadsheets/d/1IeksESLCY0aNiuMlZOi6QwQNLCPdix2uZe8c3995m2o/edit?gid=213135690#gid=213135690"
SERVICE_ACCOUNT_KEY_PATH = "taerang-12345.json"

def read_group_numbers(url: str, warehouse_name: str) -> List[str]:
    try:
        # 1. 열쇠(JSON) 파일로 로봇 알바생 로그인
        gc = gspread.service_account(filename=SERVICE_ACCOUNT_KEY_PATH)
        
        # 2. 구글 시트 주소로 찾아가서 문서 열기
        sh = gc.open_by_url(url)
        
        # 3. 첫 번째 탭(시트) 선택
        ws = sh.get_worksheet(0)
        
        # 4. E열(5번째 열)에 있는 그룹번호 데이터 전부 가져오기
        values = ws.col_values(5)
        
        print(f"✅ {warehouse_name} 접속 성공! (총 {len(values)}줄의 데이터를 읽어왔습니다)")
        return values

    except FileNotFoundError:
        print(f"❌ 에러: 같은 폴더에 '{SERVICE_ACCOUNT_KEY_PATH}' 파일이 없습니다. 파일 위치와 이름을 확인해주세요!")
        return []
    except gspread.exceptions.APIError as e:
        print(f"❌ 에러: {warehouse_name}에 로봇 알바생(이메일)이 공유되지 않았거나 주소가 틀렸습니다.\n자세한 에러: {e}")
        return []
    except Exception as e:
        print(f"❌ 알 수 없는 에러 ({warehouse_name}): {e}")
        return []

if __name__ == "__main__":
    print("🚀 구글 시트 1창고, 2창고 연동 테스트를 시작합니다...\n")
    
    # 1창고 데이터 불러오기 및 결과 확인 (너무 기니까 앞의 5개만 살짝 보여주기)
    data_1 = read_group_numbers(URL_1, "1창고")
    if data_1:
        print("▶ 1창고 데이터 미리보기:", data_1[:5])
    
    print("-" * 50)
    
    # 2창고 데이터 불러오기 및 결과 확인
    data_2 = read_group_numbers(URL_2, "2창고")
    if data_2:
        print("▶ 2창고 데이터 미리보기:", data_2[:5])
    
    print("\n🎉 테스트 종료!")