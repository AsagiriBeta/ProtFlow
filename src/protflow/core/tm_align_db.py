"""
TM-align 结果 CSV 导入数据库

将 tm_align_by_sample 下各样本的 comparison_results.csv 导入 SQLite（或通过适配层支持其他库）。
便于按 sample_id / query / target 查询、聚合和与其它表关联。
"""
import csv
import sqlite3
import logging
from pathlib import Path
from typing import Optional, Iterator, Tuple, List

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

logger = logging.getLogger(__name__)

# 与 structure_comparison 中 CSV 表头一致
CSV_HEADER = ["Query", "Target", "RMSD", "TM_score", "Alignment_length"]
DEFAULT_CSV_NAME = "comparison_results.csv"


def get_connection(db_path: Path, timeout: float = 60.0) -> sqlite3.Connection:
    """
    打开 SQLite 连接。timeout 为锁等待秒数，避免「database is locked」立即报错。
    启用外键与 WAL 以减轻并发锁冲突。
    """
    conn = sqlite3.connect(Path(db_path), timeout=timeout)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """
    创建 TM-align 结果表。
    (sample_id, query, target) 唯一，便于 INSERT OR IGNORE 去重与按样本查询。
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tm_align_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            query TEXT NOT NULL,
            target TEXT NOT NULL,
            rmsd REAL NOT NULL,
            tm_score REAL NOT NULL,
            alignment_length INTEGER,
            source_file TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(sample_id, query, target)
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_tm_align_sample ON tm_align_results(sample_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_tm_align_tm_score ON tm_align_results(tm_score)"
    )
    conn.commit()


def _parse_row(row: List[str]) -> Optional[Tuple[str, str, float, float, Optional[int]]]:
    """解析一行 CSV：query, target, rmsd, tm_score, alignment_length。"""
    if len(row) < 4:
        return None
    query = (row[0] or "").strip()
    target = (row[1] or "").strip()
    if not query or not target:
        return None
    try:
        rmsd = float(row[2])
        tm_score = float(row[3])
    except (ValueError, TypeError):
        return None
    alen: Optional[int] = None
    if len(row) >= 5 and (row[4] or "").strip():
        try:
            alen = int(row[4])
        except (ValueError, TypeError):
            pass
    return (query, target, rmsd, tm_score, alen)


def import_csv_to_db(
    conn: sqlite3.Connection,
    csv_path: Path,
    sample_id: str,
    *,
    source_file: Optional[str] = None,
    batch_size: int = 5000,
) -> int:
    """
    将单个 comparison_results.csv 导入当前连接的表。
    使用 INSERT OR IGNORE 跳过 (sample_id, query, target) 重复行。
    返回插入的行数（不含跳过的）。
    """
    csv_path = Path(csv_path)
    if not csv_path.is_file():
        logger.warning("CSV not found: %s", csv_path)
        return 0
    source = source_file or str(csv_path)
    inserted = 0
    batch: List[Tuple[str, str, str, float, float, Optional[int], str]] = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header and [h.strip() for h in header[:5]] != CSV_HEADER[:5]:
            logger.debug("CSV header %s in %s", header, csv_path)
        for row in reader:
            parsed = _parse_row(row)
            if parsed is None:
                continue
            query, target, rmsd, tm_score, alignment_length = parsed
            batch.append((sample_id, query, target, rmsd, tm_score, alignment_length, source))
            if len(batch) >= batch_size:
                inserted += _insert_batch(conn, batch)
                batch = []
        if batch:
            inserted += _insert_batch(conn, batch)
    conn.commit()
    return inserted


def _insert_batch(
    conn: sqlite3.Connection,
    batch: List[Tuple[str, str, str, float, float, Optional[int], str]],
) -> int:
    """执行一批 INSERT OR IGNORE，返回本批插入行数。"""
    if not batch:
        return 0
    before = conn.total_changes
    conn.executemany(
        """
        INSERT OR IGNORE INTO tm_align_results
        (sample_id, query, target, rmsd, tm_score, alignment_length, source_file)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        batch,
    )
    return conn.total_changes - before


def iter_sample_csv_dirs(
    tm_align_by_sample_root: Path,
    csv_name: str = DEFAULT_CSV_NAME,
) -> Iterator[Tuple[Path, str]]:
    """
    遍历 tm_align_by_sample 根目录下每个样本子目录及其 comparison_results.csv。
    产出 (csv_path, sample_id)。

    支持两种目录结构：
    - 扁平：root/<sample_id>/comparison_results.csv → sample_id 为目录名
    - 嵌套：root/<run_name>/<sample_id>/comparison_results.csv → sample_id 为 run_name/sample_id
    """
    root = Path(tm_align_by_sample_root)
    if not root.is_dir():
        return
    for sub in sorted(root.iterdir()):
        if not sub.is_dir() or sub.name.startswith("."):
            continue
        csv_path = sub / csv_name
        if csv_path.is_file():
            yield (csv_path, sub.name)
            continue
        # 直接子目录下没有 CSV：再向下一层查找（如 tm_align_esm3_vs_bf_structure/<sample_id>/comparison_results.csv）
        for grand in sorted(sub.iterdir()):
            if not grand.is_dir() or grand.name.startswith("."):
                continue
            grand_csv = grand / csv_name
            if grand_csv.is_file():
                yield (grand_csv, f"{sub.name}/{grand.name}")


def import_from_sample_dir(
    conn: sqlite3.Connection,
    tm_align_by_sample_root: Path,
    *,
    csv_name: str = DEFAULT_CSV_NAME,
    batch_size: int = 5000,
    sample_dirs: Optional[List[str]] = None,
    progress: bool = True,
) -> int:
    """
    将 tm_align_by_sample 根目录下各样本的 comparison_results.csv 全部导入。
    sample_dirs 若指定，则只处理这些子目录名；否则处理所有子目录。
    progress 为 True 时在终端显示样本进度条。
    返回总插入行数。
    """
    create_schema(conn)
    tasks = [
        (csv_path, sample_id)
        for csv_path, sample_id in iter_sample_csv_dirs(
            tm_align_by_sample_root, csv_name=csv_name
        )
        if sample_dirs is None or sample_id in sample_dirs
    ]
    total = 0
    iterator = tasks
    if progress and tqdm is not None:
        iterator = tqdm(
            tasks,
            desc="导入样本",
            unit="样本",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}] {postfix}",
        )
    for csv_path, sample_id in iterator:
        n = import_csv_to_db(
            conn, csv_path, sample_id, batch_size=batch_size
        )
        total += n
        if n > 0 and progress and tqdm is not None and hasattr(iterator, "set_postfix"):
            iterator.set_postfix_str(f"刚导入 {n} 行，累计 {total} 行", refresh=False)
        if n > 0:
            logger.debug("Imported %s: %d rows from %s", sample_id, n, csv_path)
    return total
