import pandas as pd
import os

def test_logic():
    print("=== 통합 저장 로직 테스트 ===")
    
    # 1. 가상 구글 시트 데이터
    set_1 = {'P100', 'P101'}
    set_2 = {'P200', 'P201'}
    
    # 2. 가상 입력 데이터
    data = {
        '통관고유번호(사업자등록번호)': ['P100', 'P200', 'P999', 'P101'],
        '상품명': ['A', 'B', 'C', 'D']
    }
    df = pd.DataFrame(data)
    target_col = '통관고유번호(사업자등록번호)'
    
    # 3. 분류 로직
    final_rows = []
    class_col_name = "창고구분"
    
    print("[분류 시작]")
    for index, row in df.iterrows():
        match_value = str(row[target_col]).strip()
        row_dict = row.to_dict()
        
        if match_value in set_1:
            row_dict[class_col_name] = "1창고"
            print(f"  {match_value} -> 1창고")
        elif match_value in set_2:
            row_dict[class_col_name] = "2창고"
            print(f"  {match_value} -> 2창고")
        else:
            row_dict[class_col_name] = "미분류"
            print(f"  {match_value} -> 미분류")
        
        final_rows.append(row_dict)
        
    # 4. 데이터프레임 생성 및 컬럼 이동
    final_df = pd.DataFrame(final_rows)
    
    cols = list(final_df.columns)
    if class_col_name in cols:
        cols.insert(0, cols.pop(cols.index(class_col_name)))
        final_df = final_df[cols]
        
    print("\n[최종 데이터프레임 구조]")
    print(final_df)
    
    # 컬럼 순서 확인
    if final_df.columns[0] == class_col_name:
        print("\n✅ 성공: '창고구분'이 첫 번째 컬럼입니다.")
    else:
        print(f"\n❌ 실패: 첫 번째 컬럼이 '{final_df.columns[0]}' 입니다.")

if __name__ == "__main__":
    test_logic()
