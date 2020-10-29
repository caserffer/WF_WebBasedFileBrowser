# -*- encoding: utf-8 -*-
'''
@File    :   PdfConverter.py
@Contact :   test@test.com
@License :   (C)Copyright 2020-2021, test

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/9/8 14:24   test      1.0         None
'''

import json
import xmind
from app import logUtil

class parse_xmind_to_jsmind():
    '''
    读取xmind文件转化为jsmind的node_array格式
    [
                {"id":"root", "isroot":true, "topic":"jsMind"},

                {"id":"sub1", "parentid":"root", "topic":"sub1"},
                {"id":"sub11", "parentid":"sub1", "topic":"sub11"},
                {"id":"sub12", "parentid":"sub1", "topic":"sub12"},
                {"id":"sub13", "parentid":"sub1", "topic":"sub13"},

                {"id":"sub2", "parentid":"root", "topic":"sub2"},
                {"id":"sub21", "parentid":"sub2", "topic":"sub21"},
                {"id":"sub22", "parentid":"sub2", "topic":"sub22"},

                {"id":"sub3", "parentid":"root", "topic":"sub3"},
            ]
    '''
    def __init__(self):
        '''
        初始化jsmind数据字典
        '''
        self.jsmind_json = []

    def root_topic(self, sheet):
        """
        获取xmind文件根节点并存储
        :type sheet: xmind文件的sheet obj
        """
        root_topic_dic = {}
        try:
            self.root_topic = sheet.getRootTopic()
        except BaseException as err:
            logUtil.logger.exception("%s____%s" % (BaseException, err))
        root_topic_dic['id'] = self.root_topic.getID()
        root_topic_dic['isroot'] = "true"
        root_topic_dic['topic'] = self.root_topic.getTitle()
        self.jsmind_json.append(root_topic_dic)
        logUtil.logger.info(self.jsmind_json)

    def topic(self, topic):
        '''
        遍历xmind文件中所有的topic元素
        :param topic:topic对象
        :return:
        '''
        # print(topic)
        if topic.getSubTopics() is not None:
            for child_topic in topic.getSubTopics():
                # print(child_topic)
                child_topic_dic = {}
                child_topic_dic['id'] = child_topic.getID()
                child_topic_dic['parentid'] = topic.getID()
                child_topic_dic['topic'] = child_topic.getTitle()
                child_topic_dic['direction'] = "right"
                self.jsmind_json.append(child_topic_dic)
                if topic.getSubTopics() is not None:
                    self.topic(child_topic)

    def load_xmind_file(self, path):
        workbook = xmind.load(path)
        p_sheet = workbook.getPrimarySheet()
        r_topic = p_sheet.getRootTopic()
        self.root_topic(p_sheet)
        self.topic(r_topic)