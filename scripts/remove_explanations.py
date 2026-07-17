import os, re
for root, _, files in os.walk('app/templates'):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Remove explanatory texts
            new_content = re.sub(r'\n\s*<p class="[^"]*text-secondary mb-0">.*?</p>', '', content, flags=re.IGNORECASE)
            new_content = re.sub(r'\n\s*<p class="text-secondary mb-4">.*?</p>', '', new_content, flags=re.IGNORECASE)
            
            # The login page has: <p class="text-secondary">Đăng nhập để quản lý tài liệu StudyDrive.</p>
            new_content = re.sub(r'\n\s*<p class="text-secondary">Đăng nhập để quản lý tài liệu.*?</p>', '', new_content, flags=re.IGNORECASE)
            
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Updated {path}')
