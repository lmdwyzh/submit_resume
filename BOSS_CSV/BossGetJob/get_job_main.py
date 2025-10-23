# boss_main.py
from DrissionPage._pages.chromium_page import ChromiumPage

from BOSS_CSV.BossGetJob.boss_interactor import send_message_to_hr
from BOSS_CSV.BossGetJob.job_parser import read_jobs_file, extract_job_blocks, parse_job_block
from BOSS_CSV.BossGetJob.content_generator import get_introduction, get_prompt_template
from ToolCategory.AiTool import AiTool
from ToolCategory.ToolCategory import ToolCategory

def extract_job_descriptions_and_urls():
    """主函数：提取职位描述和URL并发送消息"""
    page = ChromiumPage()
    bot = AiTool()

    content = read_jobs_file(r"./resources/jobs.md"
)
    blocks = extract_job_blocks(content)
    introduce = get_introduction()
    prompt = get_prompt_template()


    for idx, block in enumerate(blocks):
        # print(block)





        desc, url = parse_job_block(block)
        # print(desc)

        if not desc or not url:
            continue

        print(f'【职位描述 {idx}】')
        print(desc)
        print('网址:', url)





        success = send_message_to_hr(page, bot, url, desc, introduce, prompt)
        if success and success == '今天已经达到上限':
           return '今天已经达到上限'


        print('-' * 80)

    tool_category = ToolCategory()
    tool_category.clear_file_content(r"./resources/jobs.md")
    return True


if __name__ == "__main__":
    extract_job_descriptions_and_urls()
