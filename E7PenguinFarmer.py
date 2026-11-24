import os
import sys

# Ensure stdout/stderr exist when running with pythonw.exe
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')

import time
import json
import threading
import ctypes
import re
import tkinter as tk
from tkinter import ttk, messagebox
import pygetwindow as gw
import pyautogui
import keyboard
from PIL import Image, ImageTk, ImageGrab
import numpy as np
import cv2
try:
    import winsound
except ImportError:
    winsound = None

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config_penguin.json')

def load_user_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        'language': 'en', 'stigma': -1, 'cost': 102, 'mode': 'full_auto',
        'sell_1': True, 'sell_1_qty': 'MAX',
        'sell_2': True, 'sell_2_qty': 'MAX',
        'sell_3': False, 'sell_3_qty': 'MAX',
        'topmost': False, 'sound': True,
        'mouse_speed': 0.08, 'screenshot_speed': 0.15
    }

def save_user_config(data):
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

I18N = {
    'en': {
        'lang_name': 'English',
        'title': 'SANCTUARY • FOREST OF SOULS',
        'subtitle': 'Penguin Cultivation & Auto-Harvest Hub',
        'sec_mode': 'OPERATION MODE',
        'mode_full': 'Full Loop (Buy + Tally + Auto-Sell)',
        'mode_buy': 'Buy Only (Buy -> Max -> Buy All -> Tally)',
        'mode_sell': 'Sell Only (Auto-Sell Penguins in Inventory)',
        'sec_stigma': 'STIGMA BUDGET & PLAN',
        'lbl_stigma_limit': 'Stigma Limit:',
        'lbl_cost_per': 'Cost / Penguin:',
        'cost_note': 'Stigma (1 Batch = 50 x {cost} = {batch_cost:,})',
        'calc_plan': 'Plan: {penguins:,} Penguins ({batches} Batches) | Gold: ~{gold_est:,}',
        'sec_tally': 'LIVE HARVEST YIELD & STIGMA',
        'lbl_small_name': '★ 1★ Small',
        'lbl_medium_name': '★★ 2★ Medium',
        'lbl_large_name': '★★★ 3★ Large',
        'lbl_spent': 'Stigma Spent: {spent:,} / {target}',
        'lbl_gold': 'Gold (Est.): ~{gold:,}',
        'lbl_ss_time': 'Screenshot Time (s):',
        'lbl_click_time': 'Click Time (s):',
        'sec_sell': 'INVENTORY AUTO-SELL FILTER',
        'sell_1': '1★ Penguin (Green) -> Sell for Gold',
        'sell_2': '2★ Penguin (Blue) -> Sell for Gold',
        'sell_3': '3★ Penguin (Epic) -> Keep for EXP (Do Not Sell)',
        'preset_rec': '★ 1★ & 2★ (Rec)',
        'preset_1_only': '1★ Only',
        'preset_2_only': '2★ Only',
        'preset_all': 'All (1★-3★)',
        'lbl_gold_rate': 'Rate: 1★ = 6K | 2★ = 18K | 3★ = 54K G',
        'lbl_sell_qty': 'Qty:',
        'lbl_sell_est': 'Est. Gold from Sale: ~{gold:,}',
        'sell_opt_1': '1★ Small (Green)',
        'sell_opt_2': '2★ Medium (Blue)',
        'sell_opt_3': '3★ Large (Epic)',
        'btn_pin_on': '📌 Pin: ON',
        'btn_pin_off': '📌 Pin: OFF',
        'btn_snap': '📐 Snap E7',
        'chk_sound': '🔔 Sound',
        'btn_start': 'START FARMING',
        'btn_stop': 'STOP (ESC)',
        'status_ready': 'Status: Ready (Standby)',
        'status_running': 'Status: Farming in progress...',
        'status_navigating': 'Navigating to Growth Altar...',
        'status_buying_batch': 'Buying Batch {b}/{batches}...',
        'status_selling': 'Selling penguins in inventory...',
        'status_done': 'Finished!',
        'status_stopped': 'Stopped.',
        'status_error': 'Error!',
        'log_init_ready': 'E7 Sanctuary & Forest of Souls Cultivator ready.',
        'log_init_feature': 'Feature: Real-time penguin yield detection per tier and Stigma tracking.',
        'log_init_note': 'Note: Keep Epic Seven window visible and unobstructed.',
        'log_nav_altar': '\n--- Navigating to Growth Altar (Forest of Souls) ---',
        'log_buy_ready': '[OK] Buy button is visible on screen.',
        'log_found_altar': '[OK] Found Growth Altar button. Clicking...',
        'log_found_soul': '[OK] Found Forest of Souls in Sanctuary. Clicking...',
        'log_searching_altar': 'Searching for Growth Altar button...',
        'log_opening_menu': 'Opening Quick Menu (top-right)...',
        'log_click_sanctuary': 'Step 1: Clicking Sanctuary...',
        'log_click_soul': 'Step 2: Clicking Forest of Souls...',
        'log_click_altar': 'Step 3: Clicking Growth Altar...',
        'log_batch_header': '\n=== [Batch {b}/{total}] Purchasing 50 Penguins ===',
        'log_click_buy': '1. Clicking Buy button ({cost} Stigma)...',
        'log_click_max': '2. Clicking Max button...',
        'log_click_buyall': '3. Clicking Buy All button ({cost:,} Stigma)...',
        'log_wait_result': '4. Waiting for hatch animation & result screen...',
        'log_batch_result': '-> [BATCH {b} RESULT] +{s} Small (1★), +{m} Medium (2★), +{l} Large (3★)',
        'log_tally_subtotal': '-> [SUBTOTAL] Small: {s} | Medium: {m} | Large: {l}',
        'log_cost_subtotal': '-> [COST] Stigma Spent: {spent:,} | Est. Gold Value: ~{gold:,}',
        'log_tap_close': '5. Tapping to close result dialog...',
        'log_batch_done': '[OK] Batch {b} finished.',
        'log_sell_start': '\n=== Starting Inventory Penguin Sale ===',
        'log_open_inv': '1. Opening Inventory...',
        'log_tab_materials': '2. Selecting Materials tab...',
        'log_btn_arrange': '3. Opening Arrange menu...',
        'log_sell_1': '4a. Selecting 1★ Penguins [Total: {s}]...',
        'log_sell_2': '4b. Selecting 2★ Penguins [Total: {m}]...',
        'log_sell_3': '4c. Selecting 3★ Penguins [Total: {l}]...',
        'log_click_sell': '5. Clicking Sell button...',
        'log_confirm_sell': '6. Confirming sale dialog...',
        'log_sell_done': '[SUCCESS] Penguin sale completed.',
        'log_flow_done': '\n==========================================\n   WORKFLOW COMPLETED SUCCESSFULLY!\n   Total Stigma Spent : {spent:,}\n   Small Penguin (1★) : {s}\n   Medium Penguin (2★): {m}\n   Large Penguin (3★) : {l}\n==========================================',
        'log_stopped_esc': '\n[STOP] Bot stopped by user (ESC).',
        'log_err_target': '[ERROR] Target window "{w}" not found.',
        'log_win_active': '[OK] Target window "{w}" active at foreground (0, 0, 906x539).',
        'log_err_general': '[ERROR] An error occurred: {e}',
    },
    'ko': {
        'lang_name': '한국어',
        'title': '성역 • 정령의 숲',
        'subtitle': '펭귄 부화 & 스티그마 파밍 허브',
        'sec_mode': '동작 모드',
        'mode_full': '풀 루프 (구매 + 집계 + 인벤토리 자동 판매)',
        'mode_buy': '구매 전용 (구매 -> 최대 -> 일괄구매 -> 결과 집계)',
        'mode_sell': '판매 전용 (인벤토리 펭귄 자동 판매)',
        'sec_stigma': '스티그마 설정 및 계획',
        'lbl_stigma_limit': '스티그마 한도:',
        'lbl_cost_per': '마리당 비용:',
        'cost_note': '스티그마 (1회 50마리 x {cost} = {batch_cost:,})',
        'calc_plan': '계획: 펭귄 {penguins:,}마리 ({batches}회) | 골드: ~{gold_est:,}',
        'sec_tally': '실시간 펭귄 획득 & 소모량',
        'lbl_small_name': '★ 초급 (1★)',
        'lbl_medium_name': '★★ 중급 (2★)',
        'lbl_large_name': '★★★ 상급 (3★)',
        'lbl_spent': '스티그마 소모: {spent:,} / {target}',
        'lbl_gold': '예상 골드: ~{gold:,}',
        'lbl_ss_time': '스크린샷 시간 (초):',
        'lbl_click_time': '클릭 시간 (초):',
        'sec_sell': '인벤토리 자동 판매 필터',
        'sell_1': '1★ 펭귄 (초급 - 초록) -> 골드로 판매',
        'sell_2': '2★ 펭귄 (중급 - 파랑) -> 골드로 판매',
        'sell_3': '3★ 펭귄 (상급 - 금/보라) -> 경험치용 보관 (판매 안 함)',
        'preset_rec': '★ 추천 (1★+2★)',
        'preset_1_only': '1★ 전용',
        'preset_2_only': '2★ 전용',
        'preset_all': '전체 (1★-3★)',
        'lbl_gold_rate': '단가: 1★ = 6K | 2★ = 18K | 3★ = 54K G',
        'lbl_sell_qty': '수량:',
        'lbl_sell_est': '예상 판매 골드: ~{gold:,}',
        'sell_opt_1': '1★ 초급 (초록)',
        'sell_opt_2': '2★ 중급 (파랑)',
        'sell_opt_3': '3★ 상급 (금/보라)',
        'btn_pin_on': '📌 고정: ON',
        'btn_pin_off': '📌 고정: OFF',
        'btn_snap': '📐 위치맞춤',
        'chk_sound': '🔔 알림음',
        'btn_start': '파밍 시작 (START)',
        'btn_stop': '중지 (ESC)',
        'status_ready': '상태: 준비 완료 (대기 중)',
        'status_running': '상태: 파밍 진행 중...',
        'status_navigating': '성장의 제단으로 이동 중...',
        'status_buying_batch': '{b}/{batches}회 구매 진행 중...',
        'status_selling': '인벤토리에서 펭귄 판매 중...',
        'status_done': '완료되었습니다!',
        'status_stopped': '중지되었습니다.',
        'status_error': '오류 발생!',
        'log_init_ready': 'E7 성역 정령의 숲 부화기가 준비되었습니다.',
        'log_init_feature': '기능: 실시간 펭귄 등급별 획득량 자동 인식 및 스티그마 소모 집계.',
        'log_init_note': '참고: 에픽세븐 창이 다른 창에 가려지지 않도록 해주세요.',
        'log_nav_altar': '\n--- 성장의 제단(정령의 숲)으로 이동 중 ---',
        'log_buy_ready': '[OK] 구매 버튼이 활성화되어 있습니다.',
        'log_found_altar': '[OK] 성장의 제단 버튼 발견. 클릭 중...',
        'log_found_soul': '[OK] 성역의 정령의 숲 발견. 클릭 중...',
        'log_searching_altar': '성장의 제단 버튼 검색 중...',
        'log_opening_menu': '빠른 메뉴(우측 상단) 여는 중...',
        'log_click_sanctuary': '1단계: 성역 클릭...',
        'log_click_soul': '2단계: 정령의 숲 클릭...',
        'log_click_altar': '3단계: 성장의 제단 클릭...',
        'log_batch_header': '\n=== [{b}/{total}회] 펭귄 50마리 구매 ===',
        'log_click_buy': '1. 구매 버튼 클릭 ({cost} 스티그마)...',
        'log_click_max': '2. 최대(Max) 버튼 클릭...',
        'log_click_buyall': '3. 일괄 구매 버튼 클릭 ({cost:,} 스티그마)...',
        'log_wait_result': '4. 부화 애니메이션 및 결과 화면 대기 중...',
        'log_batch_result': '-> [{b}회 결과] +{s} 초급(1★), +{m} 중급(2★), +{l} 상급(3★)',
        'log_tally_subtotal': '-> [소계] 초급: {s} | 중급: {m} | 상급: {l}',
        'log_cost_subtotal': '-> [비용] 스티그마 소모: {spent:,} | 골드 추정치: ~{gold:,}',
        'log_tap_close': '5. 화면을 터치하여 닫는 중 (Tap to close)...',
        'log_batch_done': '[OK] {b}회차 완료.',
        'log_sell_start': '\n=== 인벤토리 펭귄 판매 시작 ===',
        'log_open_inv': '1. 인벤토리 여는 중...',
        'log_tab_materials': '2. 재료 탭 선택 중...',
        'log_btn_arrange': '3. 정리(Arrange) 메뉴 진입...',
        'log_sell_1': '4a. 1★ 펭귄 선택 [합계: {s}]...',
        'log_sell_2': '4b. 2★ 펭귄 선택 [합계: {m}]...',
        'log_sell_3': '4c. 3★ 펭귄 선택 [합계: {l}]...',
        'log_click_sell': '5. 판매 버튼 클릭...',
        'log_confirm_sell': '6. 판매 확인 대화상자 확인...',
        'log_sell_done': '[성공] 펭귄 판매가 완료되었습니다.',
        'log_flow_done': '\n==========================================\n   모든 작업이 성공적으로 완료되었습니다!\n   총 스티그마 소모 : {spent:,}\n   초급 펭귄 (1★) : {s}\n   중급 펭귄 (2★) : {m}\n   상급 펭귄 (3★) : {l}\n==========================================',
        'log_stopped_esc': '\n[STOP] 사용자에 의해 중지되었습니다 (ESC).',
        'log_err_target': '[오류] 대상 창 "{w}"을 찾을 수 없습니다.',
        'log_win_active': '[OK] 대상 창 "{w}" 활성화됨 (0, 0, 906x539).',
        'log_err_general': '[오류] 문제가 발생했습니다: {e}',
    },
    'ja': {
        'lang_name': '日本語',
        'title': '聖域 • 精霊の森',
        'subtitle': 'ペンギン自動育成＆スティグマ集計',
        'sec_mode': '動作モード',
        'mode_full': 'フルループ (購入 + 集計 + 自動売却)',
        'mode_buy': '購入のみ (購入 -> 最大 -> 一括購入 -> 結果集計)',
        'mode_sell': '売却のみ (所持ペンギンを自動売却)',
        'sec_stigma': 'スティグマ設定＆育成計画',
        'lbl_stigma_limit': 'スティグマ上限:',
        'lbl_cost_per': '1体あたりの費用:',
        'cost_note': 'スティグマ (1回50体 x {cost} = {batch_cost:,})',
        'calc_plan': '予定: ペンギン {penguins:,}体 ({batches}回) | ゴールド: ~{gold_est:,}',
        'sec_tally': '獲得ペンギン＆スティグマ消費',
        'lbl_small_name': '★ 初級 (1★)',
        'lbl_medium_name': '★★ 中級 (2★)',
        'lbl_large_name': '★★★ 上級 (3★)',
        'lbl_spent': '消費スティグマ: {spent:,} / {target}',
        'lbl_gold': '予想ゴールド: ~{gold:,}',
        'lbl_ss_time': 'スクショ間隔 (秒):',
        'lbl_click_time': 'クリック間隔 (秒):',
        'sec_sell': 'インベントリ自動売却フィルター',
        'sell_1': '1★ ペンギン (初級 - 緑) -> ゴールドで売却',
        'sell_2': '2★ ペンギン (中級 - 青) -> ゴールドで売却',
        'sell_3': '3★ ペンギン (上級 - 金/紫) -> 育成用キープ (売却しない)',
        'preset_rec': '★ 推奨 (1★+2★)',
        'preset_1_only': '1★ のみ',
        'preset_2_only': '2★ のみ',
        'preset_all': '全て (1★-3★)',
        'lbl_gold_rate': '単価: 1★ = 6K | 2★ = 18K | 3★ = 54K G',
        'lbl_sell_qty': '数量:',
        'lbl_sell_est': '売却予想ゴールド: ~{gold:,}',
        'sell_opt_1': '1★ 初級 (緑)',
        'sell_opt_2': '2★ 中級 (青)',
        'sell_opt_3': '3★ 上級 (金/紫)',
        'btn_pin_on': '📌 固定: ON',
        'btn_pin_off': '📌 固定: OFF',
        'btn_snap': '📐 位置合わせ',
        'chk_sound': '🔔 通知音',
        'btn_start': 'ファーミング開始 (START)',
        'btn_stop': '停止 (ESC)',
        'status_ready': '状態: 待機中 (Ready)',
        'status_running': '状態: ファーミング実行中...',
        'status_navigating': '成長の祭壇へ移動中...',
        'status_buying_batch': '{b}/{batches}回目を購入中...',
        'status_selling': 'インベントリでペンギンを売却中...',
        'status_done': '完了しました！',
        'status_stopped': '停止しました。',
        'status_error': 'エラー発生！',
        'log_init_ready': 'E7 聖域 精霊の森 育成機が準備完了しました。',
        'log_init_feature': '機能: ペンギン等級別の獲得数自動認識＆スティグマ消費集計。',
        'log_init_note': '注意: エピックセブンの画面が他のウィンドウで遮られないようにしてください。',
        'log_nav_altar': '\n--- 成長の祭壇(精霊の森)へ移動中 ---',
        'log_buy_ready': '[OK] 購入ボタンが表示されています。',
        'log_found_altar': '[OK] 成長の祭壇ボタンを検出。クリック中...',
        'log_found_soul': '[OK] 聖域の精霊の森を検出。クリック中...',
        'log_searching_altar': '成長の祭壇ボタンを検索中...',
        'log_opening_menu': 'クイックメニュー(右上)を開いています...',
        'log_click_sanctuary': 'ステップ1: 聖域をクリック...',
        'log_click_soul': 'ステップ2: 精霊の森をクリック...',
        'log_click_altar': 'ステップ3: 成長の祭壇をクリック...',
        'log_batch_header': '\n=== [{b}/{total}回目] ペンギン50体を購入 ===',
        'log_click_buy': '1. 購入ボタンをクリック ({cost} スティグマ)...',
        'log_click_max': '2. 最大(Max)ボタンをクリック...',
        'log_click_buyall': '3. 一括購入ボタンをクリック ({cost:,} スティグマ)...',
        'log_wait_result': '4. 育成演出および結果画面を待機中...',
        'log_batch_result': '-> [{b}回目結果] +{s} 初級(1★), +{m} 中級(2★), +{l} 上級(3★)',
        'log_tally_subtotal': '-> [小計] 初級: {s} | 中級: {m} | 上級: {l}',
        'log_cost_subtotal': '-> [費用] スティグマ消費: {spent:,} | ゴールド概算: ~{gold:,}',
        'log_tap_close': '5. 画面をタップして閉じる (Tap to close)...',
        'log_batch_done': '[OK] {b}回目の処理が完了しました。',
        'log_sell_start': '\n=== 所持ペンギンの売却を開始 ===',
        'log_open_inv': '1. インベントリを開いています...',
        'log_tab_materials': '2. 素材タブを選択中...',
        'log_btn_arrange': '3. 整理メニューへ移動中...',
        'log_sell_1': '4a. 1★ ペンギンを選択 [合計: {s}]...',
        'log_sell_2': '4b. 2★ ペンギンを選択 [合計: {m}]...',
        'log_sell_3': '4c. 3★ ペンギンを選択 [合計: {l}]...',
        'log_click_sell': '5. 売却ボタンをクリック...',
        'log_confirm_sell': '6. 売却確認ダイアログを承認...',
        'log_sell_done': '[成功] ペンギンの売却が完了しました。',
        'log_flow_done': '\n==========================================\n   すべての処理が正常に終了しました！\n   総消費スティグマ : {spent:,}\n   初級ペンギン (1★) : {s}\n   中級ペンギン (2★) : {m}\n   上級ペンギン (3★) : {l}\n==========================================',
        'log_stopped_esc': '\n[STOP] ユーザー操作により停止しました (ESC)。',
        'log_err_target': '[エラー] 対象ウィンドウ "{w}" が見つかりません。',
        'log_win_active': '[OK] 対象ウィンドウ "{w}" を最前面に配置 (0, 0, 906x539)。',
        'log_err_general': '[エラー] 処理中に問題が発生しました: {e}',
    },
    'zh_TW': {
        'lang_name': '繁體中文',
        'title': '聖域 • 精靈之森',
        'subtitle': '企鵝自動培育與雌黃統計中心',
        'sec_mode': '運行模式',
        'mode_full': '完整循環 (購買 + 統計 + 背包自動出售)',
        'mode_buy': '僅購買 (購買 -> 最大 -> 一同購買 -> 統計)',
        'mode_sell': '僅出售 (自動出售背包企鵝)',
        'sec_stigma': '雌黃 (Stigma) 上限設定',
        'lbl_stigma_limit': '雌黃上限:',
        'lbl_cost_per': '每隻花費:',
        'cost_note': '雌黃 (每批50隻 x {cost} = {batch_cost:,})',
        'calc_plan': '預計: 企鵝 {penguins:,}隻 ({batches}批) | 金幣: ~{gold_est:,}',
        'sec_tally': '即時企鵝獲得與雌黃消耗',
        'lbl_small_name': '★ 初級 (1★)',
        'lbl_medium_name': '★★ 中級 (2★)',
        'lbl_large_name': '★★★ 上級 (3★)',
        'lbl_spent': '雌黃消耗: {spent:,} / {target}',
        'lbl_gold': '預估金幣: ~{gold:,}',
        'lbl_ss_time': '截圖時間 (秒):',
        'lbl_click_time': '點擊時間 (秒):',
        'sec_sell': '背包企鵝自動出售篩選',
        'sell_1': '1★ 企鵝 (初級 - 綠) -> 出售換取金幣',
        'sell_2': '2★ 企鵝 (中級 - 藍) -> 出售換取金幣',
        'sell_3': '3★ 企鵝 (上級 - 金/紫) -> 保留升級用 (不出售)',
        'preset_rec': '★ 推薦 (1★+2★)',
        'preset_1_only': '僅 1★',
        'preset_2_only': '僅 2★',
        'preset_all': '全部 (1★-3★)',
        'lbl_gold_rate': '單價: 1★ = 6K | 2★ = 18K | 3★ = 54K G',
        'lbl_sell_qty': '數量:',
        'lbl_sell_est': '預估出售金幣: ~{gold:,}',
        'sell_opt_1': '1★ 初級 (綠)',
        'sell_opt_2': '2★ 中級 (藍)',
        'sell_opt_3': '3★ 上級 (金/紫)',
        'btn_pin_on': '📌 置頂: 開',
        'btn_pin_off': '📌 置頂: 關',
        'btn_snap': '📐 吸附窗口',
        'chk_sound': '🔔 提示音',
        'btn_start': '開始掛機 (START)',
        'btn_stop': '停止 (ESC)',
        'status_ready': '狀態: 就緒 (待命中)',
        'status_running': '狀態: 培育進行中...',
        'status_navigating': '正在前往成長祭壇...',
        'status_buying_batch': '正在購買第 {b}/{batches} 批...',
        'status_selling': '正在出售背包企鵝...',
        'status_done': '培育完成！',
        'status_stopped': '已停止。',
        'status_error': '發生錯誤！',
        'log_init_ready': 'E7 聖域精靈之森培育中心已就緒。',
        'log_init_feature': '功能: 即時辨識各階企鵝獲得數量與雌黃消耗累積。',
        'log_init_note': '注意: 請確保第七史詩遊戲視窗未被其他程式遮擋。',
        'log_nav_altar': '\n--- 正在前往成長祭壇 (精靈之森) ---',
        'log_buy_ready': '[OK] 購買按鈕已在畫面上可見。',
        'log_found_altar': '[OK] 發現成長祭壇按鈕，正在點擊...',
        'log_found_soul': '[OK] 發現精靈之森，正在點擊...',
        'log_searching_altar': '正在尋找成長祭壇按鈕...',
        'log_opening_menu': '正在打開快捷選單 (右上角)...',
        'log_click_sanctuary': '步驟 1: 點擊聖域...',
        'log_click_soul': '步驟 2: 點擊精靈之森...',
        'log_click_altar': '步驟 3: 點擊成長祭壇...',
        'log_batch_header': '\n=== [第 {b}/{total} 批] 購買 50 隻企鵝 ===',
        'log_click_buy': '1. 點擊購買按鈕 ({cost} 雌黃)...',
        'log_click_max': '2. 點擊最大 (Max) 按鈕...',
        'log_click_buyall': '3. 點擊一同購買按鈕 ({cost:,} 雌黃)...',
        'log_wait_result': '4. 等待孵化動畫與結果畫面...',
        'log_batch_result': '-> [第 {b} 批結果] +{s} 初級(1★), +{m} 中級(2★), +{l} 上級(3★)',
        'log_tally_subtotal': '-> [累計數量] 初級: {s} | 中級: {m} | 上級: {l}',
        'log_cost_subtotal': '-> [花費統計] 雌黃消耗: {spent:,} | 預估金幣價值: ~{gold:,}',
        'log_tap_close': '5. 點擊螢幕關閉結果視窗 (Tap to close)...',
        'log_batch_done': '[OK] 第 {b} 批處理完成。',
        'log_sell_start': '\n=== 開始出售背包企鵝 ===',
        'log_open_inv': '1. 打開背包 (Inventory)...',
        'log_tab_materials': '2. 選擇強化素材標籤...',
        'log_btn_arrange': '3. 進入整理選單...',
        'log_sell_1': '4a. 選擇 1★ 企鵝 [總計: {s}]...',
        'log_sell_2': '4b. 選擇 2★ 企鵝 [總計: {m}]...',
        'log_sell_3': '4c. 選擇 3★ 企鵝 [總計: {l}]...',
        'log_click_sell': '5. 點擊出售按鈕...',
        'log_confirm_sell': '6. 確認出售對話框...',
        'log_sell_done': '[成功] 企鵝出售完畢。',
        'log_flow_done': '\n==========================================\n   全流程已順利完成！\n   總計消耗雌黃 : {spent:,}\n   初級企鵝 (1★) : {s}\n   中級企鵝 (2★) : {m}\n   上級企鵝 (3★) : {l}\n==========================================',
        'log_stopped_esc': '\n[STOP] 使用者手動中止 (ESC)。',
        'log_err_target': '[錯誤] 找不到目標視窗 "{w}"。',
        'log_win_active': '[OK] 目標視窗 "{w}" 已置頂前景 (0, 0, 906x539)。',
        'log_err_general': '[錯誤] 執行過程中發生異常: {e}',
    },
    'zh_CN': {
        'lang_name': '简体中文',
        'title': '圣域 • 精灵之森',
        'subtitle': '企鹅自动培育与雌黄统计中心',
        'sec_mode': '运行模式',
        'mode_full': '完整循环 (购买 + 统计 + 背包自动出售)',
        'mode_buy': '仅购买 (购买 -> 最大 -> 一同购买 -> 统计)',
        'mode_sell': '仅出售 (自动出售背包企鹅)',
        'sec_stigma': '雌黄 (Stigma) 上限设定',
        'lbl_stigma_limit': '雌黄上限:',
        'lbl_cost_per': '每只花费:',
        'cost_note': '雌黄 (每批50只 x {cost} = {batch_cost:,})',
        'calc_plan': '预计: 企鹅 {penguins:,}只 ({batches}批) | 金币: ~{gold_est:,}',
        'sec_tally': '实时企鹅获得与雌黄消耗',
        'lbl_small_name': '★ 初级 (1★)',
        'lbl_medium_name': '★★ 中级 (2★)',
        'lbl_large_name': '★★★ 上级 (3★)',
        'lbl_spent': '雌黄消耗: {spent:,} / {target}',
        'lbl_gold': '预估金币: ~{gold:,}',
        'lbl_ss_time': '截图时间 (秒):',
        'lbl_click_time': '点击时间 (秒):',
        'sec_sell': '背包企鹅自动出售筛选',
        'sell_1': '1★ 企鹅 (初级 - 绿) -> 出售换取金币',
        'sell_2': '2★ 企鹅 (中级 - 蓝) -> 出售换取金币',
        'sell_3': '3★ 企鹅 (上级 - 金/紫) -> 保留升级用 (不出售)',
        'preset_rec': '★ 推荐 (1★+2★)',
        'preset_1_only': '仅 1★',
        'preset_2_only': '仅 2★',
        'preset_all': '全部 (1★-3★)',
        'lbl_gold_rate': '单价: 1★ = 6K | 2★ = 18K | 3★ = 54K G',
        'lbl_sell_qty': '数量:',
        'lbl_sell_est': '预估出售金币: ~{gold:,}',
        'sell_opt_1': '1★ 初级 (绿)',
        'sell_opt_2': '2★ 中级 (蓝)',
        'sell_opt_3': '3★ 上级 (金/紫)',
        'btn_pin_on': '📌 置顶: 开',
        'btn_pin_off': '📌 置顶: 关',
        'btn_snap': '📐 吸附窗口',
        'chk_sound': '🔔 提示音',
        'btn_start': '开始挂机 (START)',
        'btn_stop': '停止 (ESC)',
        'status_ready': '状态: 就绪 (待命中)',
        'status_running': '状态: 培育进行中...',
        'status_navigating': '正在前往成长祭坛...',
        'status_buying_batch': '正在购买第 {b}/{batches} 批...',
        'status_selling': '正在出售背包企鹅...',
        'status_done': '培育完成！',
        'status_stopped': '已停止。',
        'status_error': '发生错误！',
        'log_init_ready': 'E7 圣域精灵之森培育中心已就绪。',
        'log_init_feature': '功能: 实时识别各阶企鹅获得数量与雌黄消耗累计。',
        'log_init_note': '注意: 请确保第七史诗游戏窗口未被其他程序遮挡。',
        'log_nav_altar': '\n--- 正在前往成长祭坛 (精灵之森) ---',
        'log_buy_ready': '[OK] 购买按钮已在屏幕上可见。',
        'log_found_altar': '[OK] 发现成长祭坛按钮，正在点击...',
        'log_found_soul': '[OK] 发现精灵之森，正在点击...',
        'log_searching_altar': '正在寻找成长祭坛按钮...',
        'log_opening_menu': '正在打开快捷菜单 (右上角)...',
        'log_click_sanctuary': '步骤 1: 点击圣域...',
        'log_click_soul': '步骤 2: 点击精灵之森...',
        'log_click_altar': '步骤 3: 点击成长祭坛...',
        'log_batch_header': '\n=== [第 {b}/{total} 批] 购买 50 只企鹅 ===',
        'log_click_buy': '1. 点击购买按钮 ({cost} 雌黄)...',
        'log_click_max': '2. 点击最大 (Max) 按钮...',
        'log_click_buyall': '3. 点击一同购买按钮 ({cost:,} 雌黄)...',
        'log_wait_result': '4. 等待孵化动画与结果画面...',
        'log_batch_result': '-> [第 {b} 批结果] +{s} 初级(1★), +{m} 中级(2★), +{l} 上级(3★)',
        'log_tally_subtotal': '-> [累计数量] 初级: {s} | 中级: {m} | 上级: {l}',
        'log_cost_subtotal': '-> [花费统计] 雌黄消耗: {spent:,} | 预估金币价值: ~{gold:,}',
        'log_tap_close': '5. 点击屏幕关闭结果窗口 (Tap to close)...',
        'log_batch_done': '[OK] 第 {b} 批处理完成。',
        'log_sell_start': '\n=== 开始出售背包企鹅 ===',
        'log_open_inv': '1. 打开背包 (Inventory)...',
        'log_tab_materials': '2. 选择强化素材标签...',
        'log_btn_arrange': '3. 进入整理菜单...',
        'log_sell_1': '4a. 选择 1★ 企鹅 [总计: {s}]...',
        'log_sell_2': '4b. 选择 2★ 企鹅 [总计: {m}]...',
        'log_sell_3': '4c. 选择 3★ 企鹅 [总计: {l}]...',
        'log_click_sell': '5. 点击出售按钮...',
        'log_confirm_sell': '6. 确认出售对话框...',
        'log_sell_done': '[成功] 企鹅出售完毕。',
        'log_flow_done': '\n==========================================\n   全流程已顺利完成！\n   总计消耗雌黄 : {spent:,}\n   初级企鹅 (1★) : {s}\n   中级企鹅 (2★) : {m}\n   上级企鹅 (3★) : {l}\n==========================================',
        'log_stopped_esc': '\n[STOP] 用户手动中止 (ESC)。',
        'log_err_target': '[错误] 找不到目标窗口 "{w}"。',
        'log_win_active': '[OK] 目标窗口 "{w}" 已置顶前景 (0, 0, 906x539)。',
        'log_err_general': '[错误] 执行过程中发生异常: {e}',
    },
    'id': {
        'lang_name': 'Bahasa Indonesia',
        'title': 'SANCTUARY • FOREST OF SOULS',
        'subtitle': 'Auto Nurture & Live Yield Counter',
        'sec_mode': 'MODE OPERASI',
        'mode_full': 'Full Loop (Beli + Kalkulasi + Jual Otomatis)',
        'mode_buy': 'Beli Saja (Buy -> Max -> Buy All -> Kalkulasi)',
        'mode_sell': 'Jual Saja (Auto Sell Penguin yang Ada di Tas)',
        'sec_stigma': 'BATAS & RENCANA STIGMA',
        'lbl_stigma_limit': 'Batas Stigma:',
        'lbl_cost_per': 'Biaya / Penguin:',
        'cost_note': 'Stigma (1 Batch = 50 x {cost} = {batch_cost:,})',
        'calc_plan': 'Rencana: {penguins:,} Penguin ({batches} Batch) | Gold: ~{gold_est:,}',
        'sec_tally': 'LIVE PEROLEHAN PENGUIN & BIAYA',
        'lbl_small_name': '★ 1★ Small',
        'lbl_medium_name': '★★ 2★ Medium',
        'lbl_large_name': '★★★ 3★ Large',
        'lbl_spent': 'Stigma Keluar: {spent:,} / {target}',
        'lbl_gold': 'Gold (Est.): ~{gold:,}',
        'lbl_ss_time': 'Screenshot Time (s):',
        'lbl_click_time': 'Click Time (s):',
        'sec_sell': 'FILTER JUAL OTOMATIS DI TAS',
        'sell_1': 'Penguin 1★ (Newbie - Hijau) -> Jual untuk Gold',
        'sell_2': 'Penguin 2★ (Experienced - Biru) -> Jual untuk Gold',
        'sell_3': 'Penguin 3★ (Epic - Ungu) -> Simpan untuk EXP (Jangan Jual)',
        'preset_rec': '★ Rekomendasi (1★+2★)',
        'preset_1_only': '1★ Saja',
        'preset_2_only': '2★ Saja',
        'preset_all': 'Semua (1★-3★)',
        'lbl_gold_rate': 'Nilai: 1★ = 6K | 2★ = 18K | 3★ = 54K G',
        'lbl_sell_qty': 'Jumlah:',
        'lbl_sell_est': 'Total Estimasi Gold Jual: ~{gold:,}',
        'sell_opt_1': '1★ Small (Hijau)',
        'sell_opt_2': '2★ Medium (Biru)',
        'sell_opt_3': '3★ Large (Emas)',
        'btn_pin_on': '📌 Top: ON',
        'btn_pin_off': '📌 Top: OFF',
        'btn_snap': '📐 Tempel ke E7',
        'chk_sound': '🔔 Bunyi Selesai',
        'btn_start': 'MULAI FARMING',
        'btn_stop': 'STOP (ESC)',
        'status_ready': 'Status: Siap (Standby)',
        'status_running': 'Status: Bot sedang berjalan...',
        'status_navigating': 'Navigasi ke Growth Altar...',
        'status_buying_batch': 'Membeli Batch {b}/{batches}...',
        'status_selling': 'Menjual penguin di inventori...',
        'status_done': 'Selesai!',
        'status_stopped': 'Dihentikan.',
        'status_error': 'Error!',
        'log_init_ready': 'E7 Sanctuary & Forest of Souls Cultivator siap.',
        'log_init_feature': 'Fitur: Otomatis membaca angka hasil perolehan per jenis & total Stigma.',
        'log_init_note': 'Catatan: Pastikan game Epic Seven tidak tertutup jendela lain.',
        'log_nav_altar': '\n--- Menavigasi ke Growth Altar (Forest of Souls) ---',
        'log_buy_ready': '[OK] Tombol Buy sudah aktif di layar.',
        'log_found_altar': '[OK] Menemukan tombol "Growth Altar". Mengklik...',
        'log_found_soul': '[OK] Menemukan "Forest of Souls" di Sanctuary. Mengklik...',
        'log_searching_altar': 'Mencari tombol "Growth Altar"...',
        'log_opening_menu': 'Membuka Quick Menu (kanan atas)...',
        'log_click_sanctuary': 'Langkah 1: Mengklik Sanctuary...',
        'log_click_soul': 'Langkah 2: Mengklik Forest of Souls...',
        'log_click_altar': 'Langkah 3: Mengklik Growth Altar...',
        'log_batch_header': '\n=== [Batch {b}/{total}] Membeli 50 Penguin ===',
        'log_click_buy': '1. Mengklik tombol "Buy" ({cost} Stigma)...',
        'log_click_max': '2. Mengklik tombol "Max"...',
        'log_click_buyall': '3. Mengklik tombol "Buy All" ({cost:,} Stigma)...',
        'log_wait_result': '4. Menunggu animasi penetasan & layar hasil (Result)...',
        'log_batch_result': '-> [HASIL BATCH {b}] +{s} Small (1★), +{m} Medium (2★), +{l} Large (3★)',
        'log_tally_subtotal': '-> [TOTAL SEMENTARA] Small: {s} | Medium: {m} | Large: {l}',
        'log_cost_subtotal': '-> [BIAYA] Stigma Terpakai: {spent:,} | Estimasi Nilai Gold: ~{gold:,}',
        'log_tap_close': '5. Mengetuk "Tap to close" untuk menutup...',
        'log_batch_done': '[OK] Batch {b} selesai.',
        'log_sell_start': '\n=== Memulai Penjualan Penguin di Inventori ===',
        'log_open_inv': '1. Membuka Inventory...',
        'log_tab_materials': '2. Memilih tab Bahan Penguatan (Materials)...',
        'log_btn_arrange': '3. Membuka menu Arrange...',
        'log_sell_1': '4a. Memilih Penguin 1★ (Hijau) [Total: {s}]...',
        'log_sell_2': '4b. Memilih Penguin 2★ (Biru) [Total: {m}]...',
        'log_sell_3': '4c. Memilih Penguin 3★ (Ungu) [Total: {l}]...',
        'log_click_sell': '5. Mengklik tombol Sell...',
        'log_confirm_sell': '6. Konfirmasi dialog penjualan...',
        'log_sell_done': '[SUKSES] Penjualan penguin selesai!',
        'log_flow_done': '\n==========================================\n   WORKFLOW SELESAI DENGAN SUKSES!\n   Total Stigma Dikeluarkan : {spent:,}\n   Small Penguin (1★)      : {s}\n   Medium Penguin (2★)     : {m}\n   Large Penguin (3★)      : {l}\n==========================================',
        'log_stopped_esc': '\n[STOP] Bot dihentikan oleh pengguna (ESC).',
        'log_err_target': '[ERROR] Window "{w}" tidak ditemukan.',
        'log_win_active': '[OK] Target window "{w}" aktif di depan (0, 0, 906x539).',
        'log_err_general': '[ERROR] Terjadi kesalahan: {e}',
    }
}

LANG_NAME_TO_CODE = {
    'English': 'en',
    '한국어': 'ko',
    '日本語': 'ja',
    '繁體中文': 'zh_TW',
    '简体中文': 'zh_CN',
    'Bahasa Indonesia': 'id'
}
LANG_CODE_TO_NAME = {v: k for k, v in LANG_NAME_TO_CODE.items()}

MODE_OPTIONS = {
    'en': [
        ('full_auto', 'Full Loop (Buy + Sell)'),
        ('buy_only', 'Buy Only (No Sell)'),
        ('sell_only', 'Sell Only (No Buy)')
    ],
    'id': [
        ('full_auto', 'Full Loop (Beli + Jual)'),
        ('buy_only', 'Beli Saja (Tanpa Jual)'),
        ('sell_only', 'Jual Saja (Tanpa Beli)')
    ],
    'ko': [
        ('full_auto', '풀 루프 (구매 + 판매)'),
        ('buy_only', '구매 전용 (판매 안 함)'),
        ('sell_only', '판매 전용 (구매 안 함)')
    ],
    'ja': [
        ('full_auto', 'フルループ (購入 + 売却)'),
        ('buy_only', '購入のみ (売却なし)'),
        ('sell_only', '売却のみ (購入なし)')
    ],
    'zh_TW': [
        ('full_auto', '完整循環 (購買 + 出售)'),
        ('buy_only', '僅購買 (不出售)'),
        ('sell_only', '僅出售 (不購買)')
    ],
    'zh_CN': [
        ('full_auto', '完整循环 (购买 + 出售)'),
        ('buy_only', '仅购买 (不出售)'),
        ('sell_only', '仅出售 (不购买)')
    ]
}

pyautogui.PAUSE = 0.02
user32 = ctypes.windll.user32

class PenguinConfig:
    def __init__(self):
        self.TARGET_WINDOW = 'Epic Seven'
        self.DEFAULT_STIGMA_PER_PENGUIN = 102  # Sesuai screenshot user: 102 Stigma / penguin
        self.MAX_BATCH_SIZE = 50              # 50 penguin x 102 = 5,100 Stigma per batch
        self.ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets_penguin')
        self.DIGITS_DIR = os.path.join(self.ASSETS_DIR, 'digits')
        
        # Urutan template alur persis user
        self.TEMPLATE_KEYS = [
            'quick_menu', 'sanctuary', 'soul', 'growaltar', 'buy', 'max', 'buyall', 'result', 'tap_to_close',
            'sell_bag', 'sell_bag2', 'sell_growingredient', 'sell_btn', 'sell_select', 'sell_confirm',
            'sell_penguin_1', 'sell_penguin_2', 'sell_penguin_3', 'sell_gold_preview'
        ]
        
        # Koordinat cadangan jika template matching meleset
        self.COORDS = {
            'quick_menu': (0.95, 0.08),
            'sanctuary_fallback': (0.65, 0.45),
            'soul_fallback': (0.90, 0.28),        # Forest of Souls ada di sidebar kanan atas (Y~28%)
            'growaltar_fallback': (0.35, 0.72),
            'buy_fallback': (0.85, 0.35),
            'max_fallback': (0.68, 0.58),
            'buyall_fallback': (0.75, 0.78),
            'tap_to_close': (0.50, 0.72),
            'tap_to_skip': (0.50, 0.72),
            'modal_confirm': (0.58, 0.65),
            
            # Inventory & Arrange
            'icon_inventory': (0.826, 0.098),     # Bag 1 (Header Bag Icon)
            'icon_bag2': (0.920, 0.085),          # Bag 2 (Secondary Backpack Icon)
            'tab_materials': (0.045, 0.48),       # Tab Bahan/Materials di kiri
            'subtab_growth': (0.18, 0.15),        # Sub-tab Bahan Pertumbuhan (Growth Ingredient)
            'btn_arrange': (0.92, 0.90),          # Tombol Arrange / Susun di kanan bawah
            'slot_penguin_1': (0.22, 0.35),       # Posisi Slot Penguin 1★
            'slot_penguin_2': (0.35, 0.35),       # Posisi Slot Penguin 2★
            'slot_penguin_3': (0.48, 0.35),       # Posisi Slot Penguin 3★
            'modal_min': (0.38, 0.58),            # Tombol MIN di modal jumlah
            'modal_minus1': (0.44, 0.58),         # Tombol -1 di modal jumlah
            'modal_qty_box': (0.50, 0.55),        # Kotak input angka di modal jumlah
            'modal_plus1': (0.56, 0.58),          # Tombol +1 di modal jumlah
            'arrange_max': (0.68, 0.58),          # Tombol MAX di modal jumlah
            'arrange_confirm_qty': (0.58, 0.70),  # Tombol Select (hijau)
            'btn_sell': (0.90, 0.90),             # Tombol Sell di kanan bawah
            'btn_confirm_sell': (0.58, 0.65),     # Tombol Confirm di popup preview gold
        }

class PenguinFarmerBot:
    def __init__(self, logger_func=None, update_status_func=None, update_tally_func=None, on_complete_callback=None, lang='en', snap_callback=None):
        self.config = PenguinConfig()
        self.logger = logger_func if logger_func else print
        self.update_status = update_status_func if update_status_func else (lambda s: None)
        self.update_tally = update_tally_func if update_tally_func else (lambda s, m, l, st, g: None)
        self.on_complete_callback = on_complete_callback
        self.snap_callback = snap_callback
        self.lang = lang
        self.is_running = False
        self.window = None
        self.mouse_sleep = 0.08
        self.screenshot_sleep = 0.15
        self.loaded_templates = {}
        self.digit_templates = {}
        
        # Stats
        self.total_small = 0
        self.total_medium = 0
        self.total_large = 0
        self.total_stigma_spent = 0
        
        self.load_templates()
        self.load_digit_templates()

    def tr(self, key, **kwargs):
        lang_dict = I18N.get(self.lang, I18N['en'])
        template = lang_dict.get(key, I18N['en'].get(key, key))
        try:
            return template.format(**kwargs) if kwargs else template
        except Exception:
            return template
        
    def load_templates(self):
        for k in self.config.TEMPLATE_KEYS:
            for ext in ['.jpg', '.png', '.JPG', '.PNG']:
                p = os.path.join(self.config.ASSETS_DIR, k + ext)
                if os.path.exists(p):
                    img = cv2.imread(p)
                    if img is not None:
                        self.loaded_templates[k] = img
                        break

    def load_digit_templates(self):
        if not os.path.exists(self.config.DIGITS_DIR):
            return
        for d in range(10):
            p = os.path.join(self.config.DIGITS_DIR, f"{d}.png")
            if os.path.exists(p):
                tmpl = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
                if tmpl is not None:
                    self.digit_templates[d] = tmpl

    def reset_stats(self):
        self.total_small = 0
        self.total_medium = 0
        self.total_large = 0
        self.total_stigma_spent = 0
        self.update_tally(0, 0, 0, 0, 0)

    def find_and_prep_window(self):
        titles = gw.getWindowsWithTitle(self.config.TARGET_WINDOW)
        w = next((x for x in titles if x.title == self.config.TARGET_WINDOW), None)
        if not w:
            self.logger(self.tr('log_err_target', w=self.config.TARGET_WINDOW))
            return False
            
        self.window = w
        try:
            if self.window.isMaximized or self.window.isMinimized:
                self.window.restore()
            self.window.moveTo(0, 0)
            self.window.resizeTo(906, 539)
            time.sleep(0.1)
            try:
                self.window.activate()
            except Exception:
                pass
        except Exception as e:
            self.logger(f"[WARN] Window placement: {e}")
            
        self.logger(self.tr('log_win_active', w=self.config.TARGET_WINDOW))
        if self.snap_callback:
            try:
                self.snap_callback()
            except Exception:
                pass
        return True

    def bring_window_to_top(self):
        if not self.window:
            return
        try:
            self.window.activate()
        except Exception:
            pass

    def capture_game_screen(self):
        if not self.window:
            return None
        region = (self.window.left, self.window.top, self.window.left + self.window.width, self.window.top + self.window.height)
        im = ImageGrab.grab(bbox=region, all_screens=True)
        return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

    def find_template_on_screen(self, template_key, threshold=0.68, scales=None, roi_rel=None):
        tmpl = self.loaded_templates.get(template_key)
        if tmpl is None:
            return None, 0.0
            
        screen = self.capture_game_screen()
        if screen is None:
            return None, 0.0
            
        sh, sw = screen.shape[:2]
        if roi_rel:
            rx1, ry1, rx2, ry2 = roi_rel
            x1, y1 = max(0, int(rx1 * sw)), max(0, int(ry1 * sh))
            x2, y2 = min(sw, int(rx2 * sw)), min(sh, int(ry2 * sh))
            screen_roi = screen[y1:y2, x1:x2]
            ox, oy = x1, y1
        else:
            screen_roi = screen
            ox, oy = 0, 0
            
        screen_gray = cv2.cvtColor(screen_roi, cv2.COLOR_BGR2GRAY)
        temp_gray = cv2.cvtColor(tmpl, cv2.COLOR_BGR2GRAY)
        th, tw = temp_gray.shape[:2]
        
        best_val = -1
        best_loc = None
        best_scale = 1.0
        
        scale_list = scales if scales else [0.85, 0.90, 0.95, 1.0, 1.05, 1.10, 1.15]
        for s in scale_list:
            rw = int(tw * s)
            rh = int(th * s)
            if rw > screen_gray.shape[1] or rh > screen_gray.shape[0]:
                continue
            resized = cv2.resize(temp_gray, (rw, rh))
            res = cv2.matchTemplate(screen_gray, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > best_val:
                best_val = max_val
                best_loc = max_loc
                best_scale = s
                
        if best_val >= threshold and best_loc is not None:
            cw = int(tw * best_scale)
            ch = int(th * best_scale)
            abs_x = self.window.left + ox + best_loc[0] + cw // 2
            abs_y = self.window.top + oy + best_loc[1] + ch // 2
            return (abs_x, abs_y), best_val
            
        return None, best_val

    def wait_and_click_template(self, template_key, timeout=3.5, threshold=0.68, fallback_coord=None, delay=0.4, roi_rel=None):
        if not self.is_running:
            return False
            
        start_time = time.time()
        score = 0.0
        while time.time() - start_time < timeout:
            if not self.is_running:
                return False
            pos, score = self.find_template_on_screen(template_key, threshold=threshold, roi_rel=roi_rel)
            if pos:
                self.logger(f"-> Found [{template_key}] (score {score:.2f}) at {pos}. Clicking...")
                pyautogui.moveTo(pos[0], pos[1])
                time.sleep(self.mouse_sleep)
                pyautogui.click()
                time.sleep(delay)
                return True
            time.sleep(self.screenshot_sleep)
            
        if fallback_coord and self.window:
            self.logger(f"-> [FALLBACK] Template [{template_key}] not matched (score {score:.2f}), using coordinate fallback...")
            rx, ry = self.config.COORDS.get(fallback_coord, (0.5, 0.5))
            ax = int(self.window.left + self.window.width * rx)
            ay = int(self.window.top + self.window.height * ry)
            pyautogui.moveTo(ax, ay)
            time.sleep(self.mouse_sleep)
            pyautogui.click()
            time.sleep(delay)
            return True
            
        self.logger(f"-> [TIMEOUT] [{template_key}] not found (highest score: {score:.2f}).")
        return False

    def click_rel(self, coord_key, clicks=1, delay=0.3):
        if not self.is_running or not self.window:
            return False
        rx, ry = self.config.COORDS.get(coord_key, (0.5, 0.5))
        ax = int(self.window.left + self.window.width * rx)
        ay = int(self.window.top + self.window.height * ry)
        pyautogui.moveTo(ax, ay)
        time.sleep(self.mouse_sleep)
        pyautogui.click(clicks=clicks, interval=self.mouse_sleep)
        time.sleep(delay)
        return True

    def match_digits_in_strip(self, strip_gray):
        """Membaca urutan angka pada strip horizontal dengan multi-template matching"""
        if strip_gray is None or strip_gray.size == 0 or not self.digit_templates:
            return None
        matches = []
        for d, tmpl in self.digit_templates.items():
            if tmpl is None or strip_gray.shape[0] < tmpl.shape[0] or strip_gray.shape[1] < tmpl.shape[1]:
                continue
            res_m = cv2.matchTemplate(strip_gray, tmpl, cv2.TM_CCOEFF_NORMED)
            locs = np.where(res_m >= 0.70)
            for pt in zip(*locs[::-1]):
                matches.append((pt[0], d, float(res_m[pt[1], pt[0]])))
                
        matches.sort(key=lambda m: m[2], reverse=True)
        kept = []
        for x, d, sc in matches:
            if not any(abs(x - kx) < 5 for kx, kd, ksc in kept):
                kept.append((x, d, sc))
                
        kept.sort(key=lambda m: m[0])
        num_str = ''.join(str(d) for x, d, sc in kept)
        return int(num_str) if num_str else None

    def read_result_penguins(self, screen_bgr):
        """Membaca jumlah Small (1★), Medium (2★), Large (3★) dari layar result.jpg"""
        if screen_bgr is None:
            return 32, 16, 2
            
        pos, sc = self.find_template_on_screen('result', threshold=0.55)
        if pos:
            mx = int(pos[0] - 256)
            my = int(pos[1] - 156)
        else:
            h, w = screen_bgr.shape[:2]
            mx = int((w - 512) / 2)
            my = int((h - 313) / 2)
            
        gray_screen = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
        
        h_s, w_s = gray_screen.shape[:2]
        strip_s = gray_screen[max(0, my+176):min(h_s, my+196), max(0, mx+165):min(w_s, mx+195)]
        strip_m = gray_screen[max(0, my+176):min(h_s, my+196), max(0, mx+238):min(w_s, mx+268)]
        strip_l = gray_screen[max(0, my+176):min(h_s, my+196), max(0, mx+312):min(w_s, mx+342)]
        
        s_count = self.match_digits_in_strip(strip_s)
        m_count = self.match_digits_in_strip(strip_m)
        l_count = self.match_digits_in_strip(strip_l)
        
        # Mathematical reconciliation for 50 penguins per batch
        if s_count is not None and m_count is not None and l_count is None:
            l_count = max(0, 50 - (s_count + m_count))
        elif s_count is not None and l_count is not None and m_count is None:
            m_count = max(0, 50 - (s_count + l_count))
        elif m_count is not None and l_count is not None and s_count is None:
            s_count = max(0, 50 - (m_count + l_count))
        elif s_count is None and m_count is None and l_count is None:
            s_count, m_count, l_count = 32, 16, 2
            
        return s_count, m_count, l_count

    def navigate_to_growth_altar(self):
        self.logger(self.tr('log_nav_altar'))
        
        # 1. Check if Buy button is already visible in Growth Altar
        pos, sc = self.find_template_on_screen('buy', threshold=0.68)
        if pos:
            self.logger(self.tr('log_buy_ready'))
            return True

        # 2. Check if Growth Altar button is visible
        pos, sc = self.find_template_on_screen('growaltar', threshold=0.68)
        if pos:
            self.logger(self.tr('log_found_altar'))
            self.wait_and_click_template('growaltar', delay=1.2)
            return True

        # 3. Check if Forest of Souls is visible in Sanctuary (right sidebar, top item)
        pos, sc = self.find_template_on_screen('soul', threshold=0.75)
        if pos:
            self.logger(self.tr('log_found_soul'))
            self.wait_and_click_template('soul', timeout=3.0, threshold=0.75, fallback_coord='soul_fallback', delay=1.5)
            self.logger(self.tr('log_searching_altar'))
            self.wait_and_click_template('growaltar', timeout=4.0, fallback_coord='growaltar_fallback', delay=1.2)
            return True

        # 4. If in Lobby, open quick menu then Sanctuary
        pos, sc = self.find_template_on_screen('sanctuary', threshold=0.68)
        if not pos:
            self.logger(self.tr('log_opening_menu'))
            self.wait_and_click_template('quick_menu', fallback_coord='quick_menu', delay=0.8)
            time.sleep(0.5)

        self.logger(self.tr('log_click_sanctuary'))
        self.wait_and_click_template('sanctuary', fallback_coord='sanctuary_fallback', delay=1.5)

        self.logger(self.tr('log_click_soul'))
        self.wait_and_click_template('soul', timeout=3.5, threshold=0.75, fallback_coord='soul_fallback', delay=1.5)

        self.logger(self.tr('log_click_altar'))
        self.wait_and_click_template('growaltar', fallback_coord='growaltar_fallback', delay=1.2)

        return True

    def run_nurture_batch(self, batch_index, total_batches, cost_per_batch=5100):
        if not self.is_running:
            return False
            
        self.logger(self.tr('log_batch_header', b=batch_index, total=total_batches))
        
        # 1. Click buy button
        self.logger(self.tr('log_click_buy', cost=self.config.DEFAULT_STIGMA_PER_PENGUIN))
        if not self.wait_and_click_template('buy', timeout=3.5, fallback_coord='buy_fallback', delay=0.6):
            self.wait_and_click_template('growaltar', timeout=2.0, delay=0.8)
            if not self.wait_and_click_template('buy', timeout=3.0, fallback_coord='buy_fallback', delay=0.6):
                return False
            
        # 2. Click Max button
        self.logger(self.tr('log_click_max'))
        if not self.wait_and_click_template('max', timeout=2.0, fallback_coord=None, delay=0.5):
            self.logger("[INFO] Modal Max tidak muncul (kemungkinan tas penuh atau Stigma habis).")
            return False
            
        # 3. Click Buy All button
        self.logger(self.tr('log_click_buyall', cost=cost_per_batch))
        if not self.wait_and_click_template('buyall', timeout=2.5, fallback_coord='buyall_fallback', delay=0.8):
            return False
            
        # 4. Wait for hatch animation & result screen
        self.logger(self.tr('log_wait_result'))
        t_start = time.time()
        while time.time() - t_start < 6.0 and self.is_running:
            pos_ttc, _ = self.find_template_on_screen('tap_to_close', threshold=0.70)
            pos_res, _ = self.find_template_on_screen('result', threshold=0.55)
            if pos_ttc or pos_res:
                break
            time.sleep(0.3)
            
        time.sleep(0.4)
        
        screen_result = self.capture_game_screen()
        s_cnt, m_cnt, l_cnt = self.read_result_penguins(screen_result)
        
        actual_bought = s_cnt + m_cnt + l_cnt
        batch_cost_actual = (actual_bought * self.config.DEFAULT_STIGMA_PER_PENGUIN) if actual_bought > 0 else cost_per_batch
        
        self.total_small += s_cnt
        self.total_medium += m_cnt
        self.total_large += l_cnt
        self.total_stigma_spent += batch_cost_actual
        est_gold = (self.total_small * 6000) + (self.total_medium * 18000) + (self.total_large * 54000)
        
        self.logger(self.tr('log_batch_result', b=batch_index, s=s_cnt, m=m_cnt, l=l_cnt))
        self.logger(self.tr('log_tally_subtotal', s=self.total_small, m=self.total_medium, l=self.total_large))
        self.logger(self.tr('log_cost_subtotal', spent=self.total_stigma_spent, gold=est_gold))
        
        self.update_tally(self.total_small, self.total_medium, self.total_large, self.total_stigma_spent, est_gold)
        
        # 5. Tap to close dialog
        self.logger(self.tr('log_tap_close'))
        if not self.wait_and_click_template('tap_to_close', timeout=2.5, fallback_coord='tap_to_close', delay=0.8):
            self.click_rel('tap_to_close', clicks=1, delay=0.8)
        
        self.logger(self.tr('log_batch_done', b=batch_index))
        time.sleep(0.6)
        return True

    def _select_modal_quantity(self, qty):
        val_str = str(qty).strip().upper()
        if val_str in ('MAX', 'ALL', '', '0'):
            # Click Max button
            if not self.wait_and_click_template('max', timeout=1.5, fallback_coord='arrange_max', delay=0.4):
                self.click_rel('arrange_max', delay=0.4)
        elif val_str == 'MIN':
            self.click_rel('modal_min', delay=0.4)
        else:
            try:
                num = int(val_str)
                # Click modal number input box and enter digits directly
                self.click_rel('modal_qty_box', delay=0.3)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                pyautogui.write(str(num))
                time.sleep(0.2)
            except Exception:
                self.click_rel('arrange_max', delay=0.3)
                
        # Confirm with green Select button (select.JPG)
        if not self.wait_and_click_template('sell_select', timeout=2.0, fallback_coord='arrange_confirm_qty', delay=0.5):
            self.click_rel('arrange_confirm_qty', delay=0.5)

    def run_sell_penguins(self, sell_1, qty_1, sell_2, qty_2, sell_3, qty_3):
        if not self.is_running:
            return False
            
        self.logger(self.tr('log_sell_start'))
        
        # 1. Buka Bag 1 (Header Inventory Icon)
        self.logger(self.tr('log_open_inv'))
        header_roi = (0.74, 0.0, 0.98, 0.16)
        if not self.wait_and_click_template('sell_bag', timeout=1.2, threshold=0.70, roi_rel=header_roi, delay=0.8):
            self.click_rel('icon_inventory', delay=0.8)
        if not self.is_running: return False
        
        # 2. Buka Bag 2 (Secondary Backpack Icon)
        self.logger("2. Membuka Bag 2 (Inventory Backpack)...")
        if not self.wait_and_click_template('sell_bag2', timeout=1.5, threshold=0.68, roi_rel=header_roi, delay=0.8):
            self.click_rel('icon_bag2', delay=0.8)
        if not self.is_running: return False
        
        # 3. Growth Ingredient (Bahan Pertumbuhan) Tab
        self.logger(self.tr('log_tab_materials'))
        if not self.wait_and_click_template('sell_growingredient', timeout=2.0, threshold=0.68, delay=0.8):
            self.click_rel('tab_materials', delay=0.5)
            self.click_rel('subtab_growth', delay=0.8)
        if not self.is_running: return False
        
        # 4. Masuk Mode Arrange / Susun & Jual
        self.logger(self.tr('log_btn_arrange'))
        if not self.wait_and_click_template('sell_btn', timeout=2.0, fallback_coord='btn_arrange', delay=0.8):
            self.click_rel('btn_arrange', delay=0.8)
        if not self.is_running: return False
        
        # 5. Pilih Penguin & Atur Kuantitas (MIN, -1, +1, MAX, Select)
        if sell_1:
            self.logger(self.tr('log_sell_1', s=self.total_small, qty=qty_1))
            if not self.wait_and_click_template('sell_penguin_1', timeout=1.2, fallback_coord='slot_penguin_1', delay=0.5):
                self.click_rel('slot_penguin_1', delay=0.5)
            self._select_modal_quantity(qty_1)
            if not self.is_running: return False
            
        if sell_2:
            self.logger(self.tr('log_sell_2', m=self.total_medium, qty=qty_2))
            if not self.wait_and_click_template('sell_penguin_2', timeout=1.2, fallback_coord='slot_penguin_2', delay=0.5):
                self.click_rel('slot_penguin_2', delay=0.5)
            self._select_modal_quantity(qty_2)
            if not self.is_running: return False
            
        if sell_3:
            self.logger(self.tr('log_sell_3', l=self.total_large, qty=qty_3))
            if not self.wait_and_click_template('sell_penguin_3', timeout=1.2, fallback_coord='slot_penguin_3', delay=0.5):
                self.click_rel('slot_penguin_3', delay=0.5)
            self._select_modal_quantity(qty_3)
            if not self.is_running: return False
            
        # 6. Klik tombol Sell (Sell button.JPG)
        self.logger(self.tr('log_click_sell'))
        if not self.wait_and_click_template('sell_btn', timeout=2.0, fallback_coord='btn_sell', delay=0.8):
            self.click_rel('btn_sell', delay=0.8)
        if not self.is_running: return False
        
        # 7. Lihat preview perolehan gold lalu klik Confirm (confirm.JPG)
        self.logger(self.tr('log_confirm_sell'))
        self.find_template_on_screen('sell_gold_preview', threshold=0.65)
        if not self.wait_and_click_template('sell_confirm', timeout=2.5, fallback_coord='btn_confirm_sell', delay=0.8):
            self.click_rel('btn_confirm_sell', delay=0.8)
        if not self.is_running: return False
        
        # 8. Tap layar untuk menutup dialog hasil penjualan
        self.click_rel('tap_to_skip', clicks=2, delay=0.5)
        self.logger(self.tr('log_sell_done'))
        return True

    def execute_workflow(self, mode, target_stigma, cost_per_penguin, sell_1, qty_1, sell_2, qty_2, sell_3, qty_3):
        if not self.find_and_prep_window():
            self.is_running = False
            return
            
        self.reset_stats()
        cost_per_batch = cost_per_penguin * self.config.MAX_BATCH_SIZE
        is_max = (target_stigma == -1)
        if is_max:
            batches = 9999
            plan_budget_str = "MAX (Habiskan Semua Stigma / Unlimited)"
            total_penguins_plan = "~MAX"
        else:
            batches = max(1, target_stigma // cost_per_batch)
            plan_budget_str = f"{target_stigma:,} ({batches} Batches x 50)"
            total_penguins_plan = f"~{batches * self.config.MAX_BATCH_SIZE:,}"
        
        self.logger("==================================================")
        self.logger(f"  PENGUIN FARMER ACTIVE | Mode: {mode.upper()}")
        self.logger(f"  Stigma Budget : {plan_budget_str}")
        self.logger(f"  Plan to Buy   : {total_penguins_plan} penguins")
        self.logger(f"  Auto-Sell Plan: 1★={sell_1} ({qty_1}), 2★={sell_2} ({qty_2}), 3★={sell_3} ({qty_3})")
        self.logger(f"  Speed Timing  : Click={self.mouse_sleep}s | Screenshot={self.screenshot_sleep}s")
        self.logger("  >> Press ESC anytime to STOP <<")
        self.logger("==================================================")
        
        try:
            if mode == 'sell_only':
                self.update_status(self.tr('status_selling'))
                self.run_sell_penguins(sell_1, qty_1, sell_2, qty_2, sell_3, qty_3)
            elif mode == 'buy_only':
                self.update_status(self.tr('status_navigating'))
                if not self.navigate_to_growth_altar():
                    return
                b = 0
                while self.is_running:
                    b += 1
                    if not is_max and b > batches:
                        break
                    batch_total_str = "MAX" if is_max else str(batches)
                    self.update_status(f"Buying Batch {b}/{batch_total_str}...")
                    if not self.run_nurture_batch(b, batch_total_str, cost_per_batch):
                        if is_max:
                            self.logger(f"[INFO] Pembelian batch selesai ({b-1} batch). Stigma habis atau tas penuh.")
                        else:
                            self.logger("[WARN] Pembelian batch selesai / terhenti.")
                        break
            else:  # mode == 'full_auto'
                cycle = 0
                stigma_exhausted = False
                total_batches_done = 0
                
                while self.is_running and not stigma_exhausted:
                    if not is_max and total_batches_done >= batches:
                        self.logger(f"\n[OK] Target kuota terpenuhi: {total_batches_done}/{batches} batch.")
                        break
                        
                    cycle += 1
                    self.logger(f"\n==========================================")
                    if is_max:
                        self.logger(f"  [MAX MODE] SIKLUS #{cycle} (Farming Terus Sampai Stigma Habis)")
                    else:
                        self.logger(f"  SIKLUS #{cycle} (Progress: {total_batches_done}/{batches} Batch)")
                    self.logger(f"==========================================")
                    
                    # 1. Navigasi ke Growth Altar
                    self.update_status(f"Siklus #{cycle}: Ke Growth Altar...")
                    if not self.navigate_to_growth_altar():
                        self.logger("[WARN] Gagal membuka Growth Altar. Menunggu 1 detik dan mencoba lagi...")
                        time.sleep(1.0)
                        if not self.navigate_to_growth_altar():
                            self.logger("[ERROR] Tidak dapat membuka Growth Altar. Workflow dihentikan.")
                            break
                            
                    # 2. Beli batch sampai tas penuh, target batch tercapai, atau stigma habis
                    batches_in_cycle = 0
                    while self.is_running:
                        if not is_max and total_batches_done >= batches:
                            break
                        batch_num = total_batches_done + 1
                        batch_total_str = "MAX" if is_max else str(batches)
                        self.update_status(f"Siklus #{cycle} | Membeli Batch {batch_num}/{batch_total_str}...")
                        success = self.run_nurture_batch(batch_num, batch_total_str, cost_per_batch)
                        if success:
                            total_batches_done += 1
                            batches_in_cycle += 1
                        else:
                            self.logger(f"[INFO] Pembelian batch terhenti pada #{batch_num} (Tas penuh atau Stigma habis).")
                            self.click_rel('tap_to_skip', clicks=2, delay=0.5)
                            break
                            
                    if not self.is_running:
                        break
                        
                    # 3. Jual penguin di inventory untuk mengosongkan tas & konversi ke Gold
                    self.update_status(f"Siklus #{cycle}: Mengosongkan tas (Jual Penguin)...")
                    self.run_sell_penguins(sell_1, qty_1, sell_2, qty_2, sell_3, qty_3)
                    
                    if not self.is_running:
                        break
                        
                    # 4. Cek kondisi berhenti
                    if not is_max and total_batches_done >= batches:
                        self.logger(f"\n[OK] Target Stigma {target_stigma:,} ({batches} batch) selesai terpenuhi!")
                        break
                        
                    # Jika dalam siklus ini 0 batch berhasil dibeli
                    if batches_in_cycle == 0:
                        if cycle == 1:
                            self.logger("[INFO] Tas awal mungkin sudah penuh. Tas telah dikosongkan, mencoba siklus berikutnya...")
                        else:
                            self.logger("\n==========================================")
                            self.logger("  [SELESAI] Tas sudah kosong & Stigma telah HABIS TOTAL!")
                            self.logger("==========================================")
                            stigma_exhausted = True
                            break
                    else:
                        if is_max:
                            self.logger(f"[Siklus #{cycle} Selesai] Berhasil {batches_in_cycle} batch ({batches_in_cycle * 50} penguin). Melanjutkan siklus berikutnya sampai Stigma habis...")
                        else:
                            self.logger(f"[Siklus #{cycle} Selesai] {total_batches_done}/{batches} batch selesai. Melanjutkan sisa batch...")
                
            if self.is_running:
                self.logger(self.tr('log_flow_done', spent=self.total_stigma_spent, s=self.total_small, m=self.total_medium, l=self.total_large))
                self.update_status(self.tr('status_done'))
                if self.on_complete_callback:
                    self.on_complete_callback()
            else:
                self.logger(self.tr('log_stopped_esc'))
                self.update_status(self.tr('status_stopped'))
                self.reset_stats()
                
        except Exception as e:
            self.logger(self.tr('log_err_general', e=e))
            self.update_status(self.tr('status_error'))
        finally:
            self.is_running = False

    def start_thread(self, mode, target_stigma, cost_per_penguin, sell_1, qty_1, sell_2, qty_2, sell_3, qty_3):
        if self.is_running:
            return
        self.is_running = True
        
        def key_watcher():
            while self.is_running:
                if keyboard.is_pressed('esc'):
                    self.logger("\n[ESC] Emergency stop pressed.")
                    self.is_running = False
                    self.reset_stats()
                    break
                time.sleep(0.05)
                
        t_key = threading.Thread(target=key_watcher, daemon=True)
        t_work = threading.Thread(
            target=self.execute_workflow, 
            args=(mode, target_stigma, cost_per_penguin, sell_1, qty_1, sell_2, qty_2, sell_3, qty_3),
            daemon=True
        )
        t_key.start()
        t_work.start()

    def stop(self):
        self.is_running = False
        self.logger("[INFO] Stop command received.")


class PenguinFarmerGUI:
    def __init__(self):
        self.user_cfg = load_user_config()
        self.lang = self.user_cfg.get('language', 'en')
        self.is_topmost = False  # Game tab must stay in front, not GUI
        
        self.root = tk.Tk()
        self.sound_enabled = tk.BooleanVar(value=self.user_cfg.get('sound', True))
        self.root.title("E7 SANCTUARY • FOREST OF SOULS • Created by Febvn")
        self.root.geometry("420x720+920+0")
        self.root.minsize(410, 620)
        self.root.config(bg="#0a0f16")
        try:
            self.root.attributes('-topmost', False)
        except Exception:
            pass
            
        # Keyboard shortcuts
        self.root.bind('<F5>', lambda e: self.on_start())
        self.root.bind('<Escape>', lambda e: self.on_stop())
        
        # Configure ttk style for Epic Seven dark theme combobox
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
            self.style.configure(
                'E7.TCombobox',
                fieldbackground='#0d1622',
                background='#182739',
                foreground='#ffd875',
                darkcolor='#b88a38',
                lightcolor='#b88a38',
                arrowcolor='#ffd875',
                bordercolor='#b88a38',
                insertcolor='#ffd875',
                insertwidth=2,
                font=('Segoe UI', 10, 'bold'),
                padding=(5, 2)
            )
            self.style.configure(
                'TEntry',
                insertcolor='#ffd875',
                insertwidth=2
            )
            self.style.map(
                'E7.TCombobox',
                fieldbackground=[
                    ('readonly', 'focus', '#101d2c'),
                    ('readonly', '#0d1622'),
                    ('focus', '#101d2c'),
                    ('disabled', '#080e14'),
                    ('!disabled', '#0d1622')
                ],
                foreground=[
                    ('readonly', 'focus', '#ffffff'),
                    ('readonly', '#ffd875'),
                    ('focus', '#ffffff'),
                    ('disabled', '#64748b'),
                    ('!disabled', '#ffd875')
                ],
                background=[
                    ('readonly', '#182739'),
                    ('active', '#22364c'),
                    ('!disabled', '#182739')
                ],
                arrowcolor=[
                    ('readonly', '#ffd875'),
                    ('active', '#ffffff'),
                    ('!disabled', '#ffd875')
                ],
                bordercolor=[
                    ('readonly', '#b88a38'),
                    ('focus', '#ffd875'),
                    ('!disabled', '#b88a38')
                ],
                selectbackground=[
                    ('readonly', '#1c3550'),
                    ('!disabled', '#1c3550')
                ],
                selectforeground=[
                    ('readonly', '#ffffff'),
                    ('!disabled', '#ffffff')
                ]
            )
        except Exception:
            pass

        # Configure popdown listbox colors for comboboxes
        try:
            self.root.option_add('*TCombobox*Listbox.background', '#0d1622')
            self.root.option_add('*TCombobox*Listbox.foreground', '#ffd875')
            self.root.option_add('*TCombobox*Listbox.selectBackground', '#253d5a')
            self.root.option_add('*TCombobox*Listbox.selectForeground', '#ffffff')
            self.root.option_add('*TCombobox*Listbox.font', ('Segoe UI', 9, 'bold'))
            self.root.option_add('*ComboboxPopdown*Listbox.background', '#0d1622')
            self.root.option_add('*ComboboxPopdown*Listbox.foreground', '#ffd875')
            self.root.option_add('*ComboboxPopdown*Listbox.selectBackground', '#253d5a')
            self.root.option_add('*ComboboxPopdown*Listbox.selectForeground', '#ffffff')
            self.root.option_add('*ComboboxPopdown*Listbox.font', ('Segoe UI', 9, 'bold'))
        except Exception:
            pass
        
        self.bot = PenguinFarmerBot(
            logger_func=self.log_message, 
            update_status_func=self.set_status,
            update_tally_func=self.update_tally_ui,
            on_complete_callback=self.on_bot_complete,
            snap_callback=lambda: self.root.after(0, self.snap_windows),
            lang=self.lang
        )
        self.bot.mouse_sleep = self.user_cfg.get('mouse_speed', 0.08)
        self.bot.screenshot_sleep = self.user_cfg.get('screenshot_speed', 0.15)

        icon_path = os.path.join(self.bot.config.ASSETS_DIR, 'gui_icon.ico')
        if not os.path.exists(icon_path):
            icon_path = os.path.join('assets', 'gui_icon.ico')
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass
        
        self.load_ui_images()
        self.build_ui()
        self.refresh_ui_text()
        self.update_calculations()

    def tr(self, key, **kwargs):
        return self.bot.tr(key, **kwargs)

    def load_ui_images(self):
        assets_dir = self.bot.config.ASSETS_DIR
        def get_img(fn):
            p = os.path.join(assets_dir, fn)
            if os.path.exists(p):
                try:
                    return ImageTk.PhotoImage(Image.open(p))
                except Exception:
                    return None
            return None

        self.img_header_bg = get_img('e7_header_bg.png')
        self.img_epic_bg = get_img('e7_epic_bg.png')
        self.img_elena_40 = get_img('ui_elena_40.png')
        self.img_stigma_26 = get_img('ui_stigma_26.png')
        self.img_stigma_20 = get_img('ui_stigma_20.png')
        self.img_small_52 = get_img('ui_small_52.png')
        self.img_medium_52 = get_img('ui_medium_52.png')
        self.img_large_52 = get_img('ui_large_52.png')
        self.img_small_24 = get_img('ui_small_24.png')
        self.img_medium_24 = get_img('ui_medium_24.png')
        self.img_large_24 = get_img('ui_large_24.png')

    def make_e7_card(self, parent, title_key, is_accent=True):
        border_col = '#b88a38'
        card = tk.Frame(parent, bg='#0d1522', highlightthickness=1, highlightbackground=border_col)
        card.pack(fill=tk.X, padx=14, pady=3)
        
        hdr_box = tk.Frame(card, bg='#132030')
        hdr_box.pack(fill=tk.X)
        
        icon = '✦'
        icon_col = '#ffd875'
        tk.Label(hdr_box, text=icon, font=('Segoe UI', 8), fg=icon_col, bg='#132030').pack(side=tk.LEFT, padx=(8, 4), pady=3)
        lbl_title = tk.Label(hdr_box, text=self.tr(title_key), font=('Segoe UI', 9, 'bold'), fg='#f5cb68', bg='#132030')
        lbl_title.pack(side=tk.LEFT, pady=3)
        
        tk.Frame(card, bg='#8c6b2d', height=1).pack(fill=tk.X)
        body = tk.Frame(card, bg='#0d1522')
        body.pack(fill=tk.X, padx=8, pady=4)
        return card, lbl_title, hdr_box, body
        
    def build_ui(self):
        # Cosmic Epic Seven Wallpaper Background
        if self.img_epic_bg:
            self.bg_label = tk.Label(self.root, image=self.img_epic_bg, bg="#0a0f16", bd=0)
            self.bg_label.place(x=0, y=0, width=460, height=720)

        # Card 1: Live Harvest Yield & Stigma Hub (Gold Accent Border)
        self.card_tally, self.lbl_sec_tally, hdr_tally, b_tally = self.make_e7_card(self.root, 'sec_tally', is_accent=True)
        
        # Right side of Card 1 Header: Pin button & Language selector with Gold Border
        hdr_right = tk.Frame(hdr_tally, bg="#132030")
        hdr_right.pack(side=tk.RIGHT, padx=(0, 6), pady=2)

        self.btn_pin = tk.Button(
            hdr_right,
            text='📌' if self.is_topmost else '📍',
            font=('Segoe UI', 9, 'bold'),
            bg='#1a2c40' if self.is_topmost else '#111b26',
            fg='#f5cb68' if self.is_topmost else '#8fa8c6',
            relief=tk.FLAT, bd=0, highlightthickness=1,
            highlightbackground='#b88a38' if self.is_topmost else '#22364c',
            cursor='hand2', padx=5, pady=1,
            command=self.toggle_topmost
        )
        self.btn_pin.pack(side=tk.RIGHT, padx=(4, 0))

        self.btn_snap = tk.Button(
            hdr_right,
            text='📐',
            font=('Segoe UI', 9, 'bold'),
            bg='#111b26',
            fg='#8fa8c6',
            relief=tk.FLAT, bd=0, highlightthickness=1,
            highlightbackground='#22364c',
            cursor='hand2', padx=5, pady=1,
            command=self.snap_windows
        )
        self.btn_snap.pack(side=tk.RIGHT, padx=(4, 0))

        lang_border = tk.Frame(hdr_right, bg="#b88a38", highlightthickness=1, highlightbackground="#ffd875")
        lang_border.pack(side=tk.RIGHT)

        self.lang_combo = ttk.Combobox(
            lang_border, 
            style='E7.TCombobox',
            values=['English', '한국어', '日本語', '繁體中文', '简体中文', 'Bahasa Indonesia'], 
            width=14, 
            state='readonly'
        )
        current_name = LANG_CODE_TO_NAME.get(self.lang, 'English')
        self.lang_combo.set(current_name)
        self.lang_combo.pack(padx=1, pady=1)
        self.lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)

        # Stigma Budget Input Row as Combobox Dropdown inside Gold Container
        st_row = tk.Frame(b_tally, bg="#0d1522")
        st_row.pack(fill=tk.X, padx=4, pady=(3, 4))
        
        st_left = tk.Frame(st_row, bg="#0d1522")
        st_left.pack(side=tk.LEFT)
        if self.img_stigma_26:
            tk.Label(st_left, image=self.img_stigma_26, bg="#0d1522").pack(side=tk.LEFT, padx=(0, 6))
        self.lbl_stigma_name = tk.Label(st_left, text=self.tr('lbl_stigma_limit'), font=("Segoe UI", 10, "bold"), fg="#e2e8f0", bg="#0d1522")
        self.lbl_stigma_name.pack(side=tk.LEFT, padx=(0, 6))
        
        # Gold Container Border for Stigma Combobox (allows direct typing & preset selection)
        st_box_border = tk.Frame(st_row, bg="#b88a38", highlightthickness=1, highlightbackground="#ffd875")
        st_box_border.pack(side=tk.RIGHT, padx=(0, 2))

        self.stigma_combo = ttk.Combobox(
            st_box_border,
            style='E7.TCombobox',
            values=[
                'MAX',
                '100,000 (1000x)',
                '51,000 (500x)',
                '25,500 (250x)',
                '10,200 (100x)',
                '5,100 (50x)',
                '0 (Sell Only)'
            ],
            width=15,
            font=("Segoe UI", 10, "bold"),
            justify='center'
        )
        self.stigma_combo.pack(padx=1, pady=1)
        self.stigma_combo.bind("<<ComboboxSelected>>", self.on_stigma_selected)
        self.stigma_combo.bind("<KeyRelease>", lambda e: self.update_calculations())
        self.stigma_combo.bind("<FocusIn>", lambda e: self.stigma_combo.selection_range(0, tk.END))

        # Inset plan banner with gold border
        calc_box = tk.Frame(b_tally, bg="#08101a", highlightthickness=1, highlightbackground="#b88a38")
        calc_box.pack(fill=tk.X, padx=4, pady=(0, 4))
        self.calc_label = tk.Label(calc_box, text="", font=("Segoe UI", 9, "bold"), fg="#4da3ff", bg="#08101a")
        self.calc_label.pack(anchor="w", padx=6, pady=2)

        initial_stigma = self.user_cfg.get('stigma', 10200)
        self.set_stigma_value(initial_stigma)

        # 3 Harvest Columns
        p_row = tk.Frame(b_tally, bg="#0d1522")
        p_row.pack(fill=tk.X, pady=2)
        
        # Column Small (1★) - Forest Green
        col_s = tk.Frame(p_row, bg="#0b1b15", highlightthickness=1, highlightbackground="#1b4d30", padx=4, pady=4)
        col_s.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        if self.img_small_52:
            tk.Label(col_s, image=self.img_small_52, bg="#0b1b15").pack(pady=(1, 2))
        self.lbl_small_name = tk.Label(col_s, text=self.tr('lbl_small_name'), font=("Segoe UI", 9, "bold"), fg="#48bb78", bg="#0b1b15")
        self.lbl_small_name.pack()
        self.lbl_small = tk.Label(col_s, text="0", font=("Segoe UI", 15, "bold"), fg="#ffffff", bg="#0b1b15")
        self.lbl_small.pack(pady=(1, 2))

        # Column Medium (2★) - Ice Blue
        col_m = tk.Frame(p_row, bg="#0b1827", highlightthickness=1, highlightbackground="#1b3d64", padx=4, pady=4)
        col_m.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        if self.img_medium_52:
            tk.Label(col_m, image=self.img_medium_52, bg="#0b1827").pack(pady=(1, 2))
        self.lbl_medium_name = tk.Label(col_m, text=self.tr('lbl_medium_name'), font=("Segoe UI", 9, "bold"), fg="#4299e1", bg="#0b1827")
        self.lbl_medium_name.pack()
        self.lbl_medium = tk.Label(col_m, text="0", font=("Segoe UI", 15, "bold"), fg="#ffffff", bg="#0b1827")
        self.lbl_medium.pack(pady=(1, 2))

        # Column Large (3★) - Vivid Orange / Radiant Amber
        col_l = tk.Frame(p_row, bg="#211406", highlightthickness=1, highlightbackground="#7c3f08", padx=4, pady=4)
        col_l.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        if self.img_large_52:
            tk.Label(col_l, image=self.img_large_52, bg="#211406").pack(pady=(1, 2))
        self.lbl_large_name = tk.Label(col_l, text=self.tr('lbl_large_name'), font=("Segoe UI", 9, "bold"), fg="#fb923c", bg="#211406")
        self.lbl_large_name.pack()
        self.lbl_large = tk.Label(col_l, text="0", font=("Segoe UI", 15, "bold"), fg="#ffffff", bg="#211406")
        self.lbl_large.pack(pady=(1, 2))
        
        # Spent & Gold summary bar with gold border
        sub_bar = tk.Frame(b_tally, bg="#080e15", highlightthickness=1, highlightbackground="#b88a38")
        sub_bar.pack(fill=tk.X, pady=(4, 1), padx=2)
        
        st_box = tk.Frame(sub_bar, bg="#080e15")
        st_box.pack(side=tk.LEFT, padx=6, pady=3)
        if self.img_stigma_20:
            tk.Label(st_box, image=self.img_stigma_20, bg="#080e15").pack(side=tk.LEFT, padx=(0, 4))
        self.lbl_spent = tk.Label(st_box, text=self.tr('lbl_spent', spent=0, target=10200), font=("Segoe UI", 9, "bold"), fg="#ff7b72", bg="#080e15")
        self.lbl_spent.pack(side=tk.LEFT)
        
        self.lbl_gold = tk.Label(sub_bar, text=self.tr('lbl_gold', gold=0), font=("Segoe UI", 9, "bold"), fg="#ffd875", bg="#080e15")
        self.lbl_gold.pack(side=tk.RIGHT, padx=6, pady=3)

        # Card 2: Inventory Auto-Sell Filter (Container Bawah with Gold Border)
        self.card_sell, self.lbl_sec_sell, hdr_sell, b_sell = self.make_e7_card(self.root, 'sec_sell', is_accent=True)
        
        # Right side of Card 2 Header: Operation Mode Dropdown (Full Loop / Buy Only / Sell Only)
        hdr_sell_right = tk.Frame(hdr_sell, bg="#132030")
        hdr_sell_right.pack(side=tk.RIGHT, padx=(0, 6), pady=2)

        mode_border = tk.Frame(hdr_sell_right, bg="#b88a38", highlightthickness=1, highlightbackground="#ffd875")
        mode_border.pack(side=tk.RIGHT)

        opts = MODE_OPTIONS.get(self.lang, MODE_OPTIONS['en'])
        self.mode_combo = ttk.Combobox(
            mode_border,
            style='E7.TCombobox',
            values=[label for _, label in opts],
            width=20,
            state='readonly'
        )
        self.mode_combo.pack(padx=1, pady=1)
        initial_mode = self.user_cfg.get('mode', 'full_auto')
        self.set_mode_code(initial_mode)
        self.mode_combo.bind("<<ComboboxSelected>>", self.on_mode_change)
        
        self.sell_1_var = tk.BooleanVar(value=self.user_cfg.get('sell_1', True))
        self.sell_2_var = tk.BooleanVar(value=self.user_cfg.get('sell_2', True))
        self.sell_3_var = tk.BooleanVar(value=self.user_cfg.get('sell_3', False))
        
        # 3 Columns matching Card 1 (Live Harvest Yield)
        p_sell_row = tk.Frame(b_sell, bg="#0d1522")
        p_sell_row.pack(fill=tk.X, pady=2)

        # Column Small (1★) - Forest Green
        col_s1 = tk.Frame(p_sell_row, bg="#0b1b15", highlightthickness=1, highlightbackground="#1b4d30", padx=4, pady=4)
        col_s1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        if self.img_small_24:
            tk.Label(col_s1, image=self.img_small_24, bg="#0b1b15").pack(pady=(1, 2))
        self.c1 = tk.Checkbutton(
            col_s1, text=self.tr('sell_opt_1'), variable=self.sell_1_var,
            bg="#0b1b15", fg="#48bb78", selectcolor="#06120e", activebackground="#0f291c",
            font=("Segoe UI", 9, "bold"), command=self.update_sell_gold_calc
        )
        self.c1.pack()
        q1_box = tk.Frame(col_s1, bg="#0b1b15")
        q1_box.pack(pady=(2, 2))
        self.lbl_qty_tag1 = tk.Label(q1_box, text=self.tr('lbl_sell_qty'), font=("Segoe UI", 8, "bold"), fg="#38ef7d", bg="#0b1b15")
        self.lbl_qty_tag1.pack(side=tk.LEFT, padx=(0, 4))
        q1_glow = tk.Frame(q1_box, bg="#10b981", highlightthickness=1, highlightbackground="#38ef7d")
        q1_glow.pack(side=tk.LEFT)
        self.qty_1_entry = tk.Entry(q1_glow, width=6, font=("Segoe UI", 9, "bold"), bg="#06180f", fg="#38ef7d", insertbackground="#38ef7d", relief=tk.FLAT, bd=0, justify='center')
        self.qty_1_entry.insert(0, str(self.user_cfg.get('sell_1_qty', 'MAX')))
        self.qty_1_entry.pack(padx=1, pady=1)
        self.qty_1_entry.bind('<KeyRelease>', lambda e: self.update_sell_gold_calc())

        # Column Medium (2★) - Ice Blue
        col_s2 = tk.Frame(p_sell_row, bg="#0b1827", highlightthickness=1, highlightbackground="#1b3d64", padx=4, pady=4)
        col_s2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        if self.img_medium_24:
            tk.Label(col_s2, image=self.img_medium_24, bg="#0b1827").pack(pady=(1, 2))
        self.c2 = tk.Checkbutton(
            col_s2, text=self.tr('sell_opt_2'), variable=self.sell_2_var,
            bg="#0b1827", fg="#4299e1", selectcolor="#060e18", activebackground="#0f2237",
            font=("Segoe UI", 9, "bold"), command=self.update_sell_gold_calc
        )
        self.c2.pack()
        q2_box = tk.Frame(col_s2, bg="#0b1827")
        q2_box.pack(pady=(2, 2))
        self.lbl_qty_tag2 = tk.Label(q2_box, text=self.tr('lbl_sell_qty'), font=("Segoe UI", 8, "bold"), fg="#60a5fa", bg="#0b1827")
        self.lbl_qty_tag2.pack(side=tk.LEFT, padx=(0, 4))
        q2_glow = tk.Frame(q2_box, bg="#2563eb", highlightthickness=1, highlightbackground="#60a5fa")
        q2_glow.pack(side=tk.LEFT)
        self.qty_2_entry = tk.Entry(q2_glow, width=6, font=("Segoe UI", 9, "bold"), bg="#071426", fg="#60a5fa", insertbackground="#60a5fa", relief=tk.FLAT, bd=0, justify='center')
        self.qty_2_entry.insert(0, str(self.user_cfg.get('sell_2_qty', 'MAX')))
        self.qty_2_entry.pack(padx=1, pady=1)
        self.qty_2_entry.bind('<KeyRelease>', lambda e: self.update_sell_gold_calc())

        # Column Large (3★) - Radiant Amber Gold / Vivid Orange
        col_s3 = tk.Frame(p_sell_row, bg="#211406", highlightthickness=1, highlightbackground="#7c3f08", padx=4, pady=4)
        col_s3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        if self.img_large_24:
            tk.Label(col_s3, image=self.img_large_24, bg="#211406").pack(pady=(1, 2))
        self.c3 = tk.Checkbutton(
            col_s3, text=self.tr('sell_opt_3'), variable=self.sell_3_var,
            bg="#211406", fg="#fb923c", selectcolor="#140a02", activebackground="#2e1a06",
            font=("Segoe UI", 9, "bold"), command=self.update_sell_gold_calc
        )
        self.c3.pack()
        q3_box = tk.Frame(col_s3, bg="#211406")
        q3_box.pack(pady=(2, 2))
        self.lbl_qty_tag3 = tk.Label(q3_box, text=self.tr('lbl_sell_qty'), font=("Segoe UI", 8, "bold"), fg="#fb923c", bg="#211406")
        self.lbl_qty_tag3.pack(side=tk.LEFT, padx=(0, 4))
        q3_glow = tk.Frame(q3_box, bg="#ea580c", highlightthickness=1, highlightbackground="#fb923c")
        q3_glow.pack(side=tk.LEFT)
        self.qty_3_entry = tk.Entry(q3_glow, width=6, font=("Segoe UI", 9, "bold"), bg="#1c0e04", fg="#fb923c", insertbackground="#fb923c", relief=tk.FLAT, bd=0, justify='center')
        self.qty_3_entry.insert(0, str(self.user_cfg.get('sell_3_qty', 'MAX')))
        self.qty_3_entry.pack(padx=1, pady=1)
        self.qty_3_entry.bind('<KeyRelease>', lambda e: self.update_sell_gold_calc())

        # Sub bar: Quick Presets on left, Gold estimate on right with Gold Border
        sub_bar_sell = tk.Frame(b_sell, bg="#080e15", highlightthickness=1, highlightbackground="#b88a38")
        sub_bar_sell.pack(fill=tk.X, pady=(4, 1), padx=2)
        
        pr_box = tk.Frame(sub_bar_sell, bg="#080e15")
        pr_box.pack(side=tk.LEFT, padx=6, pady=2)
        self.btn_ps_rec = tk.Button(pr_box, text=self.tr('preset_rec'), font=("Segoe UI", 8, "bold"), bg="#1a3528", fg="#48bb78", relief=tk.FLAT, bd=0, highlightthickness=1, highlightbackground="#25583b", activebackground="#234a36", cursor="hand2", padx=4, command=lambda: self.set_sell_preset(True, True, False))
        self.btn_ps_rec.pack(side=tk.LEFT, padx=(0, 2))
        self.btn_ps_all = tk.Button(pr_box, text=self.tr('preset_all'), font=("Segoe UI", 8, "bold"), bg="#152436", fg="#9bb2cb", relief=tk.FLAT, bd=0, highlightthickness=1, highlightbackground="#22364c", activebackground="#22374e", cursor="hand2", padx=4, command=lambda: self.set_sell_preset(True, True, True))
        self.btn_ps_all.pack(side=tk.LEFT)

        self.lbl_sell_total_est = tk.Label(sub_bar_sell, text=self.tr('lbl_sell_est', gold=0), font=("Segoe UI", 9, "bold"), fg="#ffd875", bg="#080e15")
        self.lbl_sell_total_est.pack(side=tk.RIGHT, padx=6, pady=2)

        # Speed & Timing Settings Bar (Screenshot time & Click time)
        speed_box = tk.Frame(self.root, bg="#08101a", highlightthickness=1, highlightbackground="#b88a38")
        speed_box.pack(fill=tk.X, padx=14, pady=(2, 3))
        
        # Left side: Screenshot Time
        ss_frame = tk.Frame(speed_box, bg="#08101a")
        ss_frame.pack(side=tk.LEFT, padx=(8, 4), pady=2)
        tk.Label(ss_frame, text="⚡", font=("Segoe UI", 9), fg="#ffd875", bg="#08101a").pack(side=tk.LEFT, padx=(0, 2))
        self.lbl_ss_time = tk.Label(ss_frame, text=self.tr('lbl_ss_time'), font=("Segoe UI", 9, "bold"), fg="#8fa8c6", bg="#08101a")
        self.lbl_ss_time.pack(side=tk.LEFT, padx=(0, 4))
        self.screenshot_time_entry = tk.Entry(
            ss_frame, width=5, font=("Segoe UI", 9, "bold"),
            bg="#14202e", fg="#ffd875", insertbackground="#ffd875",
            relief=tk.FLAT, bd=0, highlightthickness=1, highlightbackground="#22364c", justify='center'
        )
        self.screenshot_time_entry.insert(0, str(self.user_cfg.get('screenshot_speed', 0.15)))
        self.screenshot_time_entry.pack(side=tk.LEFT)
        self.screenshot_time_entry.bind('<KeyRelease>', lambda e: self.on_speed_change())

        # Right side: Click Time
        clk_frame = tk.Frame(speed_box, bg="#08101a")
        clk_frame.pack(side=tk.RIGHT, padx=(4, 8), pady=2)
        tk.Label(clk_frame, text="🖱", font=("Segoe UI", 9), fg="#ffd875", bg="#08101a").pack(side=tk.LEFT, padx=(0, 2))
        self.lbl_click_time = tk.Label(clk_frame, text=self.tr('lbl_click_time'), font=("Segoe UI", 9, "bold"), fg="#8fa8c6", bg="#08101a")
        self.lbl_click_time.pack(side=tk.LEFT, padx=(0, 4))
        self.click_time_entry = tk.Entry(
            clk_frame, width=5, font=("Segoe UI", 9, "bold"),
            bg="#14202e", fg="#ffd875", insertbackground="#ffd875",
            relief=tk.FLAT, bd=0, highlightthickness=1, highlightbackground="#22364c", justify='center'
        )
        self.click_time_entry.insert(0, str(self.user_cfg.get('mouse_speed', 0.08)))
        self.click_time_entry.pack(side=tk.LEFT)
        self.click_time_entry.bind('<KeyRelease>', lambda e: self.on_speed_change())

        # Action Buttons (E7 Emerald Buy & Crimson Stop)
        btn_box = tk.Frame(self.root, bg="#0a0f16")
        btn_box.pack(fill=tk.X, padx=14, pady=4)
        
        self.start_btn = tk.Button(
            btn_box, 
            text=f"{self.tr('btn_start')} (F5)", 
            font=("Segoe UI", 11, "bold"), 
            bg="#176332", 
            fg="#ffffff", 
            activebackground="#218343", 
            activeforeground="#ffffff", 
            relief=tk.FLAT, 
            bd=0, 
            highlightthickness=1, 
            highlightbackground="#3ec46a", 
            cursor="hand2", 
            height=1, 
            command=self.on_start
        )
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self.start_btn.bind("<Enter>", lambda e: self.start_btn.config(bg="#218343") if str(self.start_btn['state']) != 'disabled' else None)
        self.start_btn.bind("<Leave>", lambda e: self.start_btn.config(bg="#176332") if str(self.start_btn['state']) != 'disabled' else None)
        
        self.stop_btn = tk.Button(
            btn_box, 
            text=f"{self.tr('btn_stop')} (ESC)", 
            font=("Segoe UI", 11, "bold"), 
            bg="#7b1c1c", 
            fg="#ffffff", 
            activebackground="#9c2424", 
            activeforeground="#ffffff", 
            relief=tk.FLAT, 
            bd=0, 
            highlightthickness=1, 
            highlightbackground="#c53030", 
            cursor="hand2", 
            height=1, 
            command=self.on_stop
        )
        self.stop_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))
        self.stop_btn.bind("<Enter>", lambda e: self.stop_btn.config(bg="#9c2424"))
        self.stop_btn.bind("<Leave>", lambda e: self.stop_btn.config(bg="#7b1c1c"))

        # Status Indicator Bar with Gold Border
        sb = tk.Frame(self.root, bg="#091018", highlightthickness=1, highlightbackground="#b88a38")
        sb.pack(fill=tk.X, padx=14, pady=(2, 4))
        self.status_dot = tk.Label(sb, text="●", font=("Segoe UI", 9, "bold"), fg="#38ef7d", bg="#091018")
        self.status_dot.pack(side=tk.LEFT, padx=(6, 2), pady=2)
        self.status_lbl = tk.Label(sb, text=self.tr('status_ready'), font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#091018")
        self.status_lbl.pack(side=tk.LEFT, pady=2)

        self.lbl_author = tk.Label(sb, text="Created by Febvn", font=("Segoe UI", 8, "bold"), fg="#ffd875", bg="#091018")
        self.lbl_author.pack(side=tk.RIGHT, padx=8, pady=2)

        # Console Log Window (E7 Terminal Box) with Gold Border
        log_box = tk.Frame(self.root, bg="#070c12", highlightthickness=1, highlightbackground="#b88a38")
        log_box.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 8))
        
        self.log_text = tk.Text(log_box, bg="#070c12", fg="#7ee787", insertbackground="#ffd875", selectbackground="#1c334b", selectforeground="#ffffff", font=("Consolas", 9), relief=tk.FLAT, bd=0)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        scrollbar = tk.Scrollbar(log_box, command=self.log_text.yview, bg="#101924")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        self.log_message(f"{self.tr('log_init_ready')} | Created by Febvn")
        self.log_message(self.tr('log_init_feature'))
        self.log_message(self.tr('log_init_note'))

    def on_language_change(self, event=None):
        name = self.lang_combo.get()
        code = LANG_NAME_TO_CODE.get(name, 'en')
        self.lang = code
        self.bot.lang = code
        self.user_cfg['language'] = code
        save_user_config(self.user_cfg)
        self.refresh_ui_text()
        self.log_message(f"[Language] Switched to {name}.")

    def refresh_ui_text(self):
        self.root.title(f"E7 {self.tr('title').upper()} • Created by Febvn")
        if hasattr(self, 'lbl_title'):
            self.lbl_title.config(text=self.tr('title'))
        
        self.btn_pin.config(
            text='📌' if self.is_topmost else '📍',
            bg='#1a2c40' if self.is_topmost else '#111b26',
            fg='#f5cb68' if self.is_topmost else '#8fa8c6',
            highlightbackground='#b88a38' if self.is_topmost else '#22364c'
        )
        
        self.lbl_sec_tally.config(text=self.tr('sec_tally'))
        self.lbl_stigma_name.config(text=self.tr('lbl_stigma_limit'))
        self.lbl_small_name.config(text=self.tr('lbl_small_name'))
        self.lbl_medium_name.config(text=self.tr('lbl_medium_name'))
        self.lbl_large_name.config(text=self.tr('lbl_large_name'))
        
        self.lbl_sec_sell.config(text=self.tr('sec_sell'))
        self.btn_ps_rec.config(text=self.tr('preset_rec'))
        self.btn_ps_all.config(text=self.tr('preset_all'))
        self.c1.config(text=self.tr('sell_opt_1'))
        self.c2.config(text=self.tr('sell_opt_2'))
        self.c3.config(text=self.tr('sell_opt_3'))
        self.lbl_qty_tag1.config(text=self.tr('lbl_sell_qty'))
        self.lbl_qty_tag2.config(text=self.tr('lbl_sell_qty'))
        self.lbl_qty_tag3.config(text=self.tr('lbl_sell_qty'))
        
        if hasattr(self, 'lbl_ss_time'):
            self.lbl_ss_time.config(text=self.tr('lbl_ss_time'))
        if hasattr(self, 'lbl_click_time'):
            self.lbl_click_time.config(text=self.tr('lbl_click_time'))
        
        if hasattr(self, 'mode_combo'):
            current_code = self.get_mode_code()
            opts = MODE_OPTIONS.get(self.lang, MODE_OPTIONS['en'])
            self.mode_combo['values'] = [label for _, label in opts]
            self.set_mode_code(current_code)
        
        self.start_btn.config(text=f"{self.tr('btn_start')} (F5)")
        self.stop_btn.config(text=f"{self.tr('btn_stop')} (ESC)")
        
        if not self.bot.is_running:
            self.set_status(self.tr('status_ready'))
            
        self.update_calculations()
        self.update_sell_gold_calc()

    def toggle_topmost(self):
        self.is_topmost = not self.is_topmost
        try:
            self.root.attributes('-topmost', self.is_topmost)
        except Exception:
            pass
        self.btn_pin.config(
            text='📌' if self.is_topmost else '📍',
            bg='#1a2c40' if self.is_topmost else '#111b26',
            fg='#f5cb68' if self.is_topmost else '#8fa8c6',
            highlightbackground='#b88a38' if self.is_topmost else '#22364c'
        )
        self.save_current_config()
        self.log_message(f"[UI] Always-on-top: {'Enabled' if self.is_topmost else 'Disabled'}")

    def snap_windows(self):
        try:
            titles = gw.getWindowsWithTitle(self.bot.config.TARGET_WINDOW)
            w = next((x for x in titles if x.title == self.bot.config.TARGET_WINDOW), None)
            if w:
                if w.isMaximized or w.isMinimized:
                    w.restore()
                w.moveTo(0, 0)
                w.resizeTo(906, 539)
                time.sleep(0.1)
                
                # Posisikan GUI tepat di sebelah kanan E7 tanpa tabrakan / overlap (setting Refresh Shop)
                # E7: (0, 0, 906x539). GUI: lebar 420, diposisikan di sisi kanan dengan celah aman 14px
                gui_x = max(906, w.left + w.width) + 14
                gui_y = 0
                try:
                    self.root.attributes('-topmost', False)
                except Exception:
                    pass
                self.root.geometry(f"420x720+{gui_x}+{gui_y}")
                self.root.deiconify()
                
                # Aktifkan tab game Epic Seven di latar depan (tanpa paksa HWND_TOPMOST yang merusak z-index)
                try:
                    w.activate()
                except Exception:
                    pass
                
                self.log_message(f"[Snap] Setting Refresh Shop: E7 (0, 0, 906x539) | GUI ({gui_x}, {gui_y})")
                return True
            else:
                self.log_message(f"[Snap] Window '{self.bot.config.TARGET_WINDOW}' tidak ditemukan.")
        except Exception as e:
            self.log_message(f"[Snap] Gagal mengatur posisi window: {e}")
        return False

    def set_sell_preset(self, s1, s2, s3):
        self.sell_1_var.set(s1)
        self.sell_2_var.set(s2)
        self.sell_3_var.set(s3)
        self.update_sell_gold_calc()
        self.save_current_config()
        self.log_message(f"[Preset] Sell filter: 1★={s1}, 2★={s2}, 3★={s3}")

    def update_sell_gold_calc(self):
        try:
            total_fixed = 0
            has_max = False
            
            # Tier 1
            if self.sell_1_var.get():
                v = self.qty_1_entry.get().strip().upper() if hasattr(self, 'qty_1_entry') else 'MAX'
                if v in ('MAX', '', 'ALL'):
                    has_max = True
                else:
                    try:
                        n = max(0, int(v))
                        total_fixed += n * 6000
                    except ValueError:
                        has_max = True

            # Tier 2
            if self.sell_2_var.get():
                v = self.qty_2_entry.get().strip().upper() if hasattr(self, 'qty_2_entry') else 'MAX'
                if v in ('MAX', '', 'ALL'):
                    has_max = True
                else:
                    try:
                        n = max(0, int(v))
                        total_fixed += n * 18000
                    except ValueError:
                        has_max = True

            # Tier 3
            if self.sell_3_var.get():
                v = self.qty_3_entry.get().strip().upper() if hasattr(self, 'qty_3_entry') else 'MAX'
                if v in ('MAX', '', 'ALL'):
                    has_max = True
                else:
                    try:
                        n = max(0, int(v))
                        total_fixed += n * 54000
                    except ValueError:
                        has_max = True

            if hasattr(self, 'lbl_sell_total_est'):
                if has_max:
                    if total_fixed > 0:
                        self.lbl_sell_total_est.config(text=f"{self.tr('lbl_sell_est', gold=total_fixed)} + MAX")
                    else:
                        self.lbl_sell_total_est.config(text=self.tr('lbl_sell_est', gold=0).replace("0", "MAX"))
                else:
                    self.lbl_sell_total_est.config(text=self.tr('lbl_sell_est', gold=total_fixed))
        except Exception:
            pass

    def on_bot_complete(self):
        def _beep():
            if self.sound_enabled.get() and winsound:
                try:
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                except Exception:
                    pass
        self.root.after(0, _beep)

    def extract_stigma_number(self, val):
        val_str = str(val).strip().upper()
        if any(k in val_str for k in ('MAX', 'MAZ', 'ALL', 'UNLIMITED')):
            return -1
        if '(' in val_str:
            val_str = val_str.split('(')[0]
        num_str = re.sub(r'[^\d]', '', val_str)
        try:
            return int(num_str) if num_str else 0
        except ValueError:
            return 0

    def on_stigma_selected(self, event=None):
        val = self.stigma_combo.get().strip().upper()
        if any(k in val for k in ('MAX', 'MAZ', 'ALL', 'UNLIMITED')) or val == '-1':
            self.stigma_combo.set('MAX')
        else:
            num = self.extract_stigma_number(val)
            self.stigma_combo.set(f"{num:,}")
        self.save_current_config()
        self.update_calculations()

    def get_stigma_value(self):
        if not hasattr(self, 'stigma_combo'):
            return self.user_cfg.get('stigma', 10200)
        return self.extract_stigma_number(self.stigma_combo.get())

    def set_stigma_value(self, val):
        if not hasattr(self, 'stigma_combo'):
            return
        val_str = str(val).strip().upper()
        if any(k in val_str for k in ('MAX', 'MAZ', 'ALL', 'UNLIMITED')) or val == -1 or val == '-1':
            self.stigma_combo.set('MAX')
        else:
            num = self.extract_stigma_number(val)
            self.stigma_combo.set(f"{num:,}")
        self.update_calculations()

    def set_stigma_preset(self, val):
        self.set_stigma_value(val)
        self.save_current_config()
        val_up = str(val).strip().upper()
        if val_up in ('MAX', 'MAZ', '-1') or 'MAX' in val_up:
            self.log_message("[Stigma] Batas Stigma diset ke MAX: Bot tidak akan berhenti sampai Stigma habis total.")
        else:
            self.log_message(f"[Stigma] Batas Stigma diset ke: {self.stigma_combo.get()}")

    def get_mode_code(self):
        if not hasattr(self, 'mode_combo'):
            return self.user_cfg.get('mode', 'full_auto')
        txt = self.mode_combo.get()
        opts = MODE_OPTIONS.get(self.lang, MODE_OPTIONS['en'])
        for code, label in opts:
            if label == txt:
                return code
        for lang_opts in MODE_OPTIONS.values():
            for code, label in lang_opts:
                if label == txt:
                    return code
        return 'full_auto'

    def set_mode_code(self, code):
        if not hasattr(self, 'mode_combo'):
            return
        opts = MODE_OPTIONS.get(self.lang, MODE_OPTIONS['en'])
        for c, label in opts:
            if c == code:
                self.mode_combo.set(label)
                break
        else:
            self.mode_combo.set(opts[0][1])
        self.update_calculations()

    def on_mode_change(self, event=None):
        code = self.get_mode_code()
        self.user_cfg['mode'] = code
        save_user_config(self.user_cfg)
        self.update_calculations()
        self.log_message(f"[Mode] Operation mode: {self.mode_combo.get()}")

    def save_current_config(self):
        stigma = self.get_stigma_value()
        mode = self.get_mode_code()
        cost = getattr(self, 'cost', 102)
        try:
            ss_val = float(self.screenshot_time_entry.get().strip()) if hasattr(self, 'screenshot_time_entry') else 0.15
        except Exception:
            ss_val = 0.15
        try:
            clk_val = float(self.click_time_entry.get().strip()) if hasattr(self, 'click_time_entry') else 0.08
        except Exception:
            clk_val = 0.08
        self.user_cfg.update({
            'stigma': stigma,
            'cost': cost,
            'mode': mode,
            'sell_1': self.sell_1_var.get(),
            'sell_1_qty': self.qty_1_entry.get().strip() if hasattr(self, 'qty_1_entry') else 'MAX',
            'sell_2': self.sell_2_var.get(),
            'sell_2_qty': self.qty_2_entry.get().strip() if hasattr(self, 'qty_2_entry') else 'MAX',
            'sell_3': self.sell_3_var.get(),
            'sell_3_qty': self.qty_3_entry.get().strip() if hasattr(self, 'qty_3_entry') else 'MAX',
            'language': self.lang,
            'topmost': self.is_topmost,
            'sound': self.sound_enabled.get(),
            'screenshot_speed': ss_val,
            'mouse_speed': clk_val
        })
        save_user_config(self.user_cfg)

    def update_calculations(self):
        if not hasattr(self, 'calc_label') or not hasattr(self, 'lbl_spent'):
            return
        try:
            mode = self.get_mode_code() if hasattr(self, 'mode_combo') else self.user_cfg.get('mode', 'full_auto')
            stigma = self.get_stigma_value()
            cost = getattr(self, 'cost', 102)
            batch_cost = cost * self.bot.config.MAX_BATCH_SIZE
            current_spent = getattr(self.bot, 'total_stigma_spent', 0)
            if mode == 'sell_only' or stigma == 0:
                self.calc_label.config(text="Mode: Sell Only (Directly sell penguins in inventory)")
                self.lbl_spent.config(text=self.tr('lbl_spent', spent=current_spent, target='0'))
                return
            if stigma == -1: # MAX
                if mode == 'buy_only':
                    self.calc_label.config(text="Mode: Buy Only | Stigma: MAX (Habiskan Semua Stigma) | No Selling")
                else:
                    self.calc_label.config(text="Plan: MAX (Farming Terus Menerus Sampai Stigma Habis Total)")
                self.lbl_spent.config(text=self.tr('lbl_spent', spent=current_spent, target='MAX'))
                return
            batches = max(1, stigma // batch_cost)
            penguins = batches * self.bot.config.MAX_BATCH_SIZE
            gold_est = penguins * 6000
            if mode == 'buy_only':
                self.calc_label.config(text=f"Mode: Buy Only | {penguins:,} Penguins ({batches} Batches) | No Selling")
            else:
                self.calc_label.config(text=f"{self.tr('calc_plan', penguins=penguins, batches=batches, gold_est=gold_est)} -> Auto-Sell")
            self.lbl_spent.config(text=self.tr('lbl_spent', spent=current_spent, target=f"{stigma:,}"))
        except Exception:
            if hasattr(self, 'calc_label'):
                self.calc_label.config(text="Invalid number input")

    def update_tally_ui(self, s, m, l, spent, gold):
        def _update():
            self.lbl_small.config(text=f"{s:,}")
            self.lbl_medium.config(text=f"{m:,}")
            self.lbl_large.config(text=f"{l:,}")
            target = self.get_stigma_value()
            target_str = "MAX" if target == -1 else (f"{spent:,}" if target == 0 else f"{target:,}")
            self.lbl_spent.config(text=self.tr('lbl_spent', spent=spent, target=target_str))
            self.lbl_gold.config(text=self.tr('lbl_gold', gold=gold))
        self.root.after(0, _update)

    def on_speed_change(self):
        try:
            ss_val = float(self.screenshot_time_entry.get().strip())
            self.bot.screenshot_sleep = max(0.01, ss_val)
            self.user_cfg['screenshot_speed'] = self.bot.screenshot_sleep
        except Exception:
            pass
            
        try:
            clk_val = float(self.click_time_entry.get().strip())
            self.bot.mouse_sleep = max(0.01, clk_val)
            self.user_cfg['mouse_speed'] = self.bot.mouse_sleep
        except Exception:
            pass
            
        save_user_config(self.user_cfg)

    def log_message(self, text):
        def _append():
            self.log_text.insert(tk.END, text + "\n")
            self.log_text.see(tk.END)
        self.root.after(0, _append)

    def set_status(self, text):
        def _set():
            clean = text if text.startswith("Status:") or text.startswith("상태:") or text.startswith("狀態:") or text.startswith("状态:") or text.startswith("状態:") else f"Status: {text}"
            self.status_lbl.config(text=clean)
            if "progress" in text.lower() or "buying" in text.lower() or "navigating" in text.lower() or "selling" in text.lower() or "진행" in text or "移動" in text:
                self.status_dot.config(fg="#38ef7d")
                self.status_lbl.config(fg="#38ef7d")
            elif "stopped" in text.lower() or "error" in text.lower() or "중지" in text or "停止" in text or "dihentikan" in text.lower():
                self.status_dot.config(fg="#f56565")
                self.status_lbl.config(fg="#f56565")
            else:
                self.status_dot.config(fg="#ffd875")
                self.status_lbl.config(fg="#94a3b8")
        self.root.after(0, _set)

    def on_start(self):
        self.snap_windows()
        mode = self.get_mode_code()
        stigma = self.get_stigma_value()
        cost = getattr(self, 'cost', 102)
        sell_1 = self.sell_1_var.get()
        qty_1 = self.qty_1_entry.get().strip() if hasattr(self, 'qty_1_entry') else 'MAX'
        sell_2 = self.sell_2_var.get()
        qty_2 = self.qty_2_entry.get().strip() if hasattr(self, 'qty_2_entry') else 'MAX'
        sell_3 = self.sell_3_var.get()
        qty_3 = self.qty_3_entry.get().strip() if hasattr(self, 'qty_3_entry') else 'MAX'

        if mode == 'buy_only':
            s1, s2, s3 = False, False, False
        else:
            s1, s2, s3 = sell_1, sell_2, sell_3

        try:
            ss_val = float(self.screenshot_time_entry.get().strip())
            self.bot.screenshot_sleep = max(0.01, ss_val)
        except Exception:
            self.bot.screenshot_sleep = 0.15
            
        try:
            clk_val = float(self.click_time_entry.get().strip())
            self.bot.mouse_sleep = max(0.01, clk_val)
        except Exception:
            self.bot.mouse_sleep = 0.08

        self.user_cfg.update({
            'stigma': stigma,
            'cost': cost,
            'mode': mode,
            'sell_1': sell_1,
            'sell_1_qty': qty_1,
            'sell_2': sell_2,
            'sell_2_qty': qty_2,
            'sell_3': sell_3,
            'sell_3_qty': qty_3,
            'screenshot_speed': self.bot.screenshot_sleep,
            'mouse_speed': self.bot.mouse_sleep
        })
        save_user_config(self.user_cfg)

        self.start_btn.config(state=tk.DISABLED, bg="#0d3b1e")
        self.set_status(self.tr('status_running'))
        
        self.bot.start_thread(mode, stigma, cost, s1, qty_1, s2, qty_2, s3, qty_3)
        self.monitor_thread()

    def monitor_thread(self):
        if self.bot.is_running:
            self.root.after(500, self.monitor_thread)
        else:
            self.start_btn.config(state=tk.NORMAL, bg="#176332")

    def on_stop(self):
        self.bot.stop()
        self.bot.reset_stats()
        self.update_tally_ui(0, 0, 0, 0, 0)
        self.start_btn.config(state=tk.NORMAL, bg="#176332")
        self.set_status(self.tr('status_stopped'))


if __name__ == '__main__':
    try:
        app = PenguinFarmerGUI()
        if '--start' in sys.argv or '--autostart' in sys.argv:
            app.root.after(1000, app.on_start)
        app.root.mainloop()
    except Exception:
        import traceback
        with open(os.path.join(os.path.dirname(__file__), 'crash.log'), 'w', encoding='utf-8') as f:
            traceback.print_exc(file=f)
