# Markdown PDF 简历生成器

将 Markdown 简历和头像图片生成一份 A4 PDF，版式参考 `example.pdf`：黑白、紧凑、加粗分区标题、右上角头像与右对齐日期/地点信息。

## 快速开始

```bash
cd resume-gene
python3 -m pip install -r requirements.txt
python3 resume_pdf_generator.py resume_template.md --avatar avatar.jpg --output output/pdf/张三-简历.pdf
```

头像为可选项；省略 `--avatar` 即可生成无照片版本。支持 PNG、JPG、WebP 等 ReportLab 可读取的图片格式。

默认使用 macOS 自带的宋体，以确保中文逗号、句号等标点位于正确基线。若在其它系统运行，请指定可显示中文的 TrueType 字体：

```bash
RESUME_FONT_PATH=/path/to/NotoSansCJK-Regular.ttc \
RESUME_BOLD_FONT_PATH=/path/to/NotoSansCJK-Bold.ttc \
python3 resume_pdf_generator.py resume_template.md -o output/pdf/resume.pdf
```

若指定的是 `.ttc` 字体集，可额外通过 `RESUME_FONT_INDEX` 与
`RESUME_BOLD_FONT_INDEX` 选择常规和粗体子字体。

## Markdown 结构

- 文件开头使用 `---` 包裹的元信息；`name` 必填，其余字段可按需删除。
- `#` 是简历分区，例如“教育经历”“项目经历”。
- `##` 是一条经历，使用 `|` 分隔字段：`名称 | 副标题 | 时间 | 地点`。时间和地点会靠右显示。
- 在“项目经历”分区中，使用 `项目名称 | 时间`；时间会与项目标题同一行右对齐，`个人项目` 与 `团队项目` 这类标签不会显示。
- 教育经历的学校名称后可加 `[985]` 或 `[211]`，例如 `某某大学 [985]`；PDF 会渲染为浅蓝色标签。
- `###` 是某条经历下的项目；格式与 `##` 相同。
- 普通文本会作为正文，`- ` 或 `* ` 开头的行为项目符号。
- 标题（姓名、`#`、`##`、`###`）默认加粗；正文默认常规字重。正文中可用 `**重点内容**` 加粗。

可直接复制并填写 [resume_template.md](resume_template.md)。输出会自动创建到指定目录。

## 设计说明

生成器使用内置的中文 CID 字体，避免中文缺字；页面为 A4，页边距与文字密度按参考样式设定。内容过长时会自然分页，段落和小节标题尽量保持在同一页。
