"""yt-dlp flask vue3"""

import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Optional, Union

import werkzeug
from flask import Flask, jsonify, redirect, request, send_from_directory, wrappers
from loguru import logger
from yt_dlp import YoutubeDL

import cli_to_api

PROJECT_DIR: Path = Path(__file__).parent
os.environ["PATH"] += PROJECT_DIR.as_posix()
CONFIG_FILE: Path = PROJECT_DIR / "config.json"
with open(CONFIG_FILE, mode="r+", encoding="utf-8") as f:
    config: dict[str, dict[str, Union[str, bool]]] = json.load(f)
task_state: dict[str, int] = {}
TASK_STATE_MAP = {
    99: "start",
    0: "success",
    255: "ydl exception",
}
executor = ThreadPoolExecutor(10)

app = Flask(__name__)


@app.route("/")
@app.route("/<path:path>")
def serve_static(path: Optional[str] = None) -> wrappers.Response:
    """Serves static files from the appropriate directory."""
    if path is None:
        path = "index.html"
    # logger.debug(path)
    return send_from_directory("static", path)


@app.route("/help")
def help_page() -> werkzeug.wrappers.response.Response:
    """Redirects to the yt-dlp documentation for help"""
    return redirect("https://github.com/yt-dlp/yt-dlp#readme")


@app.route("/api/config")
def api_config() -> wrappers.Response:
    return jsonify(config)


@app.route("/api/task_state")
def get_task_state() -> wrappers.Response:
    converted_task_state = {
        task_name: TASK_STATE_MAP.get(state, "other failed")
        for task_name, state in task_state.items()
    }
    return jsonify(converted_task_state)


@app.route("/apply", methods=["POST"])
def apply() -> wrappers.Response:
    global config, task_state
    data: dict[str, str] = request.form
    # logger.debug(data)
    cmd_line: list[str] = ["yt-dlp", "-v"]
    for data_key, data_value in data.items():
        if data_key == "url":
            pass
        elif data_value == "on":
            cmd_line.append(data_key)
        elif data_value is not None and data_value != "":
            cmd_line.append(f"{data_key}={data_value}")
            config[data_key]["value"] = data_value
        else:
            logger.warning(f"{data_key = }, {data_value = }")
    for config_key, config_value in config.items():
        if config_value.get("type") == "checkbox":
            config[config_key]["checked"] = (
                True if data.get(config_key) == "on" else False
            )
    url = data["url"].split("?")[0]
    url = data["url"]
    # task_id: str = base64.b64encode(url.encode("utf-8")).decode("utf-8")
    task_id = url
    task_state[task_id] = 99
    # logger.debug(f"{task_id = }")
    logger.debug(f'cmd line: {" ".join(cmd_line)} {url}')
    result: dict[str, Any] = cli_to_api.cli_to_api(cmd_line[1:], True)
    logger.debug(f"python opts: {result}")
    with open(PROJECT_DIR / "config.json", "w+", encoding="utf-8") as ff:
        json.dump(config, ff, ensure_ascii=False, indent=2)
    executor.submit(run_ydl, result, url, task_id)
    logger.info("Submit task.")
    return serve_static()


def run_ydl(ydl_opts: dict[str, Any], url: str, task_id: str) -> dict[str, int]:
    global task_state
    with YoutubeDL(ydl_opts) as ydl:
        try:
            task_state[task_id] = ydl.download(url)
        except Exception as task_e:
            logger.error(f"{task_id} failed: {task_e}")
            task_state[task_id] = 255
        if task_state[task_id] == 0:
            logger.success(f"task done: {task_id}")
        else:
            logger.error(f"task failed: {task_id}")
    return task_state


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
