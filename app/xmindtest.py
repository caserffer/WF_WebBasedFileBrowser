#!/usr/bin/env python

# -*- coding:utf-8 -*-


import json

import xmind

import pipes


def dict_to_prettify_json(data):
    print(json.dumps(data, indent=4, separators=(',', ': ')))


def custom_parse_xmind(workbook):
    elements = {}

    def _echo(tag, element, indent=0):

        title = element.getTitle()

        elements[element.getID()] = title

        print('\t' * indent, tag, ':', pipes.quote(title))

    def dump_sheet(sheet):

        root_topic = sheet.getRootTopic()

        _echo('RootTopic', root_topic, 1)

        for topic in root_topic.getSubTopics() or []:
            _echo('AttachedSubTopic', topic, 2)

        for topic in root_topic.getSubTopics(xmind.core.const.TOPIC_DETACHED) or []:
            _echo('DetachedSubtopic', topic, 2)

        for rel in sheet.getRelationships():
            id1, id2 = rel.getEnd1ID(), rel.getEnd2ID()

            print('Relationship: [%s] --> [%s]' % (elements.get(id1), elements.get(id2)))



    # 遍历画布

    for sheet in workbook.getSheets():
        _echo('Sheet', sheet)

        dump_sheet(sheet)


# 加载已有xmind文件，如果不存在，则新建

workbook = xmind.load('1.xmind')

# print(workbook.getData())  # 获取整个xmind数据(字典的形式)

dict_to_prettify_json(workbook.getData())

# # 获取某个画布的数据(字典的形式)
#
# first_sheet = workbook.getPrimarySheet()
#
# dict_to_prettify_json(first_sheet.getData())
#
# # 获取某个主题数据(字典的形式)
#
# root_topic = first_sheet.getRootTopic()
#
# dict_to_prettify_json(root_topic.getData())
#
# # 获取评论数据
#
# commentsbook = workbook.commentsbook
#
# print(commentsbook.getData())
#
# # 自定义解析
#
# custom_parse_xmind(workbook)