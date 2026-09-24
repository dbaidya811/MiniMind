import os
import sys
import subprocess
import csv
import re
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from docx import Document
    from docx.shared import Pt as DocxPt, Inches as DocxInches, RGBColor as DocxRGBColor
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
except ImportError:
    Document = None


class SystemTools:
    @staticmethod
    def get_downloads_dir() -> Path:
        return Path.home() / "Downloads"

    @staticmethod
    def _generate_dynamic_chart(title: str, chart_type: str = "bar", categories: list = None, values: list = None) -> Optional[str]:
        if not MATPLOTLIB_AVAILABLE:
            return None
        try:
            temp_dir = tempfile.gettempdir()
            chart_path = os.path.join(temp_dir, f"chart_{os.getpid()}_{hash(title) % 10000}.png")
            plt.figure(figsize=(6, 4.2), dpi=150)
            
            colors = ["#2563EB", "#F97316", "#10B981", "#8B5CF6", "#64748B"]
            clean_title = re.sub(r"[^\w\s-]", "", title)[:30]

            if chart_type == "pie":
                labels = categories or ["Core Architecture", "Data Pipeline", "Model Inference", "System Ops"]
                vals = values or [35, 25, 25, 15]
                plt.pie(vals[:len(labels)], labels=labels[:4], autopct="%1.1f%%", startangle=140, colors=colors,
                        textprops={'fontsize': 10, 'color': '#0F172A', 'weight': 'bold'})
                plt.title(f"{clean_title} Distribution", fontsize=11, fontweight='bold', pad=12, color="#0F172A")
            else:
                cats = categories or ["Phase 1", "Phase 2", "Phase 3", "Target"]
                vals = values or [25, 45, 75, 100]
                bars = plt.bar(cats[:4], vals[:4], color="#2563EB", width=0.5, edgecolor="#1D4ED8")
                plt.title(f"{clean_title} Metric Overview", fontsize=11, fontweight='bold', pad=12, color="#0F172A")
                plt.ylabel("Index / Score", fontsize=9, color="#64748B")
                for bar in bars:
                    yval = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f"{yval}", ha='center', va='bottom', fontsize=8, fontweight='bold')

            plt.tight_layout()
            plt.savefig(chart_path, dpi=150, bbox_inches="tight", facecolor="#F8FAFC")
            plt.close()
            return chart_path
        except Exception:
            return None

    @staticmethod
    def create_ppt_structured(
        filename: str,
        slides_data: List[Dict[str, Any]],
        image_generator=None,
        topic: str = "Presentation"
    ) -> Dict[str, Any]:
        """
        Builds presentation based on CoT analyzed slide objects with targeted visual prompts.
        """
        try:
            downloads = SystemTools.get_downloads_dir()
            target_path = downloads / filename

            prs = Presentation()
            prs.slide_width = Inches(13.333)
            prs.slide_height = Inches(7.5)

            NAVY_BG = RGBColor(15, 23, 42)
            ACCENT_CORAL = RGBColor(249, 115, 22)
            CARD_BG = RGBColor(248, 250, 252)
            BORDER_COLOR = RGBColor(226, 232, 240)
            TEXT_DARK = RGBColor(30, 41, 59)
            TEXT_LIGHT = RGBColor(255, 255, 255)

            for idx, s in enumerate(slides_data):
                slide = prs.slides.add_slide(prs.slide_layouts[6])
                title = s.get("title", f"Slide {idx + 1}")
                summary = s.get("summary", "")
                points = s.get("points", [])
                image_prompt = s.get("image_prompt", "")
                chart_type = s.get("chart_type", "none")

                # SLIDE 1: Cover Page
                if idx == 0:
                    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
                    bg.fill.solid()
                    bg.fill.fore_color.rgb = NAVY_BG
                    bg.line.fill.background()

                    hero_img = None
                    if image_generator and image_prompt:
                        try:
                            hero_img = image_generator.generate(image_prompt)
                        except Exception:
                            hero_img = None

                    if hero_img and os.path.exists(hero_img):
                        try:
                            slide.shapes.add_picture(hero_img, Inches(7.3), Inches(1.1), Inches(5.2), Inches(5.3))
                        except Exception:
                            pass
                        text_width = Inches(5.8)
                    else:
                        text_width = Inches(11.0)

                    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.8), Inches(1.8), Inches(0.12))
                    bar.fill.solid()
                    bar.fill.fore_color.rgb = ACCENT_CORAL
                    bar.line.fill.background()

                    tb = slide.shapes.add_textbox(Inches(1.0), Inches(2.2), text_width, Inches(4.5))
                    tf = tb.text_frame
                    tf.word_wrap = True

                    p_title = tf.paragraphs[0]
                    p_title.text = title
                    p_title.font.size = Pt(38)
                    p_title.font.bold = True
                    p_title.font.color.rgb = TEXT_LIGHT

                    p_sub = tf.add_paragraph()
                    p_sub.text = f"\n{summary or 'In-depth architectural analysis and operational strategic deck.'}"
                    p_sub.font.size = Pt(15)
                    p_sub.font.color.rgb = RGBColor(203, 213, 225)
                    continue

                # SLIDES 2+: Header + Card Layout
                top_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(1.2))
                top_bg.fill.solid()
                top_bg.fill.fore_color.rgb = NAVY_BG
                top_bg.line.fill.background()

                accent_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.15), Inches(13.333), Inches(0.05))
                accent_line.fill.solid()
                accent_line.fill.fore_color.rgb = ACCENT_CORAL
                accent_line.line.fill.background()

                top_tb = slide.shapes.add_textbox(Inches(1.0), Inches(0.25), Inches(11.3), Inches(0.7))
                top_tf = top_tb.text_frame
                top_tf.word_wrap = True
                p_top = top_tf.paragraphs[0]
                p_top.text = title
                p_top.font.size = Pt(22)
                p_top.font.bold = True
                p_top.font.color.rgb = TEXT_LIGHT

                visual_path = None
                if chart_type in ["bar", "pie"]:
                    visual_path = SystemTools._generate_dynamic_chart(title, chart_type=chart_type)
                elif image_generator and image_prompt and (idx % 2 == 1 or idx == 1):
                    try:
                        visual_path = image_generator.generate(image_prompt)
                    except Exception:
                        visual_path = None

                # Layout with Right-side Visual
                if visual_path and os.path.exists(visual_path):
                    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.6), Inches(6.8), Inches(5.3))
                    card.fill.solid()
                    card.fill.fore_color.rgb = CARD_BG
                    card.line.color.rgb = BORDER_COLOR

                    tb = slide.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(6.2), Inches(4.9))
                    tf = tb.text_frame
                    tf.word_wrap = True

                    if summary:
                        ps = tf.paragraphs[0]
                        ps.text = summary
                        ps.font.size = Pt(13)
                        ps.font.bold = True
                        ps.font.color.rgb = RGBColor(15, 23, 42)
                        ps.space_after = Pt(10)

                    for pt in points:
                        p = tf.add_paragraph()
                        p.text = f"• {pt}"
                        p.font.size = Pt(12)
                        p.font.color.rgb = TEXT_DARK
                        p.space_after = Pt(10)

                    try:
                        slide.shapes.add_picture(visual_path, Inches(8.0), Inches(1.6), Inches(4.5), Inches(5.3))
                    except Exception:
                        pass
                else:
                    # 2-column or wide card layout
                    col_width = Inches(5.5)
                    mid = (len(points) + 1) // 2
                    col_data = [points[:mid], points[mid:]] if len(points) >= 2 else [points, []]

                    if col_data[1]:
                        for c_i, c_items in enumerate(col_data):
                            left = Inches(0.9 + (c_i * 6.0))
                            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.6), col_width, Inches(5.3))
                            card.fill.solid()
                            card.fill.fore_color.rgb = CARD_BG
                            card.line.color.rgb = BORDER_COLOR

                            tb = slide.shapes.add_textbox(left + Inches(0.3), Inches(1.8), col_width - Inches(0.6), Inches(4.9))
                            tf = tb.text_frame
                            tf.word_wrap = True
                            for item in c_items:
                                p = tf.add_paragraph()
                                p.text = f"• {item}"
                                p.font.size = Pt(13)
                                p.font.color.rgb = TEXT_DARK
                                p.space_after = Pt(14)
                    else:
                        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.6), Inches(11.5), Inches(5.3))
                        card.fill.solid()
                        card.fill.fore_color.rgb = CARD_BG
                        card.line.color.rgb = BORDER_COLOR

                        tb = slide.shapes.add_textbox(Inches(1.3), Inches(1.9), Inches(10.7), Inches(4.7))
                        tf = tb.text_frame
                        tf.word_wrap = True
                        for item in points:
                            p = tf.add_paragraph()
                            p.text = f"• {item}"
                            p.font.size = Pt(14)
                            p.font.color.rgb = TEXT_DARK
                            p.space_after = Pt(16)

            prs.save(target_path)
            return {"status": "success", "path": str(target_path)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def create_word_file(filename: str, content: str) -> Dict[str, Any]:
        """Generates an executive-styled Word document (.docx) with cover styling and section formatting."""
        if Document is None:
            return {"status": "error", "message": "python-docx package is not installed."}

        try:
            downloads = SystemTools.get_downloads_dir()
            target_path = downloads / filename

            doc = Document()
            sections = doc.sections
            for section in sections:
                section.top_margin = DocxInches(1.0)
                section.bottom_margin = DocxInches(1.0)
                section.left_margin = DocxInches(1.0)
                section.right_margin = DocxInches(1.0)

            lines = content.splitlines()
            for line in lines:
                s_line = line.strip()
                if not s_line:
                    continue

                if s_line.startswith("# "):
                    h1 = doc.add_heading(s_line[2:].strip(), level=1)
                    h1.style.font.name = "Segoe UI"
                    h1.style.font.size = DocxPt(22)
                    h1.style.font.bold = True
                    h1.style.font.color.rgb = DocxRGBColor(15, 23, 42)
                elif s_line.startswith("## "):
                    h2 = doc.add_heading(s_line[3:].strip(), level=2)
                    h2.style.font.name = "Segoe UI"
                    h2.style.font.size = DocxPt(15)
                    h2.style.font.bold = True
                    h2.style.font.color.rgb = DocxRGBColor(37, 99, 235)
                elif s_line.startswith("### "):
                    h3 = doc.add_heading(s_line[4:].strip(), level=3)
                    h3.style.font.name = "Segoe UI"
                    h3.style.font.size = DocxPt(12)
                    h3.style.font.bold = True
                    h3.style.font.color.rgb = DocxRGBColor(30, 41, 59)
                elif s_line.startswith(("- ", "* ")):
                    p = doc.add_paragraph(s_line[2:].strip(), style="List Bullet")
                    p.style.font.name = "Segoe UI"
                    p.style.font.size = DocxPt(10.5)
                elif s_line.startswith("> "):
                    p = doc.add_paragraph(s_line[2:].strip())
                    p.style.font.name = "Segoe UI"
                    p.style.font.italic = True
                    p.style.font.color.rgb = DocxRGBColor(71, 85, 105)
                else:
                    p = doc.add_paragraph(s_line)
                    p.style.font.name = "Segoe UI"
                    p.style.font.size = DocxPt(10.5)

            doc.save(target_path)
            return {"status": "success", "path": str(target_path)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def create_excel_file(filename: str, content: str) -> Dict[str, Any]:
        try:
            downloads = SystemTools.get_downloads_dir()
            target_path = downloads / filename

            counter = 1
            base_name = Path(filename).stem
            ext = Path(filename).suffix or ".xlsx"
            while target_path.exists():
                try:
                    with open(target_path, "a"):
                        break
                except PermissionError:
                    target_path = downloads / f"{base_name}_{counter}{ext}"
                    counter += 1

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "DataSheet"

            raw_lines = [line.strip() for line in content.strip().splitlines() if line.strip()]
            clean_lines = [l for l in raw_lines if not l.lower().startswith(("here is", "sure", "certainly", "```", "---"))]

            parsed_rows = []
            for line in clean_lines:
                if "," in line:
                    row_data = next(csv.reader([line], skipinitialspace=True))
                elif "\t" in line:
                    row_data = line.split("\t")
                else:
                    row_data = [x.strip() for x in line.split("|") if x.strip()]
                row_data = [c.strip().strip('"').strip("'") for c in row_data]
                if any(row_data):
                    parsed_rows.append(row_data)

            if not parsed_rows:
                return {"status": "error", "message": "No valid tabular data found"}

            max_cols = max(len(r) for r in parsed_rows)
            header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
            header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
            zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
            regular_font = Font(name="Segoe UI", size=10)
            thin_border = Border(
                left=Side(style="thin", color="E2E8F0"),
                right=Side(style="thin", color="E2E8F0"),
                top=Side(style="thin", color="E2E8F0"),
                bottom=Side(style="thin", color="E2E8F0")
            )

            for r_idx, row in enumerate(parsed_rows, start=1):
                padded_row = row + [""] * (max_cols - len(row))
                for c_idx, val_str in enumerate(padded_row, start=1):
                    cell = ws.cell(row=r_idx, column=c_idx)
                    cell.border = thin_border
                    num_clean = val_str.replace(",", "").replace("$", "").replace("%", "").strip()
                    try:
                        if "." in num_clean:
                            cell.value = float(num_clean)
                        elif num_clean.isdigit():
                            cell.value = int(num_clean)
                        else:
                            cell.value = val_str
                    except ValueError:
                        cell.value = val_str

                    if r_idx == 1:
                        cell.fill = header_fill
                        cell.font = header_font
                        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                    else:
                        cell.font = regular_font
                        cell.alignment = Alignment(horizontal="right" if isinstance(cell.value, (int, float)) else "left", vertical="center")
                        if r_idx % 2 == 0:
                            cell.fill = zebra_fill

            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 4, 15)

            wb.save(target_path)
            return {"status": "success", "path": str(target_path)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def update_or_create_file(filename: str, content: str, mode: str = "w") -> Dict[str, Any]:
        try:
            downloads = SystemTools.get_downloads_dir()
            target_path = downloads / filename
            with open(target_path, mode, encoding="utf-8") as f:
                f.write(content)
            return {"status": "success", "path": str(target_path)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def read_file(path_str: str) -> Dict[str, Any]:
        try:
            p = Path(path_str)
            if not p.is_absolute():
                p = SystemTools.get_downloads_dir() / path_str
            if not p.exists():
                return {"status": "error", "message": f"File not found: {p}"}
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return {"status": "success", "path": str(p), "content": content}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def launch_app(app_name: str) -> Dict[str, Any]:
        app_lower = app_name.lower().strip()
        cmd = None
        if sys.platform == "win32":
            mapping = {
                "vscode": "code", "code": "code", "chrome": "start chrome",
                "browser": "start chrome", "notepad": "notepad", "calc": "calc",
                "calculator": "calc", "explorer": "explorer",
                "downloads": f'explorer "{SystemTools.get_downloads_dir()}"'
            }
            cmd = mapping.get(app_lower, app_lower)
        else:
            mapping = {
                "vscode": "code", "code": "code", "chrome": "google-chrome",
                "browser": "google-chrome", "calc": "gnome-calculator", "calculator": "gnome-calculator"
            }
            cmd = mapping.get(app_lower, app_lower)
        try:
            subprocess.Popen(cmd, shell=True)
            return {"status": "success", "message": f"Launched application: {app_name}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def list_directory(dir_path: Optional[str] = None) -> Dict[str, Any]:
        try:
            target = Path(dir_path) if dir_path else SystemTools.get_downloads_dir()
            if not target.is_absolute():
                target = SystemTools.get_downloads_dir() / target
            if not target.exists() or not target.is_dir():
                return {"status": "error", "message": f"Invalid directory path: {target}"}
            items = []
            for item in target.iterdir():
                items.append({
                    "name": item.name,
                    "type": "folder" if item.is_dir() else "file",
                    "size_bytes": item.stat().st_size if item.is_file() else 0
                })
            return {"status": "success", "path": str(target), "items": items}
        except Exception as e:
            return {"status": "error", "message": str(e)}