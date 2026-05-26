package com.example.localrestservice;

import com.example.localrestservice.service.AgentService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@TestPropertySource(properties = {
    "dashscope.api-key=test-key",
    "dashscope.model=qwen-plus"
})
class TestAgentService {

    @Autowired
    private AgentService agentService;

    @Test
    void testAgentServiceInitialized() {
        assertNotNull(agentService);
    }

    @Test
    void testChatWithEmptyApiKey() {
        Map<String, Object> result = agentService.chat("test-session", "Hello");

        assertNotNull(result);
        assertEquals(false, result.get("success"));
        assertNotNull(result.get("error"));
        assertTrue(result.get("error").toString().contains("API key not configured"));
    }

    @Test
    void testClearSession() {
        agentService.clearSession("test-session");
    }
}