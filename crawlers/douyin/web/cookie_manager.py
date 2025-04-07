import os
import json
import logging
import random
from typing import Dict, List, Optional, Any
from social_auto_upload.conf import BASE_DIR

class CookieManager:
    """抖音Cookie管理类，负责从account.json文件中加载和管理cookie"""
    
    def __init__(self, account_path: str = None):
        """
        初始化Cookie管理器
        
        Args:
            account_path: account.json文件的路径，如果不提供，将随机选择一个可用的账号文件
        """
        self.logger = logging.getLogger("CookieManager")
        self.cookies_data = {}
        self.current_account = None
        self.account_path = account_path
        self.available_accounts = []
        self.load_cookies()
    
    def load_cookies(self) -> bool:
        """
        加载cookies数据，如果没有指定account_path，则随机选择一个可用的账号文件
        
        Returns:
            bool: 是否成功加载
        """
        try:
            # 如果没有指定account_path，查找默认目录
            if not self.account_path:
                # 使用BASE_DIR作为基础路径
                cookies_dir = os.path.join(BASE_DIR, "cookies", "douyin_uploader")
                
                # 检查目录是否存在
                if not os.path.exists(cookies_dir):
                    self.logger.error(f"Cookies目录不存在: {cookies_dir}")
                    return False
                
                # 查找所有account.json文件
                account_files = [f for f in os.listdir(cookies_dir) if f.endswith("_account.json")]
                if not account_files:
                    self.logger.error(f"在 {cookies_dir} 中没有找到account.json文件")
                    return False
                
                # 保存所有可用账号文件路径
                self.available_accounts = [os.path.join(cookies_dir, f) for f in account_files]
                
                # 随机选择一个账号文件
                self.account_path = random.choice(self.available_accounts)
                self.logger.info(f"随机选择账号文件: {self.account_path}")
            
            # 读取account.json文件
            with open(self.account_path, "r", encoding="utf-8") as f:
                self.cookies_data = json.load(f)
                
            # 提取账号信息
            self.current_account = os.path.basename(self.account_path).split("_account.json")[0]
            self.logger.info(f"成功加载账号 {self.current_account} 的cookies")
            return True
            
        except Exception as e:
            self.logger.error(f"加载cookies失败: {str(e)}")
            return False
    
    def switch_account(self) -> bool:
        """
        切换到另一个随机账号
        
        Returns:
            bool: 是否成功切换
        """
        if not self.available_accounts or len(self.available_accounts) <= 1:
            self.logger.warning("没有其他可用账号可切换")
            return False
        
        # 从可用账号中排除当前账号，然后随机选择一个
        other_accounts = [acc for acc in self.available_accounts if acc != self.account_path]
        if not other_accounts:
            self.logger.warning("没有其他可用账号可切换")
            return False
        
        # 随机选择一个新账号
        self.account_path = random.choice(other_accounts)
        self.logger.info(f"切换到新账号: {self.account_path}")
        
        # 重新加载cookies
        return self.load_cookies()
    
    def get_cookie_string(self) -> str:
        """
        获取Cookie字符串
        
        Returns:
            str: Cookie字符串，适用于HTTP头
        """
        if not self.cookies_data or "cookies" not in self.cookies_data:
            self.logger.warning("没有可用的cookies数据")
            return ""
        
        # 将cookies列表转换为cookie字符串
        cookie_items = []
        for cookie in self.cookies_data.get("cookies", []):
            if "name" in cookie and "value" in cookie:
                cookie_items.append(f"{cookie['name']}={cookie['value']}")
        
        return "; ".join(cookie_items)
    
    def get_cookie_dict(self) -> Dict[str, str]:
        """
        获取Cookie字典
        
        Returns:
            Dict[str, str]: Cookie字典
        """
        cookie_dict = {}
        if self.cookies_data and "cookies" in self.cookies_data:
            for cookie in self.cookies_data.get("cookies", []):
                if "name" in cookie and "value" in cookie:
                    cookie_dict[cookie["name"]] = cookie["value"]
        
        return cookie_dict
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        获取账号信息
        
        Returns:
            Dict[str, Any]: 账号信息
        """
        return {
            "account": self.current_account,
            "file_path": self.account_path,
            "has_cookies": bool(self.cookies_data and "cookies" in self.cookies_data),
            "available_accounts": len(self.available_accounts)
        }
    
    def is_valid(self) -> bool:
        """
        验证cookie是否有效
        
        Returns:
            bool: 是否有效
        """
        # 检查关键cookie是否存在
        essential_cookies = ["sessionid", "sid_tt", "uid_tt"]
        if self.cookies_data and "cookies" in self.cookies_data:
            cookie_names = [c.get("name") for c in self.cookies_data.get("cookies", [])]
            return all(cookie in cookie_names for cookie in essential_cookies)
        return False 