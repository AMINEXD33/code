from jwt_multi_workers import jwt_impl



ss = jwt_impl.JWT_IMP()

ss.sync_keys()
ss.refresh_keys()


tok = ss.make_token(**{'amine':"meftah"})

print(tok)

dec = ss.decr_token(tok)

print(dec.claims)
print("done")