"""
将 TM-align 的 CSV 结果导入 SQLite 数据库

适用于 tm_align_by_sample 目录结构：
    tm_align_by_sample/
        sample_id_1/
            comparison_results.csv   # 表头: Query, Target, RMSD, TM_score, Alignment_length
        sample_id_2/
            comparison_results.csv
        ...

用法：
    python -m protflow.cli.import_tm_align_csv_to_db --input ./tm_align_by_sample --output ./tm_align_results.db
    python -m protflow.cli.import_tm_align_csv_to_db -i /path/to/tm_align_by_sample -o ./results.db --replace
"""
import argparse
import importlib.util
import logging
import sys
from pathlib import Path

# 仅加载 tm_align_db，避免触发 protflow.core 的 torch 等依赖
_this_dir = Path(__file__).resolve().parent
_src_root = _this_dir.parent.parent
if str(_src_root) not in sys.path:
    sys.path.insert(0, str(_src_root))
_spec = importlib.util.spec_from_file_location(
    "tm_align_db", _this_dir.parent / "core" / "tm_align_db.py"
)
tm_align_db = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tm_align_db)
get_connection = tm_align_db.get_connection
create_schema = tm_align_db.create_schema
import_from_sample_dir = tm_align_db.import_from_sample_dir

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="将 tm_align_by_sample 下各样本的 comparison_results.csv 导入 SQLite",
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        required=True,
        help="tm_align_by_sample 根目录（包含各样本子目录，每目录下有 comparison_results.csv）",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("tm_align_results.db"),
        help="输出的 SQLite 数据库文件路径（默认: tm_align_results.db）",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="若表已存在则先删除再创建（默认仅追加，重复的 sample_id+query+target 会跳过）",
    )
    parser.add_argument(
        "--csv-name",
        default="comparison_results.csv",
        help="每个样本目录下的 CSV 文件名（默认: comparison_results.csv）",
    )
    parser.add_argument(
        "--sample-dirs",
        nargs="*",
        default=None,
        help="仅导入这些样本子目录名；不指定则导入所有子目录",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5000,
        help="每批写入行数（默认: 5000）",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="不显示进度条",
    )
    args = parser.parse_args()

    input_dir = args.input.resolve()
    if not input_dir.is_dir():
        logger.error("输入目录不存在: %s", input_dir)
        return 1

    db_path = args.output.resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection(db_path)
    try:
        if args.replace:
            conn.execute("DROP TABLE IF EXISTS tm_align_results")
            conn.commit()
        total = import_from_sample_dir(
            conn,
            input_dir,
            csv_name=args.csv_name,
            batch_size=args.batch_size,
            sample_dirs=args.sample_dirs,
            progress=not args.no_progress,
        )
        logger.info("共导入 %d 行到 %s", total, db_path)
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
