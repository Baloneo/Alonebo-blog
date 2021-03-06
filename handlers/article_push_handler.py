from . import base_handler
import config


# 数据推送类


class GetArticle(base_handler.BaseHandler):
    """
        获取文章处理逻辑 下面是请求接口参数
        /api/get_article_count?[name=android]
        /api/get_article_count?[page_index=1]&[page_size=3]
    """

    async def get(self, *args, **kwargs):
        name = self.get_argument("article", "")
        page_index = self.get_argument('page_index', 0)  # 请求第几页文章 一页默认6篇文章
        page_size = self.get_argument('page_size', config.SINGLE_PAGE_SIZE)  # 每次请求多少篇文章
        article_id = self.get_argument('article_id', 0)  #
        try:
            page_size = int(page_size)
            page_index = int(page_index)
        except Exception as e:
            print("*****error***", e)
            return self.write({'errcode': 1, 'errmsg': 'page_size或者page_index参数错误'})
        if name != "":
            # 传递了name参数 则表示请求哪一篇文章
            try:
                res = await self.query_sql("select id,at_content,at_cate, "
                                       "at_update_time, at_create_time, at_title,"
                                       " at_summary from tb_article where at_title=%s", name)
            except Exception as e:
                print("*****error***", e)
                return self.write({'errcode': 1, 'errmsg': '查询博文错误'})
            return_value = {}
            for i in range(len(res)):
                row = res[i]

                return_value[str(i)] = {'id': row[0], 'cate': row[2],
                                        'content': row[1], 'update_time': str(row[3]), 'title': row[5],
                                        'summary': row[6]}
            self.write(return_value)
        elif page_index != 0:
            # 传递了参数请求页数
            count = await self.query_sql("select count(*) from tb_article")
            count = count[0][0]
            count = int(count)
            # 如果传递的是第一页 应该从 数据库size-(page_size*page_index) 开始查找
            offset = count - (page_size * page_index)  # 13 - (6*1) = 7
            print("offset: ", offset)
            if offset < 0:
                page_size = page_size - (-offset)
                offset = 0
            print("offset: ", offset, ";", page_size)
            res = await self.query_sql("select id, at_cate, at_content, "
                                       "at_update_time, at_create_time, at_title, at_summary from "
                                       "tb_article order by at_update_time limit %s offset %s", page_size, offset)
            return_value = {}
            count = len(res)
            for i in range(count):
                print(i)
                row = res[(count - 1) - i]
                return_value[str(i)] = {'id': row[0], 'cate': row[1],
                                        'content': row[2], 'update_time': str(row[3]), 'title': row[5],
                                        'summary': row[6]}
            self.write(return_value)
        elif article_id != 0:
            try:
                article_id = int(article_id)

            except Exception as e:
                print('error: {}'.format(e))
                return self.write({'errmsg': '参数id错误:' + str(article_id), 'errcode': 1})
            else:

                res = await self.query_sql("select id,at_cate,at_content,"
                                           "at_update_time, at_create_time, at_title, at_summary "
                                           "from tb_article where id = %s", article_id)
                if len(res) == 1:
                    self.write({'id': res[0][0], 'content': res[0][2], 'cate': res[0][1],
                                'update_time': str(res[0][3]), 'title': res[0][5],
                                'summary': res[0][6], 'errcode': 0})
                else:
                    self.write({'errmsg': '查询博文错误', 'errcode': 1})

        else:
            # 返回全部的文章逻辑
            res = await self.query_sql("select id, at_content,at_cate, "
                                       "at_update_time, at_create_time, at_title, at_summary "
                                       "from tb_article order by at_update_time desc")

            return_value = {}
            for i in range(len(res)):
                row = res[i]
                return_value[str(i)] = {'id': row[0], 'content': row[1], 'cate': row[2],
                                        'update_time': str(row[3]), 'title': row[5],
                                        'summary': row[6]}

            self.write(return_value)


class GetRecentPosts(base_handler.BaseHandler):
    """
    获取最近更新的文章
    """
    async def get(self, *args, **kwargs):
        try:
            # import asyncio 模拟休眠
            # await asyncio.sleep(10)
            res = await self.query_sql(
                "select id, at_title, at_update_time, at_cate from tb_article order by at_update_time desc")
            return_value = {}
            # print(res)
            loop_value = len(res)
            if len(res) > 8:
                loop_value = 8
            for i in range(loop_value):
                row = res[i]
                return_value[str(i)] = {'id': row[0], 'title': row[1], 'create_time': str(row[2])}

            self.write(return_value)
        except Exception as e:
            print('error:', e)
            return self.write({'errcode': 1, 'errmsg': '获取最近博客失败'})


class GetLastChangeTime(base_handler.BaseHandler):
    """
    获取最后的更新时间
    """

    async def get(self, *args, **kwargs):
        res = await self.query_sql(
            "select id, at_title, at_update_time, at_cate from tb_article order by at_update_time desc")
        if len(res) != 0:

            return_value = {'last_change_time': str(res[0][2])}
            print(str(return_value))
            self.write(return_value)
        else:
            self.write({'errmsg': '查询失败', 'errcode': 1})


class GetArticleCount(base_handler.BaseHandler):
    """
    获取文章的篇数
    """

    async def get(self, *args, **kwargs):
        try:
            res = await self.query_sql("select count(*) from tb_article")
        except Exception as e:
            print("******error****", e)
        # print(res)
        if res:
            self.write({"article_count": res[0][0]})
        else:
            self.write({"article_count": 0})


class GetCategory(base_handler.BaseHandler):
    """
    获取所有类别的项目
    """
    async def get(self, *args, **kwargs):
        try:
            result = await self.query_sql(
                "select count(*),at_cate from tb_article group by at_cate")
            print('start')
            print(result)
        except Exception as e:
            print("****error****", e)
            return self.write({'errmsg': '查询失败', 'errcode': 1})
        return_value = {}
        for i in range(len(result)):
            row = result[i]
            return_value[str(i)] = {'category_count': row[0], 'category_title': row[1]}

        self.write(return_value)


class GetArticlesInfo(base_handler.BaseHandler):
    """
    获取博客 根据page_index 返回的数据只有博文的id和title
    """
    async def get(self, *args, **kwargs):
        page_index = self.get_argument('page_index', "")
        if page_index != "":
            try:
                page_index = int(page_index)
            except Exception as e:
                print("error:", e)
                page_index = 1
            count = await self.query_sql("select count(*) from tb_article")
            count = count[0][0]
            count = int(count)
            page_size = config.SINGLE_PAGE_SIZE * 2
            # 如果传递的是第一页 应该从 数据库size-(page_size*page_index) 开始查找
            offset = count - (page_size * page_index)  # 10 - (6*2) = -2
            if offset < 0:  # 如果这一页不够 应该从
                page_size = page_size - (-offset)
                offset = 0
            res = await self.query_sql(
                "select id, at_title from tb_article order by at_update_time desc limit %s offset %s", page_size,
                offset)
            return_value = {}
            for i in range(len(res)):
                row = res[i]
                return_value[str(i)] = {'id': row[0], 'title': row[1]}
            self.write(return_value)
        else:
            res = await self.query_sql("select id, at_title from tb_article order by at_update_time desc")
            return_value = {}
            for i in range(len(res)):
                row = res[i]
                return_value[str(i)] = {'id': row[0], 'title': row[1]}
            self.write(return_value)


class GetArticleByCategory(base_handler.BaseHandler):
    async def get(self, *args, **kwargs):
        category = self.get_argument('category', '')
        if category == '':
            return self.write({'errmsg': '参数category错误', 'errcode': 1})
        try:
            res = await self.query_sql(
                "select id, at_update_time, at_title, at_cate from tb_article where at_cate = %s order by at_update_time desc",
                category)
            return_value = {}
            for i in range(len(res)):
                row = res[i]
                return_value[str(i)] = {'id': row[0], 'update_time': str(row[1]), 'title': row[2], 'category': row[3]}
            self.write(return_value)
        except Exception as e:
            print('error: {}'.format(e))
            return self.write({'errmsg': '查询失败', 'errcode': 1})


class ArticleSearch(base_handler.BaseHandler):
    async def get(self, *args, **kwargs):
        keyword = self.get_argument('keyword', None)
        if keyword:
            print(keyword)
            res = await self.query_sql("select id, at_create_time,at_title from tb_article where at_title like %s or at_content like %s or at_summary like %s",
                                       "%"+keyword+"%", "%"+keyword+"%", "%"+keyword+"%")
            # print(res)
            return_value = {}
            for i in range(len(res)):
                row = res[i]
                return_value[str(i)] = {'id': row[0], 'update_time': str(row[1]), 'title': row[2]}
            self.write(return_value)
        else:
            self.write({'errcode': 1, 'errmsg': '参数错误'})