import sys
import re
import os
import json

# ==========================================
# 敏感信息规则库 (双语轻量版)
# Bilingual Sensitive Information Rule Base
# ==========================================
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

# 正则表达式匹配 / Regex Patterns
PATTERNS = {
    "疑似身份证号 | Suspected ID": r"\b[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]\b",
    "疑似银行卡号 | Suspected Bank Card": r"\b([4569]\d{15}|\d{19})\b",
    "疑似手机号 | Suspected Phone Num": r"\b1[3-9]\d{9}\b"
}

def scan_text(text):
    """扫描文本，返回匹配到的敏感信息详情 / Scan text and return findings"""
    findings = []
    # 转小写以支持英文不区分大小写匹配
    lower_text = text.lower() 
    
    # 1. 关键字扫描
    for category, keywords in SENSITIVE_KEYWORDS.items():
        matched = []
        for kw in keywords:
            kw_lower = kw.lower()
            # 如果关键字包含英文字母，使用单词边界正则，防止发生子串误报 (例如 "bom" 匹配到 "abominable")
            # If the keyword contains English letters, use word boundary regex to avoid false positive substring matches
            if re.search(r'[a-z]', kw_lower):
                pattern = r'\b' + re.escape(kw_lower) + r'\b'
                if re.search(pattern, lower_text):
                    matched.append(kw)
            else:
                # 纯中文直接匹配 / Direct match for pure Chinese
                if kw_lower in lower_text:
                    matched.append(kw)
                    
        if matched:
            findings.append({
                "category": category, 
                "matched_keywords": matched
            })
            
    # 2. 正则扫描
    for pattern_name, pattern in PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            if len(matches) > 0: 
                findings.append({
                    "category": "个人隐私/敏感编号 | PII", 
                    "matched_keywords": [f"{pattern_name} ({len(matches)} found)"]
                })
                
    return findings

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "ERROR", "message": "Usage: python simple_scanner.py <text_or_file_path>"}, ensure_ascii=False))
        sys.exit(1)
        
    input_target = sys.argv[1]
    text_to_scan = ""
    
    if os.path.exists(input_target) and os.path.isfile(input_target):
        try:
            with open(input_target, 'r', encoding='utf-8', errors='ignore') as f:
                text_to_scan = f.read(50000) 
        except Exception as e:
            print(json.dumps({"status": "ERROR", "message": f"Cannot read file: {str(e)}"}, ensure_ascii=False))
            sys.exit(1)
    else:
        text_to_scan = input_target
        
    findings = scan_text(text_to_scan)
    
    if findings:
        result = {
            "status": "WARNING",
            "message": "⚠️ 发现疑似企业机密或敏感信息 / Warning: Suspected corporate confidential or sensitive information found",
            "details": findings
        }
    else:
        result = {
            "status": "SAFE",
            "message": "✅ 未检测到明显的机密信息 / Safe: No obvious confidential information detected",
            "details": []
        }
        
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()