# -*- coding: utf-8 -*-
import json
import pandas as pd
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from typing import Optional, Collection

class CSVJsonProcessor:
    def __init__(self, csv_folder_path: str):
        """
        初始化CSV处理器

        :param csv_folder_path: CSV文件存储的文件夹路径
        """
        self.csv_folder_path = csv_folder_path
        # 确保文件夹存在
        os.makedirs(self.csv_folder_path, exist_ok=True)

    def _get_csv_path(self, table_name: str) -> str:
        """获取CSV文件的完整路径"""
        return os.path.join(self.csv_folder_path, f"{table_name}.csv")

    def _table_exists(self, table_name: str) -> bool:
        """检查CSV文件是否存在"""
        return os.path.exists(self._get_csv_path(table_name))

    def _read_csv(self, table_name: str) -> pd.DataFrame:
        """读取CSV文件，如果不存在则返回空的DataFrame"""
        csv_path = self._get_csv_path(table_name)
        if not self._table_exists(table_name):
            return pd.DataFrame()
        return pd.read_csv(csv_path)

    def _write_csv(self, table_name: str, df: pd.DataFrame):
        """将DataFrame写入CSV文件"""
        csv_path = self._get_csv_path(table_name)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')

    def _map_json_to_csv_type(self, value: Any) -> str:
        """根据JSON值的类型映射到合适的数据类型（主要用于显示）"""
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "string"
        return "string"

    def create_table_if_not_exists(self, table_name: str, json_data: Dict[str, Any]):
        """检查并创建CSV文件（如果不存在）"""
        if not self._table_exists(table_name):
            print(f"CSV文件 '{table_name}.csv' 不存在，正在创建...")
            # 创建包含所有字段的空DataFrame
            columns = list(json_data.keys()) + ['id', 'created_at']
            df = pd.DataFrame(columns=columns)
            self._write_csv(table_name, df)
            print(f"CSV文件 '{table_name}.csv' 创建成功")

    def check_data_exists(self, table_name: str, unique_field: str, unique_value: Any) -> bool:
        """检查数据是否已存在"""
        try:
            if not self._table_exists(table_name):
                return False

            df = self._read_csv(table_name)

            # 检查字段是否存在
            if unique_field not in df.columns:
                print(f"唯一性字段 '{unique_field}' 不存在于CSV文件 '{table_name}.csv' 中")
                return False

            # 检查数据是否存在
            data_exists = unique_field in df.columns and (df[unique_field] == unique_value).any()
            return data_exists
        except Exception as e:
            print(f"检查数据存在性错误: {e}")
            return False

    def insert_json_data(self, table_name: str, json_data: Dict[str, Any]) -> int:
        """将JSON数据插入到指定CSV文件中"""
        df = self._read_csv(table_name)

        # 生成新记录的ID
        new_id = len(df) + 1 if not df.empty else 1

        # 创建新行数据
        new_row = json_data.copy()
        new_row['id'] = new_id
        new_row['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 添加到DataFrame
        new_df = pd.DataFrame([new_row])
        if df.empty:
            df = new_df
        else:
            df = pd.concat([df, new_df], ignore_index=True)

        # 保存到CSV
        self._write_csv(table_name, df)
        return new_id

    def delete_data(self, table_name: str, conditions: Optional[Dict[str, Any]] = None) -> int:
        """
        删除CSV文件中的数据

        :param table_name: 表名（CSV文件名）
        :param conditions: 删除条件，字典格式 {字段名: 字段值}
        :return: 删除的记录数
        """
        if not self._table_exists(table_name):
            print(f"删除失败：CSV文件 '{table_name}.csv' 不存在")
            return 0

        df = self._read_csv(table_name)

        if conditions is None or len(conditions) == 0:
            # 如果没有提供条件，则删除所有数据（需要用户确认）
            confirm = input(f"警告：即将删除CSV文件 '{table_name}.csv' 中的所有数据，确认请输入 'YES': ")
            if confirm != 'YES':
                print("删除操作已取消")
                return 0

            deleted_count = len(df)
            df = pd.DataFrame(columns=df.columns)  # 清空但保留列结构
        else:
            # 根据条件删除数据
            mask = pd.Series([True] * len(df))
            for field, value in conditions.items():
                if field in df.columns:
                    mask = mask & (df[field] == value)
                else:
                    print(f"警告：字段 '{field}' 不存在于CSV文件中")
                    mask = mask & False

            deleted_count = mask.sum()
            df = df[~mask].reset_index(drop=True)

        # 重新生成ID
        if not df.empty:
            df['id'] = range(1, len(df) + 1)

        # 保存修改后的数据
        self._write_csv(table_name, df)
        print(f"成功删除 {deleted_count} 条记录")
        return deleted_count

    def query_columns(
            self,
            table_name: str,
            columns: List[str],
            conditions: Optional[Dict[str, Any]] = None,
            limit: Optional[int] = None,
            distinct: bool = False
    ) -> Union[List[Any], List[Dict[str, Any]]]:
        """
        查询指定列的数据
        """
        if not self._table_exists(table_name):
            print(f"查询失败：CSV文件 '{table_name}.csv' 不存在")
            return []

        df = self._read_csv(table_name)

        # 检查请求的列是否存在
        available_columns = [col for col in columns if col in df.columns]
        missing_columns = set(columns) - set(available_columns)
        if missing_columns:
            print(f"警告：以下列不存在于CSV文件中: {missing_columns}")
            if not available_columns:
                return []

        # 应用条件过滤
        if conditions:
            mask = pd.Series([True] * len(df))
            for field, value in conditions.items():
                if field in df.columns:
                    mask = mask & (df[field] == value)
            df = df[mask]

        # 选择指定列
        result_df = df[available_columns]

        # 去重处理
        if distinct:
            result_df = result_df.drop_duplicates()

        # 限制结果数量
        if limit is not None:
            result_df = result_df.head(limit)

        # 转换为返回格式
        if len(available_columns) == 1:
            values = result_df[available_columns[0]].dropna().tolist()
            return [None if pd.isna(v) else v for v in values]
        else:
            return result_df.to_dict('records')

    def process_json(self, table_name: str, json_data: Dict[str, Any], unique_field: Optional[str] = None) -> Optional[
        Union[int, str]]:
        """
        处理JSON数据的主方法
        """
        try:
            self.create_table_if_not_exists(table_name, json_data)

            # 检查数据是否已存在
            if unique_field and unique_field in json_data and self.check_data_exists(table_name, unique_field,
                                                                                     json_data[unique_field]):
                return "数据已存在"
            return self.insert_json_data(table_name, json_data)
        except Exception as e:
            print(f"处理JSON数据错误: {e}")
            return None

    # 在CSVJsonProcessor类中添加一个计数方法
    def count_records(self, table_name: str, conditions: Optional[Dict[str, Any]] = None) -> int:
        """
        统计满足条件的记录数量

        :param table_name: 表名
        :param conditions: 查询条件
        :return: 记录数量
        """
        if not self._table_exists(table_name):
            return 0

        df = self._read_csv(table_name)

        if conditions:
            mask = pd.Series([True] * len(df))
            for field, value in conditions.items():
                if field in df.columns:
                    # print(f"[DEBUG] 过滤字段: {field}, 值: {repr(value)}")
                    if field == 'created_at' and isinstance(value, str):
                        mask &= df[field].str.startswith(value)
                    elif value is None:
                        mask &= df[field].isna() | (df[field].astype(str).str.strip() == "")
                    else:
                        mask &= df[field] == value
                else:
                    print(f"[WARN] 字段 {field} 不存在于表中")
            df = df[mask.values]
            # print(f"[DEBUG] 过滤后剩余 {len(df)} 条记录")
            # df = df[mask]

        return len(df)

    def update_row_append_fields(
            self,
            table_name: str,
            condition: Dict[str, Any],
            new_fields: Dict[str, Any]
    ) -> bool:
        """
        向唯一行追加列数据（字段不存在则自动添加）

        :param table_name: 表名
        :param condition: 定位条件，如 {"招聘链接": "https://example.com/job123"}
        :param new_fields: 要追加的新字段及其值
        """
        if not self._table_exists(table_name):
            print(f"CSV文件 '{table_name}.csv' 不存在")
            return False

        df = self._read_csv(table_name)

        # 构造布尔掩码
        mask = pd.Series([True] * len(df))
        for field, value in condition.items():
            if field not in df.columns:
                print(f"字段 '{field}' 不存在")
                return False
            mask &= df[field] == value

        if not mask.any():
            print(f"未找到匹配行：{condition}")
            return False

        # 更新
        for field, value in new_fields.items():
            if field not in df.columns:
                df[field] = None
            df.loc[mask, field] = value

        self._write_csv(table_name, df)
        # print(f"已更新 {mask.sum()} 行，追加字段：{list(new_fields.keys())}")
        return True

    def delete_empty_rows(
            self,
            table_name: str,
            field: str,
            empty_vals: Optional[Collection[str]] = None,
            strip: bool = True
    ) -> int:
        """
        删除指定字段为“空”的所有记录。
        通用：可用于任何字段，不限于 AI结果。

        :param table_name: 表名（不含 .csv）
        :param field: 要检查的字段名
        :param empty_vals: 额外视为“空”的字符串集合，如 {"待分析","暂无"}
        :param strip: 是否先 strip 再比较（默认 True）
        :return: 实际删除的行数
        """
        if not self._table_exists(table_name):
            print(f"删除失败：CSV 文件 '{table_name}.csv' 不存在")
            return 0

        df = self._read_csv(table_name)

        # 字段不存在 → 整张表都视为空
        if field not in df.columns:
            print(f"字段 '{field}' 不存在，视为全部为空")
            confirm = input(f"警告：即将删除 '{table_name}.csv' 全部数据，确认请输入 'YES': ")
            if confirm != 'YES':
                print("操作已取消")
                return 0
            deleted = len(df)
            df = df.iloc[:0]  # 清空
        else:
            # 构造空值掩码
            mask = df[field].isna()
            if strip:
                mask |= df[field].astype(str).str.strip().eq('')
            else:
                mask |= df[field].astype(str).eq('')

            if empty_vals:  # 用户自定义空值
                if strip:
                    mask |= df[field].astype(str).str.strip().isin(empty_vals)
                else:
                    mask |= df[field].astype(str).isin(empty_vals)

            deleted = mask.sum()
            df = df[~mask].reset_index(drop=True)

        # 重新生成连续 id（可选）
        if 'id' in df.columns and not df.empty:
            df['id'] = range(1, len(df) + 1)

        self._write_csv(table_name, df)
        print(f"成功删除 {deleted} 条记录")
        return deleted



# 使用示例
if __name__ == "__main__":
    sample_json = {
        'BOSS活跃': '刚刚活跃',
        '职位': '机器人编程老师',
        '薪资范围': '5-10K',
        '最低薪资': 5000,
        '最高薪资': 10000,
        '工作年限要求': '经验不限',
        '学历要求': '学历不限',
        '工作地点': '宜昌',
        '公司名称': '迈思国际教育',
        '公司规模': '20-99人',
        '招聘链接': 'https://www.zhipin.comjob_detail/09069c964894775b03J70t7GFJU.html',
        '公司行业': '培训/辅导机构',
        '福利': '福利信息未提供',
        '职位要求技能': '职位要求技能未提供',
        '职位描述': '要求：1.学历：计算机/机械工程/教育技术等相关专业本科\n2.证书：- 教师资格证（信息技术/通用技术类）\n             - 机器人技术等级考试考官资格（CCF/YCL等）\n3.年龄：23-40岁（竞赛导师可放宽至45岁）\n4.技能要求：LEGO SPIKE/EV3、Makeblock、 VEX/V5、Arduino、ROS基础 、Scratch/Python基础、C++、Java竞赛算法 、熟悉FLL/WRO规则、精通FRC/ICRA赛事技术要点、掌握Mixly、mBlock等可视化工具、能开发自定义教学插件\n     5.核心要求：- 具备跨学科整合能力（物理+数学+编程）\n- 掌握PBL项目式教学方法\n- 有机器人竞赛获奖/带队经历（省市级以上）'
    }

    # 初始化时传入CSV文件夹路径
    processor = CSVJsonProcessor("./csv_data")

    # 测试插入数据
    inserted_id = processor.process_json("job_postings", sample_json, unique_field="招聘链接")
    print(f"插入的数据ID: {inserted_id}")

    # 测试查询数据
    data = processor.query_columns("job_postings", ["BOSS活跃", "最低薪资", "职位"],conditions={"招聘链接": "https://www.zhipin.comjob_detail/09069c964894775b03J70t7GFJU.html"})
    print("查询结果:", data)

    # 测试查询所有数据
    data = processor.query_columns("job_postings", ["BOSS活跃", "最低薪资", "职位"])
    print("所有数据:", data)

    # 测试删除数据
    # data = processor.delete_data("job_postings",{"招聘链接": "https://www.zhipin.comjob_detail/09069c964894775b03J70t7GFJU.html"})
    # print(f"删除操作结果: {data}")

    # 假设你要追加的新列如下
    new_columns = {
        "岗位描述": "暂无",
        "AI结果": "待分析"
    }

    # 追加列到 job_deliver 表
    # processor.update_row_append_fields("job_postings", new_columns,unique_value="https://www.zhipin.comjob_detail/09069c964894775b03J70t7GFJU.html")
    processor.update_row_append_fields("job_postings",{"招聘链接": "https://www.zhipin.comjob_detail/09069c964894775b03J70t7GFJU.html"},new_columns)