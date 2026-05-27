from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))
from config_loader import get_scraper_headers

from scraper_logger import log


@dataclass
class ProductInfo:
    product_code: str
    product_name: str
    product_url: str
    source: str
    category: str
    series: str = ""
    status: str = "在售"
    description: str = ""
    thumbnail_url: str = ""
    specs: Dict[str, str] = field(default_factory=dict)
    links: List[Dict[str, str]] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'product_code': self.product_code,
            'product_name': self.product_name,
            'product_url': self.product_url,
            'source': self.source,
            'category': self.category,
            'series': self.series,
            'status': self.status,
            'description': self.description,
            'thumbnail_url': self.thumbnail_url,
            'specs': self.specs,
            'links': self.links
        }


@dataclass
class ScrapeResult:
    source: str
    category: str
    products: List[ProductInfo]
    total_count: int
    success_count: int
    failed_count: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    def duration(self) -> Optional[float]:
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class BaseScraper(ABC):
    
    def __init__(self, source: str, base_url: str):
        self.source = source
        self.base_url = base_url
        self.headers = get_scraper_headers()
    
    @abstractmethod
    def get_category_urls(self) -> Dict[str, str]:
        pass
    
    @abstractmethod
    def scrape_category(self, category: str, url: str) -> List[ProductInfo]:
        pass
    
    def scrape_all(self) -> ScrapeResult:
        result = ScrapeResult(
            source=self.source,
            category="all",
            products=[],
            total_count=0,
            success_count=0,
            failed_count=0,
            started_at=datetime.now()
        )
        
        category_urls = self.get_category_urls()
        
        for category, url in category_urls.items():
            try:
                products = self.scrape_category(category, url)
                result.products.extend(products)
                result.success_count += 1
                log(f"[OK] {self.source} - {category}: 爬取 {len(products)} 个产品")
            except Exception as e:
                result.failed_count += 1
                log(f"[FAIL] {self.source} - {category}: {e}")
        
        result.total_count = result.success_count + result.failed_count
        result.completed_at = datetime.now()
        
        return result
    
    def create_product_info(
        self,
        product_code: str,
        product_name: str,
        product_url: str,
        category: str,
        **kwargs
    ) -> ProductInfo:
        return ProductInfo(
            product_code=product_code,
            product_name=product_name,
            product_url=product_url,
            source=self.source,
            category=category,
            **kwargs
        )
