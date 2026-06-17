import time
import base64
import requests
import subprocess
import sys


BASE_URL = "http://127.0.0.1:5000"


def test_health():
    print("测试健康检查接口...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print(f"[OK] 健康检查通过: {data}")
        return True
    except Exception as e:
        print(f"[FAIL] 健康检查失败: {e}")
        return False


def test_wordcloud_api():
    print("\n测试词云生成 API...")

    payload = {
        "text": """
        Python Flask WordCloud 服务 API 测试
        人工智能 机器学习 深度学习 数据科学
        数据分析 可视化 云计算 大数据 物联网
        编程 开发 测试 部署 运维 安全
        算法 数据结构 网络 数据库 缓存
        前端 后端 全栈 微服务 容器化
        """,
        "width": 600,
        "height": 400,
        "background_color": "#f0f0f0",
        "max_words": 50,
        "colormap": "cool",
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/wordcloud",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        assert response.status_code == 200, f"状态码错误: {response.status_code}, {response.text}"

        data = response.json()
        assert data["success"] is True
        assert "image_base64" in data
        assert data["image_format"] == "PNG"
        assert data["mime_type"] == "image/png"
        assert data["data_uri"].startswith("data:image/png;base64,")

        base64_str = data["image_base64"]
        img_bytes = base64.b64decode(base64_str)
        assert img_bytes[:8] == b"\x89PNG\r\n\x1a\n"

        print(f"[OK] API 调用成功")
        print(f"  - 图片大小: {len(img_bytes)} 字节")
        print(f"  - Base64 长度: {len(base64_str)} 字符")
        print(f"  - Data URI: {data['data_uri'][:60]}...")

        with open("test_output.png", "wb") as f:
            f.write(img_bytes)
        print(f"  - 图片已保存到 test_output.png")

        return True

    except Exception as e:
        print(f"[FAIL] API 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wordcloud_api_chinese():
    print("\n测试中文词云生成 API...")

    payload = {
        "text": """
        中华人民共和国成立于1949年，是一个拥有五千年文明历史的伟大国家。
        北京是首都，上海是经济中心，广州、深圳是改革开放的前沿。
        科技创新是国家发展的核心驱动力，人工智能、量子计算、航天技术取得重大突破。
        绿水青山就是金山银山，生态文明建设取得显著成效。
        一带一路倡议促进了全球合作与共同发展。
        高铁、移动支付、共享单车、网购被誉为新四大发明。
        传统文化焕发新生，京剧、书法、国画、武术走向世界。
        教育、医疗、养老等民生事业不断改善，人民幸福感显著提升。
        """,
        "width": 800,
        "height": 600,
        "background_color": "white",
        "max_words": 80,
        "colormap": "Set2",
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/wordcloud",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True

        base64_str = data["image_base64"]
        img_bytes = base64.b64decode(base64_str)
        assert img_bytes[:8] == b"\x89PNG\r\n\x1a\n"

        print(f"[OK] 中文词云 API 调用成功")
        print(f"  - 图片大小: {len(img_bytes)} 字节")
        print(f"  - Base64 长度: {len(base64_str)} 字符")

        with open("test_output_chinese.png", "wb") as f:
            f.write(img_bytes)
        print(f"  - 图片已保存到 test_output_chinese.png")

        return True

    except Exception as e:
        print(f"[FAIL] 中文词云 API 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wordcloud_api_validation():
    print("\n测试 API 参数验证...")

    test_cases = [
        ({}, 400, "Missing required field: text"),
        ({"text": ""}, 400, "Field 'text' must be a non-empty string"),
        ({"text": "   "}, 400, "Field 'text' must be a non-empty string"),
        ({"text": 123}, 400, "Field 'text' must be a non-empty string"),
        ({"text": "test", "width": "invalid"}, 400, "Invalid numeric parameter"),
    ]

    all_passed = True
    for payload, expected_status, expected_error in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/wordcloud",
                json=payload,
                timeout=10,
            )
            assert response.status_code == expected_status
            data = response.json()
            assert "error" in data
            assert expected_error in data["error"]
            print(f"[OK] 验证通过: {payload} -> {expected_status}")
        except Exception as e:
            print(f"[FAIL] 验证失败: {payload} -> {e}")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    print("=" * 60)
    print("Flask API 服务测试")
    print("=" * 60)

    max_retries = 10
    retry_delay = 2

    for i in range(max_retries):
        if test_health():
            break
        if i < max_retries - 1:
            print(f"等待服务启动... ({i+1}/{max_retries})")
            time.sleep(retry_delay)
    else:
        print("\n[ERROR] 无法连接到服务，请确保 Flask 服务已启动")
        print("运行: python app.py")
        sys.exit(1)

    results = []
    results.append(test_wordcloud_api())
    results.append(test_wordcloud_api_chinese())
    results.append(test_wordcloud_api_validation())

    print("\n" + "=" * 60)
    if all(results):
        print("[ALL OK] 所有 API 测试通过!")
    else:
        print(f"[SUMMARY] 通过 {sum(results)}/{len(results)} 测试")
        sys.exit(1)
    print("=" * 60)
