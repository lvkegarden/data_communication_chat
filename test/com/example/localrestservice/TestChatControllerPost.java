package com.example.localrestservice;

import com.example.localrestservice.controller.ChatController;
import com.example.localrestservice.service.AgentService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;

import java.util.HashMap;
import java.util.Map;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@TestPropertySource(properties = {
    "dashscope.api-key=test-key",
    "dashscope.model=qwen-plus"
})
class TestChatControllerPost {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private AgentService agentService;

    @Test
    void testChatPostRequest() throws Exception {
        Map<String, String> request = new HashMap<>();
        request.put("sessionId", "test-session");
        request.put("message", "你好，测试消息");

        mockMvc.perform(post("/api/chat/chat")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk());
    }

    @Test
    void testChatPostWithEmptyMessage() throws Exception {
        Map<String, String> request = new HashMap<>();
        request.put("sessionId", "test-session");
        request.put("message", "");

        mockMvc.perform(post("/api/chat/chat")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(false));
    }

    @Test
    void testChatPostWithNullMessage() throws Exception {
        Map<String, String> request = new HashMap<>();
        request.put("sessionId", "test-session");

        mockMvc.perform(post("/api/chat/chat")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(false));
    }

    @Test
    void testChatPostWithoutSessionId() throws Exception {
        Map<String, String> request = new HashMap<>();
        request.put("message", "你好");

        mockMvc.perform(post("/api/chat/chat")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk());
    }
}