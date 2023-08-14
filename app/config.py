from decouple import config


class Config:
    """Base config, uses staging database server."""

    TESTING = False

    # Database
    DB_NAME = config("DB_NAME")
    DB_USER = config("DB_USER")
    DB_HOST = config("DB_HOST")
    DB_PW = config("DB_PW")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SWAGGER_UI_DOC_EXPANSION = "list"

    # Api documentation
    API_TITLE = "Plate Assay Image Database API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/api"
    OPENAPI_SWAGGER_UI_PATH = "/swagger"
    OPENAPI_SWAGGER_UI_URL = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/"
    OPENAPI_REDOC_PATH = "redoc"

    ITEMS_PER_PAGE = 20

    # Default regular expression for parsing image files
    CAPTURE_REGEXP_DICT = {'row': r"^.*_([A-Z])[0-9][0-9]_.*$",
                           'col': r"^.*_[A-Z]([0-9][0-9])_.*$"}
    IGNORE_REGEXP = r"^.*_thumb.*$"
    VALID_REGEXP = r"^.*\.tiff?$"

    # Generate pages from markdown files
    FLATPAGES_EXTENSION = [".md"]
    FLATPAGES_MARKDOWN_EXTENSION = ["codehilite"]

    # Azure
    APP_NAME = config("APP_NAME")
    CLIENT_SECRET = config("CLIENT_SECRET")
    CLIENT_ID = config("CLIENT_ID")
    TENANT_ID = config("TENANT_ID")

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return "postgresql+psycopg2://{}:{}@{}/{}".format(
            self.DB_USER,
            self.DB_PW,
            self.DB_HOST,
            self.DB_NAME,
        )


class ConfigTest(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"


default = Config()
prod = Config()
test = ConfigTest()
