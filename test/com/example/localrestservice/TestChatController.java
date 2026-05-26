package com.example.localrestservice;

import com.example.localrestservice.controller.ChatController;
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
class TestChatController {

    @Autowired
    private ChatController chatController;

    @Test
    void testChatControllerInitialized() {
        assertNotNull(chatController);
    }

    @Test
    void testChatWithEmptyMessage() {
        Map<String, String> request = Map.of("message", "");
        Map<String, Object> response = chatController.chat(request);

        assertNotNull(response);
        assertEquals(false, response.get("success"));
    }

    @Test
    void testChatWithNullMessage() {
        Map<String, String> request = Map.of("sessionId", "test");
        Map<String, Object> response = chatController.chat(request);

        assertNotNull(response);
        assertEquals(false, response.get("success"));
    }

    @Test
    void testClearSession() {
        Map<String, Object> response = chatController.clearSession("test-session");
        assertEquals(true, response.get("success"));
    }
}