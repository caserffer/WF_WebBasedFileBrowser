'django.middleware.csrf.CsrfViewMiddleware'
from django.shortcuts import render
from app import logUtil
import platform
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from app import Utils
from django.http import HttpResponse, Http404, FileResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import escape_uri_path
import tempfile, zipfile
from wsgiref.util import FileWrapper
import os
import json
from app import JsMind
from app import PdfConverter
from app import models
import threading
import base64

# Create your views here.
userdata = None
rootpath=None

def needUserCookies(func):
    def wrapper(req):
        if isAuthenticated(req.COOKIES.get('username'), req.COOKIES.get('password')):
            return func(req)
        return HttpResponse("ERROR check your password!")
    return wrapper


def login(req):
    return render(req, "login.html")


def error(req):
    return HttpResponse("ERROR check your password!")


def isAuthenticated(username, password):
    # global userdata
    # if userdata == None:
    #     with open("./app/userdata.conf") as config:
    #         userdata = eval(config.read())
    try:
        login_user_obj = models.User.objects.get(user_name=username)
        if login_user_obj.pass_word == password:
            logUtil.logger.info("用户："+username+"登录成功！")
            return True
        else:
            logUtil.logger.info("用户：" + username + "用户名或密码错误，登录失败！")
            return False
    except Exception:
        return False


@csrf_exempt
def checkPassword(req):
    username = req.POST.get("username")
    password = req.POST.get("password")
    language=req.POST.get("language","en")
    if isAuthenticated(username, password):
        responseJson = {
            "ok": '/index',
        }
        response = HttpResponse(json.dumps(responseJson), content_type="application/json")
        response.set_cookie('username', username, 3600)
        response.set_cookie('password', password, 3600)
        response.set_cookie('language', language, 3600)
        return response
    else:
        responseJson = {
            "ok": '/error',
        }
        return HttpResponse(json.dumps(responseJson), content_type="application/json")


@needUserCookies
def main(req):
    global rootpath
    # try:
    #     with open("./app/rootpath.conf") as root:
    #         rootpath=root.read()
    # except Exception:
    #     pass
    if platform.system() == "Windows":
        rootpath = "D:\web_file_root\SC-TestCase"
    elif platform.system() == "Linux":
        rootpath = "/opt/web_file_root"
    logUtil.logger.info("view.rootpath"+rootpath)
    Folder = Utils.Folder(rootpath)
    dataJson = Folder.getFolderJson()
    language=req.COOKIES.get('language')

    if language=="en":
        return render(req, "index_en-US.html", {"dataJson": dataJson})
    if language=="cn":
        return render(req, "index_zh-CN.html", {"dataJson": dataJson})

@csrf_exempt
@needUserCookies
def getDirContent(req):
    path = req.POST.get('path', None)
    if path is not None:
        Folder = Utils.Folder(path)
        dataJson = Folder.getFolderJson()
        return HttpResponse(dataJson, content_type="application/json")
    return HttpResponse(json.dumps({}), content_type="application/json")


@needUserCookies
def deleteFiles(req):
    deleteList = req.POST.get('deleteList', None).split(",")
    fileOperator = Utils.fileOperator()
    for file in deleteList:
        fileOperator.forceRemove(file)
    response = {
        "ok": True,

    }
    return HttpResponse(json.dumps(response), content_type="application/json")


@needUserCookies
def renameFiles(req):
    originPath = req.POST.get('originPath', None)
    logUtil.logger.info("originPath:"+originPath)
    newname = req.POST.get('newName', None)
    logUtil.logger.info("newname:"+newname)
    try:
        # test = os.path.split(originPath)[0]
        # print(test)
        renamePath = os.path.split(originPath)[0] + "/" + newname
        print("rename path:"+renamePath)
        print(os.getpid())
        os.rename(str(originPath), str(renamePath))
        logUtil.logger.info(str(originPath)+" 重命名为："+str(renamePath)+" is success!")
        result = True
    except BaseException as err:
        result = False
        logUtil.logger.exception("%s____%s" % (BaseException, err))
    response = {
        "ok": result,

    }
    return HttpResponse(json.dumps(response), content_type="application/json")


@needUserCookies
def copyFiles(req):
    needCopyFileList = req.POST.get('needCopyFileList', None).split(",")
    targetPath = req.POST.get('targetPath', None)
    isMove = req.POST.get('isMove', False)
    fileOperator = Utils.fileOperator()

    fileOperator.copyFiles(needCopyFileList, targetPath, False if isMove != "true" else True)
    response = {
        "ok": True,
    }
    return HttpResponse(json.dumps(response), content_type="application/json")


@needUserCookies
def downloadFiles(req):
    downloadFileList = req.POST.get("downloadFileList").split(",")
    print(downloadFileList)
    fileOperator = Utils.fileOperator()
    return fileOperator.zipFilesInResponse(downloadFileList)


def mkdir(req):
    path = req.POST.get("path")
    fileOperator = Utils.fileOperator()
    fileOperator.mkdir(path)
    response = {
        "ok": True,
    }
    return HttpResponse(json.dumps(response), content_type="application/json")


@needUserCookies
def uploadFiles(req):
    response = {
        "ok": True,
    }
    try:
        files = req.FILES
        path = req.META.get("HTTP_PATH").encode('utf-8').decode("unicode_escape")
        if os.path.isfile(path) or (not os.path.exists(path)):
            path = os.path.dirname(path)

        for f in files:
            file = files[f]
            destination = open(path + "/" + file.name, 'wb+')
            for chunk in file.chunks():
                destination.write(chunk)
            destination.close()
    except Exception:
        response = {
            "ok": "上传失败",
        }

    return HttpResponse(json.dumps(response), content_type="application/json")


@needUserCookies
def previewFiles(req):
    path = req.POST.get("path", None)
    ext = os.path.splitext(path)[1][1:].lower()
    logUtil.logger.info("预览文件路径："+path)
    imgExtList = ["jpg", "png", "bmp"]
    textExtList = ["txt", "ini", "inf", "py", "c", "cpp", "java", "conf"]
    officeExtList = ["doc", "docx", "ppt", "pptx", "xls", "xlsx"]
    xmindExtList = ["xmind"]
    if ext in imgExtList:
        logUtil.logger.info("预览IMG")
        with open(path, 'rb') as f:
            image_data = f.read()
        base64_data = base64.b64encode(image_data)
        s = base64_data.decode()
        imgBase64 = 'data:image/jpeg;base64,' + s
        response = {
            "file": imgBase64,
            "type": 'img'
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    if ext in textExtList:
        logUtil.logger.info("预览Text")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception:
            try:
                with open(path, 'r', encoding='gb2312') as f:
                    text = f.read()
            except Exception:
                with open(path, 'r', encoding='ansi') as f:
                    text = f.read()
        response = {
            "file": text,
            "type": 'text'
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    if ext in xmindExtList:
        logUtil.logger.info("预览Xmind")
        try:
            # print(path)
            # workbook = xmind.load(path)
            # print(workbook.to_prettify_json())
            js_mind = JsMind.parse_xmind_to_jsmind()
            js_mind.load_xmind_file(path)
            logUtil.logger.debug("jsmind json data is: ")
            logUtil.logger.debug(js_mind.jsmind_json)
        except BaseException as err:
            logUtil.logger.exception("%s____%s" % (BaseException, err))
        response = {
            "data": js_mind.jsmind_json,
            "type": 'xmind'
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    if ext in officeExtList:
        logUtil.logger.info("预览office")
        try:
            t1 = PdfConverter.PdfConverter(path)
            t1.start()
            t1.join()
        except BaseException as err:
            logUtil.logger.exception("%s____%s" % (BaseException, err))
        response = {
            "path": t1.get_result(),
            "type": 'pdf'
        }
        return HttpResponse(json.dumps(response), content_type="application/json")




    response = {
        "file": "Unsupport file \n 不支持的文件类型",
        "type": 'error'
    }
    return HttpResponse(json.dumps(response), content_type="application/json")

