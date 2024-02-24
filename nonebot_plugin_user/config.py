from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    user_token_prefix: str = "nonebot/"
    """生成令牌的前缀"""


plugin_config = get_plugin_config(Config)
