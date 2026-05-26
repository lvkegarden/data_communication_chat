package com.example.localrestservice.prompt;

public class PromptTemplate {
    
    public static final String PRODUCT_INTRODUCTION_TEMPLATE = 
        "你是一个专业的产品分析师，擅长撰写清晰、有吸引力的产品介绍。\n\n" +
        "请根据以下产品信息，生成一份专业的产品介绍：\n\n" +
        "【产品名称】{product_name}\n" +
        "【产品型号】{product_code}\n" +
        "【产品系列】{series}\n" +
        "【产品类别】{category}\n" +
        "【产品状态】{status}\n" +
        "【产品描述】{description}\n" +
        "【技术规格】{specs}\n\n" +
        "请按照以下结构输出：\n" +
        "1. 产品概述（100-200字）\n" +
        "2. 核心卖点（3-5条）\n" +
        "3. 技术亮点（3-5条）\n" +
        "4. 适用场景（2-4个）\n" +
        "5. 总结\n\n" +
        "要求：\n" +
        "- 语言专业、简洁\n" +
        "- 突出产品优势和差异化特点\n" +
        "- 使用技术术语但要易于理解\n" +
        "- 适合B2B营销场景";

    public static final String COMPETITOR_ANALYSIS_TEMPLATE = 
        "你是一个资深的竞争情报分析师，擅长进行竞品对比分析。\n\n" +
        "请对以下产品进行全面的竞品分析：\n\n" +
        "【目标产品】\n" +
        "- 产品名称：{product_name}\n" +
        "- 产品型号：{product_code}\n" +
        "- 产品系列：{series}\n" +
        "- 产品描述：{description}\n" +
        "- 技术规格：{specs}\n\n" +
        "【竞品信息】\n" +
        "{competitors_info}\n\n" +
        "请按照以下结构输出分析报告：\n" +
        "1. 市场定位分析\n" +
        "   - 目标市场\n" +
        "   - 目标客户群体\n" +
        "   - 产品定位\n\n" +
        "2. 竞品对比分析\n" +
        "   - 功能对比\n" +
        "   - 技术参数对比\n" +
        "   - 价格对比（如可获取）\n" +
        "   - 优劣势对比\n\n" +
        "3. SWOT分析\n" +
        "   - 优势（Strengths）\n" +
        "   - 劣势（Weaknesses）\n" +
        "   - 机会（Opportunities）\n" +
        "   - 威胁（Threats）\n\n" +
        "4. 竞争策略建议\n" +
        "   - 差异化策略\n" +
        "   - 市场策略\n" +
        "   - 产品优化建议\n\n" +
        "5. 总结\n\n" +
        "要求：\n" +
        "- 分析客观、数据驱动\n" +
        "- 提供具体的对比维度\n" +
        "- 给出可执行的建议\n" +
        "- 使用表格进行对比（如适用）\n" +
        "- 适合企业决策参考";

    public static String fillTemplate(String template, java.util.Map<String, String> variables) {
        String result = template;
        for (java.util.Map.Entry<String, String> entry : variables.entrySet()) {
            result = result.replace("{" + entry.getKey() + "}", 
                entry.getValue() != null ? entry.getValue() : "");
        }
        return result;
    }
}
