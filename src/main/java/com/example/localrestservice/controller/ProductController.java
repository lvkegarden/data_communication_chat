package com.example.localrestservice.controller;

import com.example.localrestservice.dto.CompetitorAnalysisRequest;
import com.example.localrestservice.dto.ProductIntroductionRequest;
import com.example.localrestservice.service.ProductService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/product")
public class ProductController {

    private final ProductService productService;

    @Autowired
    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @PostMapping("/introduction")
    public ResponseEntity<Map<String, Object>> generateIntroduction(
            @RequestBody ProductIntroductionRequest request) {
        Map<String, Object> result = new HashMap<>();
        try {
            Map<String, Object> response = productService.generateProductIntroduction(request);
            if ((Boolean) response.get("success")) {
                result.put("success", true);
                result.put("introduction", response.get("introduction"));
                result.put("prompt", response.get("prompt"));
                return ResponseEntity.ok(result);
            } else {
                result.put("success", false);
                result.put("error", response.get("error"));
                return ResponseEntity.badRequest().body(result);
            }
        } catch (Exception e) {
            result.put("success", false);
            result.put("error", e.getMessage());
            return ResponseEntity.internalServerError().body(result);
        }
    }

    @PostMapping("/competitor-analysis")
    public ResponseEntity<Map<String, Object>> generateCompetitorAnalysis(
            @RequestBody CompetitorAnalysisRequest request) {
        Map<String, Object> result = new HashMap<>();
        try {
            Map<String, Object> response = productService.generateCompetitorAnalysis(request);
            if ((Boolean) response.get("success")) {
                result.put("success", true);
                result.put("analysis", response.get("analysis"));
                result.put("prompt", response.get("prompt"));
                return ResponseEntity.ok(result);
            } else {
                result.put("success", false);
                result.put("error", response.get("error"));
                return ResponseEntity.badRequest().body(result);
            }
        } catch (Exception e) {
            result.put("success", false);
            result.put("error", e.getMessage());
            return ResponseEntity.internalServerError().body(result);
        }
    }
}
