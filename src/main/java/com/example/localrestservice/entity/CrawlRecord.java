package com.example.localrestservice.entity;

import jakarta.persistence.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "crawl_records", indexes = {
    @Index(name = "idx_product_code", columnList = "product_code"),
    @Index(name = "idx_crawled_at", columnList = "crawled_at")
})
public class CrawlRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "product_code", nullable = false, length = 100)
    private String productCode;

    @Column(name = "crawl_url", length = 500)
    private String crawlUrl;

    @Column(name = "source", length = 100)
    private String source;

    @Column(name = "status", length = 50)
    private String status;

    @Column(name = "http_status")
    private Integer httpStatus;

    @Column(name = "response_size")
    private Long responseSize;

    @Column(name = "has_changes")
    private Boolean hasChanges;

    @Column(name = "error_message", columnDefinition = "TEXT")
    private String errorMessage;

    @Column(name = "crawled_at")
    private LocalDateTime crawledAt;

    @PrePersist
    protected void onCreate() {
        if (crawledAt == null) {
            crawledAt = LocalDateTime.now();
        }
    }

    public CrawlRecord() {
    }

    public CrawlRecord(String productCode, String status) {
        this.productCode = productCode;
        this.status = status;
    }

    public static CrawlRecord success(String productCode, String crawlUrl, String source, Long responseSize) {
        CrawlRecord record = new CrawlRecord();
        record.setProductCode(productCode);
        record.setCrawlUrl(crawlUrl);
        record.setSource(source);
        record.setStatus("SUCCESS");
        record.setHttpStatus(200);
        record.setResponseSize(responseSize);
        return record;
    }

    public static CrawlRecord failure(String productCode, String crawlUrl, String source, Integer httpStatus, String errorMessage) {
        CrawlRecord record = new CrawlRecord();
        record.setProductCode(productCode);
        record.setCrawlUrl(crawlUrl);
        record.setSource(source);
        record.setStatus("FAILED");
        record.setHttpStatus(httpStatus);
        record.setErrorMessage(errorMessage);
        return record;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getProductCode() {
        return productCode;
    }

    public void setProductCode(String productCode) {
        this.productCode = productCode;
    }

    public String getCrawlUrl() {
        return crawlUrl;
    }

    public void setCrawlUrl(String crawlUrl) {
        this.crawlUrl = crawlUrl;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Integer getHttpStatus() {
        return httpStatus;
    }

    public void setHttpStatus(Integer httpStatus) {
        this.httpStatus = httpStatus;
    }

    public Long getResponseSize() {
        return responseSize;
    }

    public void setResponseSize(Long responseSize) {
        this.responseSize = responseSize;
    }

    public Boolean getHasChanges() {
        return hasChanges;
    }

    public void setHasChanges(Boolean hasChanges) {
        this.hasChanges = hasChanges;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public LocalDateTime getCrawledAt() {
        return crawledAt;
    }

    public void setCrawledAt(LocalDateTime crawledAt) {
        this.crawledAt = crawledAt;
    }
}
