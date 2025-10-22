import csv
import os
import re
from typing import Optional

from BOSS_CSV.comment.BossJobToMd import boss_job_to_md
from ToolCategory.CSVJsonProcessor import CSVJsonProcessor

# -------------------- 配置开关 --------------------
ENABLE_JAVA_FILTER    = True      # 是否启用「Java/后端」过滤（仅当关键词过滤关闭时才生效）
WRITE_NO_DELIVER      = True      # 是否把被过滤的职位落库到 no_deliver
# -------------------------------------------------

# 预编译正则，加速“经验年限”判断
EXPERIENCE_PATTERN = re.compile(r"[3-5]年以上|三年以上|四年以上|五年以上")

# 关键词集合，全大写后精确整词匹配（可根据需要调整）
JOB_KEYWORDS = {
    "C++", "日", "爬虫", "策划", "安卓", "教师", "外包", "现场", "ANDROID",
    "测试", "老师", "前端", "驻场", "视觉", "设计", "实施", "运维",
    "嵌入式", "少儿", "日本", "ERP", "QT"
}



# 核心判断：能否投递
def _should_deliver(job: dict) -> bool:
    """返回 True 表示可以投递，False 表示需要过滤。"""
    # 1. 关键词过滤
    title_up = job.get("职位", "").upper()
    if any(kw.upper() in title_up for kw in JOB_KEYWORDS):
        job["过滤原因"] = "包含其他关键词"
        return False

    # 如果开启Java过滤，保留包含Java或后端的职位
    if ENABLE_JAVA_FILTER:
        if not any(k in title_up for k in ("JAVA", "后端")):
            job["过滤原因"] = "不包含Java"
            return False





    # 3. BOSS 活跃度
    if job.get("BOSS活跃") not in {"刚刚活跃", "今日活跃", "3日内活跃"}:
        job["过滤原因"] = "BOSS活跃"
        return False


    if job['最低薪资'] =="" or job['最高薪资'] =="":
        job["过滤原因"] = "没有薪资"
        return False

    # 5. 薪资区间
    if job['最高薪资'] <= 4000:
        job["过滤原因"] = "薪资过低"
        return False
    if job['最低薪资'] >= 10000:
        job["过滤原因"] = "薪资过高"
        return False

    # 6. 经验年限
    desc = job.get("职位描述", "")
    if EXPERIENCE_PATTERN.search(desc):
        job["过滤原因"] = "需要经验"
        return False

    return True


# -------------------- 对外唯一入口 --------------------
def boss_filter(job_info: dict) -> Optional[str]:
    """
    根据职位信息判断是否可投递。
    可投递：生成 Markdown 并落库 job_deliver，返回生成好的招聘链接；
    被过滤：视 WRITE_NO_DELIVER 决定是否落库 no_deliver，返回 None。
    """
    processor = CSVJsonProcessor("./resources")
    if _should_deliver(job_info):
        # 可投递
        md_link = boss_job_to_md(job_info)
        processor.process_json("job_deliver", job_info, unique_field="招聘链接")
        return md_link

    # 被过滤
    if WRITE_NO_DELIVER:
        processor.process_json("no_deliver", job_info, unique_field="招聘链接")
    return None