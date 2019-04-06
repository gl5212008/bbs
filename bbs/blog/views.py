from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import JsonResponse
from django import views
from blog.forms import LoginForm, RegisterForm
from django.contrib import auth
from django.views.decorators.cache import never_cache
from utils.geetest import GeetestLib
from blog import models
from utils.mypage import MyPage
from django.db.models import Count, F
from django.db import transaction
import os
from django.conf import settings
from bs4 import BeautifulSoup
# Create your views here.

V_CODE = ""

# 请在官网申请ID使用，示例ID不可使用
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


# 滑动验证码第一步的API,初始化一些参数用来校验滑动验证码
def pcgetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


# 滑动验证码版本的登录
def login2(request):
    res = {"code": 0}
    if request.method == "POST":
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)

        if result:
            # 滑动验证码校验通过
            username = request.POST.get('username')
            pwd = request.POST.get('password')
            print(username, pwd)
            user = auth.authenticate(username=username, password=pwd)
            if user:
                # 用户名密码正确
                auth.login(request, user)
            else:
                # 用户名或密码错误
                res["code"] = 1
                res["msg"] = "用户名或密码错误"

        else:
            # 滑动验证码校验失败
            res["code"] = 1
            res["msg"] = "验证码错误"
        return JsonResponse(res)



        return HttpResponse(json.dumps(result))
    form_obj = LoginForm()
    return render(request, "login2.html", {"form_obj": form_obj})


# 登录
class Login(views.View):

    def get(self, request):
        form_obj = LoginForm()
        return render(request, "login.html", {"form_obj": form_obj})

    def post(self, request):
        res = {"code": 0}
        print(request.POST)
        username = request.POST.get('username')
        pwd = request.POST.get('password')
        v_code = request.POST.get('v_code')
        print(v_code)
        print(V_CODE)
        # 先判断验证码是否正确
        if v_code.upper() != request.session.get("v_code", ""):
            res["code"] = 1
            res["msg"] = "验证码错误"
        else:
            # 校验用户名密码是否正确
            user = auth.authenticate(username=username, password=pwd)
            if user:
                # 用户名密码正确
                auth.login(request, user)
            else:
                # 用户名或密码错误
                res["code"] = 1
                res["msg"] = "用户名或密码错误"
        return JsonResponse(res)


# 首页
class Index(views.View):
    def get(self, request):
        article_list = models.Article.objects.all()
        # d = {"name": "lvyang", "items": "睡觉"}
        # d.items()
        # obj = models.Article.objects.first()
        # obj.articleupdown_set.all().count()

        # 分页
        data_amount = article_list.count()
        page_num = request.GET.get("page", 1)
        page_obj = MyPage(page_num, data_amount, per_page_data=1, url_prefix='index')
        # 按照分页的设置对总数据进行切片
        data = article_list[page_obj.start:page_obj.end]
        page_html = page_obj.ret_html()
        return render(request, "index.html", {"article_list": data, "page_html": page_html})


# 专门用来返回验证码图片的视图
# 返回响应的时候告诉浏览器不要缓存
@never_cache
def v_code(request):
    # 随机生成图片
    from PIL import Image, ImageDraw, ImageFont
    import random
    # 生成随机颜色的方法
    def random_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    # 生成图片对象
    image_obj = Image.new(
        "RGB",  # 生成图片的模式
        (250, 35),  # 图片大小
        random_color()
    )
    # 生成一个准备写字的画笔
    draw_obj = ImageDraw.Draw(image_obj)  # 在哪里写
    font_obj = ImageFont.truetype('static/font/kumo.ttf', size=28)  # 加载本地的字体文件

    # 生成随机验证码
    tmp = []
    for i in range(5):
        n = str(random.randint(0, 9))
        l = chr(random.randint(65, 90))
        u = chr(random.randint(97, 122))
        r = random.choice([n, l, u])
        tmp.append(r)
        # 每一次取到要写的东西之后，往图片上写
        draw_obj.text(
            (i*45+25, 0),  # 坐标
            r,  # 内容
            fill=random_color(),  # 颜色
            font=font_obj  # 字体
        )

    # # 加干扰线
    # width = 250  # 图片宽度（防止越界）
    # height = 35
    # for i in range(5):
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
    #     draw_obj.line((x1, y1, x2, y2), fill=random_color())
    #
    # # 加干扰点
    # for i in range(40):
    #     draw_obj.point([random.randint(0, width), random.randint(0, height)], fill=random_color())
    #     x = random.randint(0, width)
    #     y = random.randint(0, height)
    #     draw_obj.arc((x, y, x+4, y+4), 0, 90, fill=random_color())

    v_code = "".join(tmp)  # 得到最终的验证码
    # global V_CODE
    # V_CODE = v_code  # 保存在全局变量不行！！！
    # 将该次请求生成的验证码保存在该请求对应的session数据中
    request.session['v_code'] = v_code.upper()

    # 将上一步生成的图片保存在本地的static目录下
    # 每一次 都在硬盘中保存再读取都涉及IO操作，会慢
    # with open('static/oo.png', 'wb') as f:
    #     image_obj.save(f)
    #
    # with open('static/oo.png', "rb") as f:
    #     data = f.read()
    # 直接将生成的图片保存在内存中
    from io import BytesIO
    f = BytesIO()
    image_obj.save(f, "png")
    # 从内存读取图片数据
    data = f.getvalue()
    return HttpResponse(data, content_type="image/png")


# -------------day75 ↓ -------------------
# 注册
class RegView(views.View):
    def get(self, request):
        form_obj = RegisterForm()
        return render(request, "register.html", {"form_obj": form_obj})

    def post(self, request):
        res = {"code": 0}
        print(request.POST)
        # 先进行验证码的校验
        v_code = request.POST.get("v_code", "")
        if v_code.upper() == request.session.get("v_code"):
            # 验证码正确
            form_obj = RegisterForm(request.POST)
            # 使用form做校验
            if form_obj.is_valid():
                # 数据有效
                # 1. 注册用户
                print(form_obj.cleaned_data)
                # 注意移除不需要的re_password
                form_obj.cleaned_data.pop("re_password")
                # 拿到用户上传的头像文件
                avatar_file = request.FILES.get("avatar")
                models.UserInfo.objects.create_user(**form_obj.cleaned_data, avatar=avatar_file)
                # 登录成功之后跳转到登录页面
                res["msg"] = '/login/'
            else:
                # 用户填写的数据不正经
                res["code"] = 1
                res["msg"] = form_obj.errors  # 拿到所有字段的错误提示信息
        else:
            res["code"] = 2
            res["msg"] = '验证码错误'
        return JsonResponse(res)


# 注销
def logout(request):
    auth.logout(request)
    return redirect("/login/")


# ----------------- day77 ↓ -------------------
# 每个用户自己的博客站点页面
def home(request, username, *args):
    print(args)
    # 先找用户
    print(username)
    # user_obj = models.UserInfo.objects.filter(username=username).first()
    # if not user_obj:
    #     return HttpResponse("404...")
    # 原理同上
    user_obj = get_object_or_404(models.UserInfo, username=username)
    # 查找当前用户关联的blog对象
    blog = user_obj.blog

    # 查找当前用户写的所有文章
    article_list = models.Article.objects.filter(user=user_obj)
    if args:
        # 表示进入分组展示文章的模式
        if args[0] == "category":
            # 表示按照文章分类查询
            article_list = article_list.filter(category__title=args[1])
        elif args[0] == "tag":
            # 表示按照文章的标签查询
            article_list = article_list.filter(tags__title=args[1])
        else:
            # 表示按照文章的日期归档查询
            try:
                year, month = args[1].split("-")
                article_list = article_list.filter(create_time__year=year, create_time__month=month)
            except Exception as e:
                article_list = []

    return render(request, "home.html", {
        "blog": blog,
        "username": username,
        "article_list": article_list
    })


def left_menu(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()

    # 查找当前用户关联的blog对象
    blog = user_obj.blog
    # 查找当前blog对应的文章分类有哪些
    category_list = models.Category.objects.filter(blog=blog)
    # 查找当前blog对应的文章标签有哪些
    tag_list = models.Tag.objects.filter(blog=blog)
    # 对当前blog的所有文章按照年月 分组 查询
    # 1. models.Article.objects.filter(user=user_obj)                   --> 查询出当前作者写的所有文章
    # 2. .extra(select={"y_m": "DATE_FORMAT(create_time, '%%Y-%%m')"}   --> 将所有文章的创建时间格式化成年-月的格式，方便后续分组
    # 3. .values("y_m").annotate(c=Count("id"))                         --> 用上一步时间格式化得到的y_m字段做分组，统计出每个分组对应的文章数
    # 4. .values("y_m", "c")                                            --> 把页面需要的日期归档和文章数字段取出来
    archive_list = models.Article.objects.filter(user=user_obj).extra(
        select={"y_m": "DATE_FORMAT(create_time, '%%Y-%%m')"}
    ).values("y_m").annotate(c=Count("id")).values("y_m", "c")

    return user_obj, blog, category_list, tag_list, archive_list


# 文章详情
def article(request, username, id):
    """
    :param request: 请求对象
    :param username: 用户名
    :param id: 主键
    :return:
    """
    user_obj = get_object_or_404(models.UserInfo, username=username)
    blog = user_obj.blog
    article_obj = models.Article.objects.filter(id=id).first()
    # 找到当前文章的评论
    comment_list = models.Comment.objects.filter(article=article_obj)
    return render(request, "article2.html", {
        "blog": blog,
        "username": username,
        "article": article_obj,
        "s12": "mengmeng",
        "comment_list": comment_list
    })


# 点赞
def mengmeng(request):
    if request.method == "POST":
        res = {"code": 0}
        print(request.POST)
        user_id = request.POST.get("userId")
        article_id = request.POST.get("articleId")
        is_up = request.POST.get("isUp")
        print(is_up, type(is_up))
        is_up = True if is_up.upper() == 'TRUE' else False
        # 5.不能给自己点赞
        article_obj = models.Article.objects.filter(id=article_id, user_id=user_id)
        if article_obj:
            # 表示是给自己写的文章点赞
            res["code"] = 1
            res["msg"] = '不能给自己的文章点赞！' if is_up else '不能反对自己的内容！'
        else:
            # 3.同一个人只能给同一篇文章点赞一次
            # 4.点赞和反对两个只能选一个
            # 判断一下当前这个人和这篇文章 在点赞表里有没有记录
            is_exist = models.ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()
            if is_exist:
                res["code"] = 1
                # 表示已经点赞过或反对过
                # if is_exist.is_up == True:
                #     # 已经点过赞
                #     res["msg"] = '已经点过赞'
                # else:
                #     # 已经反对过
                #     res["msg"] = '已经反对过'

                res["msg"] = '已经点过赞' if is_exist.is_up else '已经反对过'
            else:
                # 真正点赞
                # 注意？
                # 事务操作，，
                with transaction.atomic():
                    # 1. 先创建点赞记录
                    models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
                    # 2. 再更新文章表
                    if is_up:
                        # 更新点赞数
                        models.Article.objects.filter(id=article_id).update(up_count=F('up_count')+1)
                    else:
                        # 更新反对数
                        models.Article.objects.filter(id=article_id).update(down_count=F('down_count') + 1)
                res["msg"] = '点赞成功' if is_up else '反对成功'
        return JsonResponse(res)


# ------------day79 ↓ -----------------
def comment(request):
    if request.method == "POST":
        res = {"code": 0}
        article_id = request.POST.get("article_id")
        content = request.POST.get("content")
        user_id = request.user.id
        parent_id = request.POST.get("parent_id")

        # 创建评论内容
        with transaction.atomic():
            # 1. 先去创建新评论
            if parent_id:
                # 添加子评论
                comment_obj = models.Comment.objects.create(content=content, user_id=user_id, article_id=article_id, parent_comment_id=parent_id)
            else:
                # 添加父评论
                comment_obj = models.Comment.objects.create(content=content, user_id=user_id, article_id=article_id)
            # 2. 去更新该文章的评论数
            models.Article.objects.filter(id=article_id).update(comment_count=F("comment_count")+1)
            res["data"] = {
                "id": comment_obj.id,
                "content": comment_obj.content,
                "create_time": comment_obj.create_time.strftime("%Y-%m-%d %H:%M"),
                "username": comment_obj.user.username
            }
    return JsonResponse(res)


# day80
class Comment(views.View):

    def get(self, request, article_id):
        res = {"code": 0}
        # 根据文章id把评论都找出来
        comment_list = models.Comment.objects.filter(article_id=article_id)
        data = [{
                "id": comment.id,
                "create_time": comment.create_time.strftime("%Y-%m-%d %H:%M"),
                "content": comment.content,
                "pid": comment.parent_comment_id,
                "username": comment.user.username} for comment in comment_list]
        res["data"] = data
        return JsonResponse(res)

    def post(self, request, id):
        print("sadsadsadsadsasad")
        res = {"code": 0}
        article_id = request.POST.get("article_id")
        content = request.POST.get("content")
        user_id = request.user.id
        parent_id = request.POST.get("parent_id")

        # 创建评论内容
        with transaction.atomic():
            # 1. 先去创建新评论
            if parent_id:
                # 添加子评论
                comment_obj = models.Comment.objects.create(content=content, user_id=user_id, article_id=article_id,
                                                            parent_comment_id=int(parent_id))
            else:
                # 添加父评论
                comment_obj = models.Comment.objects.create(content=content, user_id=user_id, article_id=article_id)
            # 2. 去更新该文章的评论数
            models.Article.objects.filter(id=article_id).update(comment_count=F("comment_count") + 1)
            res["data"] = {
                "id": comment_obj.id,
                "content": comment_obj.content,
                "create_time": comment_obj.create_time.strftime("%Y-%m-%d %H:%M"),
                "username": comment_obj.user.username
            }
        return JsonResponse(res)


# 管理后台
def backend(request):
    # 现获取当前用户的所有文章
    article_list = models.Article.objects.filter(user=request.user)
    return render(request, "backend.html", {"article_list": article_list})


# 添加新文章
def add_article(request):
    if request.method == "POST":
        # 获取用户填写的文章内容
        title = request.POST.get("title")
        content = request.POST.get("content")
        category_id = request.POST.get("category")

        # 清洗用户发布的文章的内容，去掉script标签
        soup = BeautifulSoup(content, "html.parser")
        script_list = soup.select("script")
        for i in script_list:
            i.decompose()
        # print(soup.text)
        # print(soup.prettify())

        # 写入数据库
        with transaction.atomic():
            # 1. 先创建文章记录
            article_obj = models.Article.objects.create(
                title=title,
                desc=soup.text[0:150],
                user=request.user,
                category_id=category_id
            )
            # 2. 创建文章详情记录
            models.ArticleDetail.objects.create(
                content=soup.prettify(),
                article=article_obj
            )
        return redirect("/blog/backend/")

    # 把当前博客的文章分类查询出来
    category_list = models.Category.objects.filter(blog__userinfo=request.user)
    return render(request, "add_article.html", {"category_list": category_list})


# 富文本编辑器的图片上传
def upload(request):
    res = {"error": 0}
    print(request.FILES)
    file_obj = request.FILES.get("imgFile")
    file_path = os.path.join(settings.MEDIA_ROOT, "article_imgs", file_obj.name)
    with open(file_path, "wb") as f:
        for chunk in file_obj.chunks():
            f.write(chunk)
    # url = settings.MEDIA_URL + "article_imgs/" + file_obj.name
    url = "/media/article_imgs/" + file_obj.name
    res["url"] = url
    return JsonResponse(res)












