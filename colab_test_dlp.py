import os
import json
import subprocess

print("🚀 开始初始化 OpenClaw DLP Skill 双语测试环境...\n")

# ==========================================
# 1. 自动在 Colab 本地生成 simple_scanner.py
# ==========================================
SCANNER_CODE = """
import sys
import re
import os
import json

SENSITIVE_KEYWORDS = {
    "研发数据 | R&D Data": [
        "核心算法", "未公开专利", "源代码", "架构设计", "底层逻辑", "研发机密", "技术图纸", "API密钥", "sk-",
        "core algorithm", "undisclosed patent", "source code", "architecture design", "underlying logic", "R&D secret", "technical drawing", "API key"
    ],
    "项目信息 | Project Info": [
        "未发布", "保密项目", "内部立项", "预期里程碑", "Project Alpha", "绝密",
        "unreleased", "confidential project", "internal initiation", "expected milestone", "top secret"
    ],
    "客户信息 | Customer Info": [
        "客户名单", "大客户", "购买记录", "客户住址", "CRM导出",
        "customer list", "key account", "purchase record", "customer address", "CRM export"
    ],
    "财务数据 | Financial Data": [
        "营业收入", "毛利润", "净利润", "财报底稿", "银行流水", "对公账户", "避税", "审计报告",
        "revenue", "gross profit", "net profit", "financial draft", "bank statement", "corporate account", "tax evasion", "audit report"
    ],
    "员工信息及薪资 | HR & Payroll": [
        "薪资单", "绩效考核", "底薪", "五险一金", "社保基数", "劳动合同", "职级薪水", "花名册",
        "payslip", "performance review", "base salary", "social security", "labor contract", "salary grade", "roster"
    ],
    "合同内容 | Contracts": [
        "保密协议", "NDA", "独家代理", "合作条款", "违约金", "采购合同", "框架协议", "法务部审阅",
        "non-disclosure agreement", "exclusive agency", "cooperation terms", "liquidated damages", "procurement contract", "framework agreement", "legal review"
    ],
    "供应商信息 | Supplier Info": [
        "供应商报价", "底价", "供应商名单", "采购成本", "SLA条款",
        "supplier quote", "floor price", "supplier list", "procurement cost", "SLA terms"
    ],
    "生产信息 | Production Data": [
        "良品率", "生产工艺", "核心配方", "产能数据", "车间平面图", "SOP文件",
        "yield rate", "production process", "core formula", "capacity data", "workshop layout", "SOP document"
    ],
    "物料信息 | Material Info": [
        "BOM表", "物料清单", "核心零部件", "采购清单",
        "BOM", "bill of materials", "core component", "procurement list"
    ]
}

PATTERNS = {
    "疑似身份证号 | Suspected ID": r"\\b[1-9]\\d{5}(18|19|20)\\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\\d|3[01])\\d{3}[\\dXx]\\b",
    "疑似银行卡号 | Suspected Bank Card": r"\\b([4569]\\d{15}|\\d{19})\\b",
    "疑似手机号 | Suspected Phone Num": r"\\b1[3-9]\\d{9}\\b"
}

def scan_text(text):
    findings = []
    lower_text = text.lower()
    for category, keywords in SENSITIVE_KEYWORDS.items():
        matched = []
        for kw in keywords:
            kw_lower = kw.lower()
            if re.search(r'[a-z]', kw_lower):
                if re.search(r'\\b' + re.escape(kw_lower) + r'\\b', lower_text):
                    matched.append(kw)
            else:
                if kw_lower in lower_text:
                    matched.append(kw)
        if matched:
            findings.append({"category": category, "matched_keywords": matched})
            
    for pattern_name, pattern in PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            findings.append({"category": "PII", "matched_keywords": [f"{pattern_name} ({len(matches)} found)"]})
    return findings

def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    input_target = sys.argv[1]
    text_to_scan = ""
    if os.path.exists(input_target) and os.path.isfile(input_target):
        with open(input_target, 'r', encoding='utf-8', errors='ignore') as f:
            text_to_scan = f.read(50000) 
    else:
        text_to_scan = input_target
    findings = scan_text(text_to_scan)
    if findings:
        result = {"status": "WARNING", "message": "⚠️ 发现疑似企业机密 / Warning: Secrets found", "details": findings}
    else:
        result = {"status": "SAFE", "message": "✅ 安全 / Safe", "details": []}
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
"""

with open("simple_scanner.py", "w", encoding="utf-8") as f:
    f.write(SCANNER_CODE.strip())
print("✅ 成功生成依赖脚本 / Script generated: simple_scanner.py")

# ==========================================
# 2. 准备中英双语测试数据
# ==========================================
test_cases = [
    {
        "type": "text", "name": "中文安全文本 (Safe CN)", 
        "content": "今天的天气非常不错，建议大家下午去园区散步放松一下。"
    },
    {
        "type": "text", "name": "英文安全文本 (Safe EN)", 
        "content": "The abominable snowman is a myth. Let's grab lunch." # 验证 'bom' 不会被误报
    },
    {
        "type": "text", "name": "英文机密文本 (Secret EN)", 
        "content": "Please send the source code and the API key to our new contractor."
    },
    {
        "type": "file", "name": "中文机密文件 (Secret CN File)", 
        "filename": "secret_payroll.txt",
        "content": "本月净利润大增，张三的身份证号为 110105199001011234，请打入对公账户。"
    }
]

for case in test_cases:
    if case["type"] == "file":
        with open(case["filename"], "w", encoding="utf-8") as f:
            f.write(case["content"])

print("\n" + "="*50)
print("🔍 开始模拟 Agent 调用审查技能 / Starting simulation")
print("="*50 + "\n")

# ==========================================
# 3. 执行测试
# ==========================================
for case in test_cases:
    print(f"▶️ 执行 / Running: {case['name']}")
    target_arg = case["filename"] if case["type"] == "file" else case["content"]
    
    process = subprocess.run(["python", "simple_scanner.py", target_arg], capture_output=True, text=True, encoding="utf-8")
    
    try:
        output_json = json.loads(process.stdout)
        if output_json["status"] == "SAFE":
            print(f"   🟢 Agent: 安全/Safe. 放行 / Continue.\n")
        elif output_json["status"] == "WARNING":
            print(f"   🔴 Agent: 拦截/Intercepted!")
            details_str = ", ".join([d["category"] for d in output_json["details"]])
            keywords_str = ", ".join([str(kw) for d in output_json["details"] for kw in d["matched_keywords"]])
            print("   --- 🤖 Agent Reply ---")
            print("   > 🚫 **安全拦截警示 / Security Interception Warning**")
            print(f"   > **Category**: [{details_str}]")
            print(f"   > **Matched**: [{keywords_str}]")
            print("   ------------------------\n")
    except json.JSONDecodeError:
        print(f"   ❌ JSON Error:\n{process.stdout}\n")