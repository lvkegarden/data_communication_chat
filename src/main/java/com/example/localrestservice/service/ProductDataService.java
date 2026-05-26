package com.example.localrestservice.service;

import com.example.localrestservice.entity.ProductSpec;
import com.example.localrestservice.repository.ProductSpecRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class ProductDataService {

    private static final Logger logger = LoggerFactory.getLogger(ProductDataService.class);

    private final ProductSpecRepository productSpecRepository;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Autowired
    public ProductDataService(ProductSpecRepository productSpecRepository) {
        this.productSpecRepository = productSpecRepository;
    }

    public Optional<Map<String, Object>> getProductByCode(String productCode) {
        Optional<ProductSpec> productOpt = productSpecRepository.findByProductCode(productCode);
        return productOpt.map(this::convertToMap);
    }

    public List<Map<String, Object>> getProductsByCategory(String category) {
        List<ProductSpec> products = productSpecRepository.findByCategory(category);
        return products.stream().map(this::convertToMap).collect(Collectors.toList());
    }

    public List<Map<String, Object>> getProductsBySource(String source) {
        List<ProductSpec> products = productSpecRepository.findBySource(source);
        return products.stream().map(this::convertToMap).collect(Collectors.toList());
    }

    public List<Map<String, Object>> getProductsBySeries(String series) {
        List<ProductSpec> products = productSpecRepository.findBySeries(series);
        return products.stream().map(this::convertToMap).collect(Collectors.toList());
    }

    public List<Map<String, Object>> searchProducts(String keyword) {
        List<ProductSpec> allProducts = productSpecRepository.findAll();
        if (keyword == null || keyword.isEmpty()) {
            return allProducts.stream().map(this::convertToMap).collect(Collectors.toList());
        }
        
        String keywordLower = keyword.toLowerCase();
        return allProducts.stream()
            .filter(p -> 
                (p.getProductName() != null && p.getProductName().toLowerCase().contains(keywordLower)) ||
                (p.getProductCode() != null && p.getProductCode().toLowerCase().contains(keywordLower)) ||
                (p.getDescription() != null && p.getDescription().toLowerCase().contains(keywordLower))
            )
            .map(this::convertToMap)
            .collect(Collectors.toList());
    }

    public List<Map<String, Object>> findCompetitors(String productCode, int limit) {
        Optional<ProductSpec> targetProductOpt = productSpecRepository.findByProductCode(productCode);
        if (!targetProductOpt.isPresent()) {
            return Collections.emptyList();
        }

        ProductSpec targetProduct = targetProductOpt.get();
        String category = targetProduct.getCategory();
        String source = targetProduct.getSource();

        List<ProductSpec> allProducts = productSpecRepository.findAll();
        
        return allProducts.stream()
            .filter(p -> !p.getProductCode().equals(productCode))
            .filter(p -> {
                boolean sameCategory = category != null && category.equals(p.getCategory());
                boolean sameSource = source != null && source.equals(p.getSource());
                return sameCategory || sameSource;
            })
            .limit(limit)
            .map(this::convertToMap)
            .collect(Collectors.toList());
    }

    public List<Map<String, Object>> getAllProductsSummary() {
        List<ProductSpec> allProducts = productSpecRepository.findAll();
        return allProducts.stream()
            .map(p -> {
                Map<String, Object> summary = new HashMap<>();
                summary.put("product_code", p.getProductCode());
                summary.put("product_name", p.getProductName());
                summary.put("category", p.getCategory());
                summary.put("source", p.getSource());
                summary.put("series", p.getSeries());
                return summary;
            })
            .collect(Collectors.toList());
    }

    private Map<String, Object> convertToMap(ProductSpec product) {
        Map<String, Object> map = new HashMap<>();
        map.put("product_code", product.getProductCode());
        map.put("product_name", product.getProductName());
        map.put("series", product.getSeries());
        map.put("category", product.getCategory());
        map.put("source", product.getSource());
        map.put("status", product.getStatus());
        map.put("description", product.getDescription());
        map.put("specs_json", product.getSpecsJson());
        map.put("thumbnail_url", product.getThumbnailUrl());
        return map;
    }
}
