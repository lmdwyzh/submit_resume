# -*- coding: utf-8 -*-
import json
from typing import Dict, Any, List, Optional, Union
# import pymysql
import mysql.connector
import cryptography


class MySQLJsonProcessor:
    def __init__(self):
        self.host = "localhost"
        self.database = "sheayoo"
        self.user = "root"
        self.password = "root"

    import mysql.connector

    def database_operations(self, query: str, params: Optional[list] = None) -> Union[list, int]:
        """执行数据库操作的通用方法"""
        db = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8mb4'
        )
        cursor = db.cursor()

        try:
            cursor.execute(query, params or ())

            # 判断是否为SELECT查询
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                cursor.close()
                db.close()
                return result
            else:
                # 非SELECT操作需要commit
                db.commit()
                last_id = cursor.lastrowid
                cursor.close()
                db.close()
                return last_id
        except Exception as e:
            db.rollback()
            print(f"Query: {query}\nFailed: {e}")
            cursor.close()
            db.close()
            raise e

    def _map_json_to_sql_type(self, value: Any) -> str:
        """根据JSON值的类型映射到SQL数据类型"""
        if isinstance(value, bool):
            return "BOOLEAN"
        elif isinstance(value, int):
            return "INT"
        elif isinstance(value, float):
            return "FLOAT"
        elif isinstance(value, str):
            return "TEXT" if len(value) > 255 else "VARCHAR(255)"
        return "VARCHAR(255)"

    def create_table_if_not_exists(self, table_name: str, json_data: Dict[str, Any]):
        """检查并创建表（如果不存在）"""
        # 检查表是否存在
        table_exists = self.database_operations(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s AND table_name = %s",
            [self.database, table_name]
        )[0][0]

        if table_exists == 0:
            print(f"表 '{table_name}' 不存在，正在创建...")
            columns = [f"`{key}` {self._map_json_to_sql_type(value)}" for key, value in json_data.items()]
            columns.extend(["`id` INT AUTO_INCREMENT PRIMARY KEY", "`created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP"])
            create_table_query = f"""
                CREATE TABLE `{table_name}` (
                    {', '.join(columns)}
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            self.database_operations(create_table_query)
            print(f"表 '{table_name}' 创建成功")
    def check_data_exists(self, table_name: str, unique_field: str, unique_value: Any) -> bool:
        """检查数据是否已存在"""
        try:
            # 检查字段是否存在
            column_exists = self.database_operations(
                "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = %s AND table_name = %s AND column_name = %s",
                [self.database, table_name, unique_field]
            )[0][0]

            if column_exists == 0:
                print(f"唯一性字段 '{unique_field}' 不存在于表 '{table_name}' 中")
                return False

            # 检查数据是否存在
            data_exists = self.database_operations(
                f"SELECT COUNT(*) FROM `{table_name}` WHERE `{unique_field}` = %s",
                [unique_value]
            )[0][0]

            return data_exists > 0
        except Exception as e:
            print(f"检查数据存在性错误: {e}")
            return False

    def insert_json_data(self, table_name: str, json_data: Dict[str, Any]) -> int:
        """将JSON数据插入到指定表中"""
        columns = [f"`{key}`" for key in json_data.keys()]
        placeholders = ", ".join(["%s"] * len(columns))

        insert_query = f"INSERT INTO `{table_name}` ({', '.join(columns)}) VALUES ({placeholders})"
        return self.database_operations(insert_query, list(json_data.values()))

    def delete_data(self, table_name: str, conditions: Optional[Dict[str, Any]] = None) -> int:
        """
        删除表中的数据

        :param table_name: 表名
        :param conditions: 删除条件，字典格式 {字段名: 字段值}
        :return: 删除的记录数
        """
        if conditions is None or len(conditions) == 0:
            # 如果没有提供条件，则删除所有数据（需要用户确认）
            confirm = input(f"警告：即将删除表 '{table_name}' 中的所有数据，确认请输入 'YES': ")
            if confirm != 'YES':
                print("删除操作已取消")
                return 0
            delete_query = f"DELETE FROM `{table_name}`"
            params = []
        else:
            # 根据条件删除数据
            where_clause = " AND ".join([f"`{k}` = %s" for k in conditions])
            delete_query = f"DELETE FROM `{table_name}` WHERE {where_clause}"
            params = list(conditions.values())

        try:
            result = self.database_operations(delete_query, params)
            # print(f"成功删除 {result} 条记录")
            return result
        except Exception as e:
            print(f"删除数据失败: {e}")
            return 0

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

        col_part = ", ".join(f"`{c}`" for c in columns)
        base_sql = f"SELECT {'DISTINCT ' if distinct else ''}{col_part} FROM `{table_name}`"
        params = []

        if conditions:
            where_clause = " AND ".join([f"`{k}` = %s" for k in conditions])
            base_sql += f" WHERE {where_clause}"
            params.extend(conditions.values())

        if limit is not None:
            base_sql += " LIMIT %s"
            params.append(limit)

        results = self.database_operations(base_sql, params)

        return [row[0] for row in results] if len(columns) == 1 else [dict(zip(columns, row)) for row in results]


    def process_json(self, table_name: str, json_data: Dict[str, Any], unique_field: Optional[str] = None) -> Optional[
        int]:
        """
        处理JSON数据的主方法
        """
        try:
            self.create_table_if_not_exists(table_name, json_data)

            # 检查数据是否已存在
            if unique_field and unique_field in json_data and self.check_data_exists(table_name, unique_field,json_data[unique_field]):
                return "数据已存在"
            return self.insert_json_data(table_name, json_data)
        except Exception as e:
            print(f"处理JSON数据错误: {e}")
            return None


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

    processor = MySQLJsonProcessor()
    # inserted_id = processor.process_json("job_postings", sample_json, unique_field="招聘链接")
    # print(inserted_id)
    # data = processor.query_columns("job_postings",["BOSS活跃", "最低薪资", "职位"],conditions={"招聘链接": "https://www.zhipin.com/job_detail/967cef7cac90fc171nF_0tm0EFBT.html"})
    # print(data)
    #
    # data = processor.query_columns("job_postings", ["BOSS活跃", "最低薪资", "职位"])
    #
    # data = processor.query_columns("count_get_job", ["AI结果", "招聘链接"])
    # # print(data)
    # # for i in data:
    # #     print(i["AI结果"])
    # #     print()
    #
    # result = processor.database_operations(
    #     "SELECT COUNT(*) AS today_count FROM count_get_job WHERE DATE(created_at) = CURDATE();")
    # len_has_request = result[0][0]
    # print(len_has_request)
    data = processor.delete_data("job_filter_by_name", {"招聘链接":"https://www.zhipin.com/job_detail/0424f0912a7a327e03N-3N6-E1tR.html"})
