import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import schedule
import time
from datetime import datetime
import os
from pathlib import Path
import subprocess
import logging

# 使用 Selenium 進行網站截圖
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
except ImportError:
    pass

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebsiteScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("網站自動截圖工具")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # 網站配置
        self.websites = {
            "technews": "https://technews.tw/category/ai/claude/",
            "yahoo": "https://tw.news.yahoo.com/tag/AI%20%E4%BA%BA%E5%B7%A5%E6%99%BA%E6%85%A7",
            "cna": "https://www.cna.com.tw/tag/5743/",
            "cw": "https://www.cw.com.tw/search/doSearch.action?key=%E7%94%9F%E6%88%90%E5%BC%8FAI",
            "aif": "https://edge.aif.tw/ai-impact-on-journalism-trust-is-the-only-way/"
        }
        
        # 截圖資料夾設定
        self.screenshot_dir = Path.cwd() / "screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)
        
        # 狀態變數
        self.is_running = False
        self.scheduler_thread = None
        self.driver = None
        
        self.setup_ui()
        self.update_status("應用程式已啟動")
        
    def setup_ui(self):
        """設定使用者介面"""
        
        # 上方控制面板
        control_frame = ttk.LabelFrame(self.root, text="控制面板", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 按鈕
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.start_btn = ttk.Button(
            button_frame, 
            text="▶ 開始排程", 
            command=self.start_schedule
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = ttk.Button(
            button_frame, 
            text="⏸ 暫停排程", 
            command=self.pause_schedule,
            state=tk.DISABLED
        )
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.screenshot_btn = ttk.Button(
            button_frame, 
            text="📸 立即截圖", 
            command=self.manual_screenshot
        )
        self.screenshot_btn.pack(side=tk.LEFT, padx=5)
        
        self.open_folder_btn = ttk.Button(
            button_frame, 
            text="📁 開啟資料夾", 
            command=self.open_screenshot_folder
        )
        self.open_folder_btn.pack(side=tk.LEFT, padx=5)
        
        # 狀態標籤
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(status_frame, text="狀態：").pack(side=tk.LEFT)
        self.status_label = ttk.Label(
            status_frame, 
            text="已停止", 
            foreground="red",
            font=("Arial", 10, "bold")
        )
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(status_frame, text="下次執行：").pack(side=tk.LEFT, padx=(20, 0))
        self.next_run_label = ttk.Label(
            status_frame, 
            text="未排程",
            foreground="blue"
        )
        self.next_run_label.pack(side=tk.LEFT, padx=5)
        
        # 日誌面板
        log_frame = ttk.LabelFrame(self.root, text="執行日誌", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 日誌文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=20,
            width=100,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 清除日誌按鈕
        button_frame2 = ttk.Frame(self.root)
        button_frame2.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(
            button_frame2,
            text="🗑 清除日誌",
            command=self.clear_log
        ).pack(side=tk.LEFT)
        
    def update_status(self, message):
        """更新日誌和狀態"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        self.log_text.insert(tk.END, log_message + "\n")
        self.log_text.see(tk.END)
        self.log_text.update()
        
        logger.info(message)
        
    def start_schedule(self):
        """開始排程"""
        if self.is_running:
            messagebox.showwarning("提示", "排程已在執行中")
            return
        
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.status_label.config(text="執行中", foreground="green")
        
        self.update_status("⏰ 排程已啟動，每小時執行一次截圖")
        
        # 立即執行一次
        self.manual_screenshot()
        
        # 啟動排程線程
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
    def pause_schedule(self):
        """暫停排程"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.status_label.config(text="已暫停", foreground="orange")
        self.update_status("⏸ 排程已暫停")
        
    def run_scheduler(self):
        """執行排程循環"""
        schedule.every().hour.do(self.manual_screenshot)
        
        while self.is_running:
            schedule.run_pending()
            
            # 更新下次執行時間
            try:
                next_run = schedule.next_run()
                if next_run:
                    self.next_run_label.config(text=next_run.strftime("%H:%M:%S"))
            except:
                pass
            
            time.sleep(1)
            
    def manual_screenshot(self):
        """手動執行截圖"""
        if not self.is_running and threading.current_thread() != threading.main_thread():
            return
        
        self.update_status("📸 開始截圖所有網站...")
        
        # 在新線程中執行截圖，避免卡住 UI
        screenshot_thread = threading.Thread(target=self._take_screenshots, daemon=True)
        screenshot_thread.start()
        
    def _take_screenshots(self):
        """實際執行截圖邏輯"""
        try:
            # 初始化 Selenium Chrome 驅動
            options = Options()
            options.add_argument("--start-maximized")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            try:
                driver = webdriver.Chrome(options=options)
            except:
                self.update_status("❌ 未找到 ChromeDriver，嘗試使用 Edge 驅動")
                try:
                    from selenium.webdriver.edge.options import Options as EdgeOptions
                    from selenium.webdriver.edge.service import Service
                    edge_options = EdgeOptions()
                    edge_options.add_argument("--start-maximized")
                    driver = webdriver.Edge(options=edge_options)
                except:
                    self.update_status("❌ 無法初始化網頁驅動，請確保已安裝 ChromeDriver 或 EdgeDriver")
                    return
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
            for site_name, url in self.websites.items():
                try:
                    self.update_status(f"正在截圖 {site_name}...")
                    
                    # 訪問網站
                    driver.get(url)
                    time.sleep(3)  # 等待頁面加載
                    
                    # 創建網站資料夾
                    site_dir = self.screenshot_dir / site_name
                    site_dir.mkdir(exist_ok=True)
                    
                    # 儲存截圖
                    screenshot_path = site_dir / f"{timestamp}_{site_name}.png"
                    driver.save_screenshot(str(screenshot_path))
                    
                    self.update_status(f"✅ {site_name} 截圖完成 → {screenshot_path.name}")
                    
                except Exception as e:
                    self.update_status(f"❌ {site_name} 截圖失敗: {str(e)}")
                    
                    # 重試一次
                    try:
                        time.sleep(2)
                        driver.get(url)
                        time.sleep(3)
                        site_dir = self.screenshot_dir / site_name
                        site_dir.mkdir(exist_ok=True)
                        screenshot_path = site_dir / f"{timestamp}_{site_name}_retry.png"
                        driver.save_screenshot(str(screenshot_path))
                        self.update_status(f"✅ {site_name} 重試成功 → {screenshot_path.name}")
                    except Exception as e2:
                        self.update_status(f"❌ {site_name} 重試失敗: {str(e2)}")
            
            driver.quit()
            self.update_status("🎉 本輪截圖完成！")
            
        except Exception as e:
            self.update_status(f"❌ 截圖過程出錯: {str(e)}")
            try:
                driver.quit()
            except:
                pass
                
    def open_screenshot_folder(self):
        """開啟截圖資料夾"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(self.screenshot_dir))
            elif os.name == 'posix':  # macOS/Linux
                subprocess.Popen(['open', str(self.screenshot_dir)])
            
            self.update_status(f"📁 已開啟資料夾: {self.screenshot_dir}")
        except Exception as e:
            messagebox.showerror("錯誤", f"無法開啟資料夾: {str(e)}")
            self.update_status(f"❌ 無法開啟資料夾: {str(e)}")
            
    def clear_log(self):
        """清除日誌"""
        self.log_text.delete(1.0, tk.END)
        self.update_status("🗑 日誌已清除")
        
    def on_closing(self):
        """關閉應用程式"""
        if self.is_running:
            if messagebox.askyesno("確認", "排程正在執行，確定要退出嗎？"):
                self.is_running = False
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = WebsiteScreenshotApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
