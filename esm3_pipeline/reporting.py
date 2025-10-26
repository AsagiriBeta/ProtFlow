from pathlib import Path
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
import ast


def build_report(base: Path, pdb_dir: Path, out_pdf: Path) -> None:
    doc = SimpleDocTemplate(str(out_pdf))
    styles = getSampleStyleSheet()
    story = [Paragraph('ESM3-sm Prediction Report', styles['Title']), Spacer(1, 12)]

    # Pockets summary
    pock_csv = base / 'pockets_summary.csv'
    if pock_csv.exists():
        dfp = pd.read_csv(pock_csv)
        data = [['PDB', 'Score', 'CenterX', 'CenterY', 'CenterZ']]
        for _, r in dfp.iterrows():
            cx, cy, cz = ast.literal_eval(r['center']) if isinstance(r['center'], str) else r['center']
            data.append([Path(r['pdb']).name, r['score'], cx, cy, cz])
        story.append(Paragraph('Pocket prediction summary:', styles['Heading2']))
        story.append(Table(data))
        story.append(Spacer(1, 12))

    # Docking summary
    vina_csv = base / 'vina_results.csv'
    if vina_csv.exists():
        dfg = pd.read_csv(vina_csv)
        data = [['PDB', 'Affinity (kcal/mol)']]
        for _, r in dfg.iterrows():
            data.append([Path(r['pdb']).name, r['affinity']])
        story.append(Paragraph('Docking results:', styles['Heading2']))
        story.append(Table(data))
        story.append(Spacer(1, 12))

    # Generated PDB files
    story.append(Paragraph('Generated PDB files:', styles['Heading2']))
    for p in sorted(pdb_dir.glob('*.pdb')):
        story.append(Paragraph(p.name, styles['Normal']))

    doc.build(story)

