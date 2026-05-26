package com.example.localrestservice.controller;

import com.example.localrestservice.service.CollectService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/collect")
public class CollectController {

    private final CollectService collectService;

    @Autowired
    public CollectController(CollectService collectService) {
        this.collectService = collectService;
    }

    @PostMapping("/huawei")
    public Map<String, Object> collectHuawei() {
        return collectService.collectHuaweiData();
    }

    @PostMapping("/h3c")
    public Map<String, Object> collectH3C() {
        return collectService.collectH3CData();
    }

    @PostMapping("/ruijie")
    public Map<String, Object> collectRuijie() {
        return collectService.collectRuijieData();
    }

    @GetMapping("/products")
    public List<Map<String, Object>> getAllProducts() {
        return collectService.getAllProducts();
    }

    @GetMapping("/stats")
    public Map<String, Object> getStats() {
        return collectService.getProductStats();
    }

    @GetMapping("/products/{id}")
    public Map<String, Object> getProductById(@PathVariable Long id) {
        Map<String, Object> product = collectService.getProductById(id);
        if (product == null) {
            return Map.of(
                "error", "产品不存在"
            );
        }
        return product;
    }

    @DeleteMapping("/clear")
    public Map<String, Object> clearAllData() {
        collectService.clearAllData();
        return Map.of(
            "success", true,
            "message", "所有采集数据已清除"
        );
    }
}
