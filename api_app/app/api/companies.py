# app/api/companies.py
import json

from fastapi import APIRouter, Query, Depends, HTTPException
from app.services.company_search import CompanySearchService
from app.services.hotKeyword_search import hotKeywordService
from app.models.company import CompanyList
from app.models.hotkeyword import KeywordList,KeywordListWithNews, KeywordNews
from app.services.news_summary import NewsSummaryService
from app.services.news_link import NewsLinkService
from app.services.dart_report import DartReportService
from app.models.company import CompanyList, CompanyResult, DartReportResponse
from app.models.hotkeyword import KeywordList
from app.db.mongo import get_dart_collection
from app.database import get_database
from hdfs import InsecureClient
from bson import ObjectId
from datetime import datetime

companies_router = APIRouter()

@companies_router.get("/search", response_model=CompanyList)
async def search_companies(
    query: str = Query(..., min_length=1),
    search_type: str = Query("prefix", regex="^(prefix|substring)$"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),  # 한 페이지당 결과 수
    db = Depends(get_database)
):
    company_search_service = CompanySearchService(db)
    try:
        results = await company_search_service.search_companies(query, search_type, page, size)
        return CompanyList(**results)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@companies_router.get("/hotkeyword", response_model=KeywordList)
async def company_hotkeyword(
    corp_name: str ,
):
    hotkeyword_service = hotKeywordService(corp_name)
    try:
        results = await hotkeyword_service.fetch_hotkeyword()
        return KeywordList(**results)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@companies_router.get("/hotkeyword_with_news", response_model=KeywordListWithNews)
async def company_hotkeyword(
    corp_name: str ,
):
    hotkeyword_service = hotKeywordService(corp_name)
    try:
        results = await hotkeyword_service.fetch_hotkeyword_with_news()
        keywords = {}
        for word, news_list in results.items():
            keyword = []
            for news in news_list:
                keyword.append(KeywordNews(
                    title=news['title'],
                    pubDate= news['pubDate'],
                    link=news['link']
                ))
            keywords[word] = keyword
        res = KeywordListWithNews(
            corp_name= corp_name,
            keywords = keywords
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
# @companies_router.get("/news/{company_name}", response_model=CompanyResult)
# async def company_summary(
#    company_name: str,
#    db = Depends(get_database)
# ):
#     news_summary_service = NewsSummaryService(db)
#     try:
#         result = await news_summary_service.get_summary_news_from_mongo(company_name)
#         if result:
#             return CompanyResult(**result[0])
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))

@companies_router.get("/news/{company_name}", response_model=CompanyResult)
async def company_summary(
   company_name: str,
   db = Depends(get_database)
):
    news_summary_service = NewsSummaryService(db)
    news_link_service = NewsLinkService(company_name)
    try:
        summary_result = await news_summary_service.get_summary_news_from_hadoop(company_name)
        link_result = await news_link_service.get_news_link()

        if summary_result:
            if link_result:
                summary_result['news']=link_result
            else:
                summary_result['news']=[{
                'title':'최신 뉴스가 없습니다.',
                'link': 'no data'
            }]

            return summary_result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))





@companies_router.get("/news", response_model=CompanyResult)
async def all_company_summary(
   db = Depends(get_database)
):
    print('news z컨트롤러')
    news_summary_service = NewsSummaryService(db)

    try:
        result = await news_summary_service.save_all_summary_news_from_mongo_to_hadoop()
        if result:
            print("하둡저장 완료!!!")
            return CompanyResult(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@companies_router.get("/financials/{comp_name}/{year}")
async def get_financial_data(
    comp_name: str,
    year: int,
    db = Depends(get_database)
):
    collection = db.financial_data
    data = await collection.find_one({"corp_name": comp_name})

    if not data:
        raise HTTPException(status_code=404, detail="Company financial data not found")

    yearly_data = data.get("yearly_data", {}).get(str(year), {})

    if not yearly_data:
        raise HTTPException(status_code=404, detail="Financial data for the specified year not found")

    return {
        "corp_name": comp_name,
        "year": year,
        "financial_data": yearly_data
    }

@companies_router.get("/financials/{comp_name}")
async def get_financial_data(
    comp_name: str,
    db = Depends(get_database)
):
    collection = db.financial_data
    data = await collection.find_one({"corp_name": comp_name})

    if not data:
        raise HTTPException(status_code=404, detail="Company financial data not found")

    yearly_data = data.get("yearly_data", {})

    if not yearly_data:
        raise HTTPException(status_code=404, detail="No financial data found for the company")

    return {
        "corp_name": comp_name,
        "financial_data": yearly_data
    }

@companies_router.get("/dart_reports/{company_name}", response_model=DartReportResponse)
async def dart_report(
    company_name: str,
    dart_collection = Depends(get_dart_collection)  # 명확한 변수명 사용
):
    dart_report_service = DartReportService(dart_collection)  # 컬렉션을 전달
    try:
        result = await dart_report_service.get_dart_report(company_name)
        # DartReportResponse 모델로 반환
        return DartReportResponse(status="success", data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

