# -*- coding: utf-8 -*-
import pymysql
class HandlDB():
    def __init__(self):
        self.conn = pymysql.connect(
                host='127.0.0.1',
                port=3306,
                user='root',
                passwd='',
                db='proxy',
                )
        try:
            create_tb_cmd = "CREATE TABLE IF NOT EXISTS nnproxy (ip TEXT,point TEXT);"
            # 主要就是上面的语句
            cur = self.conn.cursor()
            cur.execute(create_tb_cmd)
        except Exception, e:
            print "Create table failed"
            print e.message

            #创建数据表
    #cur.execute("create table student(id int ,name varchar(20),class varchar(30),age varchar(10))")

    #插入一条数据
    #cur.execute("insert into student values('2','Tom','3 year 2 class','9')")


    #修改查询条件的数据
    #cur.execute("update student set class='3 year 1 class' where name = 'Tom'")

    #删除查询条件的数据
    #cur.execute("delete from student where age='9'")

    def insertdb(self, lis):
        cur = self.conn.cursor()
        for i in lis:
            if i[0] and i[1]:
                ip = i[0]
                point = i[1]
                cur.execute("insert into nnproxy values({},{})".format(ip, point))
        self.conn.commit()

    def selectdb(self, limit=1000):
        cur = self.conn.cursor()
        cur.execute("select ip,point from nnproxy limit {}".format(limit))
        data = cur.fetchall()
        return data
    def close(self):
        conn.close()