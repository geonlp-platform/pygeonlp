import json
import pygeonlp.api as api
import pygeonlp.capi as capi

api.init(dict_dir='test_dic')
# print(api._capi_ma.getActiveClasses())

print(api.searchWord('神保町'))
classes = [".*", "-鉄道施設/.*"]
api.setActiveClasses(classes)
print(api.searchWord('神保町'))

api.setActiveClasses()
print(api.searchWord('神保町'))
