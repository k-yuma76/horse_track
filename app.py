import streamlit as st
import streamlit.components.v1 as components
import json

# 縦型レイアウトのため、ページ全体を中央寄せに設定
st.set_page_config(layout="centered")

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

# --- 2. 縦画面専用・縦型コースのHTML/JS ---
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
    /* 【縦画面最適化】スマホの縦長画面に合わせた縦型オーバルトラック */
    #course-container {{
        position: relative;
        width: 94vw;
        max-width: 420px; /* PC閲覧時にも巨大化させない上限 */
        height: 76vh;
        max-height: 620px; /* 一般的なスマホ画面にすっぽり収まる高さ */
        background-color: #e2f0d9; /* 芝の緑色 */
        border: 4px solid #444;
        border-radius: 120px; /* 縦長の楕円を形成 */
        box-shadow: inset 0 0 20px rgba(0,0,0,0.1);
        margin: 5px auto;
        overflow: hidden;
        box-sizing: border-box;
    }}
    /* 縦長の内馬場 */
    .inner-field {{
        position: absolute;
        top: 16%;
        left: 22%;
        right: 22%;
        bottom: 16%;
        background-color: #ffffff;
        border: 3px solid #444;
        border-radius: 70px;
        z-index: 1;
        box-sizing: border-box;
    }}
    /* 馬番ピン（丸数字） */
    .horse-pin {{
        position: absolute;
        cursor: move;
        z-index: 10;
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
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        transition: transform 0.05s ease;
        box-sizing: border-box;
    }}
    .horse-pin:active {{
        transform: scale(1.3); /* タッチした瞬間に一回り大きくして指での視認性をUP */
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
        
        // 【縦長中央配置】3列 × 6行 のグリッドで内馬場に綺麗に並べる
        const cols = 3;
        const r = Math.floor(index / cols);
        const c = index % cols;
        
        // 縦長エリアのバランスに合わせたパーセンテージ位置
        const percentX = 32 + (c * 15); 
        const percentY = 22 + (r * 9);

        div.style.left = percentX + '%';
        div.style.top = percentY + '%';
        div.style.backgroundColor = horse.bg;
        div.style.color = horse.fg;
        div.innerText = horse.num;
        
        container.appendChild(div);
        
        // ドラッグ＆ドロップ制御（指の動きに追従）
        let isDragging = false;
        let startX, startY;
        let startLeft, startTop;
        
        div.addEventListener('pointerdown', (e) => {{
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            
            // ドラッグ開始時に確実なピクセル座標に固定
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
            
            // 現在の縦長コンテナのサイズをリアルタイムに取得（バグ防止）
            const currentContainerWidth = container.clientWidth;
            const currentContainerHeight = container.clientHeight;
            
            // コースの全境界（上下左右）でのハズレ防止制限
            if(newX < 0) newX = 0;
            if(newX > currentContainerWidth - div.clientWidth) newX = currentContainerWidth - div.clientWidth;
            if(newY < 0) newY = 0;
            if(newY > currentContainerHeight - div.clientHeight) newY = currentContainerHeight - div.clientHeight;
            
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

# Streamlit上の表示コンテナを高さを合わせて設置
components.html(html_code, height=640, scrolling=False)