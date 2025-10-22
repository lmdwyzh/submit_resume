from DrissionPage import ChromiumPage
page=ChromiumPage()
page.listen.start("data/getCityShowPosition?")
page.get("https://www.zhipin.com/")

r = page.listen.wait()
json_data = r.response.body
data = json_data.get('zpData', {})
# print(jobInfo_dic)

import json


def extract_positions_with_hierarchy(data):
    result = {}

    # 遍历主分类
    for main_category in data["position"]:
        main_name = main_category["name"]
        result[main_name] = {}

        # 检查是否有子分类
        if "subLevelModelList" not in main_category:
            continue

        # 遍历子分类
        for sub_category in main_category["subLevelModelList"]:
            sub_name = sub_category["name"]
            result[main_name][sub_name] = []

            # 检查是否有职位列表
            if "subLevelModelList" not in sub_category:
                continue

            # 提取职位名称
            for position in sub_category["subLevelModelList"]:
                if "name" in position:
                    result[main_name][sub_name].append(position["name"])

    return result


# 使用函数提取职位
hierarchical_positions = extract_positions_with_hierarchy(data)

# 打印层级结构
for main_category, sub_categories in hierarchical_positions.items():
    print(f"\n主分类: {main_category}")
    for sub_category, positions in sub_categories.items():
        print(f"子分类: {sub_category}",end=":     ")
        for position in positions:
            print(f"{position}",end=" ")
        print("")

# # 如果你还想要扁平化的所有职位列表
# flat_positions = [pos for main in hierarchical_positions.values()
#                   for sub in main.values()
#                   for pos in sub]
# print("\n所有职位列表(扁平化):", flat_positions)