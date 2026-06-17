import base64
import requests
from wordcloud_service import (
    generate_wordcloud_base64,
    build_stopwords,
    get_builtin_mask_names,
    create_shape_mask,
    DEFAULT_STOPWORDS,
)

BASE_URL = "http://127.0.0.1:5000"
TEST_TEXT = """
这是一个停用词和形状功能的综合测试文本，用于验证停用词过滤和各种形状词云的生成效果。
我们的目标是确保停用词能够被正确过滤掉，比如的、了、和、是、在这些常见词汇。
同时验证圆形词云、心形词云、五角星词云等多种内置形状是否能够正常生成。
Python 人工智能 机器学习 深度学习 数据科学 自然语言处理 计算机视觉
云计算 大数据 物联网 区块链 Flask WordCloud API 测试
科技创新 未来发展 梦想奋斗 算法模型 训练推理
北京 上海 广州 深圳 数据 分析 可视化
"""


def test_1_stopwords_build():
    print("=" * 60)
    print("测试 1: 停用词构建")
    print("=" * 60)

    print(f"默认停用词数量: {len(DEFAULT_STOPWORDS)}")
    print(f"包含中文停用词 '的': {'的' in DEFAULT_STOPWORDS}")
    print(f"包含英文停用词 'the': {'the' in DEFAULT_STOPWORDS}")

    sw_custom_only = build_stopwords(["hello", "世界"], use_default=False)
    print(f"仅自定义停用词数量: {len(sw_custom_only)} -> {sw_custom_only}")

    sw_combined = build_stopwords(["新增词1", "新增词2"], use_default=True)
    print(f"默认+自定义停用词数量: {len(sw_combined)}")

    print("[OK] 停用词构建测试通过\n")


def test_2_shape_masks():
    print("=" * 60)
    print("测试 2: 内置形状蒙版生成")
    print("=" * 60)

    shapes = get_builtin_mask_names()
    print(f"可用形状: {shapes}")

    for shape in shapes:
        mask = create_shape_mask(shape, 600, 600)
        assert mask is not None
        assert mask.shape == (600, 600)
        assert mask.min() == 0
        assert mask.max() == 255
        filled_pct = (mask > 0).sum() / mask.size * 100
        print(f"  {shape}: 形状={mask.shape}, 填充占比={filled_pct:.1f}%")

    print("[OK] 形状蒙版生成测试通过\n")


def test_3_wordcloud_with_stopwords():
    print("=" * 60)
    print("测试 3: 带停用词的词云生成（核心模块）")
    print("=" * 60)

    print("3a) 使用默认停用词")
    b64 = generate_wordcloud_base64(
        text=TEST_TEXT,
        width=600,
        height=400,
        max_words=100,
        colormap="plasma",
        use_default_stopwords=True,
    )
    img_bytes = base64.b64decode(b64)
    with open("shape_default_stopwords.png", "wb") as f:
        f.write(img_bytes)
    print(f"  已保存: shape_default_stopwords.png ({len(img_bytes)} 字节)")

    print("3b) 关闭默认停用词")
    b64 = generate_wordcloud_base64(
        text=TEST_TEXT,
        width=600,
        height=400,
        max_words=100,
        colormap="viridis",
        use_default_stopwords=False,
    )
    img_bytes = base64.b64decode(b64)
    with open("shape_no_stopwords.png", "wb") as f:
        f.write(img_bytes)
    print(f"  已保存: shape_no_stopwords.png ({len(img_bytes)} 字节)")

    print("3c) 自定义停用词")
    b64 = generate_wordcloud_base64(
        text=TEST_TEXT,
        width=600,
        height=400,
        max_words=100,
        colormap="cool",
        stopwords=["人工智能", "Python", "测试", "验证", "确保"],
        use_default_stopwords=True,
    )
    img_bytes = base64.b64decode(b64)
    with open("shape_custom_stopwords.png", "wb") as f:
        f.write(img_bytes)
    print(f"  已保存: shape_custom_stopwords.png ({len(img_bytes)} 字节)")

    print("[OK] 停用词词云生成测试通过\n")


def test_4_wordcloud_shapes():
    print("=" * 60)
    print("测试 4: 各种形状词云生成")
    print("=" * 60)

    shapes = get_builtin_mask_names()
    colormaps = ["Reds", "Blues", "YlOrBr"]

    for shape, cmap in zip(shapes, colormaps):
        print(f"  生成 {shape} 形状词云...")
        b64 = generate_wordcloud_base64(
            text=TEST_TEXT,
            width=800,
            height=800,
            background_color="white",
            max_words=150,
            colormap=cmap,
            shape=shape,
            use_default_stopwords=True,
        )
        img_bytes = base64.b64decode(b64)
        filename = f"shape_{shape}.png"
        with open(filename, "wb") as f:
            f.write(img_bytes)
        print(f"    已保存: {filename} ({len(img_bytes)} 字节)")

    print("[OK] 形状词云生成测试通过\n")


def test_5_api_shapes_endpoint():
    print("=" * 60)
    print("测试 5: API /api/shapes 接口")
    print("=" * 60)

    r = requests.get(f"{BASE_URL}/api/shapes")
    assert r.status_code == 200
    data = r.json()
    print(f"响应: {data}")
    assert "shapes" in data
    assert isinstance(data["shapes"], list)
    assert len(data["shapes"]) >= 3
    print("[OK] /api/shapes 接口测试通过\n")


def test_6_api_wordcloud_with_features():
    print("=" * 60)
    print("测试 6: API /api/wordcloud 带形状和停用词")
    print("=" * 60)

    payloads = [
        {
            "name": "心形词云+自定义停用词",
            "text": TEST_TEXT,
            "shape": "heart",
            "width": 600,
            "height": 600,
            "background_color": "#ffcccc",
            "colormap": "Reds",
            "stopwords": ["测试", "验证", "确保", "功能"],
            "use_default_stopwords": True,
        },
        {
            "name": "圆形词云",
            "text": TEST_TEXT,
            "shape": "circle",
            "width": 600,
            "height": 600,
            "background_color": "white",
            "colormap": "Blues",
            "use_default_stopwords": True,
        },
        {
            "name": "五角星词云（无默认停用词）",
            "text": TEST_TEXT,
            "shape": "star",
            "width": 600,
            "height": 600,
            "background_color": "#fff8e1",
            "colormap": "YlOrBr",
            "use_default_stopwords": False,
        },
    ]

    for p in payloads:
        name = p.pop("name")
        print(f"  {name}...")
        r = requests.post(f"{BASE_URL}/api/wordcloud", json=p, timeout=60)
        assert r.status_code == 200, f"失败: {r.text}"
        data = r.json()
        assert data["success"] is True
        assert "image_base64" in data
        assert "data_uri" in data
        assert data["meta"]["shape"] == p["shape"]

        img_bytes = base64.b64decode(data["image_base64"])
        safe_name = name.replace("+", "_").replace("（", "_").replace("）", "")
        filename = f"api_{safe_name}.png"
        with open(filename, "wb") as f:
            f.write(img_bytes)
        print(f"    已保存: {filename} ({len(img_bytes)} 字节)")

    print("[OK] API 词云功能测试通过\n")


def test_7_api_validation():
    print("=" * 60)
    print("测试 7: API 参数校验")
    print("=" * 60)

    tests = [
        ({"text": "test", "stopwords": "not_a_list"}, 400, "stopwords must be a list"),
        ({"text": "test", "shape": "invalid_shape_xyz"}, 400, "Unknown shape"),
        ({"text": "test", "use_default_stopwords": "yes"}, 400, "must be boolean"),
        ({"text": "test", "width": 50}, 400, "width must be between"),
        ({"text": "test", "height": 9999}, 400, "height must be between"),
    ]

    for payload, expected_status, expected_err in tests:
        r = requests.post(f"{BASE_URL}/api/wordcloud", json=payload)
        assert r.status_code == expected_status, f"期望 {expected_status}, 实际 {r.status_code}: {r.text}"
        assert expected_err in r.json()["error"], f"期望错误包含 '{expected_err}': {r.json()}"
        print(f"  {expected_status} {expected_err}: OK")

    print("[OK] API 参数校验测试通过\n")


if __name__ == "__main__":
    print("\n" + "#" * 60)
    print("# 停用词与形状功能综合测试")
    print("#" * 60 + "\n")

    try:
        test_1_stopwords_build()
        test_2_shape_masks()
        test_3_wordcloud_with_stopwords()
        test_4_wordcloud_shapes()

        print(">>> 启动 Flask 服务后运行 API 测试...")
        try:
            requests.get(f"{BASE_URL}/health", timeout=3)
            service_ok = True
        except Exception:
            service_ok = False
            print("  未检测到 Flask 服务，跳过 API 测试")

        if service_ok:
            test_5_api_shapes_endpoint()
            test_6_api_wordcloud_with_features()
            test_7_api_validation()

        print("\n" + "=" * 60)
        print("[ALL OK] 停用词与形状功能测试全部通过!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
