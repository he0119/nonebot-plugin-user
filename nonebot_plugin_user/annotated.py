from nonebot.params import Depends
from typing_extensions import Annotated

from .depends import UserSession as _UserSession
from .depends import get_user, get_user_session
from .models import User as _User

User = Annotated[_User, Depends(get_user)]
UserSession = Annotated[_UserSession, Depends(get_user_session)]
