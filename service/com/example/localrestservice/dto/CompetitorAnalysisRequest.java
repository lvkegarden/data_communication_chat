package com.example.localrestservice.dto;

import java.util.List;

public class CompetitorAnalysisRequest {
    
    private String targetProductCode;
    
    private String targetProductName;
    
    private String targetSeries;
    
    private String targetDescription;
    
    private String targetSpecsJson;
    
    private List<CompetitorInfo> competitors;

    public CompetitorAnalysisRequest() {
    }

    public String getTargetProductCode() {
        return targetProductCode;
    }

    public void setTargetProductCode(String targetProductCode) {
        this.targetProductCode = targetProductCode;
    }

    public String getTargetProductName() {
        return targetProductName;
    }

    public void setTargetProductName(String targetProductName) {
        this.targetProductName = targetProductName;
    }

    public String getTargetSeries() {
        return targetSeries;
    }

    public void setTargetSeries(String targetSeries) {
        this.targetSeries = targetSeries;
    }

    public String getTargetDescription() {
        return targetDescription;
    }

    public void setTargetDescription(String targetDescription) {
        this.targetDescription = targetDescription;
    }

    public String getTargetSpecsJson() {
        return targetSpecsJson;
    }

    public void setTargetSpecsJson(String targetSpecsJson) {
        this.targetSpecsJson = targetSpecsJson;
    }

    public List<CompetitorInfo> getCompetitors() {
        return competitors;
    }

    public void setCompetitors(List<CompetitorInfo> competitors) {
        this.competitors = competitors;
    }

    public static class CompetitorInfo {
        private String productCode;
        private String productName;
        private String series;
        private String description;
        private String specsJson;
        private String source;

        public CompetitorInfo() {
        }

        public String getProductCode() {
            return productCode;
        }

        public void setProductCode(String productCode) {
            this.productCode = productCode;
        }

        public String getProductName() {
            return productName;
        }

        public void setProductName(String productName) {
            this.productName = productName;
        }

        public String getSeries() {
            return series;
        }

        public void setSeries(String series) {
            this.series = series;
        }

        public String getDescription() {
            return description;
        }

        public void setDescription(String description) {
            this.description = description;
        }

        public String getSpecsJson() {
            return specsJson;
        }

        public void setSpecsJson(String specsJson) {
            this.specsJson = specsJson;
        }

        public String getSource() {
            return source;
        }

        public void setSource(String source) {
            this.source = source;
        }
    }
}
