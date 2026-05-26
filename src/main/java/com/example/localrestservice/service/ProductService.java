package com.example.localrestservice.service;

import com.example.localrestservice.dto.CompetitorAnalysisRequest;
import com.example.localrestservice.dto.ProductIntroductionRequest;
import com.example.localrestservice.prompt.PromptTemplate;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;

@Service
public class ProductService {

    private static final Logger logger = LoggerFactory.getLogger(ProductService.class);

    @Value("${langgraph.api-url:http://localhost:5001/api}")
    private String langGraphApiUrl;

    private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper objectMapper = new ObjectMapper();

    public Map<String, Object> generateProductIntroduction(ProductIntroductionRequest request) {
        Map<String, Object> result = new HashMap<>();

        try {
            Map<String, String> variables = new HashMap<>();
            variables.put("product_name", request.getProductName() != null ? request.getProductName() : "");
            variables.put("product_code", request.getProductCode() != null ? request.getProductCode() : "");
            variables.put("series", request.getSeries() != null ? request.getSeries() : "");
            variables.put("category", request.getCategory() != null ? request.getCategory() : "");
            variables.put("status", request.getStatus() != null ? request.getStatus() : "");
            variables.put("description", request.getDescription() != null ? request.getDescription() : "");
            variables.put("specs", request.getSpecsJson() != null ? request.getSpecsJson() : "");

            String prompt = PromptTemplate.fillTemplate(PromptTemplate.PRODUCT_INTRODUCTION_TEMPLATE, variables);

            String sessionId = "product_intro_" + UUID.randomUUID().toString();
            Map<String, Object> chatResponse = callLangGraph(sessionId, prompt);

            if ((Boolean) chatResponse.get("success")) {
                result.put("success", true);
                result.put("introduction", chatResponse.get("message"));
                result.put("prompt", prompt);
            } else {
                result.put("success", false);
                result.put("error", chatResponse.get("error"));
            }

        } catch (Exception e) {
            logger.error("Error generating product introduction", e);
            result.put("success", false);
            result.put("error", "Failed to generate product introduction: " + e.getMessage());
        }

        return result;
    }

    public Map<String, Object> generateCompetitorAnalysis(CompetitorAnalysisRequest request) {
        Map<String, Object> result = new HashMap<>();

        try {
            StringBuilder competitorsInfo = new StringBuilder();
            if (request.getCompetitors() != null && !request.getCompetitors().isEmpty()) {
                for (int i = 0; i < request.getCompetitors().size(); i++) {
                    CompetitorAnalysisRequest.CompetitorInfo comp = request.getCompetitors().get(i);
                    competitorsInfo.append("【竞品").append(i + 1).append("】\n");
                    competitorsInfo.append("- 产品名称：").append(comp.getProductName() != null ? comp.getProductName() : "").append("\n");
                    competitorsInfo.append("- 产品型号：").append(comp.getProductCode() != null ? comp.getProductCode() : "").append("\n");
                    competitorsInfo.append("- 产品系列：").append(comp.getSeries() != null ? comp.getSeries() : "").append("\n");
                    competitorsInfo.append("- 产品描述：").append(comp.getDescription() != null ? comp.getDescription() : "").append("\n");
                    competitorsInfo.append("- 技术规格：").append(comp.getSpecsJson() != null ? comp.getSpecsJson() : "").append("\n\n");
                }
            } else {
                competitorsInfo.append("无具体竞品信息，请根据行业知识进行分析。\n");
            }

            Map<String, String> variables = new HashMap<>();
            variables.put("product_name", request.getTargetProductName() != null ? request.getTargetProductName() : "");
            variables.put("product_code", request.getTargetProductCode() != null ? request.getTargetProductCode() : "");
            variables.put("series", request.getTargetSeries() != null ? request.getTargetSeries() : "");
            variables.put("description", request.getTargetDescription() != null ? request.getTargetDescription() : "");
            variables.put("specs", request.getTargetSpecsJson() != null ? request.getTargetSpecsJson() : "");
            variables.put("competitors_info", competitorsInfo.toString());

            String prompt = PromptTemplate.fillTemplate(PromptTemplate.COMPETITOR_ANALYSIS_TEMPLATE, variables);

            String sessionId = "competitor_analysis_" + UUID.randomUUID().toString();
            Map<String, Object> chatResponse = callLangGraph(sessionId, prompt);

            if ((Boolean) chatResponse.get("success")) {
                result.put("success", true);
                result.put("analysis", chatResponse.get("message"));
                result.put("prompt", prompt);
            } else {
                result.put("success", false);
                result.put("error", chatResponse.get("error"));
            }

        } catch (Exception e) {
            logger.error("Error generating competitor analysis", e);
            result.put("success", false);
            result.put("error", "Failed to generate competitor analysis: " + e.getMessage());
        }

        return result;
    }

    private Map<String, Object> callLangGraph(String sessionId, String message) {
        Map<String, Object> result = new HashMap<>();

        try {
            String requestBody = objectMapper.writeValueAsString(
                Map.of("session_id", sessionId, "message", message, "flag", "y")
            );

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<String> entity = new HttpEntity<>(requestBody, headers);

            ResponseEntity<String> response = restTemplate.exchange(
                langGraphApiUrl + "/chat",
                HttpMethod.POST,
                entity,
                String.class
            );

            Map<String, Object> responseMap = objectMapper.readValue(response.getBody(), Map.class);
            boolean success = (Boolean) responseMap.getOrDefault("success", false);

            if (success) {
                result.put("success", true);
                result.put("message", responseMap.get("message"));
            } else {
                result.put("success", false);
                result.put("error", responseMap.get("error"));
            }

        } catch (Exception e) {
            logger.error("Error calling LangGraph API", e);
            result.put("success", false);
            result.put("error", "Failed to connect to LangGraph service: " + e.getMessage());
        }

        return result;
    }
}
