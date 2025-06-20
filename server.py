# zotero_mcp_server.py
import argparse
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from pyzotero import zotero
import os
import json
from dotenv import load_dotenv
load_dotenv()

class ZoteroWrapper(zotero.Zotero):
    def __init__(self):
        try:
            super().__init__(
                library_id=os.getenv("library_id"),
                library_type='user',
                api_key=os.getenv("zotero_api_key"),
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Zotero client: {str(e)}")

    def format_item(self, item):
        """格式化 Zotero 条目"""
        data = item.get("data", {})
        return {
            "title": data.get("title", "Untitled"),
            "authors": self.format_creators(data.get("creators", [])),
            "date": data.get("date", "No date"),
            "key": data.get("key"),
            "itemType": data.get("itemType", "Unknown type"),
        }

    def format_creators(self, creators):
        """格式化作者信息"""
        names = []
        for creator in creators:
            name_parts = []
            if creator.get("firstName"):
                name_parts.append(creator["firstName"])
            if creator.get("lastName"):
                name_parts.append(creator["lastName"])
            if name_parts:
                names.append(" ".join(name_parts))
        return ", ".join(names) or "No authors listed"


mcp = FastMCP("ZoteroServer")

@mcp.tool(description="List all collections in the Zotero library.")
async def get_collections(limit: int = None) -> str:
    """
    获取 Zotero 库中的所有集合。
    """
    try:
        client = ZoteroWrapper()
        collections = client.collections(limit=limit)
        return json.dumps(collections, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch collections: {str(e)}"}, indent=2)


@mcp.tool(description="Get all items in a specific Zotero collection.")
async def get_collection_items(collection_key: str, limit: int = None) -> str:
    """
    获取指定集合中的所有条目。
    """
    try:
        client = ZoteroWrapper()
        items = client.collection_items(collection_key, limit=limit)
        formatted_items = [client.format_item(item) for item in items]
        return json.dumps(formatted_items, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch collection items: {str(e)}"}, indent=2)

@mcp.tool(description="Get detailed information about a specific item in the library.")
async def get_item_details(item_key: str) -> str:
    """
    获取指定条目的详细信息。
    """
    try:
        client = ZoteroWrapper()
        item = client.item(item_key)
        formatted_item = client.format_item(item)
        return json.dumps(formatted_item, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch item details: {str(e)}"}, indent=2)


@mcp.tool(description="Get fulltext as indexed by Zotero.")
async def get_item_fulltext(item_key: str) -> str:
    """
    获取指定条目的全文内容。
    """
    try:
        client = ZoteroWrapper()
        fulltext = client.fulltext_item(item_key)
        if not fulltext:
            return json.dumps({"error": "No fulltext found"}, indent=2)
        return json.dumps(fulltext, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch fulltext: {str(e)}"}, indent=2)


@mcp.tool(description="Retrieve PDF for item in the library.")
async def get_item_pdf(item_key: str, attachment_index: int = 0) -> str:
    """
    获取指定条目的 PDF 附件。
    """
    try:
        client = ZoteroWrapper()
        children = client.children(item_key)
        pdf_attachments = [
            {
                "key": item["key"],
                "title": item["data"].get("title", "Untitled"),
                "filename": item["data"].get("filename", "Unknown"),
                "index": idx,
            }
            for idx, item in enumerate(children)
            if item["data"]["itemType"] == "attachment"
            and item["data"].get("contentType") == "application/pdf"
        ]
        if not pdf_attachments:
            return json.dumps({"error": "No PDF attachments found"}, indent=2)
        if attachment_index >= len(pdf_attachments):
            return json.dumps(
                {
                    "error": f"Invalid attachment index {attachment_index}",
                    "available_attachments": pdf_attachments,
                },
                indent=2,
            )
        selected_attachment = pdf_attachments[attachment_index]
        pdf_uri = client.file_url(selected_attachment["key"])
        return json.dumps(
            {
                "uri": pdf_uri,
                "mimeType": "application/pdf",
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch PDF: {str(e)}"}, indent=2)

@mcp.tool(description="Get tags used in the Zotero library.")
async def get_tags(limit: int = None) -> str:
    """
    获取 Zotero 库中使用的所有标签。
    """
    try:
        client = ZoteroWrapper()
        tags = client.tags(limit=limit)
        return json.dumps(tags, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch tags: {str(e)}"}, indent=2)


@mcp.tool(description="Get recently added items to your library.")
async def get_recent(limit: int = 10) -> str:
    """
    获取最近添加到 Zotero 库中的条目。
    """
    try:
        client = ZoteroWrapper()
        items = client.items(limit=limit, sort="dateAdded", direction="desc")
        formatted_items = [client.format_item(item) for item in items]
        return json.dumps(formatted_items, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch recent items: {str(e)}"}, indent=2)


@mcp.tool(description="Search the local Zotero library of the user.")
async def search_library(query: str, qmode: str = "titleCreatorYear", itemType: str = "-attachment", limit: int = None) -> str:
    """
    搜索整个 Zotero 库。
    """
    try:
        client = ZoteroWrapper()
        items = client.items(q=query, qmode=qmode, itemType=itemType, limit=limit)
        formatted_items = [client.format_item(item) for item in items]
        return json.dumps(formatted_items, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}"}, indent=2)


if __name__ == "__main__":
    # print(os.environ.get("zotero_api_key"))
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type",
        type=str,
        default="sse",
        choices=["sse", "stdio"],
    )
    args = parser.parse_args()
    mcp.run(args.server_type)