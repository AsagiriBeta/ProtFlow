from pathlib import Path
from typing import Iterable

import torch


def load_esm3_small(device: str = None):
    """Lazy import ESM3 small model."""
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    from esm.models.esm3 import ESM3
    model = ESM3.from_pretrained('esm3-sm-open-v1').to(device)
    return model, device


def predict_pdbs(model, seq_records: Iterable, out_dir: Path) -> None:
    from esm.sdk.api import ESMProtein, GenerationConfig
    out_dir.mkdir(parents=True, exist_ok=True)
    for rec in seq_records:
        seq = str(rec.seq)
        name = rec.id.replace('|','_')[:80]
        prot = ESMProtein(sequence=seq)
        prot = model.generate(prot, GenerationConfig(track='structure', num_steps=8))
        outp = out_dir / f'{name}.pdb'
        prot.to_pdb(str(outp))

