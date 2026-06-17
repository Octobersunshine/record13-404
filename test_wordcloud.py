import base64
from wordcloud_service import generate_wordcloud_base64, segment_text


def test_segment_text():
    text = "人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。"
    result = segment_text(text)
    print("分词结果:", result)
    assert "人工智能" in result
    assert "计算机科学" in result
    print("[OK] 分词测试通过")


def test_generate_wordcloud_base64():
    text = """
    Python 是一种广泛使用的高级编程语言，由 Guido van Rossum 于 1991 年首次发布。
    Python 的设计哲学强调代码的可读性，使用显著的缩进。
    它的语言结构以及面向对象的方法，旨在帮助程序员为小型和大型项目编写清晰的、合乎逻辑的代码。
    Python 支持多种编程范式，包括结构化、面向对象和函数式编程。
    它通常被描述为"包含一切功能"的语言，因为它的标准库非常全面。
    数据科学 机器学习 人工智能 网络开发 自动化 脚本 数据分析 可视化
    Flask Django NumPy Pandas Matplotlib TensorFlow PyTorch Scikit-learn
    """

    base64_str = generate_wordcloud_base64(
        text=text,
        width=400,
        height=300,
        background_color="white",
        max_words=50,
        colormap="plasma",
    )

    assert isinstance(base64_str, str)
    assert len(base64_str) > 0

    try:
        img_bytes = base64.b64decode(base64_str)
        assert img_bytes[:8] == b"\x89PNG\r\n\x1a\n"
        print("[OK] Base64 编码验证通过，是有效的 PNG 图片")
    except Exception as e:
        raise AssertionError(f"Base64 解码失败: {e}")

    print(f"[OK] 词云生成成功，Base64 长度: {len(base64_str)} 字符")

    data_uri = f"data:image/png;base64,{base64_str}"
    print(f"Data URI 前缀: {data_uri[:50]}...")

    return base64_str


def test_generate_wordcloud_chinese():
    text = """
    中国是世界上最古老的文明之一，有着五千年的悠久历史。
    长城是中国古代的军事防御工程，是世界文化遗产之一。
    故宫是中国明清两代的皇家宫殿，位于北京中轴线的中心。
    黄河和长江是中国最长的两条河流，孕育了灿烂的中华文明。
    四大发明：造纸术、指南针、火药、印刷术，对世界文明产生了深远影响。
    孔子、孟子、老子、庄子等思想家的智慧至今仍影响着中国人。
    唐诗宋词元曲明清小说，构成了中国文学的璀璨星河。
    北京 上海 广州 深圳 杭州 成都 西安 南京 苏州 武汉
    科技 创新 发展 文化 历史 传统 现代 未来 梦想 奋斗
    """

    base64_str = generate_wordcloud_base64(
        text=text,
        width=600,
        height=400,
        background_color="black",
        max_words=100,
        colormap="rainbow",
    )

    assert isinstance(base64_str, str)
    assert len(base64_str) > 0

    img_bytes = base64.b64decode(base64_str)
    assert img_bytes[:8] == b"\x89PNG\r\n\x1a\n"

    print(f"[OK] 中文词云生成成功，Base64 长度: {len(base64_str)} 字符")
    return base64_str


if __name__ == "__main__":
    print("=" * 60)
    print("词云生成服务测试")
    print("=" * 60)

    try:
        test_segment_text()
        print()
        test_generate_wordcloud_base64()
        print()
        test_generate_wordcloud_chinese()
        print()
        print("=" * 60)
        print("[ALL OK] 所有测试通过!")
        print("=" * 60)
    except AssertionError as e:
        print(f"[FAIL] 测试失败: {e}")
        exit(1)
    except Exception as e:
        print(f"[ERROR] 发生异常: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
