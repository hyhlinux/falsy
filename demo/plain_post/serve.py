from falsy.falsy import FALSY

f = FALSY(static_path='test', static_dir='demo/plain_post/static')
f.swagger('demo/plain_post/spec.yml', ui=True, ui_language='zh-cn', theme='responsive')
api = f.api
