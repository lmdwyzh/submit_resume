from openai import OpenAI
import dashscope
from dashscope import Generation


class AiTool:
    def __init__(self):
        # Kimi 配置
        self.kimi_key = "sk-RN08YGChVMq4xi7NmE0BEJX80pnQYVedZqzWE3wuJhVcTn6T"
        self.kimi_cli = OpenAI(api_key=self.kimi_key, base_url="https://api.moonshot.cn/v1")
        self.kimi_model = "moonshot-v1-8k"

        # Qwen 配置：请替换为你的实际 DashScope API Key
        self.qwen_api_key = "sk-201aa4589b414183bef948f5bb68d1dc"
        dashscope.api_key = self.qwen_api_key
        self.qwen_model = "qwen-turbo"
        # , model = "qwen-turbo"

    def Kimi(self, user: str, system: str = "你是Kimi，由Moonshot AI训练的大语言模型。", max_words: int = -1) -> str:
        if max_words < 0:
            prompt = f"{user}"
        else:
            prompt = f"{user}（用{max_words}字以内回答）"

        r = self.kimi_cli.chat.completions.create(
            model=self.kimi_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        )
        return r.choices[0].message.content

    def Qwen(self, user: str, system: str = "你是Qwen，一个阿里云开发的助手",max_tokens: int = 2048) -> str:
        """
        使用阿里云 Qwen 模型（如 qwen-plus, qwen-turbo）生成回复。

        :param user: 用户输入
        :param system: 系统提示词
        :param max_tokens: 最大生成长度
        :return: 模型返回的文本
        """
        try:
            response = Generation.call(
                model=self.qwen_model,
                messages=[
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': user}
                ],
                result_format='message',
                max_tokens=max_tokens
            )

            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                return f"Qwen 调用失败: {response.code} - {response.message}"

        except Exception as e:
            return f"Qwen 请求出错: {str(e)}"


# 使用示例
if __name__ == "__main__":
    bot = AiTool()

    # 测试 Kimi
    print("Kimi 回答：")
    print(bot.Kimi("介绍北京"))

    print("\nQwen 回答：")
    # 测试 Qwen（请确保已设置正确的 API Key）
    print(bot.Qwen("写一个用 Python 实现快速排序的代码。"))