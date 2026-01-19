import os
import requests
import sys

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '').strip()

if not GITHUB_TOKEN:
    print("❌ 错误: 未找到 GITHUB_TOKEN 环境变量")
    print("\n请先设置 Token:")
    print('$env:GITHUB_TOKEN = "你的_Personal_Access_Token"')
    print("\n创建 Token 方法:")
    print("1. 打开 https://github.com/settings/tokens")
    print("2. 点击 'Generate new token (classic)'")
    print("3. Note: 'multimo-push'")
    print("4. 勾选 'repo' 权限")
    print("5. 点击 'Generate token'")
    print("6. 复制 token 并设置到环境变量")
    sys.exit(1)

HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'Python-script'
}

REPO_NAME = 'multimo'
DESCRIPTION = '多智能体预测引擎 - 社交模拟与预测系统'

print(f"🔧 正在创建仓库: {REPO_NAME}...")

create_url = 'https://api.github.com/user/repos'
data = {
    'name': REPO_NAME,
    'description': DESCRIPTION,
    'private': False,
    'auto_init': False
}

response = requests.post(create_url, headers=HEADERS, json=data)

if response.status_code == 201:
    print(f"✅ 仓库创建成功: https://github.com/Sea2049/{REPO_NAME}")
elif response.status_code == 422:
    print(f"⚠️  仓库已存在: https://github.com/Sea2049/{REPO_NAME}")
else:
    print(f"❌ 创建失败: {response.status_code}")
    print(response.text)
    sys.exit(1)

print("\n🔧 正在配置远程仓库...")
os.chdir(r'E:\trae\multimo')
os.system('git remote remove origin 2>nul')
os.system(f'git remote add origin https://github.com/Sea2049/{REPO_NAME}.git')

print("\n📤 正在推送代码...")
result = os.system('git push -u origin main --tags')

if result == 0:
    print("\n✅ 推送成功!")
    print(f"仓库地址: https://github.com/Sea2049/{REPO_NAME}")
    print(f"标签: v1.1")
else:
    print("\n❌ 推送失败")
