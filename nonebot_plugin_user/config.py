from nonebot import get_driver
from pydantic import BaseModel


class Config(BaseModel):
    user_token_prefix: str = "nonebot/"
    """生成令牌的前缀"""


plugin_config = Config.parse_obj(get_driver().config)
