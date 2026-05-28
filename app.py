import streamlit as st
import streamlit.components.v1 as components
import json

# 画面幅を広く使う設定
st.set_page_config(layout="wide")

# --- 【新機能】Streamlit自体の左右マージンを限界までゼロにする注入CSS ---
st.markdown("""
    <style>
        /* アプリ全体のパディング（余白）を極限まで削る */
        .block-container {
            padding-left: 0.3rem !important;
            padding-right: 0.3rem !important;
            padding-top: 0.5rem !important;
            padding-bottom: 0rem !important;
        }
        /* 不要な要素の隙間を排除 */
        iframe {
            display: block;
            margin: 0 auto;
        }
    </style>
""", unsafe_allow_html=True)

# --- 1. JRA基準の18頭立て枠順割当 ---
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
    horses_data.append({
        "num": i,
        "bg": WAKU_COLORS[waku]["bg"],
        "fg": WAKU_COLORS[waku]["fg"]
    })

# JavaScriptに渡すためにJSON文字列に変換
horses_json = json.dumps(horses_data)

# --- 2. 画面端ギリギリ・コース幅広版 HTML/JS ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-select=no">
<style>
    body {{
        margin: 0;
        padding: 0;
        background-color: transparent;
        overflow: hidden;
        -webkit-touch-callout: none;
        -webkit-user-select: none;
        user-select: none;
    }}
    /* 【修正】widthを96vwから99vwに広げ、画面の左右端ぴったりに配置 */
    #course-container {{
        position: relative;
        width: 99vw;
        max-width: 100%;
        aspect-ratio: 2.2 / 1;
        background-color: #e2f0d9; /* 芝の緑色 */
        border: 4px solid #444;
        border-radius: 1000px;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.1);
        margin: 0 auto;
        overflow: hidden;
        box-sizing: border-box;
    }}
    /* 内馬場（中央の白枠） */
    .inner-field {{
        position: absolute;
        top: 34%;
        bottom: 34%;
        left: 23%;
        right: 23%;
        background-color: #ffffff;
        border: 2.5px solid #444;
        border-radius: 1000px;
        z-index: 1;
        box-sizing: border-box;
    }}
    /* 馬番ピン */
    .horse-pin {{
        position: absolute;
        cursor: move;
        z-index: 10;
        touch-action: none;
        width: 25px;
        height: 25px;
        border-radius: 50%;
        border: 1.5px solid #222;
        display: flex;
        justify-content: center;
        align-items: center;
        font-weight: bold;
        font-size: 13px;
        box-shadow: 1px 1px 4px rgba(0,0,0,0.3);
        box-sizing: border-box;
    }}
    .horse-pin:active {{
        transform: scale(1.4);
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

    // 馬番号ピンの生成と初期配置
    horses.forEach((horse, index) => {{
        const div = document.createElement('div');
        div.className = 'horse-pin';
        
        // 下側直線レーンに綺麗に並べる（コース幅が広がったので左右の余白を12%から6%に詰めて最適化）
        const col = Math.floor(index / 2);
        const percentX = 6 + (col * 10); 
        const percentY = (index % 2 === 0) ? 72 : 86;

        div.style.left = percentX + '%';
        div.style.top = percentY + '%';
        div.style.backgroundColor = horse.bg;
        div.style.color = horse.fg;
        div.innerText = horse.num;
        
        container.appendChild(div);
        
        // ドラッグ＆ドロップ制御
        let isDragging = false;
        let startX, startY;
        let startLeft, startTop;
        
        div.addEventListener('pointerdown', (e) => {{
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            
            startLeft = div.offsetLeft;
            startTop = div.offsetTop;
            div.style.left = startLeft + 'px';
            div.style.top = startTop + 'px';
            
            div.setPointerCapture(e.pointerId);
        }});
        
        div.addEventListener('pointermove', (e) => {{
            if (!isDragging) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            
            let newX = startLeft + dx;
            let newY = startTop + dy;
            
            const currentWidth = container.clientWidth;
            const currentHeight = container.clientHeight;
            
            if(newX < 0) newX = 0;
            if(newX > currentWidth - div.clientWidth) newX = currentWidth - div.clientWidth;
            if(newY < 0) newY = 0;
            if(newY > currentHeight - div.clientHeight) newY = currentHeight - div.clientHeight;
            
            div.style.left = newX + 'px';
            div.style.top = newY + 'px';
        }});
        
        div.addEventListener('pointerup', (e) => {{
            if (!isDragging) return;
            isDragging = false;
            div.releasePointerCapture(e.pointerId);
        }});
    }});
</script>

</body>
</html>
"""

# Streamlit側の表示枠のサイズ
components.html(html_code, height=380, scrolling=False)