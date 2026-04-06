# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/), versioning follows [Semantic Versioning](https://semver.org/lang/zh-TW/).

## [Unreleased]

## [1.1.0] - 2026-04-06

### Added

- feat: crash.log error handling — write traceback + show QMessageBox on startup failure
- feat: UAC admin elevation — EXE auto-requests admin rights (required for SendInput)
- feat: display current version in window title bar
- feat: manual "check for update" button in status bar (queries GitHub Releases API)
- feat: OCR prefix fragment merging (`_merge_prefix_fragments`) — fixes split fragments like "爆擊" + "傷害:+N%"
- feat: delay range hint and animation warning in settings panel
- feat: save debug screenshots (raw + processed) on every roll, keep last 10
- docs: developer handover manual (`docs/handover.md`)
- chore: add ruff linter as dev dependency

### Fixed

- fix: 30+ new OCR misread corrections (INT I/l/1/i confusion, MaxHP M→H/[ variants, 全屬性 regex fallback, trailing noise cleanup, digit noise)
- fix: broaden INT regex to `[Il1i]NT` for direct pattern matching
- fix: broaden crit damage pattern to explicit character list `[擊擎繫系撃整]`
- fix: all-stats fallback regex for any single-char misread of 屬
- fix: debug screenshots not saving on Windows Unicode paths (cv2.imencode workaround)
- fix: strip all Unicode whitespace in OCR preprocessing (not just ASCII spaces)
- fix: trailing alpha/digit noise cleanup in OCR text

### Changed

- delay defaults: 1500ms default, 1200-3000ms range (was 1000ms, 500-2000ms)
- delay resets to default on every app launch
- delay input auto-corrects to nearest valid value

## [0.4.0] - 2026-04-06

### Added

- feat: display current version in window title bar
- feat: manual "check for update" button in status bar (queries GitHub Releases API)
- chore: add ruff linter as dev dependency

### Fixed

- fix: 13 new OCR misread corrections (crit damage, LIK/DIK, damage variants, HP recovery)
- fix: broaden crit damage pattern to catch unknown OCR misreads
- fix: debug screenshots not saving on Windows Unicode paths (cv2.imencode workaround)
- style: fix ruff E741 ambiguous variable names across codebase

## [0.3.0] - 2026-04-05

### Added

- feat: delay range hint and animation warning in settings panel
- feat: save debug screenshots (raw + processed) on every roll, keep last 10
- CI: dev branch auto-build workflow (artifact only, no Release)
- docs: CHANGELOG
- docs: OCR bugfix log

### Fixed

- fix: worker not stopping after target condition reached (missing stop() call)
- fix: compound damage attributes misidentified when whitespace between characters
- fix: strip all Unicode whitespace in OCR preprocessing (not just ASCII spaces)
- OCR: attribute misreads (全屋性/全國性/全慶性 → 全屬性)
- OCR: INT character confusion (1NT/1IT/1TT/IIT/IT → INT, with boundary guard)
- OCR: trailing digits after % (+6%6 → +6%)
- OCR: percent misread as 9 (+79 → +7%, fallback only when normal parse fails)
- OCR: MaxHP/MaxMP prefix misread (axHP → MaxHP)

### Changed

- delay defaults: 1500ms default, 1200-3000ms range (was 1000ms, 500-2000ms)
- delay resets to default on every app launch
- delay input auto-corrects to nearest valid value

## [0.2.0] - 2026-03-24

### Added

- CI: manual workflow dispatch for test builds
- CI: upload build directory for artifact downloads

### Fixed

- OCR: add corrections for 傷 misreads (佩害/集害/最終喜)
- OCR: disable doc_preprocessor to avoid UVDoc PermissionError

### Changed

- chore: enable console window for debugging

## [0.1.0] - 2026-03-15

### Added

- Core: screen capture, OCR (PaddleOCR chinese_cht), mouse control, template matching
- Core: condition checking with attribute pattern matching
- Core: cube rolling strategies (simple flow, compare flow)
- GUI: PyQt6 main window, region selector, settings panel, roll log
- Config: JSON save/load with serialization
- Tests: unit tests for condition parsing and config persistence
- Docs: architecture, GUI layout, implementation plan
