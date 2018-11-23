import mks647c
import mks647c.message

from mks647c.factory import MKS647CFactory

f = MKS647CFactory()
dr = f.create_device()

dr.test()






