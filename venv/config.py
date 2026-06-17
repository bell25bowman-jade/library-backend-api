class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:812288@localhost/library"
    DEBUG = True
    
class TestingConfig:
    pass

class ProductionConfig:
    pass