from __future__ import annotations

import tempfile
import uuid
from pathlib import Path

import gradio as gr
from PIL import Image

from radar_generator import add_avatar, draw_radar_by_anchors

# Default anchors and text positions based on current template design.
DEFAULT_ANCHORS = [
    [(770, 1210), (770, 1167), (770, 1123), (770, 1082), (770, 1040), (770, 1000), (770, 960), (770, 926), (770, 895), (770, 858), (770, 825)],
    [(770, 1210), (815, 1190), (855, 1168), (895, 1148), (935, 1126), (972, 1106), (1010, 1090), (1044, 1072), (1078, 1054), (1112, 1036), (1145, 1020)],
    [(770, 1210), (815, 1236), (855, 1260), (895, 1280), (935, 1298), (972, 1318), (1010, 1336), (1044, 1355), (1078, 1375), (1112, 1390), (1145, 1408)],
    [(770, 1210), (770, 1258), (770, 1305), (770, 1340), (770, 1385), (770, 1426), (770, 1460), (770, 1498), (770, 1530), (770, 1570), (770, 1602)],
    [(770, 1210), (728, 1236), (683, 1260), (645, 1280), (606, 1298), (570, 1318), (532, 1336), (500, 1355), (465, 1375), (430, 1390), (395, 1408)],
    [(770, 1210), (728, 1190), (686, 1168), (645, 1148), (606, 1128), (570, 1110), (532, 1090), (500, 1072), (465, 1054), (430, 1036), (395, 1020)],
]

DEFAULT_LABEL_POSITIONS = [(858, 745), (1178, 1060), (1178, 1490), (858, 1605), (260, 1490), (260, 1060)]
DEFAULT_TITLE_POSITIONS = [(865, 250), (975, 355), (978, 455)]
DEFAULT_AVATAR_CENTER = (400, 420)


def _normalize_input_image(source_path: str, target: Path) -> Path:
    """Normalize uploaded image to RGBA while keeping its source file extension."""
    with Image.open(source_path) as image:
        image.convert("RGBA").save(target)
    return target


def generate_radar_image(
    template_file: str,
    avatar_file: str | None,
    title_1: str,
    title_2: str,
    title_3: str,
    score_1: float,
    score_2: float,
    score_3: float,
    score_4: float,
    score_5: float,
    score_6: float,
    final_score: float,
) -> tuple[Image.Image, str]:
    if not template_file:
        raise gr.Error("请先上传雷达图背景模板图片。")

    titles = [title_1.strip(), title_2.strip(), title_3.strip()]
    scores = [score_1, score_2, score_3, score_4, score_5, score_6]

    with tempfile.TemporaryDirectory(prefix="radar_app_") as tmp_dir:
        tmp = Path(tmp_dir)

        template_name = Path(template_file).name
        template_path = _normalize_input_image(template_file, tmp / template_name)
        output_path = tmp / f"result_{uuid.uuid4().hex}.png"

        draw_radar_by_anchors(
            img_path=str(template_path),
            out_path=str(output_path),
            scores_0_to_10=scores,
            final_score=int(round(final_score)),
            anchors=DEFAULT_ANCHORS,
            label_positions=DEFAULT_LABEL_POSITIONS,
            name_title=titles,
            title_positions=DEFAULT_TITLE_POSITIONS,
        )

        if avatar_file:
            avatar_name = Path(avatar_file).name
            avatar_path = _normalize_input_image(avatar_file, tmp / avatar_name)
            add_avatar(str(output_path), str(avatar_path), center=DEFAULT_AVATAR_CENTER, size=290, radius=43)

        final_img = Image.open(output_path).convert("RGBA")
        persist_file = Path(tempfile.gettempdir()) / f"radar_output_{uuid.uuid4().hex}.png"
        final_img.save(persist_file)

    return final_img, str(persist_file)


def build_app() -> gr.Blocks:
    with gr.Blocks(title="AI 雷达图生成器") as demo:
        gr.Markdown("## AI 雷达图生成器\n上传模板与头像，输入标题和分数，一键生成下载图片。")

        with gr.Row():
            template_file = gr.File(label="背景模板图（必传）", file_types=["image"], type="filepath")
            avatar_file = gr.File(label="头像（可选）", file_types=["image"], type="filepath")

        with gr.Row():
            title_1 = gr.Textbox(label="标题1", value="聪哥")
            title_2 = gr.Textbox(label="标题2", value="重生50")
            title_3 = gr.Textbox(label="标题3", value="AI真人剧")

        with gr.Row():
            score_1 = gr.Slider(0, 10, value=8, step=0.1, label="剧情")
            score_2 = gr.Slider(0, 10, value=9, step=0.1, label="画面")
            score_3 = gr.Slider(0, 10, value=7, step=0.1, label="动作")

        with gr.Row():
            score_4 = gr.Slider(0, 10, value=7, step=0.1, label="镜头")
            score_5 = gr.Slider(0, 10, value=10, step=0.1, label="配音")
            score_6 = gr.Slider(0, 10, value=8, step=0.1, label="剪辑")

        final_score = gr.Slider(0, 10, value=9, step=0.1, label="总分")

        run_btn = gr.Button("生成图片", variant="primary")

        with gr.Row():
            output_image = gr.Image(label="生成结果", type="pil")
            output_file = gr.File(label="下载图片")

        run_btn.click(
            fn=generate_radar_image,
            inputs=[
                template_file,
                avatar_file,
                title_1,
                title_2,
                title_3,
                score_1,
                score_2,
                score_3,
                score_4,
                score_5,
                score_6,
                final_score,
            ],
            outputs=[output_image, output_file],
        )

    return demo


demo = build_app()


if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=7860)
