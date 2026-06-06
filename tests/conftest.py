import sys
from pathlib import Path

# srcディレクトリをパスに追加
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
