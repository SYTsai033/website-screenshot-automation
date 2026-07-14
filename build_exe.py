#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyInstaller Build Script
Compile main.py to standalone EXE executable
"""

import PyInstaller.__main__
import sys
import os

def build_exe():
    """Build EXE"""
    
    # PyInstaller arguments - correct syntax
    args = [
        'main.py',
        '--onefile',
        '--windowed',
        '--name=WebsiteScreenshotTool',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=.',
        '--hidden-import=selenium',
        '--hidden-import=schedule',
    ]
    
    print("=" * 60)
    print("Building EXE...")
    print("=" * 60)
    
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "=" * 60)
        print("Build successful!")
        print("=" * 60)
        print("\nEXE location: dist/WebsiteScreenshotTool.exe")
        print("\nImportant Notes:")
        print("1. Install ChromeDriver or EdgeDriver")
        print("2. Download from:")
        print("   - ChromeDriver: https://chromedriver.chromium.org/")
        print("   - EdgeDriver: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
        print("3. Place chromedriver.exe in the same directory as EXE or in system PATH")
        
    except Exception as e:
        print(f"\nBuild failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
