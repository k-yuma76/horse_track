import streamlit as st
import streamlit.components.v1 as components
import json

# 画面幅を最大限広く使う設定
st.set_page_config(layout="wide")

# タイトル等は表示せず、注意書きのみStreamlit側に表示
st.caption("💡 スマホの方は画面を横向きにすると、より大きく表示されて動かしやすくなります。")

# --- 1. JRA基準の18頭立て枠順割当 ---
WAKU_COLORS = {
    1: {"bg": "#ffffff", "fg": "#000000"},  # 1枠: 白
    2: {"bg": "#000000", "fg": "#ffffff"},  # 黑
    3: {"bg": "#ff3333", "fg": "#ffffff"},  # 赤
    4: {"bg": "#3333ff", "fg": "#ffffff"},  # 青
    5: {"bg": "#ffff00", "fg": "#000000"},  # 黄
    6: {"bg": "#00aa00", "fg": "#ffffff"},  # 緑
    7: {"bg": "#ff9900", "fg": "#000000"},  # 橙
    8: {"bg": "#ff99cc", "fg": "#000000"},  # 桃
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
    # 初期位置(x, top)はJavaScript側で動的に中央に計算するため、ここでは0にしておく
    horses_data.append({
        "num": i,
        "bg": WAKU_COLORS[waku]["bg"],
        "fg": WAKU_COLORS[waku]["fg"],
        "x": 0,
        "top": 0
    })

# JavaScriptに渡すためにJSON文字列に変換
horses_json = json.dumps(horses_data)

# --- 2. レスポンシブ対応のコースと丸数字のHTML/JS ---
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
    /* 【縦画面対応】コース全体を画面幅に合わせ、アスペクト比(2:1)を維持して縮小表示 */
    #course-container {{
        position: relative;
        width: 98vw; /* 画面幅の98% */
        margin: 10px auto;
        aspect-ratio: 2 / 1; /* 横2：縦1の比率を強制維持 */
        background-color: #e2f0d9; /* 芝の緑色 */
        border: 4px solid #444;
        border-radius: 500px; /* 楕円トラック */
        box-shadow: inset 0 0 20px rgba(0,0,0,0.1);
        overflow: hidden;
        box-sizing: border-box;
    }}
    /* 内馬場 */
    .inner-field {{
        position: absolute;
        top: 20%;
        left: 15%;
        width: 70%;
        height: 60%;
        background-color: #ffffff;
        border: 3px solid #444;
        border-radius: 400px;
        z-index: 1;
        box-sizing: border-box;
    }}
    /* 馬番ピン（丸数字）スマホ用に少し小さく調整 */
    .horse-pin {{
        position: absolute;
        cursor: move;
        z-index: 10;
        touch-action: none;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        border: 2px solid #222;
        display: flex;
        justify-content: center;
        align-items: center;
        font-weight: bold;
        font-size: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        transition: transform 0.05s ease;
        box-sizing: border-box;
    }}
    .horse-pin:active {{
        transform: scale(1.3); /* つまんだ時に少し大きく */
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

    // コンテナのサイズを取得
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;

    // 馬番号ピンの生成と配置
    horses.forEach((horse, index) => {{
        const div = document.createElement('div');
        div.className = 'horse-pin';
        
        // --- 【中央配置】中央の内馬場に整列させる計算 ---
        // 6列 x 3行 のグリッドで配置
        const cols = 6;
        const gridSpacingX = 45; // px
        const gridSpacingY = 40; // px
        const gridStartX = (containerWidth / 2) - ((cols - 1) * gridSpacingX / 2);
        const gridStartY = (containerHeight / 2) - ((3 - 1) * gridSpacingY / 2);

        const r = Math.floor(index / cols);
        const c = index % cols;
        const initialX = gridStartX + (c * gridSpacingX) - 15; // 15はピンの半径
        const initialY = gridStartY + (r * gridSpacingY) - 15;

        div.style.left = initialX + 'px';
        div.style.top = initialY + 'px';
        div.style.backgroundColor = horse.bg;
        div.style.color = horse.fg;
        div.innerText = horse.num;
        
        container.appendChild(div);
        
        // ドラッグ＆ドロップ制御（マルチタッチ・マウス対応）
        let isDragging = false;
        let startX, startY;
        let startLeft, startTop;
        
        div.addEventListener('pointerdown', (e) => {{
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            startLeft = div.offsetLeft;
            startTop = div.offsetTop;
            div.setPointerCapture(e.pointerId);
        }});
        
        div.addEventListener('pointermove', (e) => {{
            if (!isDragging) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            
            let newX = startLeft + dx;
            let newY = startTop + dy;
            
            // コースの枠外へのはみ出し防止（コンテナのpxサイズを基準に）
            if(newX < 0) newX = 0;
            if(newX > containerWidth - div.clientWidth) newX = containerWidth - div.clientWidth;
            if(newY < 0) newY = 0;
            if(newY > containerHeight - div.clientHeight) newY = containerHeight - div.clientHeight;
            
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

# HTMLコンポーネントを画面に合わせて描画（スマホ縦画面でもはみ出さない高さに設定）
components.html(html_code, height=520, scrolling=False)