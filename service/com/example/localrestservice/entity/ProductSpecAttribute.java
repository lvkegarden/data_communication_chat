package com.example.localrestservice.entity;

import jakarta.persistence.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "product_spec_attributes", indexes = {
    @Index(name = "idx_product_id", columnList = "product_id"),
    @Index(name = "idx_attribute_name", columnList = "attribute_name"),
    @Index(name = "idx_category", columnList = "category"),
    @Index(name = "idx_value_numeric", columnList = "value_numeric")
})
public class ProductSpecAttribute {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "product_id", nullable = false)
    private Long productId;

    @Column(name = "attribute_name", nullable = false, length = 100)
    private String attributeName;

    @Column(name = "attribute_value", length = 500)
    private String attributeValue;

    @Column(name = "value_numeric")
    private Double valueNumeric;

    @Column(name = "unit", length = 50)
    private String unit;

    @Column(name = "category", length = 100)
    private String category;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    public ProductSpecAttribute() {
    }

    public ProductSpecAttribute(Long productId, String attributeName, String attributeValue) {
        this.productId = productId;
        this.attributeName = attributeName;
        this.attributeValue = attributeValue;
    }

    public static ProductSpecAttribute of(Long productId, String name, String value) {
        ProductSpecAttribute attr = new ProductSpecAttribute(productId, name, value);
        
        String numericValue = extractNumeric(value);
        if (numericValue != null) {
            attr.setValueNumeric(Double.parseDouble(numericValue));
        }
        
        String unit = extractUnit(value);
        if (unit != null) {
            attr.setUnit(unit);
        }
        
        attr.setCategory(categorizeAttribute(name));
        
        return attr;
    }

    private static String extractNumeric(String value) {
        if (value == null) return null;
        
        java.util.regex.Matcher matcher = java.util.regex.Pattern.compile("([0-9]+\\.?[0-9]*)").matcher(value);
        if (matcher.find()) {
            return matcher.group(1);
        }
        return null;
    }

    private static String extractUnit(String value) {
        if (value == null) return null;
        
        String[] units = {"Tbps", "Gbps", "Mbps", "kg", "mm", "℃", "°C", "W", "个", "台"};
        for (String unit : units) {
            if (value.contains(unit)) {
                return unit;
            }
        }
        return null;
    }

    private static String categorizeAttribute(String name) {
        if (name == null) return "其他";
        
        if (name.contains("容量") || name.contains("性能") || name.contains("速率")) {
            return "性能";
        }
        if (name.contains("端口") || name.contains("接口")) {
            return "端口";
        }
        if (name.contains("电源") || name.contains("功耗")) {
            return "电源";
        }
        if (name.contains("尺寸") || name.contains("重量")) {
            return "物理";
        }
        if (name.contains("温度") || name.contains("湿度")) {
            return "环境";
        }
        if (name.contains("定位") || name.contains("场景")) {
            return "定位";
        }
        return "其他";
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getProductId() {
        return productId;
    }

    public void setProductId(Long productId) {
        this.productId = productId;
    }

    public String getAttributeName() {
        return attributeName;
    }

    public void setAttributeName(String attributeName) {
        this.attributeName = attributeName;
    }

    public String getAttributeValue() {
        return attributeValue;
    }

    public void setAttributeValue(String attributeValue) {
        this.attributeValue = attributeValue;
    }

    public Double getValueNumeric() {
        return valueNumeric;
    }

    public void setValueNumeric(Double valueNumeric) {
        this.valueNumeric = valueNumeric;
    }

    public String getUnit() {
        return unit;
    }

    public void setUnit(String unit) {
        this.unit = unit;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
