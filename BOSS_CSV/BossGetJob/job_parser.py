# job_parser.py
import re
from typing import List, Tuple, Optional


def extract_job_blocks(content: str) -> List[str]:
    """提取职位信息块"""
    return re.split(r'---', content.strip())


import re
from typing import Tuple, Optional

def parse_job_block(block: str) -> Tuple[Optional[str], Optional[str]]:
    """解析单个职位块，返回描述和URL"""
    # 1. 抓第一对 ``` ... ```
    desc_match = re.search(r'```(.*?)```', block, re.DOTALL)
    if not desc_match:
        return None, None

    desc = desc_match.group(1).strip()
    desc = re.sub(r'\s+', ' ', desc)        # 把换行和多余空白折叠成一个空格

    # 2. 抓 URL
    url_match = re.search(r'\[.*?\]\((https?://[^\s\)]+)\)', block)
    url = url_match.group(1) if url_match else None

    return desc, url


def read_jobs_file(file_path: str) -> str:
    """读取职位信息文件"""
    with open(file_path, encoding='utf-8') as f:
        return f.read()
if __name__ == '__main__':
    print()
    # parse_job_block(block) :