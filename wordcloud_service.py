import io
import os
import sys
import glob
import base64
import logging
import jieba
import numpy as np
from wordcloud import WordCloud
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _find_fonts_matplotlib():
    try:
        from matplotlib import font_manager

        font_names = [
            "Microsoft YaHei",
            "微软雅黑",
            "SimHei",
            "黑体",
            "SimSun",
            "宋体",
            "KaiTi",
            "楷体",
            "MingLiU",
            "细明体",
            "PingFang SC",
            "PingFang HK",
            "PingFang TC",
            "Hiragino Sans GB",
            "Heiti SC",
            "Heiti TC",
            "STHeiti",
            "WenQuanYi Micro Hei",
            "WenQuanYi Zen Hei",
            "Noto Sans CJK SC",
            "Noto Sans CJK TC",
            "Noto Sans CJK JP",
            "Noto Serif CJK SC",
            "Droid Sans Fallback",
            "Source Han Sans SC",
            "Source Han Sans CN",
            "Source Han Serif SC",
            "AR PL UMing CN",
            "AR PL UKai CN",
        ]

        font_names_lower = {name.lower(): name for name in font_names}

        for font in font_manager.fontManager.ttflist:
            fname = os.path.basename(font.fname)
            if fname.lower() in font_names_lower:
                logger.info(f"通过 matplotlib 找到字体: {font.fname} ({font.name})")
                return font.fname

        for font in font_manager.fontManager.ttflist:
            if any(
                keyword in font.name.lower()
                for keyword in [
                    "yahei",
                    "hei",
                    "song",
                    "kaiti",
                    "cjk",
                    "chinese",
                    "ming",
                    "simsun",
                    "simhei",
                    "msyh",
                    "pingfang",
                    "wqy",
                    "wenquanyi",
                    "noto sans cjk",
                    "droid sans fallback",
                    "source han",
                ]
            ):
                logger.info(f"通过 matplotlib 关键词匹配找到字体: {font.fname} ({font.name})")
                return font.fname

    except Exception as e:
        logger.warning(f"matplotlib 字体查找失败: {e}")

    return None


def _find_fonts_system():
    font_candidates = []

    if sys.platform.startswith("win"):
        windir = os.environ.get("WINDIR", "C:\\Windows")
        font_dir = os.path.join(windir, "Fonts")
        font_candidates = [
            os.path.join(font_dir, "msyh.ttc"),
            os.path.join(font_dir, "msyh.ttf"),
            os.path.join(font_dir, "msyhbd.ttc"),
            os.path.join(font_dir, "msyhl.ttc"),
            os.path.join(font_dir, "simhei.ttf"),
            os.path.join(font_dir, "simsun.ttc"),
            os.path.join(font_dir, "simsunb.ttf"),
            os.path.join(font_dir, "simkai.ttf"),
            os.path.join(font_dir, "simli.ttf"),
            os.path.join(font_dir, "simfang.ttf"),
            os.path.join(font_dir, "STXIHEI.TTF"),
            os.path.join(font_dir, "STKAITI.TTF"),
            os.path.join(font_dir, "STSONG.TTF"),
            os.path.join(font_dir, "STFANGSO.TTF"),
            os.path.join(font_dir, "STZHONGS.TTF"),
            os.path.join(font_dir, "STXINGKA.TTF"),
            os.path.join(font_dir, "STHUPO.TTF"),
            os.path.join(font_dir, "STXINWEI.TTF"),
        ]

        localappdata = os.environ.get("LOCALAPPDATA")
        if localappdata:
            local_font_dir = os.path.join(localappdata, "Microsoft", "Windows", "Fonts")
            if os.path.isdir(local_font_dir):
                for ext in ["*.ttf", "*.ttc", "*.otf"]:
                    font_candidates.extend(glob.glob(os.path.join(local_font_dir, ext)))

    elif sys.platform.startswith("darwin"):
        font_candidates = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/PingFang.ttc:0",
            "/Library/Fonts/Songti.ttc",
            "/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
            "/Library/Fonts/华文细黑.ttf",
            "/Library/Fonts/华文黑体.ttf",
            "/Library/Fonts/华文楷体.ttf",
            "/Library/Fonts/华文宋体.ttf",
            "/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
        ]
    else:
        font_dirs = [
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            os.path.expanduser("~/.fonts"),
            os.path.expanduser("~/.local/share/fonts"),
        ]

        for d in font_dirs:
            if os.path.isdir(d):
                for root, _, files in os.walk(d):
                    for f in files:
                        if f.lower().endswith((".ttf", ".ttc", ".otf")):
                            font_candidates.append(os.path.join(root, f))

    for font_path in font_candidates:
        if os.path.exists(font_path):
            logger.info(f"通过系统路径找到字体: {font_path}")
            return font_path

    return None


def _validate_font(font_path):
    if not font_path or not os.path.exists(font_path):
        return False

    try:
        from PIL import ImageFont

        try:
            font = ImageFont.truetype(font_path, 12)
            test_str = "中文测试"
            try:
                font.getbbox(test_str)
            except AttributeError:
                font.getsize(test_str)
            return True
        except Exception:
            pass
    except Exception:
        pass

    return True


def detect_chinese_font():
    logger.info("开始搜索中文字体...")

    font_path = _find_fonts_matplotlib()
    if font_path and _validate_font(font_path):
        logger.info(f"使用字体(matplotlib): {font_path}")
        return font_path

    font_path = _find_fonts_system()
    if font_path and _validate_font(font_path):
        logger.info(f"使用字体(系统路径): {font_path}")
        return font_path

    logger.warning("未找到可用的中文字体，中文可能显示为方框")
    return None


DEFAULT_FONT_PATH = detect_chinese_font()


def segment_text(text):
    seg_list = jieba.cut(text, cut_all=False)
    return " ".join(seg_list)


def contains_chinese(text):
    if not text:
        return False
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
    has_chinese = contains_chinese(text)

    if font_path is None and has_chinese:
        if DEFAULT_FONT_PATH:
            font_path = DEFAULT_FONT_PATH
            logger.info(f"自动应用中文字体: {font_path}")
        else:
            logger.warning("文本包含中文，但未找到中文字体，中文可能显示异常")

    segmented_text = segment_text(text)

    wc_params = {
        "width": width,
        "height": height,
        "background_color": background_color,
        "max_words": max_words,
        "prefer_horizontal": 0.9,
        "margin": 2,
    }

    if font_path:
        wc_params["font_path"] = font_path
    if max_font_size:
        wc_params["max_font_size"] = max_font_size
    if colormap:
        wc_params["colormap"] = colormap

    wc = WordCloud(**wc_params)
    wc.generate(segmented_text)

    img_array = wc.to_array()
    img = Image.fromarray(img_array)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()

    base64_str = base64.b64encode(img_bytes).decode("utf-8")

    logger.info(f"词云生成完成，图片大小: {len(img_bytes)} 字节")

    return base64_str


def generate_wordcloud_custom_mask(text, mask_path, **kwargs):
    mask = np.array(Image.open(mask_path))
    kwargs["mask"] = mask
    return generate_wordcloud_base64(text, **kwargs)
