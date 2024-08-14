from django.apps import AppConfig

class JwtApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jwt_api'
    my_object = None
    def ready(self):
        print("initialized")
        from jwt_multi_workers.jwt_impl import JWT_IMP
        self.my_object = JWT_IMP()
        """A very importent step to synch keys befor doing anything with them"""
        self.my_object.sync_keys()
    
