import json
import os
import time
from app import logUtil
import shutil
from django.http import HttpResponse, Http404, FileResponse
from django.utils.encoding import escape_uri_path
import tempfile, zipfile
from wsgiref.util import FileWrapper


class Folder:
    def __init__(self, path):
        self.path = path

    def __getFolderDict(self, path):
        try:
            os.chdir(path)
            content = os.listdir(path)
            currentDict = {"name": os.path.basename(path), "open": False, "path": path}
            children = []
            for i in content:
                if os.path.isdir(i):
                    children.append({"name": i, "path": path + "/" + i, "isParent": "true"})
            for i in content:
                if not os.path.isdir(i):
                    children.append({"name": i, "path": path + "/" + i})
            currentDict["children"] = children
            return children
        except BaseException as err:
            logUtil.logger.exception("%s____%s" % (BaseException, err))
            currentDict = {"name": os.path.basename(path)+" Error"+repr(err), "open": False, "path": path}
            logUtil.logger.exception("%s____%s" % (BaseException, currentDict))
            return currentDict

    def getFolderJson(self):
        return json.dumps(self.__getFolderDict(self.path))


class fileOperator:
    def __init__(self, path=None):
        self.path = path

    def forceRemove(self, path):
        try:
            # if os.path.isfile(path):
            #     os.remove(path)
            #     return
            #
            # fileList=os.listdir(path)
            # for file in fileList:
            #     if os.path.isfile(path+"/"+file):
            #         os.remove(path+"/"+file)
            #     else:
            #         self.forceRemove(path+"/"+file)
            #
            # os.removedirs(path)
            if os.path.isfile(path):
                os.remove(path)
                return
            else:
                shutil.rmtree(path)
        except BaseException as err:
            logUtil.logger.exception("%s____%s" % (BaseException, err))
        return

    def copyFiles(self, list, targetPath,isMove=False):
        copyedList=[]
        if not os.path.isdir(targetPath):
            targetPath=os.path.dirname(targetPath)
        for i in list:
            if os.path.exists(targetPath + '/' + os.path.basename(i)):
                temp = 0
                while True:
                    fname, ext = os.path.splitext(os.path.basename(i))
                    if not os.path.exists(targetPath + '/' + fname + str(temp) + ext):
                        shutil.copy(i, targetPath + '/' + fname + str(temp) + ext)
                        copyedList.append(i)
                        break
                    else:
                        temp += 1
            shutil.copy(i, targetPath + '/' + os.path.basename(i))
            copyedList.append(i)
        if isMove:
            for i in copyedList:
                os.remove(i)
        return True

    def zipFilesInResponse(self, needZipFileList):
        if len(needZipFileList) == 1 and not os.path.isdir(needZipFileList[0]):
            try:
                response = FileResponse(open(needZipFileList[0], 'rb'))
                response['content-type'] = "application/octet-stream"
                response['Content-Disposition'] = 'attachment;'
                response['filename'] = escape_uri_path((os.path.basename(needZipFileList[0])))
                return response
            except Exception:
                raise Http404
        else:
            okList = []
            temp = "temp.zip"
            zipFile = zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED)
            for file in needZipFileList:
                if os.path.isdir(file):
                    for path, dirnames, filenames in os.walk(file):
                        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
                        fpath = path.replace(file, '')
                        for filename in filenames:
                            print("pricessing "+os.path.join(path, filename))
                            if not os.path.join(path, filename) in okList:
                                okList.append(os.path.join(path, filename))
                                zipFile.write(os.path.join(path, filename), os.path.join(fpath, filename))
                else:
                    if not file in okList:
                        okList.append(file)
                        zipFile.write(file,os.path.basename(file))
            # for file in needZipFileList:
            #     if os.path.isfile(file) and (file not in okList):
            #         zipFile.write(file,os.path.basename(file))

            zipFile.close()

            response = FileResponse(open(temp, 'rb'))
            response['content-type'] = "application/octet-stream"
            response['Content-Disposition'] = 'attachment;'
            response['filename'] = "download.zip"
            os.remove("temp.zip")
            return response
            # except Exception:
            #     raise Http404
            # finally:
            #     pass

    def mkdir(self,path):
        '''
        使用时间戳作为新建文件夹后缀避免重名问题
        :param path: 当前路径
        :return:
        '''
        t = int(time.time())
        logUtil.logger.info("当前路径：" + path)
        path = path+"/newFolder_"+str(t)
        logUtil.logger.info("创建新路径："+path)
        try:
            os.makedirs(path)
            logUtil.logger.info("创建新路径：" + path+" is success!")
        except BaseException as err:
            logUtil.logger.exception("%s____%s" % (BaseException, err))
        # temp=0
        # if os.path.isdir(path):
        #     if os.path.exists(path+"/newFolder"):
        #         while True:
        #             if not os.path.exists(path+"/newFolder"+str(temp)):
        #                 os.mkdir(path+"/newFolder"+str(temp))
        #                 break
        #             temp+=1
        #     else:
        #         os.mkdir(path + "/newFolder")
        #
        # else:
        #     if os.path.exists(os.path.dirname(path)+"/newFolder"):
        #         while True:
        #             if not os.path.exists(os.path.dirname(path)+"/newFolder"+str(temp)):
        #                 os.mkdir(os.path.dirname(path)+"/newFolder"+str(temp))
        #                 break
        #             temp+=1
        #     else:
        #         os.mkdir(os.path.dirname(path) + "/newFolder")


