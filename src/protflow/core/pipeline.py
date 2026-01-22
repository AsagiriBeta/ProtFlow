"""
Prokka → ESM3 → DALI 完整工作流管道

提供端到端的基因组注释、结构预测和DALI准备功能。
"""

import shutil
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from Bio import SeqIO

from ..prediction.esm3_predict import (
    ESM3GenerationConfig,
    load_esm3_small,
    predict_pdbs,
)
from ..utils.seq_parser import extract_proteins_from_gbk


class ProkkaESM3Pipeline:
    """
    Prokka -> ESM3 -> DALI 工作流管道
    
    提供完整的基因组注释到结构预测的工作流。
    """
    
    def __init__(self, work_dir: Path):
        """
        初始化管道
        
        Args:
            work_dir: 工作目录路径
        """
        self.work_dir = Path(work_dir)
        self.prokka_dir = self.work_dir / "prokka_output"
        self.pdb_dir = self.work_dir / "esm3_structures"
        self.dali_dir = self.work_dir / "dali_ready"
        
        # 创建目录
        for d in [self.prokka_dir, self.pdb_dir, self.dali_dir]:
            d.mkdir(exist_ok=True, parents=True)
        
        self.model = None
        self.device = None
    
    def run_prokka(
        self,
        fna_file: Path,
        prefix: str = "sample",
        kingdom: str = "Bacteria",
        cpus: int = 2,
        prokka_cmd: Optional[List[str]] = None,
        **kwargs
    ) -> Path:
        """
        运行 Prokka 进行基因注释
        
        Args:
            fna_file: 输入的 FNA 文件路径
            prefix: 输出文件前缀
            kingdom: 生物界（Bacteria, Archaea, Viruses）
            cpus: 使用的 CPU 核心数
            prokka_cmd: Prokka命令（如果为None，使用默认micromamba命令）
            **kwargs: 其他 Prokka 参数
        
        Returns:
            Prokka 输出目录路径
        """
        print(f"\n{'='*60}")
        print("步骤 1: 运行 Prokka 进行基因注释")
        print(f"{'='*60}")
        
        output_dir = self.prokka_dir / prefix
        
        # 构建 Prokka 命令
        if prokka_cmd is None:
            cmd = [
                "micromamba", "run", "-n", "prokka", "prokka",
                "--outdir", str(output_dir),
                "--prefix", prefix,
                "--kingdom", kingdom,
                "--cpus", str(cpus),
                "--force",
            ]
        else:
            cmd = list(prokka_cmd) + [
                "--outdir", str(output_dir),
                "--prefix", prefix,
                "--kingdom", kingdom,
                "--cpus", str(cpus),
                "--force",
            ]
        
        # 添加额外参数
        for key, value in kwargs.items():
            cmd.extend([f"--{key}", str(value)])
        
        cmd.append(str(fna_file))
        
        print(f"运行命令: {' '.join(cmd)}")
        print("\n正在运行 Prokka（这可能需要几分钟）...")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("\n✓ Prokka 运行成功！")
            
            # 显示统计信息
            stats_file = output_dir / f"{prefix}.txt"
            if stats_file.exists():
                print("\n注释统计:")
                print(stats_file.read_text())
            
            return output_dir
            
        except subprocess.CalledProcessError as e:
            print(f"\n✗ Prokka 运行失败: {e}")
            print(f"错误输出: {e.stderr}")
            raise
    
    def load_esm3_model(self, model_name: str = 'esm3-sm-open-v1', device: Optional[str] = None):
        """
        加载 ESM3 模型（使用共享模块）
        
        Args:
            model_name: ESM3 模型名称
            device: 设备（'cuda'/'cpu'，None为自动检测）
        """
        print(f"\n{'='*60}")
        print("步骤 2: 加载 ESM3 模型")
        print(f"{'='*60}")
        
        self.model, self.device = load_esm3_small(
            device=device,
            model_name=model_name,
            use_cache=True
        )
        
        print(f"✅ Model loaded successfully on {self.device}")
        print()
    
    def predict_structures(
        self,
        prokka_dir: Path,
        prefix: str,
        generation_config: Optional[ESM3GenerationConfig] = None,
        num_steps: int = 8,
        max_length: int = 400,
        min_length: int = 30,
        temperature: Optional[float] = None,
        batch_size: Optional[int] = None,  # Batch size for ESM3 inference
    ) -> List[Path]:
        """
        使用 ESM3 预测蛋白质结构
        
        Args:
            prokka_dir: Prokka 输出目录
            prefix: Prokka 输出前缀
            generation_config: ESM3生成配置（如果为None，使用num_steps和temperature）
            num_steps: ESM3 生成步数（如果generation_config为None）
            max_length: 最大序列长度
            min_length: 最小序列长度
            temperature: 温度参数（如果generation_config为None）
            batch_size: Batch size for ESM3 inference (None = process individually)
                       Larger batch sizes can improve GPU utilization but require more memory.
                       Recommended: 4-16 for GPU, 1-4 for CPU.
        
        Returns:
            生成的 PDB 文件路径列表
        """
        print(f"\n{'='*60}")
        print("步骤 3: 使用 ESM3 预测蛋白质结构")
        print(f"{'='*60}")
        
        if self.model is None:
            self.load_esm3_model()
        
        # 读取 Prokka 输出的蛋白质序列
        faa_file = prokka_dir / f"{prefix}.faa"
        
        if not faa_file.exists():
            raise FileNotFoundError(f"找不到 Prokka 蛋白质文件: {faa_file}")
        
        # 解析序列
        sequences = list(SeqIO.parse(faa_file, "fasta"))
        print(f"\n从 Prokka 读取到 {len(sequences)} 条蛋白质序列")
        
        # 创建配置
        if generation_config is None:
            generation_config = ESM3GenerationConfig(
                track='structure',
                num_steps=num_steps,
                temperature=temperature
            )
        
        # 使用共享模块预测
        results = predict_pdbs(
            model=self.model,
            seq_records=sequences,
            out_dir=self.pdb_dir,
            generation_config=generation_config,
            min_seq_length=min_length,
            max_seq_length=max_length,
            show_progress=True,
            skip_existing=True,
            batch_size=batch_size
        )
        
        # 获取生成的PDB文件
        pdb_files = list(self.pdb_dir.glob("*.pdb"))
        
        print(f"\n✓ 结构预测完成！")
        print(f"  成功: {results['success']}")
        print(f"  跳过: {results['skipped']}")
        print(f"  错误: {results['errors']}")
        print(f"  过滤: {results['filtered']}")
        
        return pdb_files
    
    def prepare_for_dali(self, pdb_files: List[Path]) -> Path:
        """
        准备符合 DALI 输入标准的文件
        
        Args:
            pdb_files: PDB 文件路径列表
        
        Returns:
            DALI 输出目录路径
        """
        from ..prediction.dali import prepare_pdb_for_dali
        
        return prepare_pdb_for_dali(
            pdb_files=pdb_files,
            output_dir=self.dali_dir
        )
    
    def create_download_package(self, prefix: str) -> Path:
        """
        创建可下载的压缩包
        
        Args:
            prefix: 输出文件前缀
        
        Returns:
            压缩包路径
        """
        print(f"\n{'='*60}")
        print("步骤 5: 创建下载包")
        print(f"{'='*60}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_file = self.work_dir / f"{prefix}_results_{timestamp}.zip"
        
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 添加 Prokka 结果
            print("\n打包 Prokka 结果...")
            for file in self.prokka_dir.rglob('*'):
                if file.is_file():
                    arcname = file.relative_to(self.work_dir)
                    zf.write(file, arcname)
            
            # 添加 ESM3 结构
            print("打包 ESM3 结构...")
            for file in self.pdb_dir.rglob('*.pdb'):
                arcname = file.relative_to(self.work_dir)
                zf.write(file, arcname)
            
            # 添加 DALI 文件
            print("打包 DALI 文件...")
            for file in self.dali_dir.rglob('*'):
                if file.is_file():
                    arcname = file.relative_to(self.work_dir)
                    zf.write(file, arcname)
        
        size_mb = zip_file.stat().st_size / (1024 * 1024)
        print(f"\n✓ 压缩包创建完成！")
        print(f"  文件: {zip_file.name}")
        print(f"  大小: {size_mb:.2f} MB")
        
        return zip_file
    
    def run_full_pipeline(
        self,
        fna_file: Path,
        prefix: str = "sample",
        kingdom: str = "Bacteria",
        generation_config: Optional[ESM3GenerationConfig] = None,
        num_steps: int = 8,
        max_seq_length: int = 400,
        min_seq_length: int = 30,
        **prokka_kwargs
    ) -> Path:
        """
        运行完整工作流
        
        Args:
            fna_file: 输入的 FNA 文件
            prefix: 输出文件前缀
            kingdom: 生物界
            generation_config: ESM3生成配置
            num_steps: ESM3 生成步数（如果generation_config为None）
            max_seq_length: 最大序列长度
            min_seq_length: 最小序列长度
            **prokka_kwargs: Prokka 额外参数
        
        Returns:
            下载包路径
        """
        start_time = datetime.now()
        print(f"\n{'='*60}")
        print("Prokka → ESM3 → DALI 工作流")
        print(f"{'='*60}")
        print(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"输入文件: {fna_file}")
        print(f"输出前缀: {prefix}")
        
        # 步骤 1: Prokka 注释
        prokka_dir = self.run_prokka(fna_file, prefix, kingdom, **prokka_kwargs)
        
        # 步骤 2-3: ESM3 结构预测
        pdb_files = self.predict_structures(
            prokka_dir,
            prefix,
            generation_config=generation_config,
            num_steps=num_steps,
            max_length=max_seq_length,
            min_length=min_seq_length
        )
        
        # 步骤 4: 准备 DALI 文件
        self.prepare_for_dali(pdb_files)
        
        # 步骤 5: 创建下载包
        zip_file = self.create_download_package(prefix)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n{'='*60}")
        print("✓ 工作流完成！")
        print(f"{'='*60}")
        print(f"总耗时: {duration}")
        print(f"\n结果文件: {zip_file}")
        
        return zip_file
