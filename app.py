import os
import tempfile
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

from services.pdf_parser import extract_text
from services.summarizer import (
    DEFAULT_GOAL,
    DEFAULT_SCENARIO,
    GOAL_OPTIONS,
    SCENARIO_OPTIONS,
    resolve_summary_mode,
    summarize_text,
)


load_dotenv()


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20MB limit


ALLOWED_EXTENSIONS = {"pdf"}


def _is_pdf(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        goal_options=GOAL_OPTIONS,
        scenario_options=SCENARIO_OPTIONS,
        default_goal=DEFAULT_GOAL,
        default_scenario=DEFAULT_SCENARIO,
    )


@app.route("/api/summarize", methods=["POST"])
def summarize():
    upload = request.files.get("file")
    goal = request.form.get("goal", DEFAULT_GOAL)
    scenario = request.form.get("scenario", DEFAULT_SCENARIO)
    if upload is None:
        return jsonify(ok=False, error="请上传 PDF 文件"), 400

    if not upload.filename:
        return jsonify(ok=False, error="文件名为空，请重新选择文件"), 400

    if not _is_pdf(upload.filename):
        return jsonify(ok=False, error="仅支持 PDF 文件"), 400

    # On Windows, NamedTemporaryFile keeps the file handle open and blocks upload.save().
    fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    try:
        upload.save(tmp_path)
        try:
            text = extract_text(tmp_path, max_pages=30)
        except Exception as exc:
            return jsonify(ok=False, error=f"解析失败：{exc}"), 500
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    if not text.strip():
        return jsonify(ok=False, error="未能提取到文本内容，可能是扫描件或空白文件"), 400

    goal_option, scenario_option = resolve_summary_mode(goal, scenario)

    try:
        summary = summarize_text(
            text,
            goal=goal_option["value"],
            scenario=scenario_option["value"],
        )
    except RuntimeError as exc:
        return jsonify(ok=False, error=str(exc)), 400
    except Exception as exc:
        return jsonify(ok=False, error=f"生成总结失败：{exc}"), 500

    return jsonify(
        ok=True,
        summary=summary,
        goal=goal_option["value"],
        goal_label=goal_option["label"],
        scenario=scenario_option["value"],
        scenario_label=scenario_option["label"],
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
