import gspread

SPREADSHEET_URL_1 = "https://docs.google.com/spreadsheets/d/1RoPRJhE0l9UekV__h6jVWzMLwoYhoZ7UDP0_KW4J9DA/edit?gid=0#gid=0"
SERVICE_ACCOUNT_KEY_PATH = "taerang-12345.json"

gc = gspread.service_account(filename=SERVICE_ACCOUNT_KEY_PATH)
sh = gc.open_by_url(SPREADSHEET_URL_1)
ws = sh.get_worksheet(0)
headers = ws.row_values(1)
print(f"헤더 목록: {headers}")
try:
    idx = headers.index("그룹번호")
    print(f"'그룹번호'는 {idx+1}번째 열(인덱스 {idx})에 있습니다.")
except ValueError:
    print("'그룹번호' 컬럼을 찾을 수 없습니다.")
