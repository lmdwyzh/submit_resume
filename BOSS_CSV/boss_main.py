
import time
from datetime import datetime

from DrissionPage import ChromiumPage
from DrissionPage._elements.none_element import NoneElement
from BOSS_CSV.comment.BuildBossUrl import build_boss_url
from BOSS_CSV.comment.Filter import boss_filter
from BOSS_CSV.comment.ParseSalary import parse_salary
from BOSS_CSV.BossGetJob.get_job_main import extract_job_descriptions_and_urls
from ToolCategory.CSVJsonProcessor import CSVJsonProcessor

from ToolCategory.ToolCategory import ToolCategory



tool_category = ToolCategory()
page = ChromiumPage()
# processor = MySQLJsonProcessor()
processor = CSVJsonProcessor("./resources")

# 启动监听功能
page.listen.start("job/detail.json")
# url=build_boss_url("武汉", query="java", experience="应届生,经验不限,1年以内,1-3年")
# url=build_boss_url("宜昌", query="java", experience="应届生,经验不限,1年以内,1-3年")
# url=build_boss_url("宜昌", query="java", experience="应届生,经验不限,1年以内,1-3年")
# url=build_boss_url("全国", query="java线上面试", experience="在校生,应届生,经验不限,1年以内,1-3年")
url=build_boss_url("武汉", query="java", experience="应届生,经验不限,1年以内,1-3年")

# url=build_boss_url("天津", query="java", experience="应届生,经验不限,1年以内,1-3年")
# url=build_boss_url("成都", query="qt", experience="应届生")

recruitment_links = []
request_record=0


def get_json(json_data):
    jobInfo_dic = json_data.get('zpData', {})
    # print(jobInfo_dic)

    encryptId = jobInfo_dic.get('jobInfo', {}).get('encryptId', '未知链接')
    href = "https://www.zhipin.com/job_detail/" + encryptId + ".html"
    salaryDesc = jobInfo_dic.get('jobInfo', {}).get('salaryDesc', '薪资信息未提供')
    min_salary, max_salary = parse_salary(salaryDesc)

    job_info = {
        'BOSS活跃': jobInfo_dic.get('bossInfo', {}).get('activeTimeDesc', ''),
        '职位': jobInfo_dic.get('jobInfo', {}).get('jobName', '未知职位'),
        '薪资范围': salaryDesc,
        '最低薪资': min_salary,
        '最高薪资': max_salary,
        '工作年限要求': jobInfo_dic.get('jobInfo', {}).get('experienceName', '工作年限未提供'),
        '招聘链接': href,
        '学历要求': jobInfo_dic.get('jobInfo', {}).get('degreeName', '学历要求未提供'),
        '工作地点': ' '.join(filter(None, [
            jobInfo_dic.get('jobInfo', {}).get('locationName', '城市未知'),
            jobInfo_dic.get('jobInfo', {}).get('areaDistrict', ''),
            jobInfo_dic.get('jobInfo', {}).get('businessDistrict', '')
        ])),
        '公司名称': jobInfo_dic.get('brandComInfo', {}).get('brandName', '公司名称未提供'),

        '公司规模': jobInfo_dic.get('brandComInfo', {}).get('scaleName', '公司规模未提供'),
        # '公司阶段': jobInfo_dic.get('brandComInfo', {}).get('stageName', '公司阶段未提供'),

        '公司行业': jobInfo_dic.get('brandComInfo', {}).get('industryName', '公司行业未提供'),
        '福利': ', '.join(jobInfo_dic.get('jobInfo', {}).get('welfareList', [])) if jobInfo_dic.get('jobInfo', {}).get(
            'welfareList') else '福利信息未提供',
        '职位要求技能': ', '.join(jobInfo_dic.get('jobInfo', {}).get('showSkills', [])) if jobInfo_dic.get('jobInfo',
                                                                                                           {}).get(
            'showSkills') else '职位要求技能未提供',
        '职位描述': jobInfo_dic.get('jobInfo', {}).get('postDescription', '职位描述未提供'),
    }
    return job_info






is_less= False
cur_markdown_num=0
limit_markdown_num=15
limit_load_num=15*7
for i in range(3):
    success=extract_job_descriptions_and_urls()
    start_index = 0
    page.get(url)

    # 在滚动循环中添加更完善的检测逻辑
    previous_count = 0
    stable_count = 0
    if cur_markdown_num >= limit_markdown_num:
        print(f"已投递{limit_markdown_num}条Markdown数据，停止生成")
        continue
    for j in range(10):
        # print()
        page.scroll.to_bottom()
        time.sleep(1)  # 增加等待时间让数据充分加载
        job_list_divs = page.ele(".rec-job-list").children()
        current_length = len(job_list_divs)
        print("正在滚动...",current_length)
        # 判断是否连续多次数量不变
        if current_length == previous_count:
            stable_count += 1
            if stable_count >= 2:  # 连续2次无变化则退出
                print("数据加载稳定，停止滚动")
                is_less= True
                break
        else:
            stable_count = 0

        previous_count = current_length

        if current_length >= limit_load_num:
            print(f"已加载{limit_load_num}条数据，停止滚动")
            break
            # 在相应位置添加当前位置和总职位数的显示




    # print(len(job_list_divs))



    if "100010000" in url:
        expect_sharking = page.ele('text:Java(重庆)')
        expect_sharking.click()
        time.sleep(2)
    job_list_divs = page.ele(".rec-job-list").children()
    job_div = job_list_divs[0]
    hrefs = processor.query_columns("no_deliver", ["招聘链接"])




    total_jobs = len(job_list_divs)  # 获取总职位数
    for job_div in job_list_divs[start_index:]:
        current_position = job_list_divs.index(job_div) + 1  # 获取当前位置（从1开始）
        ele = job_div.ele(".job-name")
        # print(ele.text)
        href = ele.attr("href")
        # print(href)
        # print(ele.text,href)
        if href in hrefs:
            result=processor.query_columns("no_deliver", [ "BOSS活跃","职位","薪资范围","招聘链接",],conditions={"招聘链接": href})
            print(f"{current_position}/{total_jobs} 已经被过滤跳过", result[0])
            if start_index == 0:
                page.listen.start()
            continue
        elif href in recruitment_links:
            continue
        else:
            if start_index!=0:
                page.listen.start()
            # page.listen.start()
            job_div.click()
            # if start_index % 20 == 0 and start_index!=0:
            #     break
            # time.sleep(2)
            try:
                r = page.listen.wait(timeout=10)


                # print(f"{current_position}/{total_jobs}已经被过滤跳过", href)
                print(f"{current_position}/{total_jobs} 第{request_record}次请求", end=" ")
                request_record += 1
                time.sleep(0.5)
            except:
                print(f"第{request_record}次请求超时，跳过")
                request_record += 1
                continue
        if not r:
            continue

        json_data = r.response.body
        job_info=get_json(json_data)
        # recruitment_link=boss_filter(job_info)
        recruitment_link = boss_filter(job_info)

        if recruitment_link:
            cur_markdown_num+=1
            if cur_markdown_num >= limit_markdown_num:
                print(f"已投递{limit_markdown_num}条Markdown数据，停止生成")
                break
            print(f"可以投递，已生成 {cur_markdown_num}条Markdown数据", recruitment_link)
        else:
            print("被过滤，原因：", job_info.get("过滤原因"))

        if recruitment_link:
            recruitment_links.append(recruitment_link)
        start_index += 1

        job_div.click()
        job_list_divs = page.ele(".rec-job-list").children()
        if isinstance(job_div.next(), NoneElement):
            print('兄弟节点不存在，跳过或做兜底处理')
            break
        # break
    if is_less:
         break









