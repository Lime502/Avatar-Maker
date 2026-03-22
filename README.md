# Minecraft Avatar Generator 🛠️

A Python-based desktop application designed to create stylized pixel-art avatars (38x38) from Minecraft skins. The program automatically processes skin layers, adds a clean 1px outline, and applies shadows while maintaining perfect pixel clarity.

## Key Features
- **Pixel-Art Rendering**: Manual upscaling using the NEAREST filter to ensure zero blur in previews.
- **Auto-Outline**: Smart boundary-detection algorithm for a professional look.
- **Modern UI**: Dark-themed graphical interface built with CustomTkinter.
- **Portable**: Can be compiled into a single standalone `.exe` file.

## Usage & Building

### 1. Install Dependencies
```bash
pip install customtkinter pillow pyinstaller requests
```
### 2. Run the Script
```bash
python avatar_maker.py
```
### 3. Build to EXE
To create a standalone Windows application, use the following command:

```bash
pyinstaller --noconsole --onefile --icon=app.ico avatar_maker.py
```
