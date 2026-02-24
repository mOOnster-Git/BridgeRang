import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import io
import datetime
import json
import subprocess
import ctypes

# ==========================================================
# 프로그램 정보 및 설정
# ==========================================================
PROGRAM_NAME = "Bridge Rang (브릿지랑)"
VERSION = "v2.15" # v2.15: 한글 가이드 시스템 제거 및 UI 안정화
CREATOR = "mOOnster"
OUTPUT_FOLDER_NAME = "브릿지랑"

APP_DIR = os.path.join(os.getenv('APPDATA', os.path.expanduser('~')), 'BridgeRang')
if not os.path.exists(APP_DIR):
    os.makedirs(APP_DIR)
CONFIG_FILE = os.path.join(APP_DIR, "config.json")

# --- UI 색상 테마 설정 ---
BTN_BG = "#E2E8F0"
BTN_FG = "#0F172A"
ACTION_BG = "#2563EB"
ACTION_FG = "#FFFFFF"
BORDER_COLOR = "#CBD5E1"

def open_folder_and_select(file_path):
    try:
        file_path = os.path.normpath(os.path.abspath(file_path))
        dir_path = os.path.dirname(file_path)

        ole32 = ctypes.windll.ole32
        shell32 = ctypes.windll.shell32

        shell32.ILCreateFromPathW.argtypes = [ctypes.c_wchar_p]
        shell32.ILCreateFromPathW.restype = ctypes.c_void_p
        shell32.SHOpenFolderAndSelectItems.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]
        shell32.ILFree.argtypes = [ctypes.c_void_p]

        ole32.CoInitialize(None)
        dir_pidl = shell32.ILCreateFromPathW(dir_path)
        file_pidl = shell32.ILCreateFromPathW(file_path)

        if dir_pidl and file_pidl:
            pidl_array = (ctypes.c_void_p * 1)(file_pidl)
            shell32.SHOpenFolderAndSelectItems(dir_pidl, 1, pidl_array, 0)
            shell32.ILFree(dir_pidl)
            shell32.ILFree(file_pidl)
        else:
            subprocess.Popen(f'explorer /select,"{file_path}"')
        ole32.CoUninitialize()
    except Exception:
        subprocess.Popen(f'explorer /select,"{file_path}"')

class CreateToolTip(object):
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.tw = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)

    def enter(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffe0", relief='solid', borderwidth=1,
                       font=("맑은 고딕", 9, "normal"), padx=8, pady=8)
        label.pack(ipadx=1)

    def close(self, event=None):
        if self.tw:
            self.tw.destroy()

class InvoiceSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{PROGRAM_NAME} {VERSION}")
        self.root.geometry("800x720")
        
        self.selected_file_path = None
        self.url_entries = []
        self.bot_email = "연결된 키 없음"
        
        config = self.load_config()
        raw_urls = config.get("urls", [])
        self.warehouse_urls = [url for url in raw_urls if url.strip()]
        self.key_file_path = config.get("key_path", "")
        self.key_raw_text = config.get("key_raw_text", "")
        
        self.main_frame = tk.Frame(root, padx=20, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.open_folder_var = tk.BooleanVar(value=True)
        
        self.create_top_section()
        self.add_separator()
        self.create_middle_section()
        self.add_separator()
        self.create_bottom_section()

        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        self.check_initial_status()

    def check_initial_status(self):
        self.update_key_display()
        if "@" in self.bot_email: self.log(f"▶ {PROGRAM_NAME} 가동 준비 완료")
        else: self.log(f"⚠️ [주의] 인증 키가 설정되지 않았습니다. 상단의 [JSON 키 설정]을 먼저 완료해주세요.")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f)
            except: return {}
        return {}

    def save_config(self):
        current_urls = [entry.get().strip() for entry in self.url_entries if entry.get().strip()]
        data = {"urls": current_urls, "key_path": self.key_file_path, "key_raw_text": self.key_raw_text}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

    def create_top_section(self):
        header_frame = tk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        bot_info_frame = tk.Frame(header_frame)
        bot_info_frame.pack(side=tk.LEFT)
        tk.Label(bot_info_frame, text="🤖 봇 계정:", font=("맑은 고딕", 9, "bold")).pack(side=tk.LEFT)
        self.lbl_bot_email = tk.Label(bot_info_frame, text=self.bot_email, font=("맑은 고딕", 9), fg="blue", cursor="hand2")
        self.lbl_bot_email.pack(side=tk.LEFT, padx=(5, 2))
        self.lbl_bot_email.bind("<Button-1>", lambda e: self.copy_bot_email())
        self.lbl_info_icon = tk.Label(bot_info_frame, text="ⓘ", font=("맑은 고딕", 10, "bold"), fg="#555", cursor="hand2")
        self.lbl_info_icon.pack(side=tk.LEFT)
        CreateToolTip(self.lbl_info_icon, "⚠️ 시트 공유 방법: 봇 계정 메일을 구글 시트 [공유]에서 [편집자]로 초대하세요.")
        
        key_status_frame = tk.Frame(header_frame)
        key_status_frame.pack(side=tk.RIGHT)
        self.lbl_key_status = tk.Label(key_status_frame, text="확인 중...", font=("맑은 고딕", 9))
        self.lbl_key_status.pack(side=tk.LEFT, padx=(0, 8))
        self.status_tooltip = CreateToolTip(self.lbl_key_status, "⚠️ 보안 주의사항: 분실/유출 금지!")
        btn_key = tk.Button(key_status_frame, text="JSON 키 설정", command=self.open_key_settings, font=("맑은 고딕", 9), relief="flat", bg=BTN_BG, fg=BTN_FG, padx=8, cursor="hand2")
        btn_key.pack(side=tk.RIGHT)
        self.update_key_display()

        settings_section = tk.Frame(self.main_frame)
        settings_section.pack(fill=tk.X, pady=(0, 5))
        self.settings_collapsed = False
        
        self.settings_header_btn = tk.Button(settings_section, text="▼ 창고 리스트", anchor="w", command=self.toggle_settings_section, relief="flat", font=("맑은 고딕", 9, "bold"), bg="#F8FAFC", fg="#333333", pady=5)
        self.settings_header_btn.pack(fill=tk.X)
        
        self.settings_content = tk.Frame(settings_section, padx=10, pady=10, highlightbackground=BORDER_COLOR, highlightthickness=1)
        self.settings_content.pack(fill=tk.X)
        
        scroll_container = tk.Frame(self.settings_content)
        scroll_container.pack(fill=tk.X, expand=True)
        self.canvas = tk.Canvas(scroll_container, height=90, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.url_container = self.scrollable_frame
        
        for url in self.warehouse_urls: self.add_url_entry(url)
        while len(self.url_entries) < 2: self.add_url_entry("")
        
        btn_frame = tk.Frame(self.settings_content)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        tk.Button(btn_frame, text="➕ 창고 추가", command=lambda: self.add_url_entry(""), relief="flat", bg=BTN_BG, fg=BTN_FG, cursor="hand2", padx=10).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="💾 URL 저장", command=self.save_config_manual, relief="flat", bg=BTN_BG, fg=BTN_FG, cursor="hand2", padx=10).pack(side=tk.RIGHT)

    def add_url_entry(self, url_value):
        row_frame = tk.Frame(self.url_container)
        row_frame.pack(fill=tk.X, pady=2)
        idx = len(self.url_entries) + 1
        lbl = tk.Label(row_frame, text=f"{idx}창고:", width=6, anchor="w", font=("맑은 고딕", 9))
        lbl.pack(side=tk.LEFT)
        del_btn = tk.Button(row_frame, text="x", width=2, relief="flat", fg="#EF4444", bg="#FEE2E2", font=("맑은 고딕", 8, "bold"), cursor="hand2")
        del_btn.pack(side=tk.RIGHT, padx=(5,0))
        entry = tk.Entry(row_frame, font=("맑은 고딕", 9), relief="solid", bd=1)
        entry.insert(0, url_value)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        entry.bind("<Button-3>", self.show_context_menu)
        del_btn.config(command=lambda f=row_frame, e=entry: self.remove_url_entry(f, e))
        self.url_entries.append(entry)
        row_frame.lbl = lbl

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def toggle_settings_section(self):
        if self.settings_collapsed:
            self.settings_content.pack(fill=tk.X)
            self.settings_header_btn.config(text="▼ 창고 리스트")
            self.settings_collapsed = False
        else:
            self.settings_content.pack_forget()
            self.settings_header_btn.config(text="▶ 창고 리스트")
            self.settings_collapsed = True

    def update_key_display(self):
        key_content = None
        if self.key_file_path and os.path.exists(self.key_file_path):
            try:
                with open(self.key_file_path, 'r') as f: key_content = json.load(f)
            except: pass
        if not key_content and self.key_raw_text:
            try: key_content = json.loads(self.key_raw_text)
            except: pass
        if key_content:
            email = key_content.get("client_email")
            if email:
                self.bot_email = email
                self.lbl_bot_email.config(text=self.bot_email, fg="#2563EB")
                self.lbl_key_status.config(text="✅ 인증 완료", fg="#16A34A")
                return
        self.bot_email = "잘못된 키" if (self.key_file_path or self.key_raw_text) else "연결된 키 없음"
        self.lbl_bot_email.config(text=self.bot_email, fg="#DC2626" if "잘못된" in self.bot_email else "gray")
        self.lbl_key_status.config(text="❌ 키 미등록", fg="#DC2626")

    def open_key_settings(self):
        win = tk.Toplevel(self.root); win.title("JSON 키 설정"); win.geometry("500x350")
        tk.Label(win, text="[방법 1] 파일 선택", font=("맑은 고딕", 9, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
        tk.Button(win, text="📂 JSON 키 파일 찾기", command=lambda: self.select_key_file_internal(win), relief="flat", bg=BTN_BG).pack(anchor="w", padx=40)
        tk.Label(win, text="[방법 2] 직접 붙여넣기", font=("맑은 고딕", 9, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        text_area = scrolledtext.ScrolledText(win, height=8, relief="solid", bd=1); text_area.pack(fill=tk.X, padx=20)
        if self.key_raw_text: text_area.insert(tk.END, self.key_raw_text)
        tk.Button(win, text="💾 텍스트 키 저장", command=lambda: self.save_raw_key_internal(win, text_area.get("1.0", tk.END)), relief="flat", bg=BTN_BG).pack(pady=10)

    def select_key_file_internal(self, win):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.key_file_path = file_path; self.key_raw_text = ""; self.save_config(); self.update_key_display()
            self.log("✅ 인증 키 파일 설정 완료! ▶ 가동 준비 완료"); win.destroy()

    def save_raw_key_internal(self, win, text):
        try:
            json.loads(text.strip()); self.key_raw_text = text.strip(); self.key_file_path = ""; self.save_config(); self.update_key_display()
            self.log("✅ 텍스트 키 저장 완료! ▶ 가동 준비 완료"); win.destroy()
        except: messagebox.showerror("오류", "형식이 잘못되었습니다.")

    def copy_bot_email(self):
        if "@" in self.bot_email:
            self.root.clipboard_clear(); self.root.clipboard_append(self.bot_email); messagebox.showinfo("완료", "복사되었습니다.")

    def remove_url_entry(self, frame, entry):
        if entry in self.url_entries: self.url_entries.remove(entry)
        frame.destroy()
        for i, ent in enumerate(self.url_entries):
            if hasattr(ent.master, 'lbl'): ent.master.lbl.config(text=f"{i+1}창고:")

    def save_config_manual(self):
        self.save_config(); messagebox.showinfo("저장", "저장되었습니다.")

    def create_middle_section(self):
        middle_frame = tk.Frame(self.main_frame, padx=10, pady=10, highlightbackground=BORDER_COLOR, highlightthickness=1)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        tk.Label(middle_frame, text="데이터 입력", font=("맑은 고딕", 9, "bold"), fg="#333333").pack(anchor="w", pady=(0, 10))
        
        file_select_row = tk.Frame(middle_frame)
        file_select_row.pack(fill=tk.X)
        file_select_row.columnconfigure(0, weight=1)
        file_select_row.columnconfigure(1, weight=1)
        left_cell = tk.Frame(file_select_row)
        right_cell = tk.Frame(file_select_row)
        left_cell.grid(row=0, column=0, sticky="w")
        right_cell.grid(row=0, column=1, sticky="e")
        
        btn_select = tk.Button(left_cell, text="📂 원본 엑셀 찾기", command=self.select_file, relief="flat", bg=BTN_BG, fg=BTN_FG, cursor="hand2", padx=10, pady=3)
        btn_select.pack(side=tk.LEFT)
        self.file_path_label = tk.Label(left_cell, text="선택된 파일 없음", fg="gray", font=("맑은 고딕", 9))
        self.file_path_label.pack(side=tk.LEFT, padx=10)
        
        start_btn = tk.Button(right_cell, text="🚀 분류 시작", bg=ACTION_BG, fg=ACTION_FG, font=("맑은 고딕", 12, "bold"), height=2, width=15, relief="flat", cursor="hand2", command=self.start_sorting)
        start_btn.pack(side=tk.RIGHT)
        tk.Checkbutton(right_cell, text="완료 후 폴더 열기", variable=self.open_folder_var, font=("맑은 고딕", 9)).pack(side=tk.RIGHT, padx=(0, 10))
        
        paste_frame = tk.Frame(middle_frame)
        paste_frame.pack(fill=tk.X, pady=(15, 2))
        tk.Label(paste_frame, text="직접 붙여넣기:", font=("맑은 고딕", 9)).pack(side=tk.LEFT)
        
        # [핵심 수정] 입력 초기화 클릭 시 파일과 텍스트 모두 깨끗하게 비우기
        self.reset_label = tk.Label(paste_frame, text="입력 초기화", font=("맑은 고딕", 9, "underline"), fg="#64748B", cursor="hand2")
        self.reset_label.pack(side=tk.LEFT, padx=10)
        self.reset_label.bind("<Button-1>", lambda e: self.clear_all_inputs())
        
        self.text_input = tk.Text(middle_frame, height=6, relief="solid", bd=1, font=("맑은 고딕", 9))
        self.text_input.pack(fill=tk.BOTH, expand=True)
        
        # [핵심 수정] 텍스트 창에 무언가 입력/붙여넣기 되면 자동으로 기존 파일 선택 취소
        self.text_input.bind("<KeyPress>", self.clear_file_selection)
        self.text_input.bind("<<Paste>>", self.clear_file_selection)
        self.text_input.bind("<Button-3>", self.show_context_menu)

    # [새로운 함수] 파일 선택과 텍스트 창 동시 초기화
    def clear_all_inputs(self):
        self.text_input.delete("1.0", tk.END)
        self.selected_file_path = None
        self.file_path_label.config(text="선택된 파일 없음", fg="gray")

    # [새로운 함수] 텍스트 입력 시 기존 파일 선택 취소
    def clear_file_selection(self, event=None):
        if self.selected_file_path:
            self.selected_file_path = None
            self.file_path_label.config(text="선택된 파일 없음", fg="gray")

    def show_context_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="복사", command=lambda: self.root.focus_get().event_generate('<<Copy>>'))
        menu.add_command(label="붙여넣기", command=lambda: self.root.focus_get().event_generate('<<Paste>>'))
        menu.add_separator()
        menu.add_command(label="모두 선택", command=lambda: self.root.focus_get().event_generate('<<SelectAll>>'))
        menu.post(event.x_root, event.y_root)

    def create_bottom_section(self):
        bottom_frame = tk.Frame(self.main_frame); bottom_frame.pack(fill=tk.BOTH, expand=True)
        tk.Frame(bottom_frame, height=10).pack(fill=tk.X)
        self.log_box = scrolledtext.ScrolledText(bottom_frame, bg="#1E293B", fg="#F8FAFC", height=8, state='disabled', font=("Consolas", 9), relief="flat"); self.log_box.pack(fill=tk.BOTH, expand=True)
        footer = tk.Frame(bottom_frame); footer.pack(fill=tk.X, pady=(5,0))
        tk.Label(footer, text=f"제작자: {CREATOR}", font=("맑은 고딕", 9), fg="#94A3B8").pack(anchor="e")

    def log(self, message):
        self.log_box.config(state='normal'); self.log_box.insert(tk.END, f"{message}\n"); self.log_box.see(tk.END); self.log_box.config(state='disabled'); self.root.update()

    def select_file(self):
        f = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if f: 
            self.selected_file_path = f
            self.file_path_label.config(text=os.path.basename(f), fg="black")
            # [핵심 수정] 파일을 선택하면 기존 텍스트 창 비우기
            self.text_input.delete("1.0", tk.END)

    def start_sorting(self):
        self.save_config()
        if not self.key_file_path and not self.key_raw_text:
             messagebox.showerror("오류", "키를 먼저 설정하세요."); return

        txt = self.text_input.get("1.0", tk.END).strip()
        if not self.selected_file_path and not txt:
             messagebox.showwarning("주의", "분류할 엑셀 파일을 선택하거나\n데이터를 직접 붙여넣어주세요."); return
             
        self.log(f"\n[작업 시작] {datetime.datetime.now().strftime('%H:%M:%S')}")
        
        # [기능 추가] 현재 분석하는 소스가 무엇인지 로그에 명확히 표기
        if txt:
            self.log(" 📄 [데이터 소스] 붙여넣기 한 텍스트 데이터를 분석합니다.")
        elif self.selected_file_path:
            self.log(f" 📁 [데이터 소스] {os.path.basename(self.selected_file_path)} 파일을 분석합니다.")

        try:
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            if self.key_file_path: creds = Credentials.from_service_account_file(self.key_file_path, scopes=scope)
            else: creds = Credentials.from_service_account_info(json.loads(self.key_raw_text), scopes=scope)
            gc = gspread.authorize(creds)
            urls = [e.get().strip() for e in self.url_entries if e.get().strip()]
            warehouse_sets = []
            for i, url in enumerate(urls):
                try:
                    d = gc.open_by_url(url).get_worksheet(0).col_values(5)[1:]
                    warehouse_sets.append(set(str(x).strip() for x in d if str(x).strip()))
                    self.log(f" ✅ {i+1}창고: 등록번호 {len(warehouse_sets[-1])}개 확인")
                except: self.log(f" ❌ {i+1}창고 연동 실패")
            
            df = None
            if txt:
                try: df = pd.read_csv(io.StringIO(txt), sep='\t', dtype=str)
                except: df = pd.read_csv(io.StringIO(txt), dtype=str)
            elif self.selected_file_path: df = pd.read_excel(self.selected_file_path, dtype=str)
            
            if df is not None:
                target_col = df.columns[4] if len(df.columns) >= 5 else df.columns[0]
                warehouse_dfs = [[] for _ in range(len(warehouse_sets))]
                unclassified = []
                for _, row in df.iterrows():
                    val, matched = str(row[target_col]).strip(), False
                    for i, wh_set in enumerate(warehouse_sets):
                        if val in wh_set: warehouse_dfs[i].append(row); matched = True; break
                    if not matched: unclassified.append(row)
                
                total_matched = 0
                for i, rows in enumerate(warehouse_dfs):
                    count = len(rows)
                    total_matched += count
                    self.log(f" 📊 {i+1}창고: {count}건 분류 완료")
                
                unclass_count = len(unclassified)
                self.log(f" 📊 미분류: {unclass_count}건")

                if total_matched == 0:
                    self.log(" ⚠️ [안내] 시트 번호와 일치하는 데이터가 없습니다. (결과 없음)")

                path = os.path.join(os.path.expanduser("~"), "Desktop", OUTPUT_FOLDER_NAME)
                if not os.path.exists(path): os.makedirs(path)
                fname = f"BR_통합결과_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                full_path = os.path.join(path, fname)
                with pd.ExcelWriter(full_path, engine='openpyxl') as writer:
                    for i, rows in enumerate(warehouse_dfs): pd.DataFrame(rows if rows else [["데이터 없음"]]).to_excel(writer, sheet_name=f"{i+1}창고", index=False)
                    pd.DataFrame(unclassified if unclassified else [["데이터 없음"]]).to_excel(writer, sheet_name="미분류", index=False)
                self.log(f" 💾 저장 완료: {fname}"); messagebox.showinfo("완료", "분류 완료 확인!"); 
                
                if self.open_folder_var.get():
                    open_folder_and_select(full_path)
        except Exception as e: self.log(f" ❌ 오류 발생: {e}")

    def add_separator(self): tk.Frame(self.main_frame, height=2, bd=0, bg=BORDER_COLOR).pack(fill=tk.X, padx=5, pady=10)

if __name__ == "__main__":
    root = tk.Tk(); app = InvoiceSorterApp(root); root.mainloop()