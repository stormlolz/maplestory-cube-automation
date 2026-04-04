# CLAUDE.md

## Project Overview

CatStory Cube Automation — 新楓之谷（MapleStory）自動洗方塊工具。透過螢幕截圖 + OCR 辨識潛能文字，自動判斷是否達標，並操控滑鼠執行洗方塊流程。

## Tech Stack

- **Language**: Python 3.12
- **Package Manager**: uv
- **GUI**: PyQt6
- **OCR**: PaddleOCR (paddleocr + paddlepaddle)
- **Image Processing**: OpenCV (opencv-python), NumPy
- **Screen Capture**: mss
- **Testing**: pytest
- **Packaging**: PyInstaller

## Project Structure

```
app/
├── core/       # 底層工具：截圖(screen)、OCR(ocr)、滑鼠(mouse)、模板匹配(matcher)、條件判斷(condition)、自動化主迴圈(automation)
├── cube/       # 方塊策略：base(ABC) → simple_flow(珍貴/絕對/萌獸) / compare_flow(恢復方塊)
├── gui/        # PyQt6 介面：main_window, region_selector, condition_editor, roll_log, settings_panel
├── models/     # 資料模型：config(AppConfig dataclass), potential(PotentialLine, RollResult)
└── paths.py    # 路徑常數
tests/          # pytest 測試
docs/           # 設計文件（架構、GUI、潛能系統規格、實作進度）
```

## Key Commands

```bash
# 安裝依賴
uv sync

# 執行程式
uv run python main.py

# 執行測試
uv run pytest

# 打包為 exe
uv run pyinstaller cube_automation.spec
```

## Architecture Notes

- **Threading model**: 主執行緒跑 PyQt6 GUI 事件迴圈，AutomationWorker (QThread) 在工作執行緒執行自動化。透過 Qt Signal/Slot 通訊。
- **Strategy pattern**: `CubeStrategy` (ABC) 定義 `execute_roll()` 介面。SimpleFlowStrategy 用於珍貴/絕對/萌獸方塊（直接洗），CompareFlowStrategy 用於恢復方塊（前後比較決定保留或取消）。
- **Config persistence**: `AppConfig` dataclass 序列化為 JSON，啟動時載入、關閉時儲存。包含舊設定遷移邏輯。
- **OCR pipeline**: 螢幕截圖 → PaddleOCR 辨識 → `parse_potential_lines()` 解析 → `ConditionChecker.check()` 判定是否達標。

## Coding Conventions

- 繁體中文註解與 UI 文字
- Logging 使用 `app` namespace logger（不依賴 root logger，避免被 PaddleX 覆蓋）
- Dataclass 用於資料模型（非 Pydantic）
- 測試檔案放在 `tests/` 目錄，以 `test_` 前綴命名

## Domain Context

- 「洗方塊」= 使用方塊道具重新隨機潛能屬性
- 潛能分為 S潛（傳說）和罕見兩個等級，數值門檻依裝備類型與等級不同
- 詳細潛能系統規格見 `docs/potential-system.md`
