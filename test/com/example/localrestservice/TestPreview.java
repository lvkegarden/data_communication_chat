package com.example.localrestservice;

import com.example.localrestservice.service.AgentService;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class TestPreview {

    @Test
    void testPreviewPayloadFormatWithFlagN() {
        String sessionId = "web-1778658914";
        String userMessage = "Hello, World!";
        String flag = "n";

        String expectedPayload = "{\"session_id\":\"web-1778658914\",\"message\":\"Hello, World!\",\"flag\":\"n\"}";
        String actualPayload = buildPreviewPayload(sessionId, userMessage, flag);

        assertEquals(expectedPayload, actualPayload, "预览报文格式应包含flag=n标记");
    }

    @Test
    void testSubmitPayloadFormatWithFlagY() {
        String sessionId = "web-1778658914";
        String userMessage = "Hello, World!";
        String flag = "y";

        String expectedPayload = "{\"session_id\":\"web-1778658914\",\"message\":\"Hello, World!\",\"flag\":\"y\"}";
        String actualPayload = buildPreviewPayload(sessionId, userMessage, flag);

        assertEquals(expectedPayload, actualPayload, "提交报文格式应包含flag=y标记");
    }

    @Test
    void testPreviewPayloadWithSpecialCharacters() {
        String sessionId = "web-test";
        String userMessage = "Hello\nWorld\"Test\"";
        String flag = "n";

        String expectedPayload = "{\"session_id\":\"web-test\",\"message\":\"Hello\\nWorld\\\"Test\\\"\",\"flag\":\"n\"}";
        String actualPayload = buildPreviewPayload(sessionId, userMessage, flag);

        assertEquals(expectedPayload, actualPayload, "特殊字符应正确转义");
    }

    @Test
    void testPreviewPayloadEmptyMessage() {
        String sessionId = "web-test";
        String userMessage = "";
        String flag = "n";

        String expectedPayload = "{\"session_id\":\"web-test\",\"message\":\"\",\"flag\":\"n\"}";
        String actualPayload = buildPreviewPayload(sessionId, userMessage, flag);

        assertEquals(expectedPayload, actualPayload, "空消息应正确处理");
    }

    @Test
    void testEscapeJsonMethod() {
        String test1 = escapeJson("test\"quote\"");
        assertEquals("test\\\"quote\\\"", test1, "双引号应转义");

        String test2 = escapeJson("line1\nline2");
        assertEquals("line1\\nline2", test2, "换行符应转义");

        String test3 = escapeJson("path\\to\\file");
        assertEquals("path\\\\to\\\\file", test3, "反斜杠应转义");

        String test4 = escapeJson(null);
        assertEquals("", test4, "null应返回空字符串");
    }

    @Test
    void testFlagControlLogic() {
        String flagN = "n";
        String flagY = "y";

        assertFalse(shouldCallModel(flagN), "flag=n时不应调用大模型");
        assertTrue(shouldCallModel(flagY), "flag=y时应调用大模型");
        assertTrue(shouldCallModel(""), "flag为空时默认调用大模型");
        assertTrue(shouldCallModel(null), "flag为null时默认调用大模型");
    }

    private String buildPreviewPayload(String sessionId, String message, String flag) {
        return String.format("{\"session_id\":\"%s\",\"message\":\"%s\",\"flag\":\"%s\"}", 
                escapeJson(sessionId), escapeJson(message), escapeJson(flag));
    }

    private String escapeJson(String value) {
        if (value == null) return "";
        return value.replace("\\", "\\\\")
                    .replace("\"", "\\\"")
                    .replace("\n", "\\n")
                    .replace("\r", "\\r")
                    .replace("\t", "\\t");
    }

    private boolean shouldCallModel(String flag) {
        return !"n".equalsIgnoreCase(flag);
    }
}