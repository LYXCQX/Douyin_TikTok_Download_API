import os
import json
import logging
import random
from typing import Dict, List, Optional, Any
from config import PLATFORM
from social_auto_upload.conf import BASE_DIR
from PyQt6.QtCore import QSettings

logger = logging.getLogger("CookieManager")

def get_available_users() -> List[Dict]:
    """
    从注册表获取所有可用的用户
    
    Returns:
        List[Dict]: 可用用户列表
    """
    try:
        settings = QSettings("XIXI_UPLOAD", PLATFORM)
        users_json = settings.value("users", "[]")
        users = json.loads(users_json)
        
        # 过滤出在线的用户
        available_users = [
            user for user in users 
            if user.get("status") == "online" and 
            user.get("platform") == "douyin" and
            os.path.exists(user.get("cookie_file", ""))
        ]
        
        logger.info(f"找到 {len(available_users)} 个可用账号")
        return available_users
        
    except Exception as e:
        logger.error(f"获取可用用户失败: {str(e)}")
        return []

def get_cookie_string(account_path: str = None) -> str:
    """
    获取Cookie字符串，可以指定账号文件或随机选择一个
    
    Args:
        account_path: 可选的账号文件路径，如果不提供则随机选择一个
        
    Returns:
        str: Cookie字符串，适用于HTTP头
    """
    try:
        # 获取可用用户列表
        available_users = get_available_users()
        if not available_users:
            logger.warning("没有可用的账号")
            return ""
            
        # 如果指定了账号文件，使用指定的文件
        if account_path:
            user = next((u for u in available_users if u.get("cookie_file") == account_path), None)
            if not user:
                logger.warning(f"指定的账号文件不存在: {account_path}")
                return ""
        else:
            # 随机选择一个用户
            user = random.choice(available_users)
            account_path = user.get("cookie_file")
            logger.info(f"随机选择账号: {user.get('username')}")
        
        # 读取cookie文件
        with open(account_path, "r", encoding="utf-8") as f:
            cookies_data = json.load(f)
            
        if not cookies_data or "cookies" not in cookies_data:
            logger.warning("没有可用的cookies数据")
            return ""
        
        # 将cookies列表转换为cookie字符串
        cookie_items = []
        for cookie in cookies_data.get("cookies", []):
            if "name" in cookie and "value" in cookie:
                cookie_items.append(f"{cookie['name']}={cookie['value']}")
        
        return "; ".join(cookie_items)
        
    except Exception as e:
        logger.error(f"获取cookie字符串失败: {str(e)}")
        return ""

def get_cookie_dict(account_path: str = None) -> Dict[str, str]:
    """
    获取Cookie字典，可以指定账号文件或随机选择一个
    
    Args:
        account_path: 可选的账号文件路径，如果不提供则随机选择一个
        
    Returns:
        Dict[str, str]: Cookie字典
    """
    try:
        # 获取可用用户列表
        available_users = get_available_users()
        if not available_users:
            logger.warning("没有可用的账号")
            return {}
            
        # 如果指定了账号文件，使用指定的文件
        if account_path:
            user = next((u for u in available_users if u.get("cookie_file") == account_path), None)
            if not user:
                logger.warning(f"指定的账号文件不存在: {account_path}")
                return {}
        else:
            # 随机选择一个用户
            user = random.choice(available_users)
            account_path = user.get("cookie_file")
            logger.info(f"随机选择账号: {user.get('username')}")
        
        # 读取cookie文件
        with open(account_path, "r", encoding="utf-8") as f:
            cookies_data = json.load(f)
            
        if not cookies_data or "cookies" not in cookies_data:
            logger.warning("没有可用的cookies数据")
            return {}
        
        # 转换为cookie字典
        cookie_dict = {}
        for cookie in cookies_data.get("cookies", []):
            if "name" in cookie and "value" in cookie:
                cookie_dict[cookie["name"]] = cookie["value"]
        
        return cookie_dict
        
    except Exception as e:
        logger.error(f"获取cookie字典失败: {str(e)}")
        return {}

def get_random_account() -> Optional[str]:
    """
    随机获取一个可用的账号文件路径
    
    Returns:
        Optional[str]: 随机选择的账号文件路径，如果没有可用账号则返回 None
    """
    try:
        available_users = get_available_users()
        if not available_users:
            logger.warning("没有可用的账号")
            return None
            
        # 随机选择一个用户
        user = random.choice(available_users)
        account_path = user.get("cookie_file")
        logger.info(f"随机选择账号: {user.get('username')}")
        return account_path
        
    except Exception as e:
        logger.error(f"获取随机账号失败: {str(e)}")
        return None 