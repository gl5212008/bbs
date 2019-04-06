import os


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bbs.settings")
    import django
    django.setup()

    from blog import models

    # ret = models.Article.objects.all().extra(
    #     select={"create_ym": "DATE_FORMAT(create_time, '%%Y-%%m-%%d')"}
    # )
    #
    # # models.Article.objects.all()  --> [ArticleObj1, ArticleObj2, ...]
    # # .extra(select={"create_ym": "DATE_FORMAT(create_time, '%%Y-%%m-%%d')"})
    # #     --> ArticleObj1.create_ym
    #
    # for article in ret:
    #     print(article.create_time, "|", article.create_ym)
    #
    # # 更高灵活度的方式执行原生SQL语句
    # from django.db import connection  # 连接
    # # 从连接中获取光标，等待输入命令
    # cursor = connection.cursor()
    # # 光标执行SQL语句
    # cursor.execute("""SELECT DATE_FORMAT(create_time, '%Y-%m') FROM blog_article;""")
    # # 取出SQL语句执行后的结果
    # ret = cursor.fetchall()
    # print(ret)
    #
    # from django.db.models import Count
    # ret = models.Article.objects.filter(user__username='alex').extra(
    #     select={"y_m": "DATE_FORMAT(create_time, '%%Y-%%m')"}
    # ).values("y_m").annotate(c=Count("id"))
    # print(ret)

    # QuerySet --> 惰性求值
    # ret = models.Article.objects.all()  # 此时并不查询数据库
    # print(ret)
    # print(len(ret))
    # print(ret.count())

    # 修改第一篇文章的标题
    # 1. 对象.属性 = '新值'
    # article_obj = models.Article.objects.first()
    # article_obj.title = '呵呵哈哈嘿嘿'
    # article_obj.save()

    # 2. queryset的update()方法
    # query_set = models.Article.objects.filter(id=1)  # [ArticleObj1,]
    # query_set.update(title='嘿嘿哈哈呵呵')




