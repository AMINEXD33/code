from django.apps import AppConfig

class JwtApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jwt_api'
    my_object = None
    def ready(self):
        print("initialized")
        from jwt_multi_workers.jwt_impl import JWT_IMP
        """
        !!!!!!!!!!!!!!!!!!!!!
        !!!!!!!!!!
        IMPORTENT TO SYNC THE KEYS IN APP , VERY VERY IMPORTENT
        to not get the out of sync behavior that made me debug 7h
        to finally figure out thet i needed to sync from the app -_-
        don't be like me , value your time
        """
        self.my_object = JWT_IMP()
        self.my_object.sync_keys()
    
