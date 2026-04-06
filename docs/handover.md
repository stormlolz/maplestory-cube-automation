# 接手手冊 — CatStory Cube Automation

本文件供新開發者快速理解並接手此專案。

---

## 1. 專案簡介

**新楓之谷自動洗方塊工具**：透過螢幕截圖 + OCR 辨識潛能文字，自動判斷是否達標，並操控鍵盤執行洗方塊流程。

核心流程：`截圖 → OCR 辨識 → 解析潛能 → 條件判斷 → 按空白鍵洗方塊 → 重複`

---

## 2. 技術棧

| 用途 | 技術 |
|------|------|
| 語言 | Python 3.12 |
| 套件管理 | uv |
| GUI | PyQt6 |
| OCR | PaddleOCR 3.x（繁體中文） |
| 影像處理 | OpenCV + NumPy |
| 螢幕截圖 | mss |
| 測試 | pytest |
| 打包 | PyInstaller |

---

## 3. 環境建置

```bash
# 安裝 uv（如果還沒裝）
pip install uv

# 安裝所有依賴
uv sync

# 啟動程式
uv run python main.py

# 跑測試
uv run pytest

# 打包 EXE
uv run pyinstaller cube_automation.spec
# 產出：dist/CubeAutomation/CubeAutomation.exe
```

> **注意**：首次執行會自動下載 PaddleOCR 模型（約 100MB+），存放在 `models/` 目錄。

---

## 4. 目錄結構

```
main.py                 # 程式進入點（PyQt6 app 啟動 + crash log 機制）
app/
├── paths.py            # 路徑常數（APP_DIR, LOG_DIR, MODEL_DIR, CONFIG_PATH）
├── models/
│   ├── config.py       # AppConfig dataclass（JSON 序列化/反序列化）
│   └── potential.py    # PotentialLine, RollResult 資料模型
├── core/
│   ├── screen.py       # ScreenCapture — mss 截圖，回傳 numpy array
│   ├── ocr.py          # PaddleOCREngine — OCR 辨識 + 影像前處理
│   ├── condition.py    # 潛能解析 + 條件判斷（最複雜的模組）
│   ├── mouse.py        # MouseController — SendInput 發送空白鍵 + 遊戲視窗管理
│   ├── automation.py   # AutomationWorker (QThread) — 自動化主迴圈
│   ├── ocr_test_worker.py  # OCRTestWorker (QThread) — 純 OCR 測試模式
│   └── ocr_logger.py   # OCRLogSession — OCR 結果 log 管理
├── cube/
│   ├── base.py         # CubeStrategy (ABC) — 策略模式基類
│   ├── simple_flow.py  # SimpleFlowStrategy — 珍貴/絕對/萌獸方塊流程
│   └── compare_flow.py # CompareFlowStrategy — 恢復方塊流程（前後比較）
└── gui/
    ├── main_window.py      # 主視窗（按鈕、狀態列、各元件組裝）
    ├── settings_panel.py   # 設定面板（方塊類型、區域框選、延遲）
    ├── condition_editor.py # 條件編輯器（裝備類型、比對模式、自訂條件排）
    ├── region_selector.py  # 全螢幕半透明框選工具
    └── roll_log.py         # 洗方塊紀錄列表
tests/              # pytest 測試
docs/               # 設計文件
```

---

## 5. 架構核心概念

### 5.1 執行緒模型

```
主執行緒 (PyQt6 GUI 事件迴圈)
    ↕ Qt Signal/Slot
工作執行緒 (AutomationWorker / OCRTestWorker，繼承 QThread)
```

- GUI 永遠在主執行緒
- 自動化邏輯在 QThread 中執行，透過 Signal 回報結果
- 停止機制：`threading.Event`，`MouseController.wait()` 使用 `Event.wait()` 可被即時中斷

### 5.2 策略模式（方塊流程）

```
CubeStrategy (ABC)
├── SimpleFlowStrategy   → 珍貴/絕對/萌獸方塊
│   流程：按空白鍵 → 等待 → OCR → 判斷
└── CompareFlowStrategy  → 恢復附加方塊
    流程：OCR 讀取前 → 按空白鍵 → 等待 → OCR 讀取後 → 比較決定保留或取消
```

選擇邏輯在 `automation.py:57`：根據 `config.cube_type` 決定。

### 5.3 OCR 管線

```
螢幕截圖 (mss)
  → 影像前處理 (放大 + 灰階 + OTSU 二值化 + 膨脹 + padding)  [ocr.py]
  → PaddleOCR 辨識（回傳文字 + 座標）                          [ocr.py]
  → OCR 文字修正（誤讀修正表 + regex）                         [condition.py]
  → 碎片合併（數值碎片、前綴碎片按 y 座標合併）                [condition.py]
  → 分群成物理行（按 y 座標間距切割）                           [condition.py]
  → 逐行解析為 PotentialLine                                    [condition.py]
  → ConditionChecker.check() 判斷是否達標                       [condition.py]
```

### 5.4 條件判斷系統

三種比對模式：

| 模式 | 說明 | 實作 |
|------|------|------|
| 預設規則 | 選裝備+屬性，用內建門檻表自動判斷 | `_check_preset_any_pos()` |
| 逐排指定 (AND) | 每排指定屬性+門檻，全部符合才通過 | `_check_custom()` fixed_pos |
| 符合任一 (OR) | 多組條件，任一符合即通過 | `_check_custom()` any_pos |

門檻數值表在 `THRESHOLD_TABLE`（condition.py:461），結構：
```python
{
    "裝備類型": {
        "屬性": ((S潛門檻, 罕見門檻), (全屬性S潛, 全屬性罕見) or None)
    }
}
```

OCR 容錯：主屬性/全屬性/HP 有 ±2 的容錯值（`_OCR_TOLERANCE = 2`），防止 OCR 誤讀數字導致好結果被洗掉。主武器/徽章和萌獸不套用容錯。

### 5.5 鍵盤輸入

使用 Windows `SendInput` API（`mouse.py`），不是模擬滑鼠點擊。

- 透過空白鍵操作遊戲中的方塊對話框
- 送鍵前會檢查前景視窗是否為遊戲（`_GAME_WINDOW_TITLE = "貓貓TMS"`）
- 遊戲視窗名稱寫死在 `mouse.py:14`，如果遊戲更新改名需修改

### 5.6 設定持久化

`AppConfig` dataclass → JSON（`config.json`，位於 EXE 同目錄）。

- 啟動時載入、關閉時儲存
- 包含舊設定遷移邏輯（`config.py:83`）
- 每次啟動清除潛能區域，要求重新框選（防止解析度/位置變動導致框選失效）

---

## 6. 關鍵檔案導覽

### 改動頻率最高的檔案

| 檔案 | 改動原因 |
|------|---------|
| `app/core/condition.py` | 新增屬性、調整門檻、修正 OCR 誤讀 |
| `app/gui/condition_editor.py` | UI 新增裝備類型、比對模式 |
| `app/gui/settings_panel.py` | 新增方塊類型、設定選項 |
| `app/core/ocr.py` | OCR 前處理參數調整 |

### 最複雜的檔案

**`app/core/condition.py`**（約 975 行）— 包含：
- OCR 誤讀修正表（`_OCR_FIXES`，160+ 條）
- 正規表達式屬性匹配（`ATTRIBUTE_PATTERNS`）
- OCR 碎片合併邏輯（值碎片、前綴碎片）
- 潛能行分群演算法（按 y 座標間距切割）
- 門檻數值表（`THRESHOLD_TABLE`）
- 條件判斷引擎（`ConditionChecker`）

---

## 7. 常見開發任務

### 新增一種方塊類型

1. `settings_panel.py` → `CUBE_TYPES` 列表加入新類型
2. `condition.py` → `get_num_lines()` 設定排數
3. `automation.py:57` → 決定使用 SimpleFlow 或 CompareFlow
4. `simple_flow.py` / `compare_flow.py` → 調整按鍵次數/等待時間（如 `confirm_times`）

### 新增一種裝備類型

1. `condition.py` → `THRESHOLD_TABLE` 加入門檻
2. `condition.py` → `EQUIPMENT_ATTRIBUTES` 加入可選屬性
3. `condition.py` → `CUSTOM_SELECTABLE_ATTRIBUTES` + `_EQUIP_TO_CUSTOM_CATEGORY` 加入自訂模式屬性
4. 如果有特殊判斷邏輯（如手套爆傷、帽子冷卻） → 修改 `_check_line()` 和 `generate_condition_summary()`

### 修正 OCR 誤讀

1. 檢查 `logs/` 目錄下的 log 檔案，找到 RAW 文字
2. 在 `condition.py` → `_OCR_FIXES` 加入修正對（`("錯誤文字", "正確文字")`）
3. 如果是 regex 層級的問題，修改 `ATTRIBUTE_PATTERNS` 或新增 `_OCR_*` regex
4. 跑 `uv run pytest` 確認沒破壞現有解析

### 調整 OCR 前處理

`app/core/ocr.py` → `preprocess_for_ocr()`：
- `_SCALE_FACTOR`：放大倍率（預設 1.5x，恢復方塊用 2.0x）
- `_PADDING_PX`：白邊像素（防止邊緣字被截斷）
- OTSU 二值化 + 膨脹加粗（防止細筆畫斷裂如 8→6）

### 打包 EXE

```bash
uv run pyinstaller cube_automation.spec
```

spec 檔案中的關鍵設定：
- `_paddlex_datas`：PaddleX config YAML（runtime 需要）
- `_paddle_binaries`：PaddlePaddle 原生 DLL（mklml.dll 等）
- `excludes`：排除不需要的大型套件節省體積
- `console=False`：無 console 視窗（錯誤寫入 crash.log）

EXE 打包的 frozen 模式處理：
- `paths.py`：偵測 `sys.frozen` 切換路徑
- `ocr.py:62-103`：DLL 載入路徑 + `importlib.metadata` monkey patch（因為 PyInstaller 剝除 `.dist-info`）

---

## 8. 除錯技巧

### Log 檔案

- **`logs/`** — 每次執行產生獨立 log：`automation_方塊類型_時間戳.log` 或 `ocr_test_方塊類型_時間戳.log`
- **`logs/debug/`** — OCR 辨識失敗時自動存截圖（最近 5 張）
- **`crash.log`** — EXE 啟動失敗時的 traceback（在 EXE 同目錄）
- **Console 輸出** — 開發模式下 `app` namespace 的 logger 輸出到 stderr

### OCR 測試模式

GUI 上的「🔍 測試 OCR」按鈕：只截圖+辨識，不按空白鍵。用來驗證框選區域和 OCR 準確度，每 3 秒辨識一次並存 debug 截圖。

### 常見問題排查

| 問題 | 排查方向 |
|------|---------|
| OCR 辨識不到文字 | 檢查框選區域是否正確、`logs/debug/` 截圖是否包含潛能文字 |
| 辨識結果錯誤 | 檢查 log 中的 `RAW=` 欄位，對照 `_OCR_FIXES` 和 `ATTRIBUTE_PATTERNS` |
| 好結果被洗掉 | 可能是 `_OCR_TOLERANCE` 不夠、或 OTSU 二值化導致數字誤讀 |
| EXE 閃退 | 檢查 `crash.log`、確認安裝 VC++ Redistributable |
| 找不到遊戲視窗 | 確認遊戲視窗標題是否為 `"貓貓TMS"`（`mouse.py:14`） |
| 按鍵沒反應 | 確認遊戲在前景、以系統管理員身分執行程式 |

---

## 9. 已知限制 & 未完成項目

1. **CompareFlowStrategy 的保留/取消邏輯未完成**（`compare_flow.py:42-46` 有 TODO）
2. **GPU 加速已停用**（`settings_panel.py:72` checkbox disabled）
3. **遊戲視窗標題寫死**（`mouse.py:14`，`"貓貓TMS"`）— 遊戲更新可能需改
4. **恢復方塊的 _is_better 邏輯過於簡單**（只比 value>0 的行數）
5. **不支援多螢幕** — `mss` 截圖使用絕對座標，多螢幕可能偏移

---

## 10. 測試

```bash
uv run pytest          # 全部測試
uv run pytest -v       # 詳細輸出
uv run pytest -k xxx   # 指定測試
```

測試檔案在 `tests/` 目錄，主要覆蓋 `condition.py` 的解析與判斷邏輯。

---

## 11. 程式碼慣例

- **繁體中文**註解與 UI 文字
- Logging 使用 `app` namespace（`logging.getLogger(__name__)`），不依賴 root logger
- 資料模型用 **dataclass**（非 Pydantic）
- 測試檔案以 `test_` 前綴命名
- 設定遷移邏輯集中在 `AppConfig.load()`
