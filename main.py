import logging
import os
import sys
import traceback
import warnings

# 抑制第三方套件噪音（環境變數需在 import paddle 前設定）
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
os.environ["FLAGS_minloglevel"] = "2"  # 抑制 Paddle C++ INFO/WARNING
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message="urllib3.*doesn't match a supported version")
warnings.filterwarnings("ignore", message="No ccache found")

from PyQt6.QtWidgets import QApplication, QMessageBox

from app.gui.main_window import MainWindow
from app.paths import APP_DIR

# 為 app namespace 設定獨立的 handler，不依賴 root logger（避免被 PaddleX 覆蓋）
_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
_app_logger = logging.getLogger("app")
_app_logger.setLevel(logging.INFO)
_app_logger.addHandler(_handler)
_app_logger.propagate = False  # 不往 root logger 傳，避免重複或被吃掉

# 啟動錯誤 log 檔案路徑（EXE 旁邊）
_CRASH_LOG = APP_DIR / "crash.log"


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # console=False 時使用者看不到錯誤，寫入 crash.log 並彈出對話框
        tb = traceback.format_exc()
        try:
            _CRASH_LOG.write_text(tb, encoding="utf-8")
        except OSError:
            pass
        # 嘗試用 QMessageBox 顯示錯誤（QApplication 可能已建立）
        try:
            _app = QApplication.instance() or QApplication(sys.argv)
            QMessageBox.critical(None, "啟動失敗", f"程式啟動時發生錯誤，詳見 crash.log：\n\n{tb[:500]}")
        except Exception:
            pass
        sys.exit(1)
