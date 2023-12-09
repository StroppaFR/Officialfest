# hammerfest.fr uses ';' to separate arguments in query string which is not support by Flask
def args_from_query_string(query_string: bytes) -> dict:
    query_string = query_string.decode()
    query_string = query_string.replace('&', ';')
    args = {}
    for keyval in query_string.split(';'):
        if '=' in keyval:
            key = keyval.split('=')[0]
            val = ''.join(keyval.split('=')[1:])
        else:
            key = keyval
            val = ''
        if key != '':
            args[key] = val
    return args

def sanitized_page_arg(args: dict, max_page: int):
    try:
        page = args['page']
        page = int(page)
    except Exception:
        page = 1
    if page < 1 or page > max_page:
        page = 1
    return page
