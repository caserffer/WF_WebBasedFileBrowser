#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   PdfConverter.py    
@Contact :   test@test.com
@License :   (C)Copyright 2020-2021, test

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/9/8 14:24   test      1.0         None
'''


import threading
import os
import platform
import subprocess
from app import logUtil

try:
    import pythoncom
except ImportError:
    pythoncom = None

try:
    from comtypes import client
except ImportError:
    client = None

try:
    from win32com.client import constants, gencache, Dispatch, DispatchEx
except ImportError:
    constants = None
    gencache = None
    Dispatch = None
    DispatchEx = None




class PdfConverter(threading.Thread):
    def __init__(self, office_file_path):
        threading.Thread.__init__(self)
        self.pdf_path = ""
        if platform.system() == "Windows":
            self.root_path = "D:\web_file_root\SC-TestCase"
            self.work_dir = "D:\pyproject\WF_WebBasedFileBrowser"
            self.pdf_root = "static\pdfs"
        elif platform.system() == "Linux":
            self.root_path = "/opt/web_file_root/SC-TestCase"
            self.work_dir = "/opt/qc_web"
            self.pdf_root = "static/pdfs"
        self.office_file_path = office_file_path

    def get_result(self):
        try:
            return self.pdf_path
        except Exception:
            return None

    def run(self):
        '''
        exchange office file into pdf file
        :return:
        '''
        self.load_office_file(self.office_file_path)
        self.run_conver()
        logUtil.logger.info("pdf save path :"+self.pdf_path)

    def load_office_file(self, pathname):
        self._handle_postfix = ['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx']
        self._filename_list = list()
        pathname = str(pathname)
        (filepath, tempfilename) = os.path.split(pathname)
        logUtil.logger.info(filepath)
        filepath = filepath.replace(self.root_path, "")
        logUtil.logger.info("替换root_path后的filepath:"+filepath)
        # try:
        #     with open("./app/rootpath.conf") as root:
        #         self.root_path = root.read()
        # except Exception:
        #     logUtil.logger.info("rootpath.conf read error!")
        #     raise
        logUtil.logger.info("root_path:"+self.root_path)
        logUtil.logger.info("_export_folder:"+self.work_dir+'/'+self.pdf_root+filepath)
        self._export_folder = str(self.work_dir+'/'+self.pdf_root+filepath)
        # self._export_folder = filepath
        if not os.path.exists(self._export_folder):
            os.makedirs(self._export_folder)
            # os.mkdir(os.path.join(settings.USER_DIR_FLODER,card_num,'record'))
        self._enumerate_filename(pathname)

    def _enumerate_filename(self, pathname):
        '''
        读取所有文件名
        '''
        full_pathname = os.path.abspath(pathname)
        if os.path.isfile(full_pathname):
            if self._is_legal_postfix(full_pathname):
                self._filename_list.append(full_pathname)
            else:
                raise TypeError('文件 {} 后缀名不合法！仅支持如下文件类型：{}。'.format(pathname, '、'.join(self._handle_postfix)))
        elif os.path.isdir(full_pathname):
            for relpath, _, files in os.walk(full_pathname):
                for name in files:
                    filename = os.path.join(full_pathname, relpath, name)
                    if self._is_legal_postfix(filename):
                        self._filename_list.append(os.path.join(filename))
        else:
            raise TypeError('文件/文件夹 {} 不存在或不合法！'.format(pathname))

    def _is_legal_postfix(self, filename):
        return filename.split('.')[-1].lower() in self._handle_postfix and not os.path.basename(filename).startswith(
            '~')

    def run_conver(self):
        '''
        进行批量处理，根据后缀名调用函数执行转换
        '''
        logUtil.logger.info('需要转换的文件数：'+str(len(self._filename_list)))
        for filename in self._filename_list:
            postfix = filename.split('.')[-1].lower()
            filename = str(filename)
            if platform.system() == "Linux":
                logUtil.logger.info('linux环境！')
                funcCall = getattr(self, "doc2pdf_linux")
            elif platform.system() == "Windows":
                logUtil.logger.info('windows环境！')
                funcCall = getattr(self, postfix)
            logUtil.logger.info('原文件：'+filename)
            funcCall(filename)
        logUtil.logger.info('转换完成！')

    def doc(self, filename):
        '''
        doc 和 docx 文件转换
        '''
        # name = os.path.basename(filename).split('.')[0] + '.pdf'
        name = self.exchange_suffix(filename)
        exportfile = os.path.join(self._export_folder, name)
        exportfile = str(exportfile)
        pythoncom.CoInitialize()
        logUtil.logger.info('保存 PDF 文件：'+exportfile)
        gencache.EnsureModule('{00020905-0000-0000-C000-000000000046}', 0, 8, 4)
        w = Dispatch("Word.Application")
        doc = w.Documents.Open(filename)
        doc.ExportAsFixedFormat(exportfile, constants.wdExportFormatPDF,
                                Item=constants.wdExportDocumentWithMarkup,
                                CreateBookmarks=constants.wdExportCreateHeadingBookmarks)

        w.Quit(constants.wdDoNotSaveChanges)
        self.pdf_path = self.pdf_url_exchange(exportfile)

    def docx(self, filename):
        self.doc(filename)

    def xls(self, filename):
        '''
        xls 和 xlsx 文件转换
        '''
        # l = len(os.path.basename(filename).split('.'))
        # t = os.path.basename(filename).split('.')[l - 1]
        # f = os.path.basename(filename).replace(t, "")

        name = self.exchange_suffix(filename)
        exportfile = os.path.join(self._export_folder, name)
        exportfile = str(exportfile)
        pythoncom.CoInitialize()
        xlApp = DispatchEx("Excel.Application")
        xlApp.Visible = False
        xlApp.DisplayAlerts = 0
        books = xlApp.Workbooks.Open(filename, False)
        books.ExportAsFixedFormat(0, exportfile)
        books.Close(False)
        logUtil.logger.info('保存 PDF 文件：', exportfile)
        xlApp.Quit()
        self.pdf_path = self.pdf_url_exchange(exportfile)

    def xlsx(self, filename):
        self.xls(filename)

    def ppt(self, filename):
        '''
        ppt 和 pptx 文件转换
        '''
        name = os.path.basename(filename).split('.')[0] + '.pdf'
        exportfile = os.path.join(self._export_folder, name)
        #编码转换，处理中文特殊字符导致程序异常
        exportfile = str(exportfile)
        gencache.EnsureModule('{00020905-0000-0000-C000-000000000046}', 0, 8, 4)
        p = Dispatch("PowerPoint.Application")
        ppt = p.Presentations.Open(filename, False, False, False)
        ppt.ExportAsFixedFormat(exportfile, 2, PrintRange=None)
        logUtil.logger.info('保存 PDF 文件：', exportfile)
        p.Quit()

    def pptx(self, filename):
        self.ppt(filename)

    def doc2pdf_linux(self, filename):
        """
        convert a doc/docx document to pdf format (linux only, requires libreoffice)
        :param doc: path to document
        """
        name = self.exchange_suffix(filename)
        exportfile = os.path.join(self._export_folder, name)
        exportfile = str(exportfile)
        cmd = 'libreoffice --headless --convert-to pdf:writer_pdf_Export'.split() + [filename] + ['--outdir'] + [self._export_folder]
        p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        p.wait(timeout=30)
        stdout, stderr = p.communicate()
        if stderr:
            logUtil.logger.exception(stderr)
            raise subprocess.SubprocessError(stderr)
        self.pdf_path = self.pdf_url_exchange(exportfile)

    def exchange_suffix(self, filename):
        '''
        change office file suffix to pdf suffix
        :param filename: filepath with office suffix
        :return: filepath with pdf suffix
        '''
        l = len(os.path.basename(filename).split('.'))
        t = os.path.basename(filename).split('.')[l - 1]
        f = os.path.basename(filename).replace(t, "")
        pdf_name = f + 'pdf'
        return  pdf_name

    def pdf_url_exchange(self, filename):
        return filename.replace(self.work_dir, "")



# if __name__ == "__main__":
#     # 支持文件夹批量导入
#     folder = 'tmp'
#     # pathname = os.path.join(os.path.abspath('.'), folder)
#     # pathname = 'D:\1\2\3/00 123'
#     pathname = 'D:\web_file_root\SC-TestCase/00_基础功能/001 配置/StreamCache配置项汇总-by黄美珊_2017.0323final.xlsx'
#     # 也支持单个文件的转换
#     # pathname = 'test.doc'
#
#     # pdfConverter = PdfConverter(pathname)
#     # pdfConverter.run_conver()
#     p = PdfConverter(pathname)
#     p.start()
#     p.join()


