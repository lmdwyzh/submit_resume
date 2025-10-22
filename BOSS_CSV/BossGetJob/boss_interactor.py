# boss_interactor.py
import time
from DrissionPage import ChromiumPage
from DrissionPage._functions.keys import Keys

from ToolCategory.AiTool import AiTool
from ToolCategory.CSVJsonProcessor import CSVJsonProcessor



def send_message_to_hr(page: ChromiumPage, bot: AiTool, url: str, desc: str, introduce: str, prompt: str) -> bool:
    # processor = MySQLJsonProcessor()
    processor = CSVJsonProcessor("./resources")
    # processor.process_json("count_get_job", sample_json, unique_field="招聘链接")
    data = processor.query_columns("job_deliver",["AI结果"],conditions={"招聘链接": url})
    # print( data)
    if data:
        print("已经投递过")
        return False
    # print(data)



    """向HR发送消息"""

    try:
        page.get(url)
        sentence="以下是我的自我介绍\n" + introduce + "以下是岗位要求\n" + desc + prompt
        ai_result = bot.Qwen(sentence)
        print(f"{ai_result}")
        # time.sleep(1)

        btn_start_chat = page.ele(".btn btn-startchat")
        if not btn_start_chat:
            print("未找到开始聊天按钮")
            return False
        btn_start_chat.click()

        try:
            # 查找确定按钮，如果存在则处理提示框
            # btn_sure = page.ele(".btn-sure", timeout=2)
            btn_sure = page.ele("@ka=dialog_confirm", timeout=1)
            if btn_sure:
                dialog_con = page.ele("text:您今天已与")
                if dialog_con:
                    print(dialog_con.text)
                    btn_sure.click()
                    print("已点击提示框确定按钮")
                if "150" in dialog_con.text:
                    return  "今天已经达到上限"
        except Exception as e:
            print(f"处理提示框时出错: {e}")
            pass







        chat_input = page.ele(".chat-input")
        if not chat_input:
            chat_input = page.ele(".input-area")
            if not chat_input:
                print("未找到聊天输入框")
                return False





        if ai_result and ai_result != "false":
            chat_input.input(ai_result)
            time.sleep(3)
            # 鼠标移动到<chat-input>元素上
            page.actions.move_to(chat_input)
            # 点击鼠标，使光标落到元素中
            page.actions.click()

            # time.sleep(15)

            # 按下 ENTER 键
            print("点击发送按钮")
            page.actions.key_down(Keys.ENTER)
            time.sleep(0.1)
            page.actions.key_up(Keys.ENTER)
            # time.sleep(2)

            sample_json = {
                "AI结果": ai_result
            }
            processor.update_row_append_fields("job_deliver", {"招聘链接": url}, sample_json)

            return True
        else:
            print("岗位不匹配，跳过发送消息")
            return False



    except Exception as e:
        print(f"发送消息时出错: {e}")
        return False
