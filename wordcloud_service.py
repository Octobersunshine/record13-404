import io
import os
import sys
import base64
import jieba
import numpy as np
from wordcloud import WordCloud
from PIL import Image


def detect_chinese_font():
    font_candidates = []

    if sys.platform.startswith("win"):
        font_dir = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
        font_candidates = [
            os.path.join(font_dir, "msyh.ttc"),
            os.path.join(font_dir, "msyh.ttf"),
            os.path.join(font_dir, "simhei.ttf"),
            os.path.join(font_dir, "simsun.ttc"),
            os.path.join(font_dir, "simkai.ttf"),
            os.path.join(font_dir, "simli.ttf"),
        ]
    elif sys.platform.startswith("darwin"):
        font_candidates = [
            "/System/Library/Fonts/PingFang.ttc",
            "/Library/Fonts/Songti.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
        ]
    else:
        font_candidates = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/usr/share/fonts/truetype/arphic/ukai.ttc",
        ]

    for font_path in font_candidates:
        if os.path.exists(font_path):
            return font_path

    return None


DEFAULT_FONT_PATH = detect_chinese_font()


def segment_text(text):
    seg_list = jieba.cut(text, cut_all=False)
    return " ".join(seg_list)


def contains_chinese(text):
    for ch in text:
        if "\u4e00" <= ch <= "\u9fff":
            return True
    return False


def generate_wordcloud_base64(
    text,
    width=800,
    height=600,
    background_color="white",
    font_path=None,
    max_words=200,
    max_font_size=None,
    colormap="viridis",
):
    if font_path is None and contains_chinese(text) and DEFAULT_FONT_PATH:
        font_path = DEFAULT_FONT_PATH

    segmented_text = segment_text(text)

    wc = WordCloud(
        width=width,
        height=height,
        background_color=background_color,
        font_path=font_path,
        max_words=max_words,
        max_font_size=max_font_size,
        colormap=colormap,
        prefer_horizontal=0.9,
        margin=2,
    )

    wc.generate(segmented_text)

    img_array = wc.to_array()
    img = Image.fromarray(img_array)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()

    base64_str = base64.b64encode(img_bytes).decode("utf-8")

    return base64_str


def generate_wordcloud_custom_mask(text, mask_path, **kwargs):
    mask = np.array(Image.open(mask_path))
    kwargs["mask"] = mask
    return generate_wordcloud_base64(text, **kwargs)
