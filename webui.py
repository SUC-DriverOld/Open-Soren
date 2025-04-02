import os
import sys
import time
import locale
import gradio as gr
import tkinter as tk
from tkinter import filedialog
from mastering import Config, master_audio
from generate_profile import create_genre_profile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILES_DIR = os.path.join(SCRIPT_DIR, "profiles")
CUSTOM_DIR = os.path.join(SCRIPT_DIR, "custom")

class I18nAuto:
    def __init__(self, language):
        if language == "Auto":
            language = locale.getdefaultlocale()[0]
        self.language_map = self.load_language_dict(language)

    def load_language_dict(self, language):
        all = {
            "zh_CN": {
                "Please select a folder first!": "请先选择一个文件夹！",
                "Please upload an audio file": "请上传一个音频文件",
                "Either genre or reference file must be specified": "必须指定音乐风格或参考文件",
                "Processing...": "处理中...",
                "Processing completed in ": "处理完成，耗时",
                " seconds.": "秒",
                "Processing failed: ": "处理失败：",
                "Generating profile...": "生成配置文件中...",
                "Profile generated in ": "配置文件生成完成，耗时",
                "Music Genre": "音乐风格",
                "Profile generation failed: ": "配置文件生成失败：",
                "Open Soren is an auto mastering tool cracked from [Rast Sound Soren](https://rastsound.com/downloads/soren/) v1.1.0. It's only for personal learning and communication purposes.": "Open Soren 是一个自动母带处理工具，破解自 [Rast Sound Soren](https://rastsound.com/downloads/soren/) v1.1.0，仅供个人学习和交流使用。",
                "Auto Mastering": "自动母带处理",
                "Input Audio": "输入音频",
                "Upload reference audio or select music genre, choose one, priority should be given to using reference audio": "上传参考音频或选择音乐风格，二选一，优先使用参考音频",
                "Reference Audio": "参考音频",
                "Loudness": "响度",
                "EQ Profile": "EQ 配置",
                "Output Format": "输出格式",
                "Preview: Process only 30 seconds of the audio file": "预览模式：仅处理音频文件的 30 秒",
                "Output Folder": "输出文件夹",
                "Select Folder": "选择文件夹",
                "Open Folder": "打开文件夹",
                "Run Process": "开始处理",
                "Output Message": "输出信息",
                "Generate Custom Profile": "生成自定义配置文件",
                "Genre Name": "风格名称",
                "Generate": "生成",
                "Open Custom Folder": "打开自定义配置文件夹"
            }
        }
        return all.get(language, {})

    def __call__(self, key):
        return self.language_map.get(key, key)

i18n = I18nAuto("Auto")

def select_folder():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    selected_dir = filedialog.askdirectory()
    root.destroy()
    return selected_dir

def open_folder(folder):
    if folder == "":
        raise gr.Error(i18n("Please select a folder first!"))
    os.makedirs(folder, exist_ok=True)
    absolute_path = os.path.abspath(folder)
    if sys.platform == "win32":
        os.system(f"explorer {absolute_path}")
    elif sys.platform == "darwin":
        os.system(f"open {absolute_path}")
    elif sys.platform == "linux":
        os.system(f"xdg-open {absolute_path}")

def get_genre_choices():
    all_genres = [g.replace(".json", "") for g in os.listdir(PROFILES_DIR) if g.endswith(".json")]
    if os.path.exists(CUSTOM_DIR):
        all_genres += [f for f in os.listdir(CUSTOM_DIR) if os.path.isdir(os.path.join(CUSTOM_DIR, f))]
    return all_genres

def process_audio(input_audio, reference_audio, style, loudness, eq_profile, output_format, is_preview, output_folder):
    if not input_audio:
        raise gr.Error(i18n("Please upload an audio file"))
    config = Config()
    config.loudness_option = loudness
    if reference_audio and os.path.exists(reference_audio):
        config.reference_file = reference_audio
        print(f"Using custom reference file: {config.reference_file}")
    elif style:
        config.genre = style
        print(f"Using genre profile: {config.genre}")
    else:
        raise gr.Error(i18n("Either genre or reference file must be specified"))
    os.makedirs(output_folder, exist_ok=True)
    extension = os.path.splitext(os.path.basename(input_audio))[-1]
    base_name = os.path.basename(input_audio).replace(extension, "")
    preview = "_preview" if is_preview else ""
    output_file = os.path.join(output_folder, f"{base_name}_mastered_{config.genre}_{config.loudness_option}_{eq_profile}{preview}.{output_format}")
    try:
        start_time = time.time()
        yield i18n("Processing...")
        master_audio(input_audio, output_file, config, eq_profile, is_preview)
        message = i18n("Processing completed in ") + f"{time.time() - start_time:.2f}" + i18n(" seconds.")
        yield message
    except Exception as e:
        message = i18n("Processing failed: ") + str(e)
        yield message

def generate_profile(input_audio, genre_name):
    config = Config()
    try:
        start_time = time.time()
        yield i18n("Generating profile..."), None
        create_genre_profile(input_audio, genre_name, config)
        message = i18n("Profile generated in ") + f"{time.time() - start_time:.2f}" + i18n(" seconds.")
        style = gr.Dropdown(label=i18n("Music Genre"), choices=get_genre_choices(), value=get_genre_choices()[0], interactive=True)
        yield message, style
    except Exception as e:
        message = i18n("Profile generation failed: ") + str(e)
        yield message, None

def webui():
    with gr.Blocks(title="Open Soren") as demo:
        gr.Markdown('''<div align="center"><font size=6><b>Open-Soren-WebUI 1.1.0</b></font></div>''')
        gr.Markdown(i18n("Open Soren is an auto mastering tool from [Rast Sound Soren](https://rastsound.com/downloads/soren/) v1.1.0. It's only for personal learning and communication purposes."))
        with gr.Tabs():
            with gr.TabItem(label=i18n("Auto Mastering")):
                with gr.Row():
                    with gr.Column():
                        with gr.Group():
                            input_audio_1 = gr.File(label=i18n("Input Audio"), type="filepath")
                            gr.Markdown(i18n("Upload reference audio or select music genre, choose one, priority should be given to using reference audio"))
                            reference_audio = gr.File(label=i18n("Reference Audio"), type="filepath")
                            style = gr.Dropdown(label=i18n("Music Genre"), choices=get_genre_choices(), value=get_genre_choices()[0], interactive=True)
                            loudness = gr.Radio(label=i18n("Loudness"), choices=['soft', 'dynamic', 'normal', 'loud'], value="normal", interactive=True)
                            eq_profile = gr.Radio(label=i18n("EQ Profile"), choices=["Neutral", "Warm", "Bright", "Fusion"], value="Neutral", interactive=True)
                    with gr.Column():
                        with gr.Group():
                            output_format = gr.Radio(label=i18n("Output Format"), choices=["wav", "flac", "mp3"], value="wav", interactive=True)
                            is_preview = gr.Checkbox(label=i18n("Preview: Process only 30 seconds of the audio file"), value=False, interactive=True)
                            output_folder = gr.Textbox(label=i18n("Output Folder"), value="results", interactive=True)
                            with gr.Row():
                                select_folder_btn = gr.Button(i18n("Select Folder"))
                                open_folder_btn = gr.Button(i18n("Open Folder"))
                        run_process_btn = gr.Button(value=i18n("Run Process"), variant="primary")
                        message_1 = gr.Textbox(label=i18n("Output Message"), interactive=False)
            with gr.TabItem(label=i18n("Generate Custom Profile")):
                with gr.Row():
                    with gr.Column():
                        with gr.Group():
                            input_audio_2 = gr.File(label=i18n("Input Audio"), type="filepath")
                            genre_name = gr.Textbox(label=i18n("Genre Name"), value="CustomProfile", interactive=True)
                    with gr.Column():
                        generate_btn = gr.Button(value=i18n("Generate"), variant="primary")
                        with gr.Group():
                            message_2 = gr.Textbox(label=i18n("Output Message"), interactive=False)
                            open_custom_folder_btn = gr.Button(i18n("Open Custom Folder"))

        select_folder_btn.click(fn=select_folder, inputs=[], outputs=output_folder)
        open_folder_btn.click(fn=open_folder, inputs=output_folder, outputs=[])
        run_process_btn.click(fn=process_audio, inputs=[input_audio_1, reference_audio, style, loudness, eq_profile, output_format, is_preview, output_folder], outputs=message_1)
        generate_btn.click(fn=generate_profile, inputs=[input_audio_2, genre_name], outputs=[message_2, style])
        open_custom_folder_btn.click(fn=open_folder, inputs=gr.Textbox(value=CUSTOM_DIR, visible=False), outputs=[])

    return demo

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Open Soren WebUI")
    parser.add_argument("-i", "--ip_address", type=str, default=None, help="Server IP address")
    parser.add_argument("-p", "--port", type=int, default=None, help="Server port")
    parser.add_argument("-s", "--share", action="store_true", default=False, help="Open share link")
    args = parser.parse_args()

    webui().queue().launch(inbrowser=True, server_name=args.ip_address, server_port=args.port, share=args.share)