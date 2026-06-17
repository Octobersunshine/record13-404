import base64
import os
from wordcloud_service import (
    detect_chinese_font,
    DEFAULT_FONT_PATH,
    contains_chinese,
    generate_wordcloud_base64,
    _find_fonts_matplotlib,
    _find_fonts_system,
    _validate_font,
)

print("=" * 60)
print("中文字体检测与词云效果验证")
print("=" * 60)

print("\n1. 中文字符检测测试:")
test_cases = [
    "你好世界",
    "Hello World",
    "Python 人工智能",
    "12345",
    "",
    None,
]
for tc in test_cases:
    print(f"  '{tc}' -> {contains_chinese(tc)}")

print("\n2. 字体查找方式测试:")
matplotlib_font = _find_fonts_matplotlib()
print(f"  matplotlib 查找: {matplotlib_font}")
system_font = _find_fonts_system()
print(f"  系统路径查找: {system_font}")

print(f"\n3. 默认字体: {DEFAULT_FONT_PATH}")

if DEFAULT_FONT_PATH:
    print(f"  字体文件存在: {os.path.exists(DEFAULT_FONT_PATH)}")
    print(f"  字体验证通过: {_validate_font(DEFAULT_FONT_PATH)}")

print("\n4. 生成词云测试 (含中文):")
chinese_text = """
中华人民共和国 北京 上海 广州 深圳
人工智能 机器学习 深度学习 数据科学
自然语言处理 计算机视觉 语音识别
Python Flask WordCloud 词云 图片
科技 创新 发展 未来 梦想 奋斗
数据 算法 模型 训练 推理 部署
云计算 大数据 物联网 区块链
"""

b64 = generate_wordcloud_base64(
    text=chinese_text,
    width=800,
    height=600,
    background_color="white",
    max_words=100,
    colormap="plasma",
)

print(f"  Base64 长度: {len(b64)} 字符")

img_bytes = base64.b64decode(b64)
print(f"  图片大小: {len(img_bytes)} 字节")
print(f"  PNG 头验证: {img_bytes[:8] == b'\\x89PNG\\r\\n\\x1a\\n'}")

output_path = "verify_chinese_font.png"
with open(output_path, "wb") as f:
    f.write(img_bytes)
print(f"  图片已保存: {output_path}")

print("\n5. 生成纯英文词云测试:")
english_text = """
Python Flask Django FastAPI WordCloud
Machine Learning Deep Learning AI Data Science
NLP Computer Vision Speech Recognition
Algorithm Model Training Deployment
Cloud Computing Big Data IoT Blockchain
"""

b64_en = generate_wordcloud_base64(
    text=english_text,
    width=600,
    height=400,
    background_color="#1a1a2e",
    max_words=50,
    colormap="cool",
)

img_bytes_en = base64.b64decode(b64_en)
print(f"  Base64 长度: {len(b64_en)} 字符")
print(f"  PNG 头验证: {img_bytes_en[:8] == b'\\x89PNG\\r\\n\\x1a\\n'}")
with open("verify_english_font.png", "wb") as f:
    f.write(img_bytes_en)
print(f"  图片已保存: verify_english_font.png")

print("\n6. 自定义字体路径测试:")
if DEFAULT_FONT_PATH:
    b64_custom = generate_wordcloud_base64(
        text="自定义字体 测试效果 非常好 完美显示",
        width=400,
        height=300,
        background_color="lightyellow",
        font_path=DEFAULT_FONT_PATH,
        max_words=20,
        colormap="Set2",
    )
    img_bytes_custom = base64.b64decode(b64_custom)
    print(f"  自定义字体 Base64 长度: {len(b64_custom)} 字符")
    with open("verify_custom_font.png", "wb") as f:
        f.write(img_bytes_custom)
    print(f"  图片已保存: verify_custom_font.png")
else:
    print("  未找到中文字体，跳过自定义字体测试")

print("\n" + "=" * 60)
print("[ALL DONE] 验证完成，请查看生成的 PNG 图片确认中文字体显示效果")
print("=" * 60)
