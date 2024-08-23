# cf2toj
將CF(Polygon)格式轉換成TOJ格式

## 使用方法
1. `python cf2toj.py /path/to/input/directory /path/to/output/directory (-d, --debug) (-c, --clear-output-directory)`
2. 等待壓縮完成

## windows詳細用法
1.先把這個cf2toj tool clone到你的資料夾
2.在有cf2toj.py的這個資料夾內開啟cmd 或 powershall
3.輸入 `ptthon cf2toj.py /path/to/input/directory /path/to/output/directory (-d, --debug) (-c, --clear-output-directory)`
  /path/to/input/directory 為CF格式之資料夾(pakage下載為linux格式，且記得解壓縮)
  /path/to/output/directory 為預輸出之資料夾(假如未存在則會自動創建)
  (-d 或 --debug) 為 debug 模式 (未輸入則視為不開啟)
  (-c 或 --clear-output-directory) 為 clear_output_directory 模式 (未輸入則視為不開啟) 他將會將輸出後未壓縮的檔案資料夾刪除，只留下.tar.xz檔(TOJ格式)
  註. 檔名不包含特殊自元、windows複製路徑中為右斜線`\`但在此須轉換為左斜線`/`，解決方法可以直接改為 r"C:\user\somthing\inputfile"
