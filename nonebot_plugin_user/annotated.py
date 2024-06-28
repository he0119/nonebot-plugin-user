from nonebot.params import Depends
from typing import Annotated

from .models import User as _User
from .params import UserSession as _UserSession
from .params import get_user, get_user_session

User = Annotated[_User, Depends(get_user)]
UserSession = Annotated[_UserSession, Depends(get_user_session)]
