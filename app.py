import streamlit as st
import streamlit.components.v1 as components
import json

# 画面幅を最大限広く使う設定
st.set_page_config(layout="wide")

# --- 1. JRA基準の18頭立て枠順割当とデータ生成 ---
WAKU_COLORS = {
    1: {"bg": "#ffffff", "fg": "#000000"},  # 1枠: 白
    2: {"bg": "#000000", "fg": "#ffffff"},  # 2枠: 黒
    3: {"bg": "#ff3333", "fg": "#ffffff"},  # 3枠: 赤
    4: {"bg": "#3333ff", "fg": "#ffffff"},  # 4枠: 青
    5: {"bg": "#ffff00", "fg": "#000000"},  # 5枠: 黄
    6: {"bg": "#00aa00", "fg": "#ffffff"},  # 6枠: 緑
    7: {"bg": "#ff9900", "fg": "#000000"},  # 7枠: 橙
    8: {"bg": "#ff99cc", "fg": "#000000"},  # 8枠: 桃
}

def get_waku_for_18(num):
    if num in [1, 2]: return 1
    elif num in [3, 4]: return 2
    elif num in [5, 6]: return 3
    elif num in [7, 8]: return 4
    elif num in [9, 10]: return 5
    elif num in [11, 12]: return 6
    elif num in [13, 14, 15]: return 7
    else: return 8

horses_data = []
for i in range(1, 19):
    waku = get_waku_for_18(i)
    
    # 18頭がコース下側のレーンに綺麗に収まるよう初期位置を計算 (2列の互い違い)
    col_index = (i - 1) // 2
    x_pos = 80 + (col_index * 95)
    y_pos = 425 if i % 2 == 1 else 465

    horses_data.append({
        "num": i,
        "bg": WAKU_COLORS[waku]["bg"],
        "fg": WAKU_COLORS[waku]["fg"],
        "x": x_pos,
        "top": y_pos
    })

# JavaScriptに渡すためにJSON文字列に変換
horses_json = json.dumps(horses_data)

# --- 2. コースと丸数字のみをレンダリングするHTML/JS ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{
        margin: 0;
        padding: 0;
        background-color: transparent;
        overflow: hidden;
    }}
    /* 横に広い綺麗な楕円トラック */
    #course-container {{
        position: relative;
        width: 96vw;
        height: 520px;
        background-color: #e2f0d9; /* 芝の緑色 */
        border: 4px solid #444;
        border-radius: 260px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.1);
        margin: 10px auto;
        overflow: hidden;
    }}
    /* 内馬場 */
    .inner-field {{
        position: absolute;
        top: 110px;
        left: 160px;
        right: 160px;
        bottom: 110px;
        background-color: #ffffff;
        border: 3px solid #444;
        border-radius: 150px;
        z-index: 1;
    }}
    /* 馬番ピン（丸数字単体） */
    .horse-pin {{
        position: absolute;
        cursor: move;
        z-index: 10;
        user-select: none;
        touch-action: none;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        border: 2px solid #222;
        display: flex;
        justify-content: center;
        align-items: center;
        font-weight: bold;
        font-size: 16px;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        transition: transform 0.05s ease;
    }}
    .horse-pin:active {{
        transform: scale(1.15);
        z-index: 100;
    }}
</style>
</head>
<body>

<div id="course-container">
    <div class="inner-field"></div>
</div>

<script>
    const horses = {horses_json};
    const container = document.getElementById('course-container');

    // 馬番号ピンの生成と配置
    horses.forEach(horse => {{
        const div = document.createElement('div');
        div.className = 'horse-pin';
        div.style.left = horse.x + 'px';
        div.style.top = horse.top + 'px';
        div.style.backgroundColor = horse.bg;
        div.style.color = horse.fg;
        div.innerText = horse.num;
        
        container.appendChild(div);
        
        // ドラッグ＆ドロップ制御（マルチタッチ・マウス対応）
        let isDragging = false;
        let startX, startY;
        let initialX, initialY;
        
        div.addEventListener('pointerdown', (e) => {{
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            initialX = div.offsetLeft;
            initialY = div.offsetTop;
            div.setPointerCapture(e.pointerId);
            div.style.zIndex = 100;
        }});
        
        div.addEventListener('pointermove', (e) => {{
            if (!isDragging) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            
            let newX = initialX + dx;
            let newY = initialY + dy;
            
            // コースの枠外へのはみ出し防止
            if(newX < 0) newX = 0;
            if(newX > container.clientWidth - div.clientWidth) newX = container.clientWidth - div.clientWidth;
            if(newY < 0) newY = 0;
            if(newY > container.clientHeight - div.clientHeight) newY = container.clientHeight - div.clientHeight;
            
            div.style.left = newX + 'px';
            div.style.top = newY + 'px';
        }});
        
        div.addEventListener('pointerup', (e) => {{
            if (!isDragging) return;
            isDragging = false;
            div.releasePointerCapture(e.pointerId);
            div.style.zIndex = 10;
        }});
    }});
</script>

</body>
</html>
"""

# 画面いっぱいに描画
components.html(html_code, height=550, scrolling=False)