import sys
import json
from datetime import datetime
import io

from huawei_scraper import HuaweiScraper


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    try:
        scraper = HuaweiScraper()
        result = scraper.scrape_all()
        
        output = {
            "success": True,
            "source": result.source,
            "total_products": len(result.products),
            "success_categories": result.success_count,
            "failed_categories": result.failed_count,
            "started_at": result.started_at.isoformat() if result.started_at else None,
            "completed_at": result.completed_at.isoformat() if result.completed_at else None,
            "products": [
                {
                    "product_code": p.product_code,
                    "product_name": p.product_name,
                    "product_url": p.product_url,
                    "source": p.source,
                    "category": p.category,
                    "series": p.series,
                    "status": p.status,
                    "description": p.description,
                    "thumbnail_url": p.thumbnail_url,
                    "specs": p.specs,
                    "links": p.links
                }
                for p in result.products
            ]
        }
        
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        error_output = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_output, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
