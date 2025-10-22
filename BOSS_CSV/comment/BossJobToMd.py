import os
import random


def generate_random_filename():
    """生成一个随机的八位数文件名"""
    return str(random.randint(10000000, 99999999))


def boss_job_to_md(job_info):
    # 指定文档路径
    doc_path = r"C:\Users\lmdwy\Desktop\Folder\Projects\PycharmProjects\Sheayoo\Game_assistance\BOSS_CSV\resources\jobs.md"
    os.makedirs(os.path.dirname(doc_path), exist_ok=True)
    # 检查链接是否已存在
    if os.path.exists(doc_path):
        with open(doc_path, "r", encoding="utf-8") as md_file:
            content = md_file.read()
            if job_info['招聘链接'] in content:
                print(f"职位链接 {job_info['招聘链接']} 已存在，跳过写入。")
                return job_info['招聘链接']

    with open(doc_path, "a", encoding="utf-8") as md_file:
        # 添加职位标题

        md_file.write(f"## [{job_info['职位']}]({job_info['招聘链接']})\n\n")
        md_file.write(f"**{job_info['公司名称']}**\n")
        # 添加活跃状态
        md_file.write(f"- **BOSS最近活跃**: {job_info['BOSS活跃']}\n\n")
        md_file.write(f"- **薪资范围**: {job_info['薪资范围']}\n\n")

        # 添加关键信息
        md_file.write(f"- **职位描述**: \n```\n{job_info['职位描述']}\n```\n\n")
        md_file.write(f"- **工作地点**: {job_info['工作地点']}\n")
        md_file.write(f"- **工作经验**: {job_info['工作年限要求']}\n")
        md_file.write(f"- **学历要求**: {job_info['学历要求']}\n\n")

        # 添加公司信息

        md_file.write(f"- **公司名称**: {job_info['公司名称']}\n")
        md_file.write(f"- **公司规模**: {job_info['公司规模']}\n")
        md_file.write(f"- **行业领域**: {job_info['公司行业']}\n\n")

        # 添加职位要求

        md_file.write(f"- **必备技能**: {job_info['职位要求技能']}\n\n")

        # 添加福利信息

        md_file.write(f"- **福利信息**: {job_info['福利'] if job_info['福利'] else '无特别福利信息'}\n\n")



        # 添加分隔线
        md_file.write("---\n\n")
    return job_info['招聘链接']


if __name__ == '__main__':
    job_data = {
        'BOSS活跃': '刚刚活跃',
        '职位': '数字孪生工程师',
        '薪资范围': '3-6K',
        '最低薪资': 3000,
        '是否低薪': True,
        '工作年限要求': '经验不限',
        '学历要求': '大专',
        '工作地点': '宜昌',
        '公司名称': '宜昌祈泰',
        '公司规模': '20-99人',
        '公司阶段': '',
        '公司行业': '自动化设备',
        '福利': '福利信息未提供',
        '职位要求技能': 'OpenGL'
    }
    boss_job_to_md(job_data)