package com.example.localrestservice.controller;

import com.example.localrestservice.service.ProductDataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/product-data")
public class ProductDataController {

    private final ProductDataService productDataService;

    @Autowired
    public ProductDataController(ProductDataService productDataService) {
        this.productDataService = productDataService;
    }

    @GetMapping("/detail/{productCode}")
    public ResponseEntity<Map<String, Object>> getProductDetail(@PathVariable String productCode) {
        Map<String, Object> result = new HashMap<>();
        Optional<Map<String, Object>> productOpt = productDataService.getProductByCode(productCode);
        
        if (productOpt.isPresent()) {
            result.put("success", true);
            result.put("product", productOpt.get());
            return ResponseEntity.ok(result);
        } else {
            result.put("success", false);
            result.put("error", "Product not found: " + productCode);
            return ResponseEntity.ok(result);
        }
    }

    @GetMapping("/search")
    public ResponseEntity<Map<String, Object>> searchProducts(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String category,
            @RequestParam(required = false) String source) {
        
        Map<String, Object> result = new HashMap<>();
        List<Map<String, Object>> products;
        
        if (keyword != null && !keyword.isEmpty()) {
            products = productDataService.searchProducts(keyword);
        } else if (category != null && !category.isEmpty()) {
            products = productDataService.getProductsByCategory(category);
        } else if (source != null && !source.isEmpty()) {
            products = productDataService.getProductsBySource(source);
        } else {
            products = productDataService.getAllProductsSummary();
        }
        
        result.put("success", true);
        result.put("products", products);
        result.put("count", products.size());
        return ResponseEntity.ok(result);
    }

    @GetMapping("/competitors/{productCode}")
    public ResponseEntity<Map<String, Object>> getCompetitors(
            @PathVariable String productCode,
            @RequestParam(defaultValue = "3") int limit) {
        
        Map<String, Object> result = new HashMap<>();
        List<Map<String, Object>> competitors = productDataService.findCompetitors(productCode, limit);
        
        result.put("success", true);
        result.put("competitors", competitors);
        result.put("count", competitors.size());
        return ResponseEntity.ok(result);
    }

    @GetMapping("/summary")
    public ResponseEntity<Map<String, Object>> getAllProductsSummary() {
        Map<String, Object> result = new HashMap<>();
        List<Map<String, Object>> products = productDataService.getAllProductsSummary();
        
        result.put("success", true);
        result.put("products", products);
        result.put("count", products.size());
        return ResponseEntity.ok(result);
    }
}
