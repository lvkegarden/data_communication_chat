package com.example.localrestservice.repository;

import com.example.localrestservice.entity.CrawlRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface CrawlRecordRepository extends JpaRepository<CrawlRecord, Long> {

    List<CrawlRecord> findByProductCodeOrderByCrawledAtDesc(String productCode);

    List<CrawlRecord> findByStatus(String status);

    List<CrawlRecord> findBySource(String source);

    List<CrawlRecord> findByCrawledAtAfter(LocalDateTime time);

    List<CrawlRecord> findByProductCodeAndStatus(String productCode, String status);
}
