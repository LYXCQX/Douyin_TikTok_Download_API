import asyncio  # 异步I/O
import json
import os  # 系统操作
import time  # 时间操作
from typing import Dict, Optional
from urllib.parse import urlencode  # URL编码

import yaml  # 配置文件
# 基础爬虫客户端和抖音API端点
from Douyin_TikTok_Download_API.crawlers.base_crawler import BaseCrawler
from Douyin_TikTok_Download_API.crawlers.douyin.web.endpoints import DouyinAPIEndpoints
# 抖音接口数据请求模型
# 抖音应用的工具类
from Douyin_TikTok_Download_API.crawlers.douyin.web.utils import (  # Aweme ID获取
    BogusManager,  # XBogus管理
    # 安全用户ID获取
    TokenManager,  # 令牌管理
    # 验证管理
    # 直播ID获取
    # URL提取
)

from Douyin_TikTok_Download_API.crawlers.douyin.web.models import (
    SuggestWord, GeneralSearch,
    SortType, PublishTime, FilterDuration, SearchRange, ContentType
)

from Douyin_TikTok_Download_API.crawlers.douyin.web.cookie_manager import get_cookie_string

# 配置文件路径
path = os.path.abspath(os.path.dirname(__file__))

# 读取配置文件
with open(f"{path}/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


class DouyinOtherCrawler:
    def __init__(self, account_path: str = None):
        """
        初始化抖音Web爬虫
        
        Args:
            account_path: account.json文件的路径，如果不提供，将使用默认路径
        """
    # 从配置文件中获取抖音的请求头，同时使用cookie_manager中的cookie
    async def get_douyin_headers(self,account_path=None):
        douyin_config = config["TokenManager"]["douyin"]
        # 获取cookie管理器中的cookie字符串
        cookie_string = get_cookie_string(account_path)
        # 如果cookie管理器中没有有效的cookie，则使用配置文件中的cookie
        # if not cookie_string:
        #     self.logger.warning("使用配置文件中的默认Cookie")
        #     cookie_string = douyin_config["headers"]["Cookie"]
        kwargs = {
            "headers": {
                "Accept-Language": douyin_config["headers"]["Accept-Language"],
                "User-Agent": douyin_config["headers"]["User-Agent"],
                "Referer": douyin_config["headers"]["Referer"],
                "Cookie": cookie_string,
            },
            "proxies": {"http://": douyin_config["proxies"]["http"], "https://": douyin_config["proxies"]["https"]},
        }
        return kwargs

    def get_douyin_headers_sync(self):
        douyin_config = config["TokenManager"]["douyin"]
        # 获取cookie管理器中的cookie字符串
        cookie_string = get_cookie_string()
        # 如果cookie管理器中没有有效的cookie，则使用配置文件中的cookie
        # if not cookie_string:
        #     self.logger.warning("使用配置文件中的默认Cookie")
        #     cookie_string = douyin_config["headers"]["Cookie"]

        kwargs = {
            "headers": {
                "Accept-Language": douyin_config["headers"]["Accept-Language"],
                "User-Agent": douyin_config["headers"]["User-Agent"],
                "Referer": douyin_config["headers"]["Referer"],
                "Cookie": cookie_string,
            },
            "proxies": {"http://": douyin_config["proxies"]["http"], "https://": douyin_config["proxies"]["https"]},
        }
        return kwargs

    "-------------------------------------------------------handler接口列表-------------------------------------------------------"

    # 获取单个作品数据
    async def fetch_suggest_words(self, from_group_id=str, business_id='30088', key_words = ''):
        # 获取抖音的实时Cookie
        kwargs = await self.get_douyin_headers()
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            params = SuggestWord(querry=key_words, business_id=business_id, from_group_id=from_group_id)
            params_dict = params.dict()
            params_dict["msToken"] = TokenManager.gen_real_msToken()
            a_bogus = BogusManager.ab_model_2_endpoint(params_dict, kwargs["headers"]["User-Agent"])
            endpoint = f"{DouyinAPIEndpoints.SUGGEST_WORDS}?{urlencode(params_dict)}&a_bogus={a_bogus}"

            response = await crawler.fetch_get_json(endpoint)
        return response

    async def fetch_general_search(self, key_words: str, offset: int = 0, count: int = 20,
                                   search_id: str = "",
                                   sort_type: Optional[SortType] = None,
                                   publish_time: Optional[PublishTime] = None,
                                   filter_duration: Optional[FilterDuration] = None,
                                   search_range: Optional[SearchRange] = None,
                                   content_type: Optional[ContentType] = None,
                                   filter_options: Optional[Dict[str, str]] = None,
                                   account_path: str = None
                                   ):
        """
        抖音综合搜索接口
        
        Args:
            key_words: 搜索关键词
            offset: 偏移量，默认为0
            count: 返回结果数量，默认为10
            from_group_id: 来源组ID，默认为空
            sort_type: 排序方式枚举
            publish_time: 发布时间枚举
            filter_duration: 视频时长枚举
            search_range: 搜索范围枚举
            content_type: 内容类型枚举
            filter_options: 自定义筛选选项字典，会覆盖枚举设置
            
        Returns:
            搜索结果的JSON响应
        """
        # 获取抖音的实时Cookie
        kwargs = await self.get_douyin_headers(account_path)
        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            # 使用当前时间生成search_id
            # 构建请求参数
            params = GeneralSearch(
                keyword=key_words,
                offset=offset,
                count=count,
                search_id=search_id
            )

            # 默认筛选设置
            default_filter = {}
            # 使用枚举值更新筛选选项
            if sort_type is not None:
                default_filter["sort_type"] = sort_type.value
            if publish_time is not None:
                default_filter["publish_time"] = publish_time.value
            if filter_duration is not None:
                default_filter["filter_duration"] = filter_duration.value
            if search_range is not None:
                default_filter["search_range"] = search_range.value
            if content_type is not None:
                default_filter["content_type"] = content_type.value

            # 如果提供了自定义筛选选项，则覆盖枚举设置
            if filter_options:
                default_filter.update(filter_options)

            # 更新params的filter_selected字段
            if default_filter:
                params.filter_selected = json.dumps(default_filter, separators=(',', ':'))
            # params.filter_selected = default_filter
            params_dict = params.dict()
            # print(params)
            # 获取有效的msToken
            params_dict["msToken"] = TokenManager.gen_real_msToken()
            # 生成a_bogus参数
            a_bogus = BogusManager.ab_model_2_endpoint(params_dict, kwargs["headers"]["User-Agent"])
            # 构建完整的API请求URL
            endpoint = f"{DouyinAPIEndpoints.GENERAL_SEARCH}?{urlencode(params_dict)}&a_bogus={a_bogus}"
            # 发送请求并获取响应
            response = await crawler.fetch_get_json(endpoint)
            return response


if __name__ == "__main__":
    # 初始化
    # DouyinWebCrawler = DouyinOtherCrawler()

    # 开始时间
    start = time.time()

    # 测试建议词接口
    # asyncio.run(DouyinWebCrawler.fetch_suggest_words('来自星星的你'))

    # 测试综合搜索接口 - 方式1: 使用字典进行筛选
    '''
    search_result = asyncio.run(DouyinWebCrawler.fetch_general_search(
        key_words='私藏一片坠落的星光',
        offset=0,
        count=20,
        filter_options={
            "sort_type": "0",  # 综合排序
            "publish_time": "7",  # 一周内
            "filter_duration": "0-1",  # 1分钟以下
            "content_type": "1"  # 只显示视频
        }
    ))
    '''

    # 测试综合搜索接口 - 方式2: 使用枚举进行筛选（推荐）
    # search_result = asyncio.run(DouyinWebCrawler.fetch_general_search(
    #     key_words='私藏一片坠落的星光',
    #     offset=0,
    #     count=20,
    #     sort_type=SortType.COMPREHENSIVE,  # 综合排序
    #     publish_time=PublishTime.WITHIN_WEEK,  # 一周内
    #     filter_duration=FilterDuration.UNDER_ONE_MINUTE,  # 1分钟以下
    #     content_type=ContentType.VIDEO  # 只显示视频
    # ))
    #
    # # 打印结果中的关键数据
    # if search_result and "data" in search_result:
    #     print(f"搜索结果数量: {len(search_result['data'])}")
    #     for i, item in enumerate(search_result['data'][:3]):  # 只打印前3条结果
    #         if "aweme_info" in item:
    #             aweme = item["aweme_info"]
    #             print(f"\n结果 {i + 1}:")
    #             print(f"标题: {aweme.get('desc', '无标题')}")
    #             print(f"作者: {aweme.get('author', {}).get('nickname', '未知作者')}")
    #             print(f"点赞: {aweme.get('statistics', {}).get('digg_count', 0)}")
    #             print(f"评论: {aweme.get('statistics', {}).get('comment_count', 0)}")

    # 结束时间
    end = time.time()
    print(f"耗时：{end - start}秒")
