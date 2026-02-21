import gspread

SPREADSHEET_URL_1 = "https://docs.google.com/spreadsheets/d/1RoPRJhE0l9UekV__h6jVWzMLwoYhoZ7UDP0_KW4J9DA/edit?gid=0#gid=0"
SERVICE_ACCOUNT_KEY_PATH = "taerang-12345.json"

gc = gspread.service_account(filename=SERVICE_ACCOUNT_KEY_PATH)
sh = gc.open_by_url(SPREADSHEET_URL_1)
ws = sh.get_worksheet(0)
col_d = ws.col_values(4) # 배송묶음번호
print(f"D열(배송묶음번호) 예시: {col_d[:5]}")
