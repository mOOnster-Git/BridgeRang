import pandas as pd

file_path = r"c:\Users\mOOnster\Desktop\Taerang_sheets\결과_미분류.xlsx"
try:
    df = pd.read_excel(file_path)
    print("=== 컬럼 목록 ===")
    print(df.columns.tolist())
    print("\n=== 상위 5행 데이터 ===")
    print(df.head())
    print("\n=== '그룹번호' 열 데이터 확인 ===")
    if '그룹번호' in df.columns:
        print(df['그룹번호'].head())
        print("\n데이터 타입:", df['그룹번호'].dtype)
    else:
        print("'그룹번호' 열이 없습니다!")
except Exception as e:
    print("오류 발생:", e)
