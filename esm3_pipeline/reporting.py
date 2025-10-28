"""
PDF report generation with error handling.
"""
from pathlib import Path
from typing import Optional
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus.tables import TableStyle
import ast

from .logger import get_logger

logger = get_logger(__name__)


def build_report(base: Path, pdb_dir: Path, out_pdf: Path) -> None:
    """
    Build a summary PDF report.

    Args:
        base: Base directory containing results
        pdb_dir: Directory containing PDB files
        out_pdf: Output PDF file path
    """
    try:
        doc = SimpleDocTemplate(str(out_pdf), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph('ESM3 Pipeline Results Report', styles['Title']))
        story.append(Spacer(1, 20))

        # Pockets summary
        pock_csv = base / 'pockets_summary.csv'
        if pock_csv.exists():
            try:
                dfp = pd.read_csv(pock_csv)
                if not dfp.empty:
                    data = [['PDB', 'Pocket', 'Score', 'Center X', 'Center Y', 'Center Z']]
                    for _, r in dfp.head(10).iterrows():  # Limit to top 10
                        try:
                            center = ast.literal_eval(r['center']) if isinstance(r['center'], str) else r['center']
                            cx, cy, cz = center
                            pdb_name = Path(r['pdb']).name
                            pocket_rank = r.get('pocket_rank', 1)
                            score = f"{r['score']:.2f}" if pd.notna(r['score']) else 'N/A'
                            data.append([pdb_name, str(pocket_rank), score,
                                       f'{cx:.2f}', f'{cy:.2f}', f'{cz:.2f}'])
                        except Exception as e:
                            logger.warning(f"Skipping pocket row: {e}")
                            continue

                    if len(data) > 1:  # Has data rows
                        story.append(Paragraph('Detected Binding Pockets (Top 10)', styles['Heading2']))
                        t = Table(data)
                        t.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        story.append(t)
                        story.append(Spacer(1, 20))
            except Exception as e:
                logger.error(f"Failed to add pocket summary to report: {e}")
                story.append(Paragraph('Error loading pocket data', styles['Normal']))
                story.append(Spacer(1, 12))

        # Docking summary
        vina_csv = base / 'vina_results.csv'
        if vina_csv.exists():
            try:
                dfg = pd.read_csv(vina_csv)
                # Filter successful docking results
                dfg_valid = dfg[dfg['affinity'].notna()].sort_values('affinity')

                if not dfg_valid.empty:
                    data = [['PDB', 'Pocket', 'Affinity (kcal/mol)']]
                    for _, r in dfg_valid.head(10).iterrows():  # Top 10 by affinity
                        pdb_name = Path(r['pdb']).name
                        pocket_rank = r.get('pocket_rank', 1)
                        affinity = f"{r['affinity']:.2f}"
                        data.append([pdb_name, str(pocket_rank), affinity])

                    story.append(Paragraph('Docking Results (Top 10 by Affinity)', styles['Heading2']))
                    t = Table(data)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 20))
            except Exception as e:
                logger.error(f"Failed to add docking summary to report: {e}")
                story.append(Paragraph('Error loading docking data', styles['Normal']))
                story.append(Spacer(1, 12))

        # Generated PDB files
        pdb_files = sorted(pdb_dir.glob('*.pdb'))
        if pdb_files:
            story.append(Paragraph(f'Generated PDB Files ({len(pdb_files)} total)', styles['Heading2']))
            story.append(Spacer(1, 6))
            for p in pdb_files[:20]:  # Limit to first 20
                story.append(Paragraph(f'• {p.name}', styles['Normal']))
            if len(pdb_files) > 20:
                story.append(Paragraph(f'... and {len(pdb_files) - 20} more', styles['Normal']))
            story.append(Spacer(1, 12))

        # Build document
        doc.build(story)
        logger.info(f"Report generated successfully: {out_pdf}")

    except Exception as e:
        logger.error(f"Failed to build report: {e}")
        raise

