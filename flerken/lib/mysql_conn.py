#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# https://github.com/frankie-huang/pythonMySQL

import sys,os
sys.path.append(os.getcwd()+'/flerken/config')
from global_config import DB_CONFIG
import mysql.connector
import traceback
import re
import datetime

class pythonMySQL(object):
    configs = {}  # 设置连接参数，配置信息(字典)

    current = 0  # 标识当前对应的数据库配置，可以是数字或者字符串
    config = {}  # 保存当前模型的数据库配置
    con = None  # 保存连接标识符
    cur = None  # 保存数据库游标
    dbdebug = False  # 是否开启DEBUG模式
    database = ''  # 记录连接的数据库
    table_name = ''  # 记录操作的数据表名
    columns = []  # 记录表中字段名
    connected = False  # 是否连接成功
    queryStr = ''  # 保存最后执行的操作
    SQLerror = {}  # SQL执行报错错误信息
    lastInsertId = 0  # 保存上一步插入操作产生AUTO_INCREMENT
    numRows = 0  # 上一步操作产生受影响的记录的条数

    tmp_table = ''
    aliasString = ''
    fieldString = ''
    joinString = ''
    whereString = ''
    groupString = ''
    havingString = ''
    orderString = ''
    limitString = ''
    fetchSql = False

    whereStringArray = []
    whereValueArray = []

    SQL_logic = ['AND', 'OR', 'XOR']  # SQL语句支持的逻辑运算符

    # 对于参数dbConfig，需为dict，包含host、port、user、password、database、charset、autocommit、DB_DEBUG、MYSQL_LOG，至少须包含user、password、database
    def __init__(self, dbtable, ConfigID=0, dbConfig=None):
        if not isinstance(ConfigID, (int, str)):
            self.throw_exception("第二个参数只能是数字或字符串", True)
        # 将类变量中的可变元素初始化
        self.columns = []  # 记录表中字段名
        self.whereStringArray = []
        self.whereValueArray = []
        self.SQLerror = {}
        # 如果数据库配置已被存在self.configs中时,直接读取self.configs中数据进行连接
        if ConfigID in pythonMySQL.configs:
            self.init(ConfigID, dbtable)
            return
        # 以下为数据库配置还未被存在self.configs中时,进行配置读取
        if dbConfig == None:
            if not isset('DB_CONFIG'):
                self.throw_exception("配置文件未定义DB_CONFIG", True)
            # 检查配置文件中是否有对应的配置信息
            if ConfigID not in DB_CONFIG:
                self.throw_exception(
                    "配置文件中无" + (str(ConfigID) if isinstance(ConfigID, int) else "'" + ConfigID + "'") + "的配置信息", True)
            # 使用配置文件中对应的配置
            if ConfigID == 0:
                dbConfig = DB_CONFIG[0]
            else:
                dbConfig = dict(DB_CONFIG[0])
                dbConfig.update(DB_CONFIG[ConfigID])
        if 'DB_DEBUG' in dbConfig:
            if dbConfig['DB_DEBUG'] == True:
                self.dbdebug = True
            del dbConfig['DB_DEBUG']
        if 'password' not in dbConfig:
            if 'password' in DB_CONFIG[0]:
                dbConfig['password'] = DB_CONFIG[0]['password']
            else:
                self.throw_exception('数据库未设置密码')
        if 'host' not in dbConfig:
            dbConfig['host'] = '127.0.0.1'
        if 'user' not in dbConfig:
            dbConfig['user'] = 'root'
        if 'port' not in dbConfig:
            dbConfig['port'] = '3306'
        if 'autocommit' not in dbConfig:
            dbConfig['autocommit'] = True
        pythonMySQL.configs[ConfigID] = dbConfig
        self.current = ConfigID
        self.config = dbConfig
        self.database = dbConfig['database']
        self.init(self.current, dbtable)


    # 新建连接
    def init(self, current, dbtable):
        self.current = current
        self.config = pythonMySQL.configs[current]
        self.con = mysql.connector.connect(**self.config)
        self.cur = self.con.cursor(dictionary=True)
        if 'DB_DEBUG' in self.config and self.config['DB_DEBUG'] == True:
            self.dbdebug = True
        self.database = self.config['database']
        if self.in_db(dbtable):
            self.table_name = dbtable
        else:
            self.throw_exception('数据库' + self.config['database'] + '中不存在' + dbtable + '表')
        self.connected = True

    def in_db(self, dbtable):
        self.cur.execute('show tables')
        tables = self.cur.fetchall()
        key = 'Tables_in_' + self.database
        for table in tables:
            if dbtable == table[key]:
                return True
        return False

    def set_columns(self, dbtable):
        self.cur.execute("SHOW COLUMNS FROM `" + dbtable + "`")
        columns = self.cur.fetchall()
        self.columns = ['', ]
        for column in columns:
            if column['Key'] == 'PRI':
                self.columns[0] = column['Field']
            self.columns.append(column['Field'])

    def get_columns(self):
        return self.cur.column_names

        # 字符串查询
        # where("id = 1 and nick = 'frankie'")
        # where("id = %d and nick = '%s'", 1, 'frankie')
        # where("id = %d and nick = '%s'", (1, 'frankie'))
        # where("id = %d and nick = '%s'", [1, 'frankie'])
        # 字典查询
        # where({'id':1, 'nick':'frankie'})
        # where({'id&nick':"1"}) # WHERE `id`='1' AND `nick`='1'
        # where({'id&nick':[1, 'frankie']}) = where({'id&nick':[1, 'frankie', '', 's']}) # 其中's'代表single单对应
        # where({'id':[1, 2, 3, 'or', 'm']}) # WHERE `id`=1 OR `id`=2 OR `id`=3 # 其中'm'代表multi多对应
        # where({'id&nick':[1, 'frankie', 'or', 'm']}) # WHERE (`id`=1 OR `id`='frankie') AND (`nick`=1 OR `nick`='frankie') # 其中'm'代表multi多对应

    def where(self, *where):
        param_number = len(where)
        if isinstance(where[0], str):
            if param_number == 1:
                whereSubString = '( ' + where[0] + ' )'
            elif param_number > 1:
                if isinstance(where[1], tuple):
                    whereSubString = where[0] % where[1]
                elif isinstance(where[1], list):
                    whereSubString = where[0] % tuple(where[1])
                else:
                    param_array = []
                    for i in range(1, param_number):
                        param_array.append(where[i])
                    whereSubString = where[0] % tuple(param_array)
                whereSubString = '( ' + whereSubString + ' )'
        elif isinstance(where[0], dict):
            whereSubString = self._parseWhereArrayParam(where[0])
        else:
            self.throw_exception("where子句的参数只支持字符串和字典")
        self.whereStringArray.append(whereSubString)
        return self

    def parseWhere(self):
        length = len(self.whereStringArray)
        if length == 0:
            return
        if length > 1:
            self.whereString = ' WHERE ( ' + self.whereStringArray[0] + ' )'
            for i in range(1, length):
                self.whereString += ' AND ( ' + self.whereStringArray[i] + ' )'
        else:
            self.whereString = ' WHERE ' + self.whereStringArray[0]

    # table('table_name') | table('table_name AS t') | table('database.table_name AS t1')
    # table({'table_name':'', 'table_name':'t', 'database.table_name':'t1'})
    def table(self, table):
        if isinstance(table, str):
            self.tmp_table = table
        elif isinstance(table, dict):
            if len(table) == 0:
                self.throw_exception('table子句参数不能传空字典')
            self.tmp_table = ''
            for key, val in table.items():
                if val != '':
                    strpos = key.find('.')
                    if strpos == -1:
                        self.tmp_table += '`' + key.strip() + '` AS `' + val.strip() + '`,'
                    else:
                        self.tmp_table += key.strip() + ' AS `' + val.strip() + '`,'
                else:
                    strpos = key.find('.')
                    if strpos == -1:
                        self.tmp_table += '`' + key.strip() + '`,'
                    else:
                        self.tmp_table += key.strip() + ','
            self.tmp_table = self.tmp_table.rstrip(',')
        else:
            self.throw_exception('table子句的参数类型错误："' + table + '"')
        return self

    def alias(self, alias):
        self.aliasString = ' AS `' + alias + '`'
        return self

    # field() | field('') | field('*') | field(True) | field('id,username as name, db.pass')
    # field({'id':'', 'username':'name', 'db.pass':''})
    # field('sex,head', True) | field(('sex', 'head'), True)  过滤sex和head字段
    def field(self, field='', filter=False):
        if field == True:
            # 显示调用所有字段
            self.set_columns(self.table_name if not self.tmp_table else self.tmp_table)
            self.fieldString += ' '
            columns_array = self.columns
            columns_array.pop(0)
            for column in columns_array:
                self.fieldString += '`' + column + '`,'
            self.fieldString = self.fieldString.rstrip(',')
            return self
        if filter:
            # 过滤字段
            if not isinstance(field, (str, set, list, tuple)):
                self.throw_exception("过滤字段时，field子句的参数只支持字符串或set、list、tuple")
            self.set_columns(self.table_name if self.tmp_table == '' else self.tmp_table)
            columns_list = self.columns
            columns_list.pop(0)
            columns_dict = {}
            for index, item in enumerate(columns_list):
                columns_dict[str(index)] = item
            explode_array = []
            if isinstance(field, str):
                explode_array = re.split('\s{0,},\s{0,}', field.strip())
            else:
                for single_field in field:
                    explode_array.append(single_field.strip())
            for index, item in list(columns_dict.items()):
                if item in explode_array:
                    columns_dict.pop(index)
            for index, item in columns_dict.items():
                self.fieldString += '`' + item + '`,'
            self.fieldString = ' ' + self.fieldString.rstrip(',')
            return self
        if field == '' or field == '*':
            self.fieldString = ' *'
            return self
        if isinstance(field, str):
            field_array = field.split(',')
            field_array = list(map(self._addSpecialChar, field_array))
            self.fieldString = ','.join([item for item in field_array])
        elif isinstance(field, dict):
            for key, val in field.items():
                if val == '':
                    after_process_key = self._addSpecialChar(key)
                    self.fieldString += after_process_key + ','
                else:
                    after_process_key = self._addSpecialChar(key)
                    after_process_val = self._addSpecialChar(val)
                    self.fieldString += after_process_key + ' AS ' + after_process_val + ','
            self.fieldString = self.fieldString.rstrip(',')
        else:
            self.throw_exception("field子句的参数只支持字符串或dict")
        self.fieldString = ' ' + self.fieldString
        return self

    def order(self, order):
        if isinstance(order, str):
            self.orderString = ' ORDER BY ' + order
        elif isinstance(order, dict):
            self.orderString = ' ORDER BY '
            for key, val in order.items():
                if val == '':
                    self.orderString += '`' + key.strip() + '`,'
                else:
                    if val.lower() != 'asc' and val.lower() != 'desc':
                        self.throw_exception("order子句请使用asc或desc关键词指定排序，默认为asc，出现未知字符")
                    self.orderString += '`' + key.strip() + '` ' + val + ','
            self.orderString = self.orderString.rstrip(',')
        else:
            self.throw_exception("order子句的参数只支持字符串和字典")
        return self

    def limit(self, *limit):
        param_number = len(limit)
        if param_number == 1:
            if not isinstance(limit[0], (int, str)):
                self.throw_exception("limit子句的参数非法")
            if isinstance(limit[0], str):
                if not re.match('^\d+\s{0,},\s{0,}\d+$', limit[0].strip()) and not re.match('^\d+$', limit[0].strip()):
                    self.throw_exception("limit子句的参数非法")
            self.limitString = ' LIMIT ' + str(limit[0])
        elif param_number == 2:
            for i in range(2):
                if not is_numeric(limit[i]):
                    self.throw_exception("limit子句的参数非法")
            self.limitString = ' LIMIT ' + str(limit[0]) + ',' + str(limit[1])
        else:
            self.throw_exception("limit子句的参数数量必须为一或两个")
        return self

    def page(self, page_number, amount):
        if not is_numeric(page_number) or not is_numeric(amount):
            self.throw_exception("page方法只支持两个数字参数的写法")
        start = (int(page_number) - 1) * int(amount)
        self.limitString = ' LIMIT ' + str(start) + ',' + str(amount)
        return self

    def group(self, group):
        if not isinstance(group, str):
            self.throw_exception("group子句的参数只支持字符串")
        self.groupString = ' GROUP BY ' + group
        return self

    def having(self, having):
        if not isinstance(having, str):
            self.throw_exception("having子句的参数只支持字符串")
        self.havingString = ' HAVING BY ' + having
        return self

    def join(self, join):
        if isinstance(join, str):
            self.joinString += ' INNER JOIN ' + join
        elif isinstance(join, (list, tuple)):
            if len(join) != 2:
                self.throw_exception("join子句的数组参数必须有两个元素")
            self.joinString += ' ' + join[1] + ' JOIN ' + join[0]
        else:
            self.throw_exception("join子句的参数只支持字符串或list、tuple")
        return self

    def fetchSql(self, fetchSql=True):
        self.fetchSql = fetchSql
        return self

    def count(self, field='*'):
        self.fieldString = ' COUNT(' + field + ') AS f_count'
        self.limitString = ' LIMIT 1'
        is_fetchSql = False
        if self.fetchSql == True:
            is_fetchSql = True
        res = self.select()
        if is_fetchSql:
            return res
        else:
            return res[0]['f_count']

    def max(self, field):
        self.fieldString = ' MAX(' + field + ') AS f_max'
        self.limitString = ' LIMIT 1'
        is_fetchSql = False
        if self.fetchSql == True:
            is_fetchSql = True
        res = self.select()
        if is_fetchSql:
            return res
        else:
            return res[0]['f_max']

    def min(self, field):
        self.fieldString = ' MIN(' + field + ') AS f_min'
        self.limitString = ' LIMIT 1'
        is_fetchSql = False
        if self.fetchSql == True:
            is_fetchSql = True
        res = self.select()
        if is_fetchSql:
            return res
        else:
            return res[0]['f_min']

    def avg(self, field):
        self.fieldString = ' AVG(' + field + ') AS f_avg'
        self.limitString = ' LIMIT 1'
        is_fetchSql = False
        if self.fetchSql == True:
            is_fetchSql = True
        res = self.select()
        if is_fetchSql:
            return res
        else:
            return res[0]['f_avg']

    def sum(self, field):
        self.fieldString = ' SUM(' + field + ') AS f_sum'
        self.limitString = ' LIMIT 1'
        is_fetchSql = False
        if self.fetchSql == True:
            is_fetchSql = True
        res = self.select()
        if is_fetchSql:
            return res
        else:
            return res[0]['f_sum']

    def buildSql(self):
        sqlString = ''
        if self.tmp_table != '':
            table_name = self.tmp_table + self.aliasString
        else:
            table_name = '`' + self.table_name + '`' + self.aliasString
        self.fieldString = ' *' if self.fieldString == '' else self.fieldString
        self.parseWhere()
        sqlString += 'SELECT' + self.fieldString + ' FROM ' + table_name + self.joinString + self.whereString + self.groupString + self.havingString + self.orderString + self.limitString
        buildSql = self._replaceSpecialChar('%s', self.whereValueArray, sqlString)
        self._clearSubString()
        return '( ' + buildSql + ' )'

    def find(self, primary_key_value=''):
        sqlString = ''
        if self.tmp_table != '':
            table_name = self.tmp_table + self.aliasString
        else:
            table_name = '`' + self.table_name + '`' + self.aliasString
        if primary_key_value != '':
            self.set_columns(self.table_name if self.tmp_table == '' else self.tmp_table)
            self.whereStringArray.append('`' + self.columns[0] + '` = %s')
            self.whereValueArray.append(primary_key_value)
        self.limitString = ' LIMIT 1'
        self.fieldString = ' *' if self.fieldString == '' else self.fieldString
        self.parseWhere()
        sqlString += 'SELECT' + self.fieldString + ' FROM ' + table_name + self.joinString + self.whereString + self.groupString + self.havingString + self.orderString + self.limitString
        res = self.query(sqlString, True)
        return res

    def select(self, query=True):
        sqlString = ''
        if self.tmp_table != '':
            table_name = self.tmp_table + self.aliasString
        else:
            table_name = '`' + self.table_name + '`' + self.aliasString
        self.fieldString = ' *' if self.fieldString == '' else self.fieldString
        self.parseWhere()
        sqlString += 'SELECT' + self.fieldString + ' FROM ' + table_name + self.joinString + self.whereString + self.groupString + self.havingString + self.orderString + self.limitString
        if query == False:
            self.fetchSql = True
        res = self.query(sqlString)
        return res

    def add(self, data=''):
        field_str = ''
        if data != '':
            if not isinstance(data, dict):
                self.throw_exception('add方法只支持传入字典')
            length = len(data)
            if length == 0:
                placeholder = ''
            else:
                for key, val in data.items():
                    field_str += '`' + key + '`,'
                    self.whereValueArray.append(val)
                field_str = field_str.rstrip(',')
                placeholder = '%s'
                for i in range(1, length):
                    placeholder += ',%s'
        else:
            placeholder = ''
        if self.tmp_table != '':
            table_name = self.tmp_table
        else:
            table_name = '`' + self.table_name + '`'
        sqlString = 'INSERT INTO ' + table_name + ' (' + field_str + ') VALUES (' + placeholder + ')'
        res = self.execute(sqlString)
        if isinstance(res, str) or res == False:
            return res
        self.lastInsertId = self.cur.lastrowid
        return self.lastInsertId

    def addAll(self, dataList):
        if not isinstance(dataList, (list, tuple)):
            self.throw_exception('addAll方法只支持传入list或tuple')
        field_str = ''
        fieldList = []
        number = len(dataList)
        valueListStr = ''
        if number == 0:
            self.throw_exception('addAll方法请勿传入空数组')
        if not isinstance(dataList[0], dict):
            self.throw_exception('addAll方法传入的参数须为由字典组成的列表或元组')
        number_field = len(dataList[0])
        if number_field == 0:
            valueListStr += '()'
            for i in range(1, number):
                if not isinstance(dataList[i], dict):
                    self.throw_exception('addAll方法传入的参数须为由字典组成的列表或元组')
                valueListStr += ',()'
        else:
            valueStr = '('
            for key, val in dataList[0].items():
                fieldList.append(key)
                self.whereValueArray.append(val)
                field_str += key + ','
                valueStr += '%s,'
            field_str = field_str.rstrip(',')
            valueStr = valueStr.rstrip(',')
            valueStr += ')'
            valueListStr += valueStr
            for i in range(1, number):
                for j in range(number_field):
                    self.whereValueArray.append(dataList[i][fieldList[j]])
                valueListStr += ',' + valueStr
        if self.tmp_table != '':
            table_name = self.tmp_table
        else:
            table_name = '`' + self.table_name + '`'
        sqlString = 'INSERT INTO ' + table_name + ' (' + field_str + ') VALUES ' + valueListStr
        res = self.execute(sqlString)
        if isinstance(res, str) or res == False:
            return res
        self.lastInsertId = self.cur.lastrowid
        return self.lastInsertId

    def setField(self, *field):
        param_number = len(field)
        if field == 0:
            self.throw_exception('setField子句须传入参数')
        self.parseWhere()
        if self.whereString == '':
            self.set_columns(self.table_name if self.tmp_table == '' else self.tmp_table)
            if isinstance(field[0], dict) and self.columns[0] != '' and self.columns[0] in field[0]:
                if isinstance(field[0][self.columns[0]], (list, tuple)):
                    if field[0][self.columns[0]][0].upper() == 'EXP':
                        self.whereString = ' WHERE `' + self.columns[0] + '` = ' + field[0][self.columns[0]][1].strip()
                    else:
                        self.throw_exception('setField子句仅支持exp表达式更新')
                else:
                    self.whereString = ' WHERE `' + self.columns[0] + '` = %s'
                    self.whereValueArray.append(field[0][self.columns[0]])
                del field[0][self.columns[0]]
            elif self.columns[0] == '':
                self.throw_exception('没有任何更新条件，且指定数据表无主键，不被允许执行更新操作')
            else:
                self.throw_exception('没有任何更新条件，数据对象本身也不包含主键字段，不被允许执行更新操作')
        setFieldStr = ''
        updateValueArray = []
        if isinstance(field[0], str):
            if param_number != 2:
                self.throw_exception('setField子句接收两个参数（属性名，属性值）')
            if field[0].find('.') == -1:
                setFieldStr += '`' + field[0].strip() + '` = %s'
            else:
                setFieldStr += field[0].strip() + ' = %s'
            updateValueArray.append(field[1])
        elif isinstance(field[0], dict):
            if param_number != 1:
                self.throw_exception('setField子句只接收一个数组参数')
            for key, val in field[0].items():
                if isinstance(val, (list, tuple)):
                    if val[0].upper() == 'EXP':
                        if key.find('.') == -1:
                            setFieldStr += '`' + key.strip() + '` = ' + val[1].strip() + ','
                        else:
                            setFieldStr += key.strip() + ' = ' + val[1].strip() + ','
                    else:
                        self.throw_exception('setField子句仅支持exp表达式更新')
                else:
                    if key.find('.') == -1:
                        setFieldStr += '`' + key.strip() + '` = %s,'
                    else:
                        setFieldStr += key.strip() + ' = %s,'
                    updateValueArray.append(val)
            setFieldStr = setFieldStr.rstrip(',')
        else:
            self.throw_exception('setField子句传入的参数类型错误：' + field[0])
        self.whereValueArray = updateValueArray + self.whereValueArray
        if self.tmp_table != '':
            table_name = self.tmp_table + self.aliasString
        else:
            table_name = '`' + self.table_name + '`' + self.aliasString
        sqlString = 'UPDATE ' + table_name + self.joinString + ' SET ' + setFieldStr + self.whereString + self.orderString + self.limitString
        res = self.execute(sqlString)
        return res

    def setInc(self, field, value=1):
        data = {}
        data[field] = ['EXP', field + ' + ' + str(value)]
        return self.save(data)

    def setDec(self, field, value=1):
        data = {}
        data[field] = ['EXP', field + ' - ' + str(value)]
        return self.save(data)

    def save(self, data):
        if not isinstance(data, dict):
            self.throw_exception('save子句只接收数组参数')
        self.parseWhere()
        if self.whereString == '':
            self.set_columns(self.table_name if self.tmp_table == '' else self.tmp_table)
            if self.columns[0] != '' and self.columns[0] in data:
                if isinstance(data[self.columns[0]], (list, tuple)):
                    if data[self.columns[0]][0].upper() == 'EXP':
                        self.whereString = ' WHERE `' + self.columns['PRI'] + '` = ' + data[self.columns[0]][1].strip()
                    else:
                        self.throw_exception('save子句仅支持exp表达式更新')
                else:
                    self.whereString = ' WHERE `' + self.columns[0] + '` = %s'
                    self.whereValueArray.append(data[self.columns[0]])
                del data[self.columns[0]]
            elif self.columns[0] == '':
                self.throw_exception('没有任何更新条件，且指定数据表无主键，不被允许执行更新操作')
            else:
                self.throw_exception('没有任何更新条件，数据对象本身也不包含主键字段，不被允许执行更新操作')
        setFieldStr = ''
        updateValueArray = []
        for key, val in data.items():
            if isinstance(val, (list, tuple)):
                # 支持exp表达式进行数据更新
                if val[0].upper == 'EXP':
                    if key.find('.') == -1:
                        setFieldStr += '`' + key.strip() + '` = ' + val[1].strip() + ','
                    else:
                        setFieldStr += key.strip() + ' = ' + val[1].strip() + ','
                else:
                    self.throw_exception('save子句仅支持exp表达式更新')
            else:
                if key.find('.') == -1:
                    setFieldStr += '`' + key.strip() + '` = %s,'
                else:
                    setFieldStr += key.strip() + ' = %s,'
                updateValueArray.append(val)
        setFieldStr = setFieldStr.rstrip(',')
        self.whereValueArray = updateValueArray + self.whereValueArray
        if self.tmp_table != '':
            table_name = self.tmp_table + self.aliasString
        else:
            table_name = '`' + self.table_name + '`' + self.aliasString
        sqlString = 'UPDATE ' + table_name + self.joinString + ' SET ' + setFieldStr + self.whereString + self.orderString + self.limitString
        res = self.execute(sqlString)
        return res

    def delete(self, table=''):
        sqlString = ''
        if self.tmp_table != '':
            table_name = self.tmp_table + self.aliasString
        else:
            table_name = '`' + self.table_name + '`' + self.aliasString
        if table != '':
            table = ' ' + table
        self.parseWhere()
        if self.whereString == '':
            if self.joinString == '' or self.joinString.upper().find(' ON ') == -1:
                self.throw_exception('没有传入任何条件，不被允许执行删除操作')
        sqlString = 'DELETE' + table + ' FROM ' + table_name + self.joinString + self.whereString + self.orderString + self.limitString
        res = self.execute(sqlString)
        return res

    def deleteById(self, primary_key_value, table=''):
        sqlString = ''
        if self.tmp_table != '':
            table_name = self.tmp_table + self.aliasString
        else:
            table_name = '`' + self.table_name + '`' + self.aliasString
        if table != '':
            table = ' ' + table
        if primary_key_value != '':
            self.set_columns(self.table_name if self.tmp_table == '' else self.tmp_table)
            self.whereStringArray.append('`' + self.columns[0] + '` = %s')
            self.whereValueArray.append(primary_key_value)
        self.parseWhere()

        sqlString = 'DELETE' + table + ' FROM ' + table_name + self.joinString + self.whereString
        res = self.execute(sqlString)
        return res

    def query(self, queryStr, is_find=False):
        if not isinstance(queryStr, str):
            self.throw_exception('query查询须传入字符串')
        if self.fetchSql == True:
            buildSql = self._replaceSpecialChar('%s', self.whereValueArray, queryStr)
            self._clearSubString()
            return buildSql
        try:
            self.queryStr = self._replaceSpecialChar('%s', self.whereValueArray, queryStr)
            tmp_whereValueArray = self.whereValueArray
            self._clearSubString()
            if len(tmp_whereValueArray) > 0:
                self.cur.execute(queryStr, tmp_whereValueArray)
            else:
                self.cur.execute(queryStr)
            if is_find == True:
                res = self.cur.fetchone()
            else:
                res = self.cur.fetchall()
            return res
        except mysql.connector.Error as err:
            return self.haveErrorThrowException(err)

    def execute(self, execStr):
        if not isinstance(execStr, str):
            self.throw_exception('execute操作须传入字符串')
        if self.fetchSql == True:
            buildSql = self._replaceSpecialChar('%s', self.whereValueArray, execStr)
            self._clearSubString()
            return buildSql
        try:
            self.queryStr = self._replaceSpecialChar('%s', self.whereValueArray, execStr)
            tmp_whereValueArray = self.whereValueArray
            self._clearSubString()
            if len(tmp_whereValueArray) > 0:
                self.cur.execute(execStr, tmp_whereValueArray)
            else:
                self.cur.execute(execStr)
            self.numRows = self.cur.rowcount
            return self.numRows
        except mysql.connector.Error as err:
            return self.haveErrorThrowException(err)

    # If consistent_snapshot is True, Connector/Python sends WITH CONSISTENT SNAPSHOT with the statement. MySQL ignores this for isolation levels for which that option does not apply.
    # isolation_level: permitted values are 'READ UNCOMMITTED', 'READ COMMITTED', 'REPEATABLE READ', and 'SERIALIZABLE'
    # The readonly argument can be True to start the transaction in READ ONLY mode or False to start it in READ WRITE mode. If readonly is omitted, the server's default access mode is used.
    def startTrans(self, consistent_snapshot=False, isolation_level=None, readonly=False):
        for link in pythonMySQL.links.values():
            link.start_transaction(consistent_snapshot, isolation_level, readonly)

    def inTrans(self):
        return self.con.in_transaction

    def rollback(self):
        for link in pythonMySQL.links.values():
            link.rollback()

    def commit(self):
        for link in pythonMySQL.links.values():
            link.commit()

    def getLastSql(self):
        if not self.dbdebug:
            self.throw_exception('请先开启DEBUG模式')
        return self.queryStr

    def _sql(self):
        # mysql.connector的MySQLCursor类有statement属性，可以直接拿到最后执行的SQL语句
        return self.cur.statement

    def _parseWhereArrayParam(self, whereArrayParam):
        logic = ' AND '
        whereSubString = ''
        if '_complex' in whereArrayParam:
            whereSubString = '( ' + self._parseWhereArrayParam(whereArrayParam['_complex']) + ' )'
            del whereArrayParam['_complex']
        if '_logic' in whereArrayParam:
            if whereArrayParam['_logic'].upper() in self.SQL_logic:
                logic = ' ' + whereArrayParam['_logic'].upper() + ' '
            else:
                self.throw_exception('_logic参数指定的逻辑运算符不被支持："' + whereArrayParam['_logic'] + '"')
            del whereArrayParam['_logic']
        if '_string' in whereArrayParam:
            whereSubString += logic + '( ' + whereArrayParam['_string'] + ' )'
            del whereArrayParam['_string']
        if '_query' in whereArrayParam:
            explode_query = whereArrayParam['_query'].split('&')
            explode_array = {}
            for key_val in explode_query:
                explode_sub_query = key_val.split('=')
                explode_array[explode_sub_query[0]] = explode_sub_query[1]
            if '_logic' in explode_array:
                if explode_array['_logic'].upper() in self.SQL_logic:
                    sub_logic = ' ' + explode_array['_logic'].upper() + ' '
                else:
                    self.throw_exception('_query中的_logic参数指定的逻辑运算符不被支持："' + explode_array['_logic'] + '"')
                del explode_array['_logic']
            querySubString = ''
            for key, val in explode_array.items():
                start = key.find('.')
                if start != -1:
                    querySubString += sub_logic + key + " = '" + val + "'"
                else:
                    querySubString += sub_logic + "`" + key + "` = '" + val + "'"
            querySubString = querySubString.lstrip(sub_logic)
            whereSubString += logic + '( ' + querySubString + ' )'
            del whereArrayParam['_query']
        for key, val in whereArrayParam.items():
            whereArraySubString = ''
            have_and = key.find('&')
            have_or = key.find('|')
            if isinstance(val, (list, tuple)):
                if have_and == -1 and have_or == -1:
                    # 无&和|符号
                    whereArraySubString += self._singleKey2Array(key, val)
                elif (have_and != -1 and have_or == -1) or (have_and == -1 and have_or != -1):
                    # 有&符号，无|符号 或者 无&符号，有|符号
                    if have_and != -1:
                        string_logic = '&'
                        sub_logic = ' AND '
                    else:
                        string_logic = '|'
                        sub_logic = ' OR '
                    explode_array = key.split(string_logic)
                    signal = 1  # 1代表字段对应数组元素单条件查询，2代表字段对应数组元素多条件查询，3代表表达式查询
                    if len(explode_array) == len(val):
                        signal = 1
                    else:  # 带&或|的字段查询，后两位必须留位指定逻辑符(默认and)和查询方式(默认s)
                        if val[-1] == '' or val[-1] == 's':
                            signal = 1
                        elif val[-1] == 'm':
                            signal = 2
                        elif val[-1] == 'e':
                            signal = 3
                        else:
                            self.throw_exception('指定的查询方式不受支持："' + val[-1] + '"')
                    if signal == 1:
                        # 字段对应数组元素单条件查询
                        index = 0
                        for explode_val in explode_array:
                            if isinstance(val[index], (list, tuple)):
                                whereArraySubString += self._singleKey2Array(explode_val, val[index])
                            else:
                                start = explode_val.find('.')
                                if start != -1:
                                    whereArraySubString += sub_logic + explode_val + " = %s"
                                else:
                                    whereArraySubString += sub_logic + "`" + explode_val + "` = %s"
                                self.whereValueArray.append(val[index])
                            index += 1
                    elif signal == 2:
                        # 字段对应数组元素多条件查询
                        for explode_val in explode_array:
                            get_parseMultiQuery = self._parseMultiQuery(explode_val, val)
                            whereArraySubString += sub_logic + get_parseMultiQuery
                    else:
                        # 表达式查询
                        for explode_val in explode_array:
                            get_parseExpQuery = self._parseExpQuery(explode_val, val)
                            whereArraySubString += sub_logic + get_parseExpQuery
                    whereArraySubString = whereArraySubString.lstrip(sub_logic)
                    whereArraySubString = '( ' + whereArraySubString + ' )'
                else:
                    # 既有&符号，又有|符号
                    self.throw_exception('快捷查询方式中“|”和“&”不能同时使用')
            else:
                start = key.find('.')
                if have_and == -1 and have_or == -1:
                    # 无&和|符号
                    if start != -1:
                        whereArraySubString += key + " = %s"
                    else:
                        whereArraySubString += "`" + key + "` = %s"
                    self.whereValueArray.append(val)
                elif (have_and != -1 and have_or == -1) or (have_and == -1 and have_or != -1):
                    # 有&符号，无|符号 或者 无&符号，有|符号
                    if have_and != -1:
                        string_logic = '&'
                        sub_logic = ' AND '
                    else:
                        string_logic = '|'
                        sub_logic = ' OR '
                    explode_array = key.split(string_logic)
                    whereArraySubString = ''
                    for explode_val in explode_array:
                        start = explode_val.find('.')
                        if start != -1:
                            whereArraySubString += sub_logic + explode_val + " = %s"
                        else:
                            whereArraySubString += sub_logic + "`" + explode_val + "` = %s"
                        self.whereValueArray.append(val)
                    whereArraySubString = whereArraySubString.lstrip(sub_logic)
                    whereArraySubString = '( ' + whereArraySubString + ' )'
                else:
                    # 既有&符号，又有|符号
                    self.throw_exception('快捷查询方式中“|”和“&”不能同时使用')
            whereSubString += logic + whereArraySubString
        whereSubString = whereSubString.lstrip(logic)
        return whereSubString

    def _singleKey2Array(self, key, array):
        # 参数array后两位必须留位指定逻辑符(默认and)和查询方式(默认m)
        if array[-1] == '' or array[-1] == 'm':
            # 多条件查询
            return self._parseMultiQuery(key, array)
        elif array[-1] == 'e':
            # 表达式查询
            return self._parseExpQuery(key, array)
        else:
            self.throw_exception('指定的查询方式此处不受支持："' + array[-1] + '"')

    def _parseExpQuery(self, column, array):
        # 记得，传进来的array参数末尾留有两个位，一个记录逻辑符，一个记录查询类型
        expQueryString = ''
        start = column.find('.')
        specialChar_index = column.find('`')
        if specialChar_index == -1 and start == -1:
            column = '`' + column + '`'
        exp_type = array[0].upper()
        if exp_type == "EQ":
            expQueryString += column + ' = %s'
            self.whereValueArray.append(array[1])
        elif exp_type == "NEQ":
            expQueryString += column + ' <> %s'
            self.whereValueArray.append(array[1])
        elif exp_type == "GT":
            expQueryString += column + ' > %s';
            self.whereValueArray.append(array[1])
        elif exp_type == "EGT":
            expQueryString += column + ' >= %s';
            self.whereValueArray.append(array[1])
        elif exp_type == "LT":
            expQueryString += column + ' < %s';
            self.whereValueArray.append(array[1])
        elif exp_type == "ELT":
            expQueryString += column + ' <= %s';
            self.whereValueArray.append(array[1])
        elif exp_type == "LIKE" or exp_type == "NOTLIKE" or exp_type == "NOT LIKE":
            if exp_type == "LIKE":
                string = ' LIKE '
            else:
                string = ' NOT LIKE '
            if isinstance(array[1], (list, tuple, set)):
                logic = ' AND '
                if array[2] != '':
                    if array[2].upper() in self.SQL_logic:
                        logic = ' ' + array[2].upper() + ' '
                    else:
                        self.throw_exception('[NOT] LIKE查询中的逻辑运算符"' + array[2] + '"不被支持')
                for val in array[1]:
                    expQueryString += logic + column + string + ' %s'
                    self.whereValueArray.append(str(val))
                expQueryString = expQueryString.lstrip(logic)
                expQueryString = '( ' + expQueryString + ' )'
            elif isinstance(array[1], str):
                expQueryString += column + string + ' %s'
                self.whereValueArray.append(array[1])
            else:
                self.throw_exception('[NOT] LIKE查询中的第二个参数必须为字符串或list、tuple、set')
        elif exp_type == "BETWEEN" or exp_type == "NOTBETWEEN" or exp_type == "NOT BETWEEN":
            # 示例 array('between','1,8') | array('between',1,8) | array('between',array('1','8'))
            if exp_type == "BETWEEN":
                string = ' BETWEEN '
            else:
                string = ' NOT BETWEEN '
            expQueryString += column + string + '%s AND %s'
            if isinstance(array[1], (list, tuple)):
                self.whereValueArray.append(array[1][0])
                self.whereValueArray.append(array[1][1])
            elif isinstance(array[1], str):
                explode_array = array[1].split(',')
                if len(explode_array) != 2:
                    self.throw_exception('表达式查询之[NOT]BETWEEN后的参数错误：' + array[1])
                self.whereValueArray.append(explode_array[0].strip())
                self.whereValueArray.append(explode_array[1].strip())
            elif is_numeric(array[1]):
                if not is_numeric(array[2]):
                    self.throw_exception('表达式查询之[NOT]BETWEEN后的参数错误(two number expected)');
                self.whereValueArray.append(array[1])
                self.whereValueArray.append(array[2])
            else:
                self.throw_exception('表达式查询之[NOT]BETWEEN后的参数错误：' + array[1])
        elif exp_type == "IN" or exp_type == "NOTIN" or exp_type == "NOT IN":
            # 示例：array('not	in',array('a','b','c')) | array('not in','a,b,c')
            if exp_type == "IN":
                string = ' IN '
            else:
                string = ' NOT IN '
            if isinstance(array[1], (list, tuple)):
                length = len(array[1])
                if length == 0:
                    self.throw_exception('表达式查询之[NOT]IN后的数组参数为空：array()')
                expQueryString += column + string + '('
                expQueryString += '%s'
                self.whereValueArray.append(array[1][0])
                for i in range(1, length):
                    expQueryString += ',%s'
                    self.whereValueArray.append(array[1][i])
                expQueryString += ')'
            elif isinstance(array[1], str):
                explode_array = array[1].split(',')
                length = len(explode_array)
                expQueryString += column + string + '('
                expQueryString += '%s'
                self.whereValueArray.append(explode_array[0])
                for i in range(1, length):
                    expQueryString += ',%s'
                    self.whereValueArray.append(explode_array[i])
                expQueryString += ')'
            else:
                self.throw_exception('表达式查询之[NOT]IN后的参数错误：' + array[1])
        elif exp_type == "EXP":
            if isinstance(array[1], str):
                expQueryString += column + array[1]
            else:
                self.throw_exception('表达式查询之exp后的参数错误：' + array[1])
        else:
            self.throw_exception('表达式查询之表达式错误："' + array[0] + '"')
        return expQueryString

    def _parseMultiQuery(self, column, array):
        # 记得，传进来的array参数末尾留有两个位，一个记录逻辑符，一个记录查询类型
        multiQueryString = ''
        start = column.find('.')
        specialChar_index = column.find('`')
        if specialChar_index == -1 and start == -1:
            column = '`' + column + '`'
        length = len(array) - 2
        logic = ' AND '
        if array[-2] != '':
            if array[-2].upper() in self.SQL_logic:
                logic = ' ' + array[-2].upper() + ' '
            else:
                self.throw_exception('多条件查询中的逻辑运算符"' + array[-2] + '"不被支持')
        for i in range(length):
            if isinstance(array[i], (list, tuple)):
                multiQueryString += logic + self._singleKey2Array(column, array[i])
            else:
                multiQueryString += logic + column + ' = %s'
                self.whereValueArray.append(array[i])
        multiQueryString = multiQueryString.lstrip(logic)
        multiQueryString = '( ' + multiQueryString + ' )'
        return multiQueryString

    def _addSpecialChar(self, value):
        value = value.strip()
        if value.find(' as ') != -1:
            # 字符串中有" as "
            value = re.sub('\s+', ' ', value)
            # 匹配出as后的字符串
            MatchObject = re.search('(?<=\s{1}as\s{1})\w+$', value, re.I)
            if MatchObject == None:
                self.throw_exception('"' + value + '"匹配错误，请合法输入')
            else:
                table_alias = MatchObject.group(0)
            value = re.sub('(?<=\s{1}as\s{1})\w+$', '`' + table_alias + '`', value, 0, re.I)
            # 匹配出as前的字符串
            table_name = re.search('^.*(?=\s{1}as\s{1}`)', value, re.I).group(0)
            if re.match('^\w+$', table_name):
                value = re.sub('^\w+(?=\s{1}as\s{1}`)', '`' + table_name + '`', value, 0, re.I)
        elif re.match('^\w+\.\w+$', value):
            pass
        else:
            # 其他
            if not re.search('\W+', value):
                value = '`' + value + '`'
        return value

    def _replaceSpecialChar(self, pattern, replacement, subject):
        for val in replacement:
            if isinstance(val, int):
                subject = re.sub(pattern, str(val), subject, 1)
            else:
                subject = re.sub(pattern, pdo_quote(val), subject, 1)
        return subject

    # 获取文件最后一行/倒数第n行
    def _get_file_lastline(self, file_name, n=1):
        try:
            with open(file_name, 'rb') as f:
                # for line in f.readlines()[::-1] 可倒序遍历文件每一行，[::1]表示取所有元素，每1个取一个，[::-1]类同（详见python高级特性：切片）
                # 使用 for line in f.readlines()[-n:]: 可倒序遍历文件n行
                # 但是当文件过大时，使用readlines()很耗内存，故采用移动指针读取
                f.seek(-1, 2)  # 将指针定位到末尾前一个字符
                content = ''
                while n > 0:
                    s = f.read(1).decode('ascii')
                    if s == '\n' and content:
                        n -= 1
                        if n == 0:
                            break
                        content = ''
                    content = s + content
                    f.seek(-2, 1)
                return content.strip()
        except BaseException as e:
            self.throw_exception(e)

    def _clearSubString(self):
        self.SQLerror = {}
        self.fieldString = ''
        self.joinString = ''
        self.whereString = ''
        self.groupString = ''
        self.havingString = ''
        self.orderString = ''
        self.limitString = ''
        self.aliasString = ''
        self.tmp_table = ''
        self.fetchSql = False
        self.whereStringArray = []
        self.whereValueArray = []

    def haveErrorThrowException(self, err):
        if self.dbdebug:
            self.SQLerror = {
                'errno': err.errno,
                'sqlstate': err.sqlstate,
                'msg': err.msg,
                'sql': self.queryStr
            }
        return False

    def showError(self):
        if self.dbdebug:
            if 'errno' in self.SQLerror:
                print('Error Code:    ' + str(self.SQLerror['errno']))
                print('SQLSTATE:      ' + self.SQLerror['sqlstate'])
                print('Error Message: ' + self.SQLerror['msg'])
                print('Error SQL:     ' + self.SQLerror['sql'])
            else:
                print("最近一次SQL操作并没有发生错误")
        else:
            print("开启DEBUG模式查看详细错误信息")

    def getNumRows(self):
        return self.numRows

    def close(self):
        if self.connected:
            # self.cur.close()
            self.con.close()

    def __del__(self):
        self.close()

    def throw_exception(self, errMsg, ignore_debug=False):
        if self.dbdebug or ignore_debug:
            print('Error: ' + errMsg + '\n\n' + '错误追踪: \n')
            length = len(traceback.format_stack())
            # 将错误信息追踪逐行打印，length-1是因为最后一行错误追踪无意义
            for i in range(length - 1):
                print(traceback.format_stack()[i])
        else:
            errMsg = "系统出错，请联系管理员。"
            print(errMsg)
        sys.exit(0)


# 判断一个变量是否已被设置
def isset(variable):
    return variable in locals() or variable in globals()


# 判断是否数字，或者纯数字字符串
def is_numeric(var):
    try:
        float(var)
        return True
    except ValueError:
        return False


# 仿PHP的PDO::quote，当前仅对单双引号进行转义，并在字符串左右加上单引号
def pdo_quote(string):
    return "'" + re.sub(r'(?<=[^\\])([\'\"])', r'\\\1', str(string)) + "'"

#M函数
def M(dbtable, ConfigID=0, dbConfig=None):
    return pythonMySQL(dbtable, ConfigID, dbConfig)
