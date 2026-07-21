import streamlit as st
from google import genai

api_key = st.secrets["GEMINI_API_KEY"]
clilent = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-3.5-flash"

# ページ設定
st.set_page_config(page_title="今日のランチレシピ", page_icon="🍳", layout="centered")

st.title("今日のランチレシピ🍳")
st.write("冷蔵庫にある食材を入れると、「ツンデレちゃん」がお昼ごはんのレシピを考えてくれるよ！")

# --- サイドバー：設定 ---
with st.sidebar:
    st.header("設定")
    num_recipes = st.slider("提案してほしいレシピの数", min_value=1, max_value=5, value=3)
    cooking_time = st.selectbox(
        "調理時間の目安",
        ["指定なし", "10分以内", "20分以内", "30分以内"],
    )
    genre = st.selectbox(
        "気分のジャンル",
        ["おまかせ", "和食", "洋食", "中華", "がっつり系", "さっぱり系"],
    )

# --- メイン：食材入力 ---
st.subheader("冷蔵庫にある食材を入力してね")
ingredients_text = st.text_area(
    "食材をカンマや改行で区切って入力（例：卵, 玉ねぎ, ベーコン, ごはん）",
    height=100,
    placeholder="卵, 玉ねぎ, ベーコン, ごはん",
)

extra_request = st.text_input(
    "その他の希望（任意）", placeholder="例：辛いものが食べたい、ダイエットを意識したもの など"
)

submit = st.button("レシピを考えてとお願いする", type="primary")


def build_prompt(ingredients, num, time_pref, genre_pref, extra):
    time_line = f"調理時間は{time_pref}を目安にしてください。" if time_pref != "指定なし" else ""
    genre_line = f"ジャンルの希望は「{genre_pref}」です。" if genre_pref != "おまかせ" else ""
    extra_line = f"その他の希望：{extra}" if extra else ""

    return f"""あなたは家庭料理が得意なツンデレ料理人です。
以下の食材を使って、お昼ごはんのレシピを{num}個提案してください。

【使える食材】
{ingredients}

{time_line}
{genre_line}
{extra_line}

※ 食材はすべて使い切る必要はありません。ある食材を活用したレシピを考えてください。
※ 基本的な調味料（塩、こしょう、醤油、油など）は自由に使ってOKとします。

各レシピについて、以下の形式で出力してください。

## レシピ名
- 調理時間の目安
- 材料（分量も簡単に）
- 作り方（手順を3〜6ステップ程度で）
- ちょっとしたコツやアレンジ案

レシピ同士は "---" で区切ってください。
"""


if submit:
    if not ingredients_text.strip():
        st.warning("食材を入力してね！")
    else:
        if "GEMINI_API_KEY" not in st.secrets:
            st.error(".streamlit/secrets.toml に GEMINI_API_KEY を設定してください。")
        else:
            with st.spinner("AIがレシピを考え中..."):
                try:
                    # 最新の google-genai SDK クライアントの初期化
                    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                    
                    prompt = build_prompt(
                        ingredients_text, num_recipes, cooking_time, genre, extra_request
                    )
                    
                    # Gemini 2.5 Flash モデルを使用（高速かつ日本語も得意です）
                    response = client.models.generate_content(
                        model="gemini-3.5-flash",
                        contents=prompt,
                    )
                    
                    # 生成されたテキストをセッション状態に保存
                    st.session_state["result"] = response.text
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

if "result" in st.session_state:
    st.subheader("🍽️ 提案されたレシピ")
    recipes = st.session_state["result"].split("---")
    for recipe in recipes:
        recipe = recipe.strip()
        if recipe:
            st.markdown(recipe)
            st.divider()

