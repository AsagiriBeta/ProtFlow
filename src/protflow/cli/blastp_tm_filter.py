"""
TM-align 筛选 + BLASTP：从 tm_align_results 中筛出 TM-score > 阈值且 RMSD < 阈值的 (query, target)，
用 Prokka 的 query 序列与 bf_seq 的 target 序列做 BLASTP，结果写入同一库的 blast_results 表。

筛选条件（默认）：tm_score > 0.75 且 rmsd < 3.5。

用法：
    # 一键命令（先设置环境变量，筛选条件默认 TM-score > 0.75 且 RMSD < 3.5）：
    export PROKKA_DIR=/path/to/prokka_results
    export BF_SEQ_DIR=/path/to/bf_seq
    python -m protflow.cli.blastp_tm_filter

    # 或直接传路径：
    python -m protflow.cli.blastp_tm_filter --db ./tm_align_results.db --prokka /path/to/prokka_results --bf-seq /path/to/bf_seq
    python -m protflow.cli.blastp_tm_filter --db ./tm_align_results.db --tm-cutoff 0.75 --rmsd-cutoff 3.5 -w 150
"""
import os
import sqlite3
import tempfile
import argparse
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed

from Bio.Blast.Applications import NcbiblastpCommandline
from Bio.Blast import NCBIXML
from Bio import SeqIO
from tqdm import tqdm

if os.path.exists("/dev/shm"):
    tempfile.tempdir = "/dev/shm"

# ---------------------------------------------------------------------------
# 数据库
# ---------------------------------------------------------------------------

def get_connection(db_path: Path, timeout: float = 60.0) -> sqlite3.Connection:
    """打开 SQLite，WAL + timeout 防锁。"""
    conn = sqlite3.connect(str(Path(db_path)), timeout=timeout)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    return conn


def create_blast_schema(conn: sqlite3.Connection) -> None:
    """创建 blast_results 表及索引。"""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS blast_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            query TEXT NOT NULL,
            target TEXT NOT NULL,
            e_value REAL,
            score REAL,
            identity REAL,
            UNIQUE(sample_id, query, target)
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS ix_blast_sample ON blast_results(sample_id)")
    conn.commit()


def _insert_batch(conn: sqlite3.Connection, batch: list) -> int:
    """INSERT OR IGNORE 一批，返回本批实际新增行数。"""
    if not batch:
        return 0
    before = conn.total_changes
    conn.executemany(
        """
        INSERT OR IGNORE INTO blast_results
        (sample_id, query, target, e_value, score, identity)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        batch,
    )
    return conn.total_changes - before


# ---------------------------------------------------------------------------
# 序列加载
# ---------------------------------------------------------------------------

def preload_target_sequences(directory: Path) -> dict:
    """
    加载 bf_seq 目录下所有 .fasta/.fa 的序列。
    以 rec.id（及首词）为主键；单条记录时同时用文件 stem 作为键，多条时 stem 取第一条。
    """
    cache = {}
    path = Path(directory)
    print(f"[*] 正在加载 Target 序列库: {path}")
    fasta_files = list(path.glob("*.fasta")) + list(path.glob("*.fa"))

    for f_path in fasta_files:
        stem_name = f_path.stem.strip()
        for enc in ("utf-8", "latin-1", "gbk"):
            try:
                with open(f_path, "r", encoding=enc) as f:
                    for rec in SeqIO.parse(f, "fasta"):
                        seq_str = str(rec.seq)
                        key = rec.id.split()[0] if rec.id.split() else rec.id
                        cache[key] = seq_str
                        cache[rec.id.strip()] = seq_str
                        if stem_name not in cache:
                            cache[stem_name] = seq_str
                break
            except Exception:
                continue
    print(f"[+] Target 序列载入完成: {len(fasta_files)} 个文件, {len(cache)} 个键")
    return cache


def load_prokka_queries_for_sample(prokka_root: Path, sample_id: str) -> dict:
    """根据 sample_id 取 Prokka 样本目录下 .faa 中所有序列，返回 id -> seq。"""
    real_id = Path(sample_id).name.strip()
    sample_dir = prokka_root / real_id
    if not sample_dir.exists():
        return {}
    faa_files = list(sample_dir.glob("*.faa"))
    if not faa_files:
        return {}
    found = {}
    try:
        with open(faa_files[0], "r", encoding="utf-8", errors="ignore") as f:
            for rec in SeqIO.parse(f, "fasta"):
                full_id = rec.id.strip()
                short_id = full_id.split()[0]
                seq = str(rec.seq)
                found[full_id] = found[short_id] = seq
    except Exception:
        pass
    return found


# ---------------------------------------------------------------------------
# BLASTP worker（子进程内运行）
# ---------------------------------------------------------------------------

def _blastp_worker(task_data: tuple) -> tuple | None:
    """对单对 (query_seq, target_seq) 跑 BLASTP，返回 (sample_id, query, target, e_value, score, identity) 或 None。"""
    s_id, q_id, t_id, q_seq, t_seq = task_data
    q_path = t_path = out_xml = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".fasta", delete=False) as q_f:
            q_path = q_f.name
            q_f.write(f">query\n{q_seq}\n")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".fasta", delete=False) as t_f:
            t_path = t_f.name
            t_f.write(f">target\n{t_seq}\n")
        out_f = tempfile.NamedTemporaryFile(suffix=".xml", delete=False)
        out_xml = out_f.name
        out_f.close()

        cline = NcbiblastpCommandline(query=q_path, subject=t_path, outfmt=5, out=out_xml)
        cline()

        if os.path.exists(out_xml) and os.path.getsize(out_xml) > 0:
            with open(out_xml) as res_handle:
                records = list(NCBIXML.parse(res_handle))
                if records and records[0].alignments:
                    hsp = records[0].alignments[0].hsps[0]
                    identity = (hsp.identities / hsp.align_length) if hsp.align_length else 0.0
                    return (s_id, q_id, t_id, hsp.expect, hsp.score, identity)
    except Exception:
        pass
    finally:
        for p in (q_path, t_path, out_xml):
            if p and os.path.exists(p):
                try:
                    os.unlink(p)
                except OSError:
                    pass
    return None


def blastp_worker(task_data: tuple) -> tuple | None:
    """兼容多进程调用的包装（多进程时子进程会重新导入，finally 在 return 之后仍会执行）。"""
    return _blastp_worker(task_data)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def get_filtered_pairs(conn: sqlite3.Connection, tm_cutoff: float, rmsd_cutoff: float) -> list:
    """从 tm_align_results 中筛出 tm_score > tm_cutoff 且 rmsd < rmsd_cutoff 的 (sample_id, query, target)。"""
    cur = conn.execute(
        "SELECT sample_id, query, target FROM tm_align_results WHERE tm_score > ? AND rmsd < ?",
        (tm_cutoff, rmsd_cutoff),
    )
    return cur.fetchall()


def resolve_query_seq(found_queries: dict, q_id_clean: str) -> str | None:
    """从 Prokka 序列字典中解析 query 序列（支持精确 id 或包含匹配）。"""
    seq = found_queries.get(q_id_clean)
    if seq:
        return seq
    for k in found_queries:
        if q_id_clean in k or k in q_id_clean:
            return found_queries[k]
    return None


def resolve_target_seq(target_cache: dict, t_id_clean: str) -> str | None:
    """从 target 缓存解析序列。"""
    seq = target_cache.get(t_id_clean)
    if seq:
        return seq
    for k in target_cache:
        if k in t_id_clean:
            return target_cache[k]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="TM-align 筛选 (TM-score > 阈值, RMSD < 阈值) + BLASTP，结果写入 blast_results 表",
    )
    parser.add_argument("--db", type=Path, default=Path("tm_align_results.db"), help="SQLite 库路径（含 tm_align_results 表）")
    parser.add_argument("--prokka", type=Path, default=None, help="Prokka 结果根目录；不传时用环境变量 PROKKA_DIR")
    parser.add_argument("--bf-seq", type=Path, default=None, help="参考序列目录（bf_seq）；不传时用环境变量 BF_SEQ_DIR")
    parser.add_argument("--tm-cutoff", type=float, default=0.75, help="TM-score 下限（默认 0.75）")
    parser.add_argument("--rmsd-cutoff", type=float, default=3.5, help="RMSD 上限（默认 3.5）")
    parser.add_argument("-w", "--workers", type=int, default=150, help="BLASTP 并发进程数")
    args = parser.parse_args()

    _prokka = args.prokka or (Path(os.environ["PROKKA_DIR"]) if os.environ.get("PROKKA_DIR") else None)
    _bf_seq = args.bf_seq or (Path(os.environ["BF_SEQ_DIR"]) if os.environ.get("BF_SEQ_DIR") else None)
    prokka_root = _prokka.resolve() if _prokka else None
    bf_seq_dir = _bf_seq.resolve() if _bf_seq else None
    db_path = args.db.resolve()

    if not prokka_root or not prokka_root.is_dir():
        print("[!] 请指定 Prokka 目录：--prokka /path/to/prokka_results 或设置环境变量 PROKKA_DIR")
        return 1
    if not bf_seq_dir or not bf_seq_dir.is_dir():
        print("[!] 请指定 bf_seq 目录：--bf-seq /path/to/bf_seq 或设置环境变量 BF_SEQ_DIR")
        return 1

    if not db_path.is_file():
        print(f"[!] 数据库不存在: {db_path}")
        return 1

    target_cache = preload_target_sequences(bf_seq_dir)
    if not target_cache:
        print("[!] 未加载到任何 Target 序列")
        return 1

    read_conn = get_connection(db_path)
    create_blast_schema(read_conn)
    pairs = get_filtered_pairs(read_conn, args.tm_cutoff, args.rmsd_cutoff)
    read_conn.close()

    print(f"[*] 筛选条件: TM-score > {args.tm_cutoff}, RMSD < {args.rmsd_cutoff}")
    print(f"[*] 筛选出 {len(pairs)} 对 (sample_id, query, target)")

    sample_groups = defaultdict(list)
    for s_id, q_id, t_id in pairs:
        sample_groups[Path(s_id).name.strip()].append((s_id, q_id, t_id))

    tasks = []
    for real_id, qt_list in tqdm(sample_groups.items(), desc="组装序列"):
        found_queries = load_prokka_queries_for_sample(prokka_root, real_id)
        for orig_s_id, q_id, t_id in qt_list:
            q_seq = resolve_query_seq(found_queries, q_id.strip())
            t_seq = resolve_target_seq(target_cache, t_id.strip())
            if q_seq and t_seq:
                tasks.append((orig_s_id, q_id, t_id, q_seq, t_seq))

    print(f"[+] 有效 BLASTP 任务数: {len(tasks)}")
    if not tasks:
        return 0

    results_to_save = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(blastp_worker, t): t for t in tasks}
        for f in tqdm(as_completed(futures), total=len(tasks), desc="BLASTP", unit="pair"):
            res = f.result()
            if res:
                results_to_save.append(res)

    if not results_to_save:
        print("未产生有效 BLASTP 结果")
        return 0

    print(f"[*] 写入 {len(results_to_save)} 条结果到 blast_results...")
    write_conn = get_connection(db_path)
    batch_size = 5000
    total_inserted = 0
    for i in range(0, len(results_to_save), batch_size):
        batch = results_to_save[i : i + batch_size]
        write_conn.execute("BEGIN TRANSACTION")
        total_inserted += _insert_batch(write_conn, batch)
        write_conn.commit()
    write_conn.close()
    print(f"完成。结果条数 {len(results_to_save)}，实际新增（去重后）{total_inserted} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
