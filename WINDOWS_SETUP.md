# 🚀 QUICK SETUP FOR WINDOWS

## Option 1: Automatic Setup (Recommended)
**Just double-click `setup.bat` and follow the prompts!**

## Option 2: PowerShell Setup
```powershell
# Run in PowerShell
.\setup.ps1
```

## Option 3: Manual Setup
```cmd
# 1. Create virtual environment
python -m venv .venv

# 2. Activate it
.venv\Scripts\activate

# 3. Install packages
pip install -r requirements.txt

# 4. Install browsers
playwright install

# 5. Test installation
python -c "import requests, bs4, playwright, pandas; print('Success!')"
```

## 📋 Requirements
- ✅ Python 3.8+ ([Download here](https://www.python.org/downloads/))
- ✅ Windows 10/11
- ✅ Internet connection

## 🎯 Quick Test
After setup, test with:
```cmd
python test_site_access.py
```

## 🔧 Troubleshooting
**Python not found?**
- Install Python from python.org
- ✅ Check "Add Python to PATH" during installation

**PowerShell execution policy error?**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Package installation fails?**
- Check internet connection
- Try running as administrator
- Update pip: `python -m pip install --upgrade pip`

---
*For full documentation, see README.md*
