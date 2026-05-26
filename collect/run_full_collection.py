import sys
import json
from datetime import datetime
import io

from huawei_scraper import HuaweiScraper
from h3c_scraper import H3CScraper
from ruijie_scraper import RuijieScraper
from scraper_logger import log, clear_log


def run_single_brand(brand_name, scraper_class):
    try:
        log(f"\n{'='*60}")
        log(f"[INFO] 开始采集 {brand_name} 数据...")
        log(f"{'='*60}")
        
        scraper = scraper_class()
        result = scraper.scrape_all()
        
        products_data = [
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
        
        output = {
            "success": True,
            "brand": brand_name,
            "source": result.source,
            "total_products": len(result.products),
            "success_categories": result.success_count,
            "failed_categories": result.failed_count,
            "started_at": result.started_at.isoformat() if result.started_at else None,
            "completed_at": result.completed_at.isoformat() if result.completed_at else None,
            "products": products_data
        }
        
        log(f"[OK] {brand_name} 采集完成: {len(result.products)} 个产品")
        return output
        
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        log(f"[ERROR] {brand_name} 采集失败: {e}")
        log(error_msg)
        return {
            "success": False,
            "brand": brand_name,
            "error": str(e),
            "traceback": error_msg
        }


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    clear_log()
    log(f"全量采集任务开始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    overall_start = datetime.now()
    overall_results = {
        "task": "full_collection",
        "started_at": overall_start.isoformat(),
        "brands": []
    }
    
    brands = [
        ("华为", HuaweiScraper),
        ("华三", H3CScraper),
        ("锐捷", RuijieScraper),
    ]
    
    for brand_name, scraper_class in brands:
        result = run_single_brand(brand_name, scraper_class)
        overall_results["brands"].append(result)
    
    overall_end = datetime.now()
    overall_results["completed_at"] = overall_end.isoformat()
    overall_results["duration_seconds"] = (overall_end - overall_start).total_seconds()
    
    total_products = sum(
        b.get("total_products", 0) 
        for b in overall_results["brands"] 
        if b.get("success")
    )
    success_brands = sum(1 for b in overall_results["brands"] if b.get("success"))
    failed_brands = sum(1 for b in overall_results["brands"] if not b.get("success"))
    
    overall_results["summary"] = {
        "total_products": total_products,
        "success_brands": success_brands,
        "failed_brands": failed_brands,
        "total_brands": len(brands)
    }
    
    log(f"\n{'='*60}")
    log(f"[INFO] 全量采集任务完成!")
    log(f"{'='*60}")
    log(f"总产品数: {total_products}")
    log(f"成功品牌: {success_brands}/{len(brands)}")
    log(f"耗时: {overall_results['duration_seconds']:.2f}秒")
    
    for brand in overall_results["brands"]:
        brand_name = brand.get("brand", "Unknown")
        if brand.get("success"):
            log(f"  {brand_name}: {brand['total_products']} 个产品")
        else:
            log(f"  {brand_name}: 失败 - {brand.get('error', 'Unknown error')}")
    
    print(json.dumps(overall_results, ensure_ascii=False, indent=2))
    return 0 if success_brands == len(brands) else 1


if __name__ == "__main__":
    sys.exit(main())
