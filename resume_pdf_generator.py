#!/usr/bin/env python3
"""Generate a compact, A4 Chinese resume PDF from Markdown and an optional photo.

The layout follows the visual language of ``example.pdf``: a restrained black
and white one-page resume, bold section bars, compact body copy, and a photo
in the upper-right corner.
"""

from __future__ import annotations

import argparse
import html
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, Image, KeepTogether, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)


# macOS ships these CJK fonts. Embedding the TrueType outlines keeps the PDF
# portable (unlike a device-dependent CID font), including in Poppler preview.
# Songti's horizontal punctuation is correctly positioned in generated PDFs.
# Some CJK sans TTC faces map punctuation to their vertical presentation glyphs.
DEFAULT_FONT_PATH = "/System/Library/Fonts/Supplemental/Songti.ttc"
FONT_PATH = Path(os.environ.get("RESUME_FONT_PATH", DEFAULT_FONT_PATH))
FONT_BOLD_PATH = Path(os.environ.get("RESUME_BOLD_FONT_PATH", DEFAULT_FONT_PATH))
# Songti.ttc contains multiple faces: 6 is Songti SC Regular and 1 is Songti
# SC Bold. Keeping these explicit preserves the intended body/title contrast.
FONT_INDEX = int(os.environ.get("RESUME_FONT_INDEX", "6" if str(FONT_PATH) == DEFAULT_FONT_PATH else "0"))
BOLD_FONT_INDEX = int(os.environ.get("RESUME_BOLD_FONT_INDEX", "1" if str(FONT_BOLD_PATH) == DEFAULT_FONT_PATH else "0"))
if not FONT_PATH.exists():
    raise RuntimeError("A CJK TrueType font is required. Set RESUME_FONT_PATH to a .ttf/.ttc font file.")
pdfmetrics.registerFont(TTFont("ResumeCJK", str(FONT_PATH), subfontIndex=FONT_INDEX))
pdfmetrics.registerFont(TTFont("ResumeCJKBold", str(FONT_BOLD_PATH), subfontIndex=BOLD_FONT_INDEX))
pdfmetrics.registerFontFamily("ResumeCJK", normal="ResumeCJK", bold="ResumeCJKBold", italic="ResumeCJK", boldItalic="ResumeCJKBold")
FONT = "ResumeCJK"
PAGE_W, PAGE_H = A4
LEFT = RIGHT = 18 * mm
TOP, BOTTOM = 16 * mm, 15 * mm


@dataclass
class Entry:
    title: str
    meta: list[str] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)
    bullets: list[str] = field(default_factory=list)
    projects: list["Entry"] = field(default_factory=list)


@dataclass
class Section:
    title: str
    entries: list[Entry] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)
    bullets: list[str] = field(default_factory=list)


def clean(text: str) -> str:
    """Small Markdown subset -> ReportLab paragraph markup."""
    text = html.escape(text.strip())
    text = re.sub(r"`([^`]+)`", r"<font name=\"Courier\">\1</font>", text)
    # ``ResumeCJK`` has an explicit ReportLab font-family mapping, so <b>
    # resolves to the embedded CJK bold face instead of a Latin fallback.
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*", r"<i>\1</i>", text)
    return text


def parse_markdown(path: Path) -> tuple[dict[str, str], list[Section]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    meta: dict[str, str] = {}
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is None:
            raise ValueError("YAML metadata block is missing its closing ---")
        for line in lines[1:end]:
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip().strip('"\'')
        lines = lines[end + 1:]

    sections: list[Section] = []
    section: Section | None = None
    entry: Entry | None = None
    project: Entry | None = None
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("<!--"):
            continue
        if line.startswith("# "):
            section = Section(line[2:].strip())
            sections.append(section)
            entry = project = None
        elif line.startswith("## "):
            if section is None:
                raise ValueError("Use '# Section title' before '## Entry title'.")
            parts = [p.strip() for p in line[3:].split("|")]
            entry = Entry(parts[0], parts[1:])
            section.entries.append(entry)
            project = None
        elif line.startswith("### "):
            if entry is None:
                raise ValueError("Use '## Entry title' before '### Project title'.")
            parts = [p.strip() for p in line[4:].split("|")]
            project = Entry(parts[0], parts[1:])
            entry.projects.append(project)
        elif line.startswith("- ") or line.startswith("* "):
            target = project or entry or section
            if target is None:
                raise ValueError("Bullet found before a section title.")
            target.bullets.append(line[2:].strip())
        else:
            target = project or entry or section
            if target is None:
                raise ValueError("Text found before a section title.")
            target.paragraphs.append(line)
    if not meta.get("name"):
        raise ValueError("Metadata must include 'name'.")
    return meta, sections


class SectionTitle(Flowable):
    def __init__(self, text: str, width: float):
        Flowable.__init__(self)
        self.text, self.width, self.height = text, width, 8 * mm

    def draw(self):
        self.canv.setFont("ResumeCJKBold", 12)
        self.canv.drawString(0, 4.1 * mm, self.text)
        self.canv.setLineWidth(0.55)
        self.canv.line(0, 2.4 * mm, self.width, 2.4 * mm)


def styles() -> dict[str, ParagraphStyle]:
    common = dict(fontName=FONT, textColor=colors.black)
    return {
        "name": ParagraphStyle("name", textColor=colors.black, fontName="ResumeCJKBold", fontSize=20, leading=24, spaceAfter=3),
        "contact": ParagraphStyle("contact", **common, fontSize=10.5, leading=13),
        "entry": ParagraphStyle("entry", textColor=colors.black, fontName="ResumeCJKBold", fontSize=10.6, leading=13, spaceAfter=0),
        "sub": ParagraphStyle("sub", **common, fontSize=9.8, leading=12.2),
        "body": ParagraphStyle("body", **common, fontSize=9.2, leading=11.4, spaceAfter=0),
        "bullet": ParagraphStyle("bullet", **common, fontSize=9.2, leading=11.4, leftIndent=4.5 * mm, firstLineIndent=-3.4 * mm),
        "right": ParagraphStyle("right", **common, fontSize=9.6, leading=12, alignment=TA_RIGHT),
    }


def paragraph(text: str, style: ParagraphStyle, *, markup: bool = False) -> Paragraph:
    return Paragraph(text if markup else clean(text), style)


def meta_rows(meta: dict[str, str]) -> list[str]:
    rows = []
    if meta.get("phone") or meta.get("email"):
        rows.append("  |  ".join(x for x in [f"电话：{meta['phone']}" if meta.get("phone") else "", f"邮箱：{meta['email']}" if meta.get("email") else ""] if x))
    basic = [f"年龄：{meta['age']}" if meta.get("age") else "", f"性别：{meta['gender']}" if meta.get("gender") else ""]
    if any(basic): rows.append("  |  ".join(x for x in basic if x))
    if meta.get("status") or meta.get("location"):
        rows.append("  |  ".join(x for x in [f"当前状态：{meta['status']}" if meta.get("status") else "", f"意向城市：{meta['location']}" if meta.get("location") else ""] if x))
    return rows


def split_school_tags(title: str) -> tuple[str, list[str]]:
    """Extract `[985]` / `[211]` tags without exposing the syntax in the PDF."""
    tags = re.findall(r"\[(985|211)\]", title)
    plain_title = re.sub(r"\s*\[(?:985|211)\]", "", title).strip()
    return plain_title, tags


class TitleWithTags(Flowable):
    """An experience title followed by small rounded school-level tags."""

    tag_fill = colors.HexColor("#E7F0FF")
    tag_text = colors.HexColor("#4A83DE")

    def __init__(self, title: str, tags: list[str], font_size: float, leading: float):
        super().__init__()
        self.title, self.tags = title, tags
        self.font_size, self.height = font_size, leading
        self.tag_font_size = 8.2
        self.tag_height = 11.2
        self.tag_padding_x = 2.6
        self.tag_gap = 2.2
        self.title_width = pdfmetrics.stringWidth(title, "ResumeCJKBold", font_size)
        self.tag_widths = [pdfmetrics.stringWidth(tag, FONT, self.tag_font_size) + 2 * self.tag_padding_x for tag in tags]
        self.width = self.title_width + (4.2 if tags else 0) + sum(self.tag_widths) + self.tag_gap * max(0, len(tags) - 1)

    def wrap(self, available_width, available_height):
        return min(self.width, available_width), self.height

    def draw(self):
        text_y = (self.height - self.font_size) / 2 + 1.2
        self.canv.setFont("ResumeCJKBold", self.font_size)
        self.canv.setFillColor(colors.black)
        self.canv.drawString(0, text_y, self.title)
        x = self.title_width + 4.2
        tag_y = (self.height - self.tag_height) / 2
        for tag, tag_width in zip(self.tags, self.tag_widths):
            self.canv.setFillColor(self.tag_fill)
            self.canv.roundRect(x, tag_y, tag_width, self.tag_height, 2.4, fill=1, stroke=0)
            self.canv.setFillColor(self.tag_text)
            self.canv.setFont(FONT, self.tag_font_size)
            self.canv.drawCentredString(x + tag_width / 2, tag_y + (self.tag_height - self.tag_font_size) / 2 + 1.0, tag)
            x += tag_width + self.tag_gap


def entry_flowables(entry: Entry, s: dict[str, ParagraphStyle], available: float) -> list:
    title, tags = split_school_tags(entry.title)
    left = [TitleWithTags(title, tags, s["entry"].fontSize, s["entry"].leading)] if tags else [paragraph(title, s["entry"])]
    if entry.meta:
        left.append(paragraph(entry.meta[0], s["sub"]))
    for text in entry.paragraphs:
        left.append(paragraph(text, s["body"]))
    right_text = "<br/>".join(clean(value) for value in entry.meta[1:]) if len(entry.meta) > 1 else ""
    if right_text:
        table = Table([[left, paragraph(right_text, s["right"], markup=True)]], colWidths=[available - 47 * mm, 47 * mm], hAlign="LEFT")
        table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
        result: list = [table]
    else:
        result = left
    for text in entry.bullets:
        result.append(paragraph(f"•　{text}", s["bullet"]))
    for project in entry.projects:
        result.extend(entry_flowables(project, s, available))
    return result


def build(meta: dict[str, str], sections: Iterable[Section], avatar: Path | None, output: Path) -> None:
    available = PAGE_W - LEFT - RIGHT
    doc = BaseDocTemplate(str(output), pagesize=A4, leftMargin=LEFT, rightMargin=RIGHT, topMargin=TOP, bottomMargin=BOTTOM)
    doc.addPageTemplates([PageTemplate(id="resume", frames=[Frame(LEFT, BOTTOM, available, PAGE_H - TOP - BOTTOM, id="body")])])
    s = styles()
    story: list = []
    profile = [paragraph(meta["name"], s["name"])] + [paragraph(row, s["contact"]) for row in meta_rows(meta)]
    if avatar:
        if not avatar.exists(): raise FileNotFoundError(f"Avatar image not found: {avatar}")
        profile_width = available - 33 * mm
        profile_height = sum(item.wrap(profile_width, 1000)[1] + item.style.spaceAfter for item in profile)
        image_width, image_height = ImageReader(str(avatar)).getSize()
        photo_width = profile_height * image_width / image_height
        photo = Image(str(avatar), width=photo_width, height=profile_height)
        table = Table([[profile, photo]], colWidths=[available - 33 * mm, 33 * mm], hAlign="LEFT")
        table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (1, 0), (1, 0), "RIGHT"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
        story.extend([table, Spacer(1, 3 * mm)])
    else:
        story.extend(profile + [Spacer(1, 3 * mm)])
    for section in sections:
        heading = SectionTitle(section.title, available)
        # Keep the heading with only the first small content block. Keeping an
        # entire long experience together would create a mostly blank page.
        if section.paragraphs:
            story.append(KeepTogether([heading, paragraph(section.paragraphs[0], s["body"])]))
            story.extend(paragraph(text, s["body"]) for text in section.paragraphs[1:])
            story.extend(paragraph(f"•　{text}", s["bullet"]) for text in section.bullets)
            for entry in section.entries:
                story.append(KeepTogether(entry_flowables(entry, s, available) + [Spacer(1, 1.5 * mm)]))
        elif section.bullets:
            story.append(KeepTogether([heading, paragraph(f"•　{section.bullets[0]}", s["bullet"])]))
            story.extend(paragraph(f"•　{text}", s["bullet"]) for text in section.bullets[1:])
            for entry in section.entries:
                story.append(KeepTogether(entry_flowables(entry, s, available) + [Spacer(1, 1.5 * mm)]))
        elif section.entries:
            first_entry = section.entries[0]
            first_flowables = entry_flowables(first_entry, s, available)
            story.append(KeepTogether([heading, first_flowables[0]]))
            story.extend(first_flowables[1:] + [Spacer(1, 1.5 * mm)])
            for entry in section.entries[1:]:
                story.append(KeepTogether(entry_flowables(entry, s, available) + [Spacer(1, 1.5 * mm)]))
        else:
            story.append(heading)
        story.append(Spacer(1, 1.4 * mm))
    doc.build(story)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an A4 PDF resume from Markdown.")
    parser.add_argument("markdown", type=Path, help="Input Markdown resume")
    parser.add_argument("-a", "--avatar", type=Path, help="Headshot image (PNG/JPG/WebP)")
    parser.add_argument("-o", "--output", type=Path, default=Path("output/pdf/resume.pdf"), help="Output PDF path")
    args = parser.parse_args()
    meta, sections = parse_markdown(args.markdown)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    build(meta, sections, args.avatar, args.output)
    print(f"Created {args.output}")


if __name__ == "__main__":
    main()
