import os, re

classes_found = set()
for root, _, files in os.walk('app/templates'):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            matches = re.findall(r'class=[\'\"]([^\'\"]+)[\'\"]', content)
            for m in matches:
                for c in m.split():
                    classes_found.add(c)
for c in sorted(classes_found):
    if any(c.startswith(prefix) for prefix in ['btn', 'table', 'alert', 'badge', 'bg-', 'text-', 'nav', 'pagination', 'page-', 'dropdown', 'list-group', 'card', 'form-', 'modal', 'progress']):
        print(c)
