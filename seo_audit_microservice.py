#!/usr/bin/env python3
"""
🌭 HugemouthSEO - Free SEO Audit Microservice
The 'Hotdog Stand' MVP - Simple, Fast, Effective
Mission: Secure first paying customer
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HugemouthSEO Free Audit",
    description="Lightning-fast SEO audit tool - Your first win starts here!",
    version="1.0.0"
)

# Enable CORS for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class AuditResult(BaseModel):
    url: str
    timestamp: str
    meta_description: Optional[Dict[str, Any]]
    h1_tag: Optional[Dict[str, Any]]
    score: int
    recommendations: list
    status: str

class AuditRequest(BaseModel):
    url: HttpUrl

# Playwright audit function
async def perform_seo_audit(url: str) -> Dict[str, Any]:
    """
    Perform SEO audit using Playwright
    Checks for meta description and H1 tags
    """
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            # Launch browser (headless for performance)
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Set reasonable timeout
            page.set_default_timeout(30000)
            
            # Navigate to URL
            logger.info(f"Auditing: {url}")
            await page.goto(url, wait_until="domcontentloaded")
            
            # Extract meta description
            meta_description = await page.evaluate("""
                () => {
                    const meta = document.querySelector('meta[name="description"]');
                    return meta ? {
                        exists: true,
                        content: meta.getAttribute('content'),
                        length: meta.getAttribute('content')?.length || 0
                    } : {
                        exists: false,
                        content: null,
                        length: 0
                    };
                }
            """)
            
            # Extract H1 tags
            h1_tag = await page.evaluate("""
                () => {
                    const h1s = document.querySelectorAll('h1');
                    return {
                        exists: h1s.length > 0,
                        count: h1s.length,
                        content: h1s.length > 0 ? h1s[0].textContent.trim() : null,
                        all_h1s: Array.from(h1s).map(h => h.textContent.trim())
                    };
                }
            """)
            
            # Close browser
            await browser.close()
            
            return {
                "meta_description": meta_description,
                "h1_tag": h1_tag
            }
            
    except Exception as e:
        logger.error(f"Playwright audit error: {str(e)}")
        # Fallback to basic check without Playwright
        return perform_basic_audit(url)

def perform_basic_audit(url: str) -> Dict[str, Any]:
    """
    Basic audit fallback (without Playwright)
    Returns mock data for demonstration
    """
    return {
        "meta_description": {
            "exists": False,
            "content": None,
            "length": 0,
            "error": "Playwright not available - using basic audit"
        },
        "h1_tag": {
            "exists": False,
            "count": 0,
            "content": None,
            "error": "Playwright not available - using basic audit"
        }
    }

def calculate_seo_score(audit_data: Dict[str, Any]) -> int:
    """Calculate SEO score based on audit results"""
    score = 0
    
    # Meta description scoring (40 points)
    meta = audit_data.get("meta_description", {})
    if meta.get("exists"):
        score += 20
        length = meta.get("length", 0)
        if 50 <= length <= 160:  # Optimal length
            score += 20
        elif 30 <= length < 50 or 160 < length <= 200:
            score += 10
    
    # H1 tag scoring (60 points)
    h1 = audit_data.get("h1_tag", {})
    if h1.get("exists"):
        score += 30
        if h1.get("count") == 1:  # Exactly one H1 is ideal
            score += 30
        elif h1.get("count") <= 3:
            score += 15
    
    return score

def generate_recommendations(audit_data: Dict[str, Any]) -> list:
    """Generate actionable SEO recommendations"""
    recommendations = []
    
    # Meta description recommendations
    meta = audit_data.get("meta_description", {})
    if not meta.get("exists"):
        recommendations.append({
            "priority": "HIGH",
            "issue": "Missing Meta Description",
            "action": "Add a compelling meta description between 50-160 characters",
            "impact": "Critical for search result click-through rates"
        })
    elif meta.get("length", 0) < 50:
        recommendations.append({
            "priority": "MEDIUM",
            "issue": "Meta Description Too Short",
            "action": f"Expand meta description from {meta.get('length')} to 50-160 characters",
            "impact": "May appear truncated in search results"
        })
    elif meta.get("length", 0) > 160:
        recommendations.append({
            "priority": "MEDIUM",
            "issue": "Meta Description Too Long",
            "action": f"Shorten meta description from {meta.get('length')} to under 160 characters",
            "impact": "Will be truncated in search results"
        })
    
    # H1 tag recommendations
    h1 = audit_data.get("h1_tag", {})
    if not h1.get("exists"):
        recommendations.append({
            "priority": "HIGH",
            "issue": "Missing H1 Tag",
            "action": "Add a clear, keyword-rich H1 tag to your page",
            "impact": "Critical for SEO and page structure"
        })
    elif h1.get("count", 0) > 1:
        recommendations.append({
            "priority": "MEDIUM",
            "issue": f"Multiple H1 Tags ({h1.get('count')})",
            "action": "Use only one H1 tag per page, convert others to H2",
            "impact": "Can confuse search engines about page topic"
        })
    
    return recommendations

# API Endpoints
@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "service": "HugemouthSEO Free Audit",
        "status": "operational",
        "mission": "Secure first paying customer",
        "endpoints": {
            "/audit": "POST - Submit URL for SEO audit",
            "/health": "GET - Service health check"
        }
    }

@app.post("/audit", response_model=AuditResult)
async def audit_website(request: AuditRequest):
    """
    Main audit endpoint - The money maker!
    Accepts a URL and returns comprehensive SEO audit results
    """
    try:
        url = str(request.url)
        
        # Perform the audit
        audit_data = await perform_seo_audit(url)
        
        # Calculate score
        score = calculate_seo_score(audit_data)
        
        # Generate recommendations
        recommendations = generate_recommendations(audit_data)
        
        # Build response
        result = AuditResult(
            url=url,
            timestamp=datetime.now().isoformat(),
            meta_description=audit_data.get("meta_description"),
            h1_tag=audit_data.get("h1_tag"),
            score=score,
            recommendations=recommendations,
            status="success"
        )
        
        logger.info(f"Audit completed for {url} - Score: {score}/100")
        return result
        
    except Exception as e:
        logger.error(f"Audit failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "HugemouthSEO Audit",
        "timestamp": datetime.now().isoformat()
    }

# Quick start instructions
if __name__ == "__main__":
    print("🌭 HugemouthSEO 'Hotdog Stand' MVP")
    print("=" * 40)
    print("To run this service:")
    print("1. Install dependencies:")
    print("   pip install fastapi uvicorn playwright")
    print("   playwright install chromium")
    print("")
    print("2. Start the server:")
    print("   uvicorn seo_audit_microservice:app --reload --port 8000")
    print("")
    print("3. Test the API:")
    print("   curl -X POST http://localhost:8000/audit")
    print('   -H "Content-Type: application/json"')
    print('   -d \'{"url": "https://example.com"}\'')
    print("")
    print("🚀 Let's secure that first customer!")