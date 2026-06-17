from flask import Flask, request, jsonify
from flask_cors import CORS
from wordcloud_service import generate_wordcloud_base64, get_builtin_mask_names

app = Flask(__name__)
CORS(app)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "WordCloud service is running"})


@app.route("/api/shapes", methods=["GET"])
def available_shapes():
    return jsonify({"shapes": get_builtin_mask_names()})


@app.route("/api/wordcloud", methods=["POST"])
def generate_wordcloud():
    try:
        data = request.get_json()

        if not data or "text" not in data:
            return jsonify({"error": "Missing required field: text"}), 400

        text = data["text"]

        if not isinstance(text, str) or len(text.strip()) == 0:
            return jsonify({"error": "Field 'text' must be a non-empty string"}), 400

        width = data.get("width", 800)
        height = data.get("height", 600)
        background_color = data.get("background_color", "white")
        font_path = data.get("font_path", None)
        max_words = data.get("max_words", 200)
        max_font_size = data.get("max_font_size", None)
        colormap = data.get("colormap", "viridis")
        stopwords = data.get("stopwords", None)
        use_default_stopwords = data.get("use_default_stopwords", True)
        shape = data.get("shape", None)

        try:
            width = int(width)
            height = int(height)
            max_words = int(max_words)
            if max_font_size is not None:
                max_font_size = int(max_font_size)
            if width < 100 or width > 4000:
                return jsonify({"error": "width must be between 100 and 4000"}), 400
            if height < 100 or height > 4000:
                return jsonify({"error": "height must be between 100 and 4000"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid numeric parameter"}), 400

        if stopwords is not None and not isinstance(stopwords, list):
            return jsonify({"error": "stopwords must be a list of strings"}), 400

        if shape is not None:
            available = get_builtin_mask_names()
            if shape.lower() not in available:
                return jsonify({
                    "error": f"Unknown shape '{shape}'. Available shapes: {', '.join(available)}"
                }), 400

        if not isinstance(use_default_stopwords, bool):
            return jsonify({"error": "use_default_stopwords must be boolean"}), 400

        base64_image = generate_wordcloud_base64(
            text=text,
            width=width,
            height=height,
            background_color=background_color,
            font_path=font_path,
            max_words=max_words,
            max_font_size=max_font_size,
            colormap=colormap,
            stopwords=stopwords,
            use_default_stopwords=use_default_stopwords,
            shape=shape,
        )

        return jsonify(
            {
                "success": True,
                "image_base64": base64_image,
                "image_format": "PNG",
                "mime_type": "image/png",
                "data_uri": f"data:image/png;base64,{base64_image}",
                "meta": {
                    "shape": shape,
                    "stopwords_count": len(stopwords) if stopwords else 0,
                    "use_default_stopwords": use_default_stopwords,
                },
            }
        )

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
