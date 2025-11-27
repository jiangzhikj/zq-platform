import os
# dev, uat, prd
ENV = os.environ.get('ZQ_ENV', 'dev')


if ENV == 'dev':
    from env.dev_env import *
elif ENV == 'uat':
    from env.uat_env import *
elif ENV == 'prd':
    from env.prd_env import *


