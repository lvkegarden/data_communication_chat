import requests
import os
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

JAVA_API_URL = os.getenv("JAVA_API_URL", "http://localhost:8080/api/product-data")


class ProductDataFetcher:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or JAVA_API_URL
        logger.info("ProductDataFetcher initialized with base_url: %s", self.base_url)

    def get_product_by_code(self, product_code: str) -> Optional[Dict[str, Any]]:
        logger.info("Fetching product by code: %s", product_code)
        try:
            url = f"{self.base_url}/detail/{product_code}"
            logger.info("Requesting URL: %s", url)
            response = requests.get(url)
            logger.info("Response status: %d", response.status_code)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    product = data.get("product")
                    logger.info("Product fetched successfully: %s", product.get("product_name", "unknown"))
                    return product
                else:
                    logger.warning("Product fetch returned non-success: %s", data.get("error", "unknown error"))
            else:
                logger.warning("Request failed with status: %d", response.status_code)
            
            return None
        except Exception as e:
            logger.error("Error fetching product by code %s: %s", product_code, str(e), exc_info=True)
            return None

    def search_products(self, keyword: str = None, category: str = None, source: str = None) -> List[Dict[str, Any]]:
        logger.info("Searching products - keyword: %s, category: %s, source: %s", keyword, category, source)
        try:
            params = {}
            if keyword:
                params["keyword"] = keyword
            if category:
                params["category"] = category
            if source:
                params["source"] = source
            
            url = f"{self.base_url}/search"
            logger.info("Requesting URL: %s with params: %s", url, params)
            response = requests.get(url, params=params)
            logger.info("Response status: %d", response.status_code)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    products = data.get("products", [])
                    logger.info("Search returned %d products", len(products))
                    return products
                else:
                    logger.warning("Search returned non-success: %s", data.get("error", "unknown error"))
            else:
                logger.warning("Request failed with status: %d", response.status_code)
            
            return []
        except Exception as e:
            logger.error("Error searching products: %s", str(e), exc_info=True)
            return []

    def get_competitors(self, product_code: str, limit: int = 3) -> List[Dict[str, Any]]:
        logger.info("Fetching competitors for product: %s (limit: %d)", product_code, limit)
        try:
            url = f"{self.base_url}/competitors/{product_code}"
            logger.info("Requesting URL: %s", url)
            response = requests.get(url, params={"limit": limit})
            logger.info("Response status: %d", response.status_code)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    competitors = data.get("competitors", [])
                    logger.info("Competitors fetched: %d", len(competitors))
                    return competitors
                else:
                    logger.warning("Competitors fetch returned non-success: %s", data.get("error", "unknown error"))
            else:
                logger.warning("Request failed with status: %d", response.status_code)
            
            return []
        except Exception as e:
            logger.error("Error fetching competitors for %s: %s", product_code, str(e), exc_info=True)
            return []

    def get_all_products_summary(self) -> List[Dict[str, Any]]:
        logger.info("Fetching all products summary")
        try:
            url = f"{self.base_url}/summary"
            logger.info("Requesting URL: %s", url)
            response = requests.get(url)
            logger.info("Response status: %d", response.status_code)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    products = data.get("products", [])
                    logger.info("Products summary fetched: %d products", len(products))
                    return products
                else:
                    logger.warning("Products summary returned non-success: %s", data.get("error", "unknown error"))
            else:
                logger.warning("Request failed with status: %d", response.status_code)
            
            return []
        except Exception as e:
            logger.error("Error fetching products summary: %s", str(e), exc_info=True)
            return []

    def format_product_for_prompt(self, product: Dict[str, Any]) -> str:
        logger.info("Formatting product for prompt: %s", product.get("product_code", "unknown"))
        lines = []
        if product.get("product_name"):
            lines.append(f"产品名称：{product['product_name']}")
        if product.get("product_code"):
            lines.append(f"产品型号：{product['product_code']}")
        if product.get("series"):
            lines.append(f"产品系列：{product['series']}")
        if product.get("category"):
            lines.append(f"产品类别：{product['category']}")
        if product.get("source"):
            lines.append(f"产品来源：{product['source']}")
        if product.get("status"):
            lines.append(f"产品状态：{product['status']}")
        if product.get("description"):
            lines.append(f"产品描述：{product['description']}")
        if product.get("specs_json"):
            lines.append(f"技术规格：{product['specs_json']}")
        return "\n".join(lines)

    def format_competitors_for_prompt(self, competitors: List[Dict[str, Any]]) -> str:
        logger.info("Formatting %d competitors for prompt", len(competitors))
        if not competitors:
            logger.info("No competitors to format, returning placeholder")
            return "无具体竞品信息，请根据行业知识进行分析。"
        
        lines = []
        for i, comp in enumerate(competitors, 1):
            lines.append(f"【竞品{i}】")
            lines.append(self.format_product_for_prompt(comp))
            lines.append("")
        return "\n".join(lines)
