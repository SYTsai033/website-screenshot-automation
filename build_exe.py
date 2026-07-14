#!/usr/bin/env python
"""
PyInstaller 編譯腳本
將 main.py 編譯成獨立的 EXE 執行檔
"""

import PyInstaller.__main__
import sys
import os

def build_exe():
    """編譯成 EXE"""
    
    # PyInstaller 參數
    args = [
        'main.py',
        '--onefile',  # 生成單一 EXE 檔
        '--windowed',  # 無控制台窗口
        '--name=網站自動截圖工具',  # EXE 名稱
        '--icon=NONE',  # 圖示（可選）
        '--distpath=dist',  # 輸出目錄
        '--buildpath=build',
        '--specpath=.',
        '--hidden-import=selenium',
        '--hidden-import=schedule',
    ]
    
    print("=" * 60)
    print("開始編譯 EXE...")
    print("=" * 60)
    
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "=" * 60)
        print("✅ 編譯成功！")
        print("=" * 60)
        print(f"\n📍 EXE 位置: dist/網站自動截圖工具.exe")
        print("\n⚠️  重要提示:")
        print("1. 需要安裝 ChromeDriver 或 EdgeDriver")
        print("2. 下載地址:")
        print("   - ChromeDriver: https://chromedriver.chromium.org/")
        print("   - EdgeDriver: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
        print("3. 將 chromedriver.exe 放在 EXE 同目錄或系統 PATH 中")
        
    except Exception as e:
        print(f"\n❌ 編譯失敗: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
