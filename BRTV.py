import os
import time
import string
import re
import urllib.parse
import requests
import json
import base64
import hashlib
import random
import subprocess
from html import unescape

def base64_decode(s):
    decoded_bytes = base64.b64decode(s)
    decoded_str = decoded_bytes.decode('utf-8', errors='replace')
    escaped_str = unescape(decoded_str)
    return urllib.parse.unquote(escaped_str)

def get_beijing_tv():
    gids = [
        ("573ib1kp5nk92irinpumbo9krlb", "BEIJINGTV"),
        ("54db6gi5vfj8r8q1e6r89imd64s", "BEIJINGWY"),
        ("53bn9rlalq08lmb8nf8iadoph0b", "BEIJINGKJ"),
        ("50mqo8t4n4e8gtarqr3orj9l93v", "BEIJINGYS"),
        ("50e335k9dq488lb7jo44olp71f5", "BEIJINGCJ"),
        ("50j015rjrei9vmp3h8upblr41jf", "BEIJINGSH"),
        ("53gpt1ephlp86eor6ahtkg5b2hf", "BEIJINGXW"),
        ("55skfjq618b9kcq9tfjr5qllb7r", "BEIJINGSR")
    ]
    beijing_tvs = []
    for gid, placeholder in gids:
        timestamp = str(int(time.time()))
        sign_str = f"{gid}151{timestamp}TtJSg@2g*$K4PjUH"
        sign = hashlib.md5(sign_str.encode()).hexdigest()[:8]
        try:
            headers = {
                "Referer": "https://www.btime.com/"
            }
            response = requests.get(f"https://pc.api.btime.com/video/play?id={gid}&type_id=151&timestamp={timestamp}&sign={sign}", headers=headers)
            response.raise_for_status()
            stream_url = json.loads(response.text)["data"]["video_stream"][0]["stream_url"]
            beijing_tv = base64_decode(base64_decode(stream_url[::-1]))
            if beijing_tv:
                print(f"{placeholder}：{beijing_tv}")
                beijing_tvs.append({placeholder: beijing_tv})
            else:
                print("北京获取失败")
        except Exception as e:
            print(e)
    return beijing_tvs

def update_data(data_list):
    template_path = '/www/wwwroot/IPTV/beijing/BRTV'
    output_path = '/www/wwwroot/IPTV/beijing/BRTV.m3u'
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        for info in data_list:
            for placeholder, value in info.items():
                template_content = template_content.replace(f'{{{placeholder}}}', value or '')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        print("数据更新完成")
    else:
        print("模版文件不存在")

def add_safe_directory(repo_path):
    try:
        subprocess.run(['sudo', '-u', 'www', 'git', 'config', '--global', '--add', 'safe.directory', repo_path], check=True)
        print(f"{repo_path} 已添加到 Git 安全目录列表")
    except subprocess.CalledProcessError as e:
        print(f"添加安全目录时出错: {e}")

def set_git_identity(repo_path, name, email):
    try:
        # 以 www 用户身份配置用户名
        subprocess.run(['sudo', '-u', 'www', 'git', '-C', repo_path, 'config', 'user.name', name], check=True)
        # 以 www 用户身份配置邮箱
        subprocess.run(['sudo', '-u', 'www', 'git', '-C', repo_path, 'config', 'user.email', email], check=True)
        print(f"Git 用户身份已配置为 {name} <{email}>")
    except subprocess.CalledProcessError as e:
        print(f"配置 Git 用户身份时出错: {e}")

def add_remote_repository(repo_path, remote_name, remote_url):
    try:
        # 以 www 用户身份添加远程仓库
        subprocess.run(['sudo', '-u', 'www', 'git', '-C', repo_path, 'remote', 'add', remote_name, remote_url], check=True)
        print(f"已关联远程仓库 {remote_name}: {remote_url}")
    except subprocess.CalledProcessError as e:
        print(f"关联远程仓库时出错: {e}")

def git_push(repo_path, commit_message):
    try:
        # 添加安全目录
        add_safe_directory(repo_path)
        # 配置 Git 用户身份
        set_git_identity(repo_path, "0047ol", "i0047ol@qq.com")
        # 关联远程仓库
        remote_name = "origin"
        remote_url = "git@github.com:0047ol/BRTV-Live-M3U8.git"
        add_remote_repository(repo_path, remote_name, remote_url)
        # 以 www 用户身份执行 git add
        subprocess.run(['sudo', '-u', 'www', 'git', '-C', repo_path, 'add', 'BRTV.m3u'], check=True)
        print("文件已添加到暂存区")
        # 以 www 用户身份执行 git commit
        subprocess.run(['sudo', '-u', 'www', 'git', '-C', repo_path, 'commit', '-m', commit_message], check=True)
        print("更新已提交到本地仓库")
        # 以 www 用户身份设置上游分支并推送
        local_branch = "master"  # 根据实际情况修改
        remote_branch = "main"
        subprocess.run(['sudo', '-u', 'www', 'git', '-C', repo_path, 'push', '--set-upstream', remote_name, f"{local_branch}:{remote_branch}"], check=True)
        print("更新已推送到远程仓库")
    except subprocess.CalledProcessError as e:
        print(f"Git 操作出错: {e}")
def main():

    data_list = []
    print("获取北京数据中...")
    data_list.extend(get_beijing_tv())

    print("正在更新数据中...")
    update_data(data_list)
    
    repo_path = '/www/wwwroot/IPTV/beijing'
    commit_message = "Update"
    print("正在将更新推送到 GitHub 仓库...")
    git_push(repo_path, commit_message)

if __name__ == "__main__":
    main()