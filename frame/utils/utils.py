import os.path

import yaml
from genson import SchemaBuilder
import json

import pymysql

from jsonschema.validators import validate


class Utils:

    @classmethod
    def get_yaml_data(cls,file_path):
        """
        读取yaml文件
        :param file_path: yaml文件的路径
        :return: yaml文件的内容
        """
        with open(file_path, "r", encoding="utf-8") as f:
            datas=yaml.safe_load(f)
        return datas

    @classmethod
    def generate_schema(cls,obj,file_path):
        """
        自动生成json schema文件
        :param obj:要生成 json schema的对象
        :param file_path:保存json schema文件的路径
        """
        builder=SchemaBuilder()
        #把预期响应添加到builder中
        builder.add_object(obj)
        #生成json schema
        schema_content=builder.to_schema()
        print(f"生成的json schema为{schema_content}")
        #写入json文件
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(schema_content, f)

    @classmethod
    def schema_validate(cls,obj,schema):
        """
        对比json格式对象与生成的json schema结构是否一致
        :param obj: json格式对象
        :param schema: 生成的json schema的结构
        :return:
        """
        try:
            validate(instance=obj,schema=schema)
            return True
        except Exception as e:
            print(f"schema 结构校验异常{e}")
            return False
    @classmethod
    def query_db(cls,sql,database_info):
        """
        连接数据库，执行对应的sql语句，获得执行结果
        :param sql:要执行的sql语句
        :param database_info:数据库配置信息
        :return:sql执行结果
        """
        #连接数据库
        #connect=pymysql.Connect(host="",port="",database"",user="",password="",charset="")
        conn=pymysql.Connect(**database_info)
        #创建游标
        cursor=conn.cursor()
        print(f"创建的游标为{cursor}")
        print(f"要执行的sql语句为{sql}")
        #执行sql语句
        cursor.execute(sql)
        #获取查询结果
        datas=cursor.fetchall()
        print(f"执行结果数据为{datas}")
        #关闭连接
        cursor.close()
        conn.close()
        return datas

    @classmethod
    def get_frame_root_path(cls):
        """
        获取当前文件所在的绝对路径
        :return:
        """
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))