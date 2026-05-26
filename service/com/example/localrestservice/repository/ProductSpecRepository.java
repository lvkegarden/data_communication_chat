package com.example.localrestservice.repository;

import com.example.localrestservice.entity.ProductSpec;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ProductSpecRepository extends JpaRepository<ProductSpec, Long> {

    Optional<ProductSpec> findByProductCode(String productCode);

    List<ProductSpec> findBySource(String source);

    List<ProductSpec> findByCategory(String category);

    List<ProductSpec> findBySeries(String series);

    boolean existsByProductCode(String productCode);
}
