🛡️ OpenClaw Enterprise DLP Guard (Bilingual Lightweight Version)

🛡️ OpenClaw 本地机密审查技能 (中英双语轻量版)

(English follows below)



这是一个为 OpenClaw Agent 打造的本地数据防泄漏（DLP）技能。它的主要目的是在 Agent 读取本地文件、分析文本或向云端大模型发送数据之前，进行极速的本地敏感信息预检（支持中文和英文）。如果发现疑似企业机密（如财务数据、源代码、员工隐私等），Agent 将自动拦截任务并发出警示。

This is a local Data Loss Prevention (DLP) skill tailored for OpenClaw Agent. Its main purpose is to perform ultra-fast local sensitive information pre-checks (supporting both English and Chinese) before the Agent reads local files, analyzes text, or sends data to cloud-based LLMs.



✨ 特性 / Features

🚀 极速本地运行 / Ultra-fast Local Execution：纯 Python 实现，零外部依赖 / Pure Python implementation, zero external dependencies.

🔒 隐私安全 / Privacy：扫描完全在本地完成 / Scanning is entirely done locally.

🌐 中英双语支持 / Bilingual Support：优化了英文单词的正则边界匹配（Word Boundary），避免类似短英文单词的误判。

🛠️ 高度可定制 / Highly Customizable：通过简单的字典即可扩充企业的专属机密词库 / Easily expand corporate exclusive terminology via simple dictionaries.



📂 仓库目录 / Directory Structureopenclaw-dlp-guard/
├── simple\_skill.md        # OpenClaw 技能定义与 Agent 提示词配置 (Agent Prompts)
├── simple\_scanner.py      # 核心本地扫描引擎 / Core Scanning Engine
├── tests/  
│   └── colab\_test\_dlp.py  # 包含一键测试逻辑的脚本 / Testing script
├── README.md              # 项目说明文档 / Documentation
└── LICENSE                # 开源许可证


🚀 安装指南 / Installation

进入你的 OpenClaw 技能挂载目录 / Go to your OpenClaw skills directory (\~/.openclaw/skills/).

将本仓库克隆或下载到该目录下 / Clone this repo:cd \~/.openclaw/skills/
git clone [https://github.com/YourUsername/openclaw-dlp-guard.git](https://github.com/YourUsername/openclaw-dlp-guard.git)
重新加载或重启你的 OpenClaw Agent / Restart your OpenClaw Agent.



⚙️ 如何自定义规则？ / Customizing Rules

打开 simple\_scanner.py，你可以在文件顶部找到 SENSITIVE\_KEYWORDS 和 PATTERNS 字典。直接添加项目代号或专属黑话即可。

Open simple\_scanner.py and modify SENSITIVE\_KEYWORDS at the top of the file:

SENSITIVE\_KEYWORDS = {
"项目信息 | Project Info": \["内部立项", "Project Alpha", "Your Top Secret Project Name"],
# ...
}


🧪 测试与验证 / Testing

你可以直接在终端或 Google Colab 中运行测试脚本 / Run the test script directly in terminal or Colab:


python colab_test_dlp.py

