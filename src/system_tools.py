import os
import subprocess
import platform
import re
from pathlib import Path
from typing import Dict, Any

class SystemTools:
    @staticmethod
    def get_downloads_dir() -> Path:
        downloads = Path.home() / "Downloads"
        downloads.mkdir(parents=True, exist_ok=True)
        return downloads

    @staticmethod
    def create_ppt_file(filename: str, content: str, image_generator=None, topic: str = "Presentation") -> Dict[str, Any]:
        """Creates an executive, content-dense PowerPoint (.pptx) deck with clean typography and balanced layout."""
        if not filename.lower().endswith(".pptx"):
            filename += ".pptx"
        target = SystemTools.get_downloads_dir() / filename

        try:
            from pptx import Presentation
            from pptx.util import Inches, Pt
            from pptx.dml.color import RGBColor
            from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
            from pptx.enum.shapes import MSO_SHAPE

            prs = Presentation()
            prs.slide_width = Inches(13.333)
            prs.slide_height = Inches(7.5)
            blank_layout = prs.slide_layouts[6]

            COLOR_BG = RGBColor(15, 23, 42)          # Deep Slate
            COLOR_CARD = RGBColor(30, 41, 59)        # Card Background
            COLOR_ACCENT = RGBColor(217, 119, 87)    # Accent Orange
            COLOR_CYAN = RGBColor(56, 189, 248)      # Highlight Cyan
            COLOR_WHITE = RGBColor(248, 250, 252)    # Title White
            COLOR_MUTED = RGBColor(203, 213, 225)    # Body Text

            raw_slides = [s.strip() for s in re.split(r"(?:^|\n)(?:---|===)", content) if s.strip()]
            if not raw_slides:
                raw_slides = [content]

            generated_img_path = None
            if image_generator:
                try:
                    img_prompt = f"concept visual representation of {topic}, high quality digital illustration, dark cinematic aesthetic"
                    generated_img_path = image_generator.generate(img_prompt)
                except Exception:
                    generated_img_path = None

            def clean_text(text: str) -> str:
                t = re.sub(r"\*\*|\*", "", text)
                t = re.sub(r"^slide\s*\d+\s*:\s*", "", t, flags=re.IGNORECASE)
                t = re.sub(r"^title\s*slide\s*:\s*", "", t, flags=re.IGNORECASE)
                return t.strip()

            for idx, slide_text in enumerate(raw_slides):
                slide = prs.slides.add_slide(blank_layout)

                bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
                bg.fill.solid()
                bg.fill.fore_color.rgb = COLOR_BG
                bg.line.fill.background()

                raw_lines = [l.strip() for l in slide_text.split("\n") if l.strip()]
                if not raw_lines:
                    continue

                if idx == 0:
                    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.12))
                    top_bar.fill.solid()
                    top_bar.fill.fore_color.rgb = COLOR_ACCENT
                    top_bar.line.fill.background()

                    title_box = slide.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(7.5), Inches(3.5))
                    tf = title_box.text_frame
                    tf.word_wrap = True

                    p_tag = tf.paragraphs[0]
                    p_tag.text = "MINIMIND RESEARCH & INTELLIGENCE"
                    p_tag.font.bold = True
                    p_tag.font.size = Pt(13)
                    p_tag.font.color.rgb = COLOR_CYAN

                    main_title = clean_text(raw_lines[0]) or topic.title()
                    p_title = tf.add_paragraph()
                    p_title.text = main_title
                    p_title.font.bold = True
                    p_title.font.size = Pt(36)
                    p_title.font.color.rgb = COLOR_WHITE
                    p_title.space_before = Pt(16)
                    p_title.space_after = Pt(14)

                    sub_lines = [clean_text(x) for x in raw_lines[1:] if clean_text(x)]
                    sub_text = " | ".join(sub_lines) if sub_lines else f"A structured overview covering key architectures and applications in {topic}."
                    p_sub = tf.add_paragraph()
                    p_sub.text = sub_text
                    p_sub.font.size = Pt(15)
                    p_sub.font.color.rgb = COLOR_MUTED

                    if generated_img_path and os.path.exists(generated_img_path):
                        try:
                            img_frame = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), Inches(1.5), Inches(3.6), Inches(4.5))
                            img_frame.fill.solid()
                            img_frame.fill.fore_color.rgb = COLOR_CARD
                            img_frame.line.color.rgb = COLOR_ACCENT
                            slide.shapes.add_picture(generated_img_path, Inches(8.9), Inches(1.6), width=Inches(3.4), height=Inches(4.3))
                        except Exception:
                            pass

                else:
                    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.5), Inches(0.8))
                    htf = header_box.text_frame
                    htf.word_wrap = True

                    h_p = htf.paragraphs[0]
                    h_p.text = clean_text(raw_lines[0])
                    h_p.font.bold = True
                    h_p.font.size = Pt(26)
                    h_p.font.color.rgb = COLOR_WHITE

                    divider = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.4), Inches(2.2), Inches(0.04))
                    divider.fill.solid()
                    divider.fill.fore_color.rgb = COLOR_ACCENT
                    divider.line.fill.background()

                    points = []
                    for line in raw_lines[1:]:
                        cleaned = clean_text(line).lstrip("-*•> ").strip()
                        if cleaned:
                            points.append(cleaned)

                    if not points:
                        points = [
                            "Comprehensive technical review and foundational principles.",
                            "Execution considerations and performance trade-offs."
                        ]

                    card_width = Inches(3.6)
                    card_gap = Inches(0.4)
                    start_x = Inches(0.8)

                    for c_idx, point_text in enumerate(points[:3]):
                        cx = start_x + (c_idx * (card_width + card_gap))
                        card_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, Inches(1.8), card_width, Inches(5.1))
                        card_shape.fill.solid()
                        card_shape.fill.fore_color.rgb = COLOR_CARD
                        card_shape.line.color.rgb = COLOR_ACCENT if c_idx == 0 else COLOR_CARD
                        card_shape.line.width = Pt(1.5)

                        ctf = card_shape.text_frame
                        ctf.vertical_anchor = MSO_ANCHOR.TOP
                        ctf.word_wrap = True
                        ctf.margin_left = Inches(0.2)
                        ctf.margin_right = Inches(0.2)
                        ctf.margin_top = Inches(0.25)
                        ctf.margin_bottom = Inches(0.2)

                        p_num = ctf.paragraphs[0]
                        p_num.text = f"PILLAR 0{c_idx + 1}"
                        p_num.font.bold = True
                        p_num.font.size = Pt(10)
                        p_num.font.color.rgb = COLOR_CYAN
                        p_num.space_after = Pt(8)

                        if ":" in point_text:
                            p_title_str, p_desc_str = point_text.split(":", 1)
                            p_card_title = ctf.add_paragraph()
                            p_card_title.text = p_title_str.strip()
                            p_card_title.font.bold = True
                            p_card_title.font.size = Pt(15)
                            p_card_title.font.color.rgb = COLOR_WHITE
                            p_card_title.space_after = Pt(6)

                            p_body = ctf.add_paragraph()
                            p_body.text = p_desc_str.strip()
                            p_body.font.size = Pt(11)
                            p_body.font.color.rgb = COLOR_MUTED
                            p_body.line_spacing = 1.15
                        else:
                            p_body = ctf.add_paragraph()
                            p_body.text = point_text
                            p_body.font.size = Pt(12)
                            p_body.font.color.rgb = COLOR_WHITE
                            p_body.line_spacing = 1.15

            prs.save(str(target))
            return {"status": "success", "path": str(target), "filename": filename}

        except ImportError:
            txt_path = target.with_suffix(".txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"status": "warning", "path": str(txt_path), "message": "python-pptx missing. Saved as txt."}
        except Exception as e:
            return {"status": "error", "message": str(e), "path": str(target)}

    @staticmethod
    def create_word_file(filename: str, content: str) -> Dict[str, Any]:
        if not filename.endswith(".docx"):
            filename += ".docx"
        target = SystemTools.get_downloads_dir() / filename
        try:
            import docx
            doc = docx.Document()
            for line in content.strip().split("\n"):
                l = line.strip()
                if l.startswith("# "):
                    doc.add_heading(l.replace("# ", ""), level=1)
                elif l.startswith("## "):
                    doc.add_heading(l.replace("## ", ""), level=2)
                elif l.startswith("### "):
                    doc.add_heading(l.replace("### ", ""), level=3)
                elif l:
                    doc.add_paragraph(l)
            doc.save(str(target))
            return {"status": "success", "path": str(target), "filename": filename}
        except Exception as e:
            return {"status": "error", "message": str(e), "path": str(target)}

    @staticmethod
    def create_excel_file(filename: str, content: str) -> Dict[str, Any]:
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"
        target = SystemTools.get_downloads_dir() / filename
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Sheet1"
            for r_idx, line in enumerate(content.strip().split("\n"), start=1):
                clean_line = line.strip().strip("|")
                cols = [c.strip() for c in clean_line.replace("|", ",").split(",") if c.strip()]
                for c_idx, val in enumerate(cols, start=1):
                    ws.cell(row=r_idx, column=c_idx, value=val)
            wb.save(str(target))
            return {"status": "success", "path": str(target), "filename": filename}
        except Exception as e:
            return {"status": "error", "message": str(e), "path": str(target)}

    @staticmethod
    def update_or_create_file(file_name: str, content: str, mode: str = "w") -> Dict[str, Any]:
        target = Path(file_name).expanduser()
        if not target.is_absolute():
            target = SystemTools.get_downloads_dir() / target
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, mode, encoding="utf-8") as f:
                f.write(content)
            return {"status": "success", "path": str(target), "filename": target.name}
        except Exception as e:
            return {"status": "error", "message": str(e), "path": str(target)}

    @staticmethod
    def list_directory(path: str = None) -> Dict[str, Any]:
        target = SystemTools.get_downloads_dir() if not path or path == "." else Path(path).expanduser().resolve()
        if not target.exists():
            return {"status": "error", "message": f"Path not found: {path}"}
        try:
            items = [{"name": it.name, "type": "folder" if it.is_dir() else "file", "size_bytes": it.stat().st_size if it.is_file() else 0} for it in target.iterdir()]
            return {"status": "success", "path": str(target), "items": items[:50]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def read_file(file_path: str) -> Dict[str, Any]:
        target = Path(file_path).expanduser()
        if not target.is_absolute():
            target = SystemTools.get_downloads_dir() / target
        if not target.exists() or not target.is_file():
            return {"status": "error", "message": f"File not found: {str(target)}"}
        try:
            with open(target, "r", encoding="utf-8", errors="ignore") as f:
                return {"status": "success", "content": f.read(4000), "path": str(target)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def launch_app(app_name: str) -> Dict[str, Any]:
        cmd = app_name.lower().strip()
        alias_map = {
            "vscode": "code",
            "vs code": "code",
            "word": "winword",
            "excel": "excel",
            "powerpoint": "powerpnt",
            "notepad": "notepad",
            "chrome": "chrome",
            "calculator": "calc"
        }
        cmd = alias_map.get(cmd, cmd)
        try:
            subprocess.Popen(cmd, shell=True)
            return {"status": "success", "message": f"Launched '{app_name}'"}
        except Exception as e:
            return {"status": "error", "message": str(e)}