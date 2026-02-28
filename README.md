# AItest

一个基于 **Python + PIL + Gradio** 的雷达图生成应用，支持：

- 固定使用内置背景模板（`assets/fixed_template.png`）
- 上传头像（可选）
- 填写 3 个文本字段：姓名、作品名称、风格类型
- 调整 6 个维度分数 + 总分
- 一键生成图片并在结果图里直接下载

## Files

- `radar_generator.py`：核心绘图逻辑（雷达多边形、分数文本、时间戳、头像叠加）
- `app.py`：Gradio Web 应用入口
- `requirements.txt`：依赖清单（给本地或魔搭社区用）

## 部署方式（推荐）：魔搭社区（ModelScope）

既然你准备改用魔搭社区，可以直接把这个 Gradio 项目作为 Space 应用部署。

### 1) 新建应用

- 登录魔搭社区
- 创建应用 / Space（选择 **Gradio**）
- Python 版本用默认即可

### 2) 上传仓库文件

至少上传这些文件（含固定模板）：

- `app.py`
- `radar_generator.py`
- `requirements.txt`
- `assets/fixed_template.png`
- `assets/scores/1.png` ... `assets/scores/10.png`

### 3) 等待自动构建

平台会自动：

- 安装 `requirements.txt` 依赖
- 启动 `app.py`

构建完成后即可获得在线访问地址。

## 本地运行（可选）

```bash
pip install -r requirements.txt
python app.py
```

访问：

- `http://127.0.0.1:7860`

## Notes

- 不再上传背景图：应用固定读取 `assets/fixed_template.png` 作为背景。
- 最终得分优先使用 `assets/scores/{1..10}.png` 贴图；若缺失对应图片则回退为文字。
- 前端上传头像后会按上传文件名处理，不再依赖类似 `聪.jpg` 的固定文件名。
- 目前默认锚点坐标、文字坐标、头像中心点是按现有模板配置在 `app.py` 里的常量。
- 如果你换模板图，需要同步调整这些坐标。
- 结果区只有一个“生成结果”窗口，下载请使用图片右下角下载按钮。
- 上传 JPG/PNG 都会先转为 PNG 再处理，避免 JPEG 与 RGBA 模式冲突导致报错。
