from ToolCategory.MysqlTool import MySQLJsonProcessor


def parse_salary(salary_str):
    """
    解析薪资字符串，返回最低薪资和最高薪资（单位：元）
    :param salary_str: 薪资字符串，如 "7-10K"、"120-150元/天"、"8-9K·13薪"、"面议"等
    :return: (最低薪资, 最高薪资)，解析失败返回 (None, None)
    """
    if not salary_str or "面议" in salary_str:
        return None, None

    try:
        # 清理字符串：去掉空格、附加信息（如13薪）、"薪"字等
        clean_str = salary_str.replace(" ", "").split("·")[0].replace("薪", "")

        # 处理日薪情况
        if "元/天" in clean_str:
            daily_range = clean_str.replace("元/天", "")
            if "-" in daily_range:
                daily_min, daily_max = daily_range.split("-")
            else:
                daily_min = daily_max = daily_range

            min_salary = int(daily_min) * 30  # 按30天估算月薪
            max_salary = int(daily_max) * 30
            return min_salary, max_salary

        # 处理时薪情况（可选）
        if "元/小时" in clean_str:
            hourly_range = clean_str.replace("元/小时", "")
            if "-" in hourly_range:
                hourly_min, hourly_max = hourly_range.split("-")
            else:
                hourly_min = hourly_max = hourly_range

            # 按8小时/天，22天/月估算
            min_salary = int(hourly_min) * 8 * 22
            max_salary = int(hourly_max) * 8 * 22
            return min_salary, max_salary

        # 处理K为单位的情况
        multiplier = 1
        if "K" in clean_str:
            clean_str = clean_str.replace("K", "")
            multiplier = 1000

        # 解析薪资范围
        if "-" in clean_str:
            min_val, max_val = clean_str.split("-")
            min_salary = int(min_val) * multiplier
            max_salary = int(max_val) * multiplier
        else:
            # 单值情况，如 "10K"
            min_salary = max_salary = int(clean_str) * multiplier

        return min_salary, max_salary

    except (ValueError, AttributeError, IndexError):
        return None, None




if __name__ == '__main__':

    # 测试用例
    test_cases = [
        "7-10K",
        "120-150元/天",
        "8-9K·13薪",
        "15K",
        "面议",
        "80-100元/小时",
        "5-8",
        "invalid"
    ]

    processor = MySQLJsonProcessor()
    result=processor.query_data_columns("job_postings",["薪资范围"])
    print( result)


    for test in result:
        min_sal, max_sal =parse_salary(test)

        print(f"'{test}' -> 最低: {min_sal}, 最高: {max_sal}")