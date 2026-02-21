import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox

class InvoiceSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("택배 송장 자동 분류기")
        self.root.geometry("700x800")
        
        # 메인 프레임 (여백을 위해)
        self.main_frame = tk.Frame(root, padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. 상단: 구글 시트 연동 상태
        self.create_top_section()
        
        # 구분선
        self.add_separator()
        
        # 2. 중단: 데이터 입력 (파일 첨부 및 직접 붙여넣기)
        self.create_middle_section()
        
        # 구분선
        self.add_separator()
        
        # 3. 하단: 실행 및 로그
        self.create_bottom_section()
        
    def create_top_section(self):
        # 상단 프레임
        top_frame = tk.LabelFrame(self.main_frame, text="구글 시트 연동 상태", padx=10, pady=10)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 상태 라벨
        self.status_label_1 = tk.Label(top_frame, text="✅ 1창고 연동 대기중", fg="blue", font=("맑은 고딕", 10, "bold"))
        self.status_label_1.pack(anchor="w")
        
        self.status_label_2 = tk.Label(top_frame, text="✅ 2창고 연동 대기중", fg="blue", font=("맑은 고딕", 10, "bold"))
        self.status_label_2.pack(anchor="w")
        
    def create_middle_section(self):
        # 중단 프레임
        middle_frame = tk.LabelFrame(self.main_frame, text="데이터 입력", padx=10, pady=10)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 방식 A: 파일 첨부
        file_frame = tk.Frame(middle_frame)
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(file_frame, text="방식 A (파일 첨부):", font=("맑은 고딕", 9, "bold")).pack(anchor="w")
        
        btn_frame = tk.Frame(file_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.btn_select_file = tk.Button(btn_frame, text="📂 원본 엑셀 파일 찾기", command=self.select_file)
        self.btn_select_file.pack(side=tk.LEFT)
        
        self.file_path_label = tk.Label(btn_frame, text="선택된 파일 없음", fg="gray")
        self.file_path_label.pack(side=tk.LEFT, padx=10)
        
        # 방식 B: 직접 붙여넣기
        paste_frame = tk.Frame(middle_frame)
        paste_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(paste_frame, text="방식 B (직접 붙여넣기):", font=("맑은 고딕", 9, "bold")).pack(anchor="w")
        tk.Label(paste_frame, text="※ 엑셀 파일이 열리지 않으면, 내용을 복사해서 아래에 붙여넣으세요", fg="red").pack(anchor="w", pady=(2, 5))
        
        # 넓은 텍스트 입력창
        self.text_input = tk.Text(paste_frame, height=10)
        self.text_input.pack(fill=tk.BOTH, expand=True)
        
    def create_bottom_section(self):
        # 하단 프레임
        bottom_frame = tk.LabelFrame(self.main_frame, text="실행 및 결과", padx=10, pady=10)
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        # 자동 분류 시작 버튼
        self.btn_start = tk.Button(bottom_frame, text="🚀 자동 분류 시작", bg="lightgreen", font=("맑은 고딕", 12, "bold"), height=2, command=self.start_sorting)
        self.btn_start.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(bottom_frame, text="진행 로그:", font=("맑은 고딕", 9)).pack(anchor="w")
        
        # 로그 출력 박스 (검은색 배경)
        self.log_box = scrolledtext.ScrolledText(bottom_frame, bg="black", fg="white", height=10, state='disabled')
        self.log_box.pack(fill=tk.BOTH, expand=True)
        
    def add_separator(self):
        tk.Frame(self.main_frame, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)

    def log(self, message):
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, f"{message}\n")
        self.log_box.see(tk.END)
        self.log_box.config(state='disabled')
        
    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")])
        if file_path:
            self.file_path_label.config(text=file_path, fg="black")
            self.log(f"[파일 선택] {file_path}")
        else:
            self.log("[파일 선택 취소]")

    def start_sorting(self):
        self.log("[시작] 자동 분류 작업이 시작되었습니다.")
        # 여기에 추후 로직 추가 예정
        input_text = self.text_input.get("1.0", tk.END).strip()
        if input_text:
             self.log(f"[입력 확인] 텍스트 입력창에 {len(input_text)} 글자가 입력되어 있습니다.")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceSorterApp(root)
    root.mainloop()
