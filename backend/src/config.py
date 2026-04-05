from backend_framework.config import FrameworkSettings


class AppSettings(FrameworkSettings):
    my_app_specific_flag: bool = False