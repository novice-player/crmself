
from django.utils.safestring import mark_safe

class Paging:

    def __init__(self,page_num,total_number,base_url="",number_each_page=3,max_page=3):
        """

        :param page_num: 当前所在页码
        :param total_number: 总数据条数
        :param base_url: 传入URL来保证在页码跳转时保存原URL信息
        :param number_each_page: 每页条数
        :param max_page: 最大显示页码数量
        """

        # 获取当前页码
        try:
            self.page_num = int(page_num)
            if self.page_num <= 0:
                self.page_num = 1
        except Exception:
            self.page_num = 1

        # 每页显示数据量
        self.number_each_page = number_each_page

        # 总数据条数
        self.total_number = total_number

        # 总页数
        # divmod(a, b) 返回一个包含商和余数的元组(a // b, a % b)
        self.page_count, more = divmod(self.total_number, self.number_each_page)
        if more:
            self.page_count += 1

        # 最大显示页码数量
        self.max_page = max_page
        self.half_page = max_page // 2

        # 搜索url
        self.base_url = base_url

    # 控制显示页码数量
    @property
    def page_html(self):
        if self.page_count <= self.max_page:
            page_start = 1
            page_end = self.page_count
        else:
            if self.page_num <= self.half_page:
                page_start = 1
                page_end = self.max_page
            elif self.page_num + self.half_page >= self.page_count:
                page_start = self.page_count - self.max_page + 1
                page_end = self.page_count
            else:
                page_start = self.page_num - self.half_page
                page_end = self.page_num + self.half_page

        # 控制页数不低于1
        page_list = []
        if self.page_num == 1:
            page_list.append(f'<li class="disabled"><a href="?{self.base_url}&page=1">首页</a></li>')
            page_list.append(f'<li class="disabled"><a href="?{self.base_url}&page={self.page_num}">上一页</a></li>')
        else:
            page_list.append(f'<li><a href="?{self.base_url}&page=1">首页</a></li>')
            page_list.append(f'<li><a href="?{self.base_url}&page={self.page_num - 1}">上一页</a></li>')

        for page in range(page_start, page_end + 1):
            if page == self.page_num:
                page_list.append(f'<li class="active"><a href="?{self.base_url}&page={page}">{page}</a></li>')
            else:
                page_list.append(f'<li><a href="?{self.base_url}&page={page}">{page}</a></li>')

        # 控制页数不超过总页数
        if self.page_num == self.page_count:
            page_list.append(f'<li class="disabled"><a href="?{self.base_url}&page={self.page_count}">下一页</a></li>')
            page_list.append(f'<li class="disabled"><a href="?{self.base_url}&page={self.page_count}">尾页</a></li>')
        else:
            page_list.append(f'<li ><a href="?{self.base_url}&page={self.page_num + 1}">下一页</a></li>')
            page_list.append(f'<li ><a href="?{self.base_url}&page={self.page_count}">尾页</a></li>')

        page_html = "".join(page_list)

        return mark_safe(page_html)

    @property
    def start(self):
        return (self.page_num - 1) * self.number_each_page

    @property
    def end(self):
        return self.page_num * self.number_each_page

