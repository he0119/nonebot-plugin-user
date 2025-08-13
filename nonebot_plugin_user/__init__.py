from nonebot import require

require("nonebot_plugin_alconna")
require("nonebot_plugin_uninfo")
require("nonebot_plugin_orm")

from nonebot.plugin import PluginMetadata, inherit_supported_adapters

from .annotated import User as User
from .annotated import UserSession as UserSession
from .config import Config
from .utils import get_user as get_user
from .utils import get_user_by_id as get_user_by_id
from .utils import get_user_platform_ids as get_user_platform_ids

__plugin_meta__ = PluginMetadata(
    name="用户",
    description="管理和绑定不同平台的用户",
    usage="""查看用户信息
/user
修改用户名
/user -l [用户名]
绑定用户
/bind
解除绑定
/bind -r""",
    type="application",
    homepage="https://github.com/he0119/nonebot-plugin-user",
    config=Config,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna", "nonebot_plugin_uninfo"),
)


__all__ = [
    "get_user",
    "get_user_by_id",
    "get_user_platform_ids",
    "User",
    "UserSession",
]

from . import matchers  # noqa: F401
