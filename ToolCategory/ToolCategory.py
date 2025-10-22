import os
import shutil
import json
import requests

class ToolCategory:
    # KIMIKEY = "sk-zlcWei2MbV40IWGEhguXw51TqVDRds4fPEgOp5qLwWVaLj93"
    # KIMIKEY = "sk-JxZVv7oTF8pxndZNvcJQMSUo4dNbc8MjaJ2zvmXkTQf4Hxxv"
    KIMIKEY = "sk-RN08YGChVMq4xi7NmE0BEJX80pnQYVedZqzWE3wuJhVcTn6T"

    @staticmethod
    def empty_directory(folder_path):
        # 检查文件夹是否存在
        if not os.path.exists(folder_path):
            print(f"文件夹 {os.path.basename(folder_path)} 不存在。")
            return

        # 遍历文件夹内的所有文件和子文件夹
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)

            # 如果是文件，删除文件
            if os.path.isfile(item_path):
                os.remove(item_path)
                # print(f"已删除文件：{item}")
            # 如果是文件夹，递归删除文件夹及其内容
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                # print(f"已删除文件夹：{item}")

        # 输出清空的文件夹名称
        print(f"文件夹 {os.path.basename(folder_path)} 已清空")


    @staticmethod
    def clear_file_content(file_path):
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"文件 {os.path.basename(file_path)} 不存在。")
            return

        # 检查是否是文件
        if not os.path.isfile(file_path):
            print(f"{os.path.basename(file_path)} 不是一个文件。")
            return

        # 打开文件并清空内容
        with open(file_path, 'w', encoding='utf-8') as file:
            file.truncate()
        print(f"文件 {os.path.basename(file_path)} 的内容已清空")
    @staticmethod
    def goto_txt(file_path: str, information: str) -> None:
        """
        将字符串 information 追加写入指定 txt 文件。
        若目录或文件不存在，则自动创建；若已存在，则在文件末尾追加。

        参数:
            file_path (str): 目标 txt 文件完整路径。
            information (str): 要追加写入的内容。
        """
        # 1. 若目录不存在则创建
        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        # 2. 以追加模式写入
        try:
            with open(file_path, mode='a', encoding='utf-8') as f:
                f.write(information)
                # 若希望每次追加后换行，可取消下一行注释
                f.write('\n')
        except OSError as e:
            # 捕获并提示文件写入错误
            print(f"写入文件失败: {e}")
    @staticmethod
    def get_txt(file_path):
        """
             读取指定文本文件的所有行，并去除每行首尾空白字符。

             :param file_path: 文件路径，可为字符串或 pathlib.Path 对象。
             :return: 去除换行符后的字符串列表。若文件不存在或读取失败，返回空列表。
             """

        information = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()  # 读取所有行

            # 逐行打印
            for index, line in enumerate(lines):
                # print(f"Line {index}: {line.strip()}")  # 使用 strip() 去掉每行末尾的换行符
                information.append(line.strip())
            return information
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' does not exist.")
    @staticmethod
    def send_message(message: str,uids=["UID_7bgC5pYlolkDL0tXvAxHHEgGVneD"]):

        URL = "https://wxpusher.zjiecode.com/api/send/message"

        payload = {
            "appToken": "AT_WC9ooPxKKiqQRe56iDxQoDB2SZynOyLo",
            "content": message,
            "summary": "消息推送",
            "contentType": 2,
            "uids": uids,  # ← 换成真实 UID
            "topicIds": [],  # 如果不用群发主题，留空即可
            "url": "https://wxpusher.zjiecode.com",
            "verifyPayType": 0
        }

        resp = requests.post(URL, json=payload, timeout=10)
        # print("HTTP 状态码:", resp.status_code)
        # print("响应内容:", json.dumps(resp.json(), ensure_ascii=False, indent=2))




if __name__ == '__main__':
    tool_category = ToolCategory()
    tool_category.send_message("55555")
    # information=tool_category.get_txt(r"C:\Users\lmdwy\Desktop\Folder\Projects\PycharmProjects\Sheayoo\Game_assistance\抖音\resources\car.txt")
    # print(information)
    # tool_category.goto_txt(r"C:\Users\lmdwy\Desktop\Folder\Projects\PycharmProjects\Sheayoo\Game_assistance\抖音\resources\car.txt","hfuhufhuh")

    # tool_category.empty_directory(r"C:\Users\lmdwy\Desktop\Folder\Projects\PycharmProjects\Sheayoo\Game_assistance\tieBa\resources\images")
    # tool_category.clear_file_content(r"C:\Users\lmdwy\Desktop\Folder\Projects\PycharmProjects\Sheayoo\Game_assistance\tieBa\resources\user.md")