package com.example.localrestservice.service;

import com.example.localrestservice.entity.CrawlRecord;
import com.example.localrestservice.entity.ProductSpec;
import com.example.localrestservice.repository.CrawlRecordRepository;
import com.example.localrestservice.repository.ProductSpecRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class CollectService {

    private static final Logger logger = LoggerFactory.getLogger(CollectService.class);

    private final ProductSpecRepository productSpecRepository;
    private final CrawlRecordRepository crawlRecordRepository;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Autowired
    public CollectService(ProductSpecRepository productSpecRepository,
                         CrawlRecordRepository crawlRecordRepository) {
        this.productSpecRepository = productSpecRepository;
        this.crawlRecordRepository = crawlRecordRepository;
    }

    public Map<String, Object> collectHuaweiData() {
        return runCollectScript("run_huawei_collect.py", "华为");
    }

    public Map<String, Object> collectH3CData() {
        return runCollectScript("run_h3c_collect.py", "华三");
    }

    public Map<String, Object> collectRuijieData() {
        return runCollectScript("run_ruijie_collect.py", "锐捷");
    }

    private Map<String, Object> runCollectScript(String scriptName, String brand) {
        Map<String, Object> result = new HashMap<>();
        result.put("success", false);
        result.put("message", "");
        result.put("products_saved", 0);
        result.put("records_created", 0);

        try {
            String projectDir = System.getProperty("user.dir");
            Path scriptPath = Paths.get(projectDir, "collect", scriptName);
            
            logger.info("开始执行{}数据采集脚本: {}", brand, scriptPath);
            
            ProcessBuilder pb = new ProcessBuilder("python", scriptPath.toString());
            pb.redirectErrorStream(true);
            Process process = pb.start();
            
            BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8)
            );
            
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }
            
            int exitCode = process.waitFor();
            logger.info("脚本执行完成，退出码: {}", exitCode);
            
            if (exitCode != 0) {
                logger.error("{}脚本执行失败，输出: {}", brand, output);
                result.put("message", "脚本执行失败，退出码: " + exitCode);
                return result;
            }
            
            String jsonOutput = output.toString();
            logger.debug("脚本输出: {}", jsonOutput.substring(0, Math.min(500, jsonOutput.length())));
            
            JsonNode root = objectMapper.readTree(jsonOutput);
            
            if (!root.path("success").asBoolean()) {
                result.put("message", "脚本返回失败: " + root.path("error").asText());
                return result;
            }
            
            int totalProducts = root.path("total_products").asInt();
            logger.info("{}采集到 {} 个产品", brand, totalProducts);
            
            ArrayNode productsNode = (ArrayNode) root.path("products");
            int savedCount = 0;
            int recordCount = 0;
            
            for (JsonNode productNode : productsNode) {
                String productCode = productNode.path("product_code").asText();
                
                if (!isValidProductCode(productCode)) {
                    logger.debug("跳过无效产品型号: {}", productCode);
                    continue;
                }
                
                try {
                    ProductSpec productSpec = saveOrUpdateProductSpec(productNode);
                    savedCount++;
                    
                    CrawlRecord record = createCrawlRecord(productNode, 200, null);
                    crawlRecordRepository.save(record);
                    recordCount++;
                    
                } catch (Exception e) {
                    logger.error("保存产品 {} 失败: {}", productCode, e.getMessage());
                    
                    CrawlRecord errorRecord = createCrawlRecord(
                        productNode, 
                        500, 
                        "保存失败: " + e.getMessage()
                    );
                    crawlRecordRepository.save(errorRecord);
                }
            }
            
            result.put("success", true);
            result.put("message", "数据采集成功");
            result.put("products_saved", savedCount);
            result.put("records_created", recordCount);
            result.put("total_collected", totalProducts);
            
            logger.info("{}数据采集完成: 保存 {} 个产品, 创建 {} 条记录", brand, savedCount, recordCount);
            
        } catch (Exception e) {
            logger.error("{}数据采集失败", brand, e);
            result.put("message", "执行失败: " + e.getMessage());
        }
        
        return result;
    }

    private boolean isValidProductCode(String productCode) {
        if (productCode == null || productCode.isEmpty()) {
            return false;
        }
        
        if (productCode.length() > 50) {
            return false;
        }
        
        if (productCode.matches("\\d{30,}")) {
            return false;
        }
        
        return true;
    }

    private ProductSpec saveOrUpdateProductSpec(JsonNode productNode) {
        String productCode = productNode.path("product_code").asText();
        
        ProductSpec productSpec = productSpecRepository.findByProductCode(productCode)
            .orElse(new ProductSpec(productCode));
        
        productSpec.setProductName(productNode.path("product_name").asText());
        productSpec.setProductUrl(productNode.path("product_url").asText());
        productSpec.setSource(productNode.path("source").asText());
        productSpec.setCategory(productNode.path("category").asText());
        productSpec.setSeries(productNode.path("series").asText());
        productSpec.setStatus(productNode.path("status").asText("在售"));
        productSpec.setDescription(productNode.path("description").asText());
        productSpec.setThumbnailUrl(productNode.path("thumbnail_url").asText());
        
        if (productNode.has("specs")) {
            try {
                productSpec.setSpecsJson(objectMapper.writeValueAsString(productNode.path("specs")));
            } catch (Exception e) {
                logger.warn("序列化 specs 失败", e);
            }
        }
        
        if (productNode.has("links")) {
            try {
                productSpec.setLinksJson(objectMapper.writeValueAsString(productNode.path("links")));
            } catch (Exception e) {
                logger.warn("序列化 links 失败", e);
            }
        }
        
        return productSpecRepository.save(productSpec);
    }

    private CrawlRecord createCrawlRecord(JsonNode productNode, Integer httpStatus, String errorMessage) {
        CrawlRecord record = new CrawlRecord();
        record.setProductCode(productNode.path("product_code").asText());
        record.setCrawlUrl(productNode.path("product_url").asText());
        record.setSource(productNode.path("source").asText());
        record.setHttpStatus(httpStatus);
        record.setCrawledAt(LocalDateTime.now());
        
        if (errorMessage != null) {
            record.setStatus("FAILED");
            record.setErrorMessage(errorMessage);
        } else {
            record.setStatus("SUCCESS");
        }
        
        return record;
    }

    public List<Map<String, Object>> getAllProducts() {
        List<Map<String, Object>> result = new ArrayList<>();
        List<ProductSpec> products = productSpecRepository.findAll();
        
        for (ProductSpec product : products) {
            Map<String, Object> item = new HashMap<>();
            item.put("id", product.getId());
            item.put("product_code", product.getProductCode());
            item.put("product_name", product.getProductName());
            item.put("source", product.getSource());
            item.put("category", product.getCategory());
            item.put("series", product.getSeries());
            item.put("status", product.getStatus());
            item.put("created_at", product.getCreatedAt());
            item.put("updated_at", product.getUpdatedAt());
            
            // 添加 specs 字段用于列表预览
            if (product.getSpecsJson() != null && !product.getSpecsJson().isEmpty()) {
                try {
                    Map<String, Object> specs = objectMapper.readValue(product.getSpecsJson(), Map.class);
                    item.put("specs", specs);
                } catch (Exception e) {
                    logger.warn("解析 specsJson 失败", e);
                    item.put("specs", new HashMap<>());
                }
            } else {
                item.put("specs", new HashMap<>());
            }
            
            result.add(item);
        }
        
        return result;
    }

    public Map<String, Object> getProductStats() {
        Map<String, Object> stats = new HashMap<>();
        
        List<ProductSpec> allProducts = productSpecRepository.findAll();
        
        Map<String, Integer> bySource = new HashMap<>();
        Map<String, Integer> byCategory = new HashMap<>();
        
        for (ProductSpec product : allProducts) {
            String source = product.getSource();
            String category = product.getCategory();
            
            bySource.put(source, bySource.getOrDefault(source, 0) + 1);
            byCategory.put(category, byCategory.getOrDefault(category, 0) + 1);
        }
        
        stats.put("total_products", allProducts.size());
        stats.put("by_source", bySource);
        stats.put("by_category", byCategory);
        
        return stats;
    }

    public Map<String, Object> getProductById(Long id) {
        ProductSpec product = productSpecRepository.findById(id).orElse(null);
        if (product == null) {
            return null;
        }

        Map<String, Object> result = new HashMap<>();
        result.put("id", product.getId());
        result.put("product_code", product.getProductCode());
        result.put("product_name", product.getProductName());
        result.put("source", product.getSource());
        result.put("category", product.getCategory());
        result.put("series", product.getSeries());
        result.put("status", product.getStatus());
        result.put("description", product.getDescription());
        result.put("product_url", product.getProductUrl());
        result.put("thumbnail_url", product.getThumbnailUrl());
        result.put("created_at", product.getCreatedAt());
        result.put("updated_at", product.getUpdatedAt());

        // 解析 specsJson
        if (product.getSpecsJson() != null && !product.getSpecsJson().isEmpty()) {
            try {
                result.put("specs", objectMapper.readValue(product.getSpecsJson(), Map.class));
            } catch (Exception e) {
                logger.warn("解析 specsJson 失败", e);
                result.put("specs", new HashMap<>());
            }
        } else {
            result.put("specs", new HashMap<>());
        }

        // 解析 linksJson
        if (product.getLinksJson() != null && !product.getLinksJson().isEmpty()) {
            try {
                result.put("links", objectMapper.readValue(product.getLinksJson(), List.class));
            } catch (Exception e) {
                logger.warn("解析 linksJson 失败", e);
                result.put("links", new ArrayList<>());
            }
        } else {
            result.put("links", new ArrayList<>());
        }

        return result;
    }

    public void clearAllData() {
        crawlRecordRepository.deleteAll();
        productSpecRepository.deleteAll();
        logger.info("已清除所有采集数据");
    }
}
