package com.example.localrestservice.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;

@Service
public class AgentService {

    private static final Logger logger = LoggerFactory.getLogger(AgentService.class);

    @Value("${langgraph.api-url:http://localhost:5001/api}")
    private String langGraphApiUrl;

    private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper objectMapper = new ObjectMapper();

    @PostConstruct
    public void init() {
        logger.info("AgentService initialized with LangGraph API: {}", langGraphApiUrl);
    }

    public Map<String, Object> chat(String sessionId, String userMessage, String flag) {
        Map<String, Object> result = new HashMap<>();

        try {
            String requestBody = String.format("{\"session_id\":\"%s\",\"message\":\"%s\",\"flag\":\"%s\"}", 
                    escapeJson(sessionId), escapeJson(userMessage), escapeJson(flag));

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<String> entity = new HttpEntity<>(requestBody, headers);

            ResponseEntity<String> response = restTemplate.exchange(
                    langGraphApiUrl + "/chat",
                    HttpMethod.POST,
                    entity,
                    String.class
            );

            JsonNode responseJson = objectMapper.readTree(response.getBody());
            boolean success = responseJson.path("success").asBoolean();

            if (success) {
                String assistantMessage = responseJson.path("message").asText();
                String responseSessionId = responseJson.path("session_id").asText();
                JsonNode preview = responseJson.path("preview");

                result.put("success", true);
                result.put("message", assistantMessage);
                result.put("sessionId", responseSessionId);
                
                if (!preview.isMissingNode()) {
                    result.put("preview", preview.asText());
                }
            } else {
                String error = responseJson.path("error").asText();
                result.put("success", false);
                result.put("error", error);
            }

        } catch (Exception e) {
            logger.error("Error calling LangGraph API", e);
            result.put("success", false);
            result.put("error", "Failed to connect to LangGraph service: " + e.getMessage());
        }

        return result;
    }

    public Map<String, Object> chat(String sessionId, String userMessage) {
        return chat(sessionId, userMessage, "y");
    }

    private String escapeJson(String value) {
        if (value == null) return "";
        return value.replace("\\", "\\\\")
                    .replace("\"", "\\\"")
                    .replace("\n", "\\n")
                    .replace("\r", "\\r")
                    .replace("\t", "\\t");
    }

    public Map<String, Object> chatWithHistory(String sessionId, String userMessage, int maxHistory) {
        return chat(sessionId, userMessage);
    }

    public void clearSession(String sessionId) {
        try {
            restTemplate.exchange(
                    langGraphApiUrl + "/session/" + sessionId,
                    HttpMethod.DELETE,
                    null,
                    String.class
            );
            logger.info("Session cleared: {}", sessionId);
        } catch (Exception e) {
            logger.error("Error clearing session", e);
        }
    }

    public static class Message {
        private String role;
        private String content;

        public Message() {}

        public Message(String role, String content) {
            this.role = role;
            this.content = content;
        }

        public static Message userMessage(String content) {
            return new Message("user", content);
        }

        public static Message assistantMessage(String content) {
            return new Message("assistant", content);
        }

        public String getRole() { return role; }
        public void setRole(String role) { this.role = role; }
        public String getContent() { return content; }
        public void setContent(String content) { this.content = content; }
    }
}