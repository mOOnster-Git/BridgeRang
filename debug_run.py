import gspread
import pandas as pd
import io

# --- 설정 ---
SPREADSHEET_URL_1 = "https://docs.google.com/spreadsheets/d/1RoPRJhE0l9UekV__h6jVWzMLwoYhoZ7UDP0_KW4J9DA/edit?gid=0#gid=0"
SPREADSHEET_URL_2 = "https://docs.google.com/spreadsheets/d/1IeksESLCY0aNiuMlZOi6QwQNLCPdix2uZe8c3995m2o/edit?gid=213135690#gid=213135690"
SERVICE_ACCOUNT_KEY_PATH = "taerang-12345.json"

def run_debug():
    print("=== 디버깅 시작 ===")
    
    # 1. 구글 시트 데이터 가져오기
    try:
        gc = gspread.service_account(filename=SERVICE_ACCOUNT_KEY_PATH)
        
        # 1창고
        sh1 = gc.open_by_url(SPREADSHEET_URL_1)
        ws1 = sh1.get_worksheet(0)
        group_1 = ws1.col_values(5)
        print(f"\n[1창고] 데이터 {len(group_1)}개 가져옴")
        print(f"  └ 예시: {group_1[:5]}")
        
        # 2창고
        sh2 = gc.open_by_url(SPREADSHEET_URL_2)
        ws2 = sh2.get_worksheet(0)
        group_2 = ws2.col_values(5)
        print(f"\n[2창고] 데이터 {len(group_2)}개 가져옴")
        print(f"  └ 예시: {group_2[:5]}")
        
    except Exception as e:
        print(f"구글 시트 오류: {e}")
        return

    # 2. 입력 데이터 읽기 (debug_input.txt)
    try:
        with open("debug_input.txt", "r", encoding="utf-8") as f:
            input_text = f.read()
        
        # 탭으로 구분된 텍스트를 데이터프레임으로 변환
        # 첫 줄이 헤더일 것이므로 그대로 읽음
        # 탭이나 공백이 섞여 있을 수 있으니 정규식으로 분리 시도하거나 sep='\t' 사용
        # 사용자가 제공한 텍스트는 탭으로 구분된 것처럼 보임 (또는 공백)
        
        # 탭 구분이 확실하지 않을 수 있으므로, sep='\t'로 시도해보고 안되면 sep='\s+' 등 고려
        # 하지만 사용자가 복사 붙여넣기 했다고 했으므로 탭일 가능성 높음
        df = pd.read_csv(io.StringIO(input_text), sep='\t')
        
        # 만약 컬럼이 하나로 뭉쳐지면 구분자 문제
        if len(df.columns) < 5:
            print("\n[경고] 탭 구분 실패, 공백 구분 시도")
            df = pd.read_csv(io.StringIO(input_text), sep=r'\s+')
            
        print(f"\n[입력 데이터] {len(df)}행 읽음")
        print(f"  └ 컬럼 목록: {df.columns.tolist()}")
        
        if '그룹번호' in df.columns:
            print(f"  └ 그룹번호 예시: {df['그룹번호'].head().tolist()}")
        else:
            print("  └ '그룹번호' 컬럼 없음!")
            # 공백이 섞여있을 수 있으니 컬럼명 정리
            df.columns = df.columns.str.strip()
            if '그룹번호' in df.columns:
                 print(f"  └ (공백제거 후) 그룹번호 예시: {df['그룹번호'].head().tolist()}")
            else:
                 print("  └ 여전히 '그룹번호' 컬럼 없음. 컬럼명 확인 필요.")
                 return

    except Exception as e:
        print(f"데이터 읽기 오류: {e}")
        return

    # 3. 매칭 테스트 (통관고유번호로 매칭 시도)
    print("\n=== 매칭 결과 테스트 (통관고유번호 기준) ===")
    set_1 = set(str(x).strip() for x in group_1 if str(x).strip())
    set_2 = set(str(x).strip() for x in group_2 if str(x).strip())
    
    match_1 = 0
    match_2 = 0
    match_un = 0
    
    # 입력 데이터의 컬럼명 공백 제거
    df.columns = df.columns.str.strip()
    
    target_col = '통관고유번호(사업자등록번호)'
    if target_col not in df.columns:
        print(f"'{target_col}' 컬럼을 찾을 수 없습니다.")
        return

    for index, row in df.iterrows():
        p_code = str(row[target_col]).strip()
        
        if p_code in set_1:
            match_1 += 1
            print(f"  [매칭] {p_code} -> 1창고")
        elif p_code in set_2:
            match_2 += 1
            print(f"  [매칭] {p_code} -> 2창고")
        else:
            match_un += 1
            print(f"  [미분류] {p_code}")
            
    print(f"\n결과: 1창고 {match_1}건, 2창고 {match_2}건, 미분류 {match_un}건")

if __name__ == "__main__":
    run_debug()
