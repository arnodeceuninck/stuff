class FrameworkSettings(BaseSettings):
    database_url: str
    auth_secret: str
    grafana_push_url: str | None = None

# app/config.py
class AppSettings(FrameworkSettings):
    my_app_specific_flag: bool = False