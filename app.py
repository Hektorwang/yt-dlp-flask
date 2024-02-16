"""yt-dlp flask vue3"""

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Optional, Sequence, Union

from flask import Flask, jsonify, make_response, redirect, request
from loguru import logger
from yt_dlp import YoutubeDL

import cli_to_api

PROJECT_DIR: Path = Path(__file__).parent
CONFIG_FILE: Path = PROJECT_DIR / "config.json"
with open(CONFIG_FILE, mode="r+", encoding="utf-8") as f:
    # config: dict = json.load(f)
    config: dict[str, dict[str, Union[str, bool]]] = json.load(f)
executor = ThreadPoolExecutor(10)

app = Flask(__name__)


@app.route("/help")
def help_page():
    """Redirects to the yt-dlp documentation for help"""
    return redirect("https://github.com/yt-dlp/yt-dlp#readme")


@app.route("/api/config")
def api_config():
    return jsonify(config)


@app.route("/apply", methods=["POST"])
def apply() -> Any:
    global config
    data: dict[str, str] = request.form
    logger.debug(data)
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
    logger.debug(f'cmd line: {" ".join(cmd_line)}')
    result: dict[str, Any] = cli_to_api.cli_to_api(cmd_line[1:], True)
    # result["url"] = data.get("url")
    logger.debug(f"python opts: {result}")
    with open(PROJECT_DIR / "config.json", "w+", encoding="utf-8") as ff:
        json.dump(config, ff, ensure_ascii=False)
    executor.submit(run_ydl, result, data["url"])
    logger.info("Submit task.")
    result = {
        "code": "200",
        "message": "success",
        "data": {
            "url": data["url"],
            "ydl_opts": result,
        },
    }
    return make_response(jsonify(result))


def run_ydl(ydl_opts: dict[str, Any], url: str):
    # with YoutubeDL(ydl_opts) as ydl:
    #     info = ydl.extract_info(
    #         url,
    #         download=False,
    #     )
    # logger.info(json.dumps(ydl.sanitize_info(info), ensure_ascii=False))
    with YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(url)
        logger.info(json.dumps(ydl.sanitize_info(error_code), ensure_ascii=False))
