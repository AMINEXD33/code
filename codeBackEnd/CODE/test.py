from jwt_multi_workers.jwt_impl import JWT_IMP

ss = JWT_IMP()
ss.sync_keys()
ss.refresh_keys()