from pprint import pprint

DIVIDER = "/"
urls = [
    "users/clients/not_bought_product/list",
    "users/clients/bought_product/list",
    "users/admins/only_comments/list",
    "users/admins/only_news/list",
    "users/admins/all_privileges/list",
    "users/admins/full_list",
    "users/staff/managers/list",
    "users/staff/carriers/list",
    "users/all_users_list"
]

result = {}
for url in urls:
    url_parts = url.split(DIVIDER)
    for i, part in enumerate(url_parts):
        last = len(url_parts) - 1
        pathway = result
        for j, key in enumerate(url_parts[:i+1]):
            pathway = pathway.setdefault(key, {} if j != last else None)

pprint(result)
