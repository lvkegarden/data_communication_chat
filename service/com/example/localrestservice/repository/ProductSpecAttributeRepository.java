package com.example.localrestservice.repository;

import com.example.localrestservice.entity.ProductSpecAttribute;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ProductSpecAttributeRepository extends JpaRepository<ProductSpecAttribute, Long> {

    List<ProductSpecAttribute> findByProductId(Long productId);

    List<ProductSpecAttribute> findByProductIdAndCategory(Long productId, String category);

    List<ProductSpecAttribute> findByAttributeName(String attributeName);

    @Query("SELECT a FROM ProductSpecAttribute a WHERE a.category = :category AND a.attributeName = :attributeName AND a.valueNumeric IS NOT NULL")
    List<ProductSpecAttribute> findNumericAttributesByCategoryAndName(@Param("category") String category,
                                                                       @Param("attributeName") String attributeName);
}
