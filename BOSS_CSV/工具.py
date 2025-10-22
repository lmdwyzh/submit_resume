# 初始化时传入CSV文件夹路径
from ToolCategory.CSVJsonProcessor import CSVJsonProcessor
from ToolCategory.ToolCategory import ToolCategory

processor = CSVJsonProcessor("./resources")
processor.delete_empty_rows(table_name="job_deliver",field="AI结果",empty_vals={"待分析", "暂无"})
tool_category = ToolCategory()
tool_category.clear_file_content("./resources/jobs.md")