from decouple import config
import os


class Config:
    """Base config, uses staging database server."""

    TESTING = False

    # Database
    DB_NAME = config("DB_NAME")
    DB_USER = config("DB_USER")
    DB_HOST = config("DB_HOST")
    DB_PW = config("DB_PW")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # suppress strange warning
    SQLALCHEMY_ENGINE_OPTIONS = {'enable_from_linting':False}

    SWAGGER_UI_DOC_EXPANSION = "list"

    # Api documentation
    API_TITLE = "Plate Assay Image Database API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/api"
    OPENAPI_SWAGGER_UI_PATH = "/swagger"
    OPENAPI_SWAGGER_UI_URL = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/"
    OPENAPI_REDOC_PATH = "redoc"

    VIEWS_ITEMS_PER_PAGE = 20
    API_ITEMS_PAGE_SIZE = 100
    API_ITEMS_MAX_PAGE_SIZE = 300

    # Default regular expression for parsing files
    ADDITIONAL_REGEXP = {
        "row": r"^.*_([A-Z])[0-9][0-9]_.*$",
        "col": r"^.*_[A-Z]([0-9][0-9])_.*$",
        "site": r"^.*_s([0-9]?[0-9])_.*$",
        "chan": r"^.*_w([0-9]?[0-9])_.*$",
    }
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

    PARSER_SUPPORTED_SCHEMES = ['s3']

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
    # in-memory
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    API_ITEMS_PAGE_SIZE = 10000
    API_ITEMS_MAX_PAGE_SIZE = 10000
    PARSER_SUPPORTED_SCHEMES = ['scheme']


default = Config()
prod = Config()
test = ConfigTest()
