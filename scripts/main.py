import gradio as gr
import sys
import io
from pathlib import Path
from fastapi import FastAPI
from modules import scripts, script_callbacks, shared

import warnings

# Gradioに、Pythonの標準出力を表示するUIを追加する

stdout_captured = None  # type: io.StringIO # type: ignore
stdout_val = ""  # type: str


def init(demo: gr.Blocks, app: FastAPI) -> None:
    global stdout_captured
    global stdout_val
    stdout_captured = io.StringIO()
    stdout_val = ""
    capture_stdout()
    capture_stderr()
    get_stdout_val()


# Pythonの標準出力をキャプチャーする
def capture_stdout() -> io.StringIO:
    global stdout_captured
    print("[console log integrater] start stdout capture")
    sys.stdout = stdout_captured
    return stdout_captured


def release_stdout() -> None:
    sys.stdout = sys.__stdout__


def capture_stderr() -> io.StringIO:
    global stdout_captured
    print("[console log integrater] start stderr capture")
    sys.stderr = stdout_captured
    return stdout_captured


def release_stderr() -> None:
    sys.stderr = sys.__stderr__


def update_stdout() -> None:
    global stdout_captured
    global stdout_val
    # print("[console log integrater] sys.stdout == stdout_captured: ",sys.stdout == stdout_captured)
    # if sys.stdout != stdout_captured:
    # Warning("[console log integrater] sys.stdout != stdout_captured")
    # capture_stdout()
    # print("[console log integrater] update")

    # stdout_val = stdout_captured.getvalue()
    # offset: int = sys.__stdout__.tell()
    # stdout_captured.seek(offset, io.SEEK_SET)
    # sys.__stdout__.write(stdout_captured.read())
    # stdout_captured.seek(0, io.SEEK_END)

    stdout_val = stdout_captured.getvalue()
    sys.__stdout__.write(stdout_val)


def get_stdout_val() -> str:
    global stdout_val
    update_stdout()
    return stdout_val


def stdout2html(stdout_val: str) -> str:
    html: str = stdout_val.replace("\n", "<br>")
    # ANSI escape to HTML tags
    html = html.replace("\033", "\x1b")
    html = html.replace("\x1b[0m", "</span>")
    html = html.replace("\x1b[1m", "<span style='font-weight: bold;'>")
    html = html.replace("\x1b[2m", "<span style='font-weight: lighter;'>")
    html = html.replace("\x1b[3m", "<span style='font-style: italic;'>")
    html = html.replace("\x1b[4m", "<span style='text-decoration: underline;'>")
    html = html.replace("\x1b[5m", "<span style='text-decoration: blink;'>")
    html = html.replace("\x1b[7m", "<span style='text-decoration: overline;'>")
    html = html.replace("\x1b[8m", "<span style='text-decoration: line-through;'>")
    html = html.replace("\x1b[30m", "<span style='color: black;'>")
    html = html.replace("\x1b[31m", "<span style='color: red;'>")
    html = html.replace("\x1b[32m", "<span style='color: green;'>")
    html = html.replace("\x1b[33m", "<span style='color: yellow;'>")
    html = html.replace("\x1b[34m", "<span style='color: blue;'>")
    html = html.replace("\x1b[35m", "<span style='color: magenta;'>")
    html = html.replace("\x1b[36m", "<span style='color: cyan;'>")
    html = html.replace("\x1b[37m", "<span style='color: white;'>")
    html = html.replace("\x1b[40m", "<span style='background-color: black;'>")
    html = html.replace("\x1b[41m", "<span style='background-color: red;'>")
    html = html.replace("\x1b[42m", "<span style='background-color: green;'>")
    html = html.replace("\x1b[43m", "<span style='background-color: yellow;'>")
    html = html.replace("\x1b[44m", "<span style='background-color: blue;'>")
    html = html.replace("\x1b[45m", "<span style='background-color: magenta;'>")
    html = html.replace("\x1b[46m", "<span style='background-color: cyan;'>")
    html = html.replace("\x1b[47m", "<span style='background-color: white;'>")
    return html


def on_ui_tabs():
    def add_css(html="") -> str:
        dir_path: str = Path(__file__).resolve().parent.as_posix() + "/"
        return "<style>" + open(dir_path + "../css/style.css", "r").read() + "</style>" + html
    global stdout_val
    with gr.Blocks(analytics_enabled=False) as console_log:
        with gr.Row():
            with gr.Column(scale=9):
                with gr.Box():
                    stdout_box = gr.Textbox(stdout_val, label="Python standard output", interactive=False,
                                            lines=20, elem_id="console_log_box")
                    # with gr.Row():
                    #     with gr.Column(scale=9):
                    #         stdout_html = gr.HTML(add_css(stdout2html(stdout_val)),
                    #                               Label="Python standard output (html)",
                    #                               elem_id="console_log_box")
                    #     with gr.Column(scale=1, min_width=120):
                    #         update_btn = gr.Button("Update", variant='primary')
                    #         update_btn.click(lambda: add_css(stdout2html(stdout_val)),
                    #                          inputs=None,
                    #                          outputs=stdout_html)
            with gr.Column(scale=1, min_width=120, visible=True):
                update_btn = gr.Button("Update", variant='primary')
                update_btn.click(get_stdout_val,
                                 inputs=None,
                                 outputs=stdout_box)
                test_btn = gr.Button("Test msg")
                test_btn.click(lambda: [print("[console log integrater] test msg to stdout"), warnings.warn(Warning("[console log integrater] test msg to stderr"))],
                               inputs=None,
                               outputs=None)
            with gr.Column(visible=False) as hidden_items:
                pass

        # console_log.load(fn=hoge,
        #                  inputs=None,
        #                  outputs=stdout_box,
        #                  queue=True,
        #                  every=1)
        # console_log.queue()

    return (console_log, "Console log", "console_log"),


script_callbacks.on_app_started(init)
script_callbacks.on_ui_tabs(on_ui_tabs)
