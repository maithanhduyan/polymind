import json
import requests
from datetime import datetime


def load_law_chunks():
    """Load law chunks from JSON file"""
    with open(
        r"c:\Users\tiach\Downloads\polymind\mcp-server\docs\luat_ke_toan_vietnam_2015.chunked.json",
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)
    return data


def add_chunks_to_chromadb(law_data):
    """Add all chunks to ChromaDB collection"""

    # MCP tools API endpoint
    mcp_endpoint = "http://localhost:3000"

    # First, delete existing collection if it exists
    try:
        print("🗑️  Deleting existing collection...")
        delete_response = requests.post(
            f"{mcp_endpoint}/mcp/tools/mcp_tools-mcp_chromadb_chromadb_delete_collection",
            json={"name": "luat_ke_toan_vietnam_2015"},
        )
        if delete_response.status_code == 200:
            print("✅ Existing collection deleted")
        else:
            print("ℹ️  No existing collection to delete")
    except Exception as e:
        print(f"ℹ️  Collection doesn't exist: {e}")

    # Create new collection
    print("📁 Creating new collection...")
    collection_metadata = {
        "law_number": law_data["metadata"]["law_number"],
        "year": law_data["metadata"]["year"],
        "language": law_data["metadata"]["language"],
        "total_articles": law_data["metadata"]["total_articles"],
        "created_at": datetime.now().isoformat(),
    }

    create_response = requests.post(
        f"{mcp_endpoint}/mcp/tools/mcp_tools-mcp_chromadb_chromadb_create_collection",
        json={
            "name": "luat_ke_toan_vietnam_2015",
            "metadata": collection_metadata,
            "embeddingFunction": "nomic-embed-text",
        },
    )

    if create_response.status_code != 200:
        print(f"❌ Failed to create collection: {create_response.text}")
        return False

    print("✅ Collection created successfully")

    # Process chunks in batches
    chunks = law_data["chunks"]
    batch_size = 10
    total_chunks = len(chunks)

    print(f"📝 Adding {total_chunks} chunks to ChromaDB...")

    for i in range(0, total_chunks, batch_size):
        batch = chunks[i : i + batch_size]

        # Prepare batch data
        documents = []
        metadatas = []
        ids = []

        for chunk in batch:
            # Create document text combining title and content
            doc_text = f"{chunk['title']}\n\n{chunk['content']}"
            documents.append(doc_text)

            # Create metadata
            metadata = {
                "id": chunk["id"],
                "type": chunk["type"],
                "chapter": chunk.get("chapter"),
                "article_number": chunk.get("article_number"),
                "title": chunk["title"],
                "keywords": ",".join(chunk["metadata"].get("keywords", [])),
                "legal_status": chunk["metadata"].get("legal_status", "active"),
                "importance": chunk["metadata"].get("importance", "medium"),
                "cross_references": ",".join(
                    chunk["metadata"].get("cross_references", [])
                ),
            }
            metadatas.append(metadata)
            ids.append(chunk["id"])

        # Add batch to ChromaDB
        try:
            add_response = requests.post(
                f"{mcp_endpoint}/mcp/tools/mcp_tools-mcp_chromadb_chromadb_add_documents",
                json={
                    "collectionName": "luat_ke_toan_vietnam_2015",
                    "documents": documents,
                    "metadatas": metadatas,
                    "ids": ids,
                },
            )

            if add_response.status_code == 200:
                print(
                    f"✅ Added batch {i//batch_size + 1}/{(total_chunks + batch_size - 1)//batch_size}"
                )
            else:
                print(
                    f"❌ Failed to add batch {i//batch_size + 1}: {add_response.text}"
                )

        except Exception as e:
            print(f"❌ Error adding batch {i//batch_size + 1}: {e}")

    print(f"🎉 Successfully added all {total_chunks} chunks to ChromaDB!")
    return True


def test_semantic_search():
    """Test semantic search functionality"""
    print("\n🔍 Testing semantic search...")

    mcp_endpoint = "http://localhost:3000"

    test_queries = [
        "kế toán trưởng có trách nhiệm gì",
        "quy định về chứng từ kế toán",
        "báo cáo tài chính phải làm như thế nào",
        "những hành vi bị nghiêm cấm trong kế toán",
        "điều kiện để thành lập doanh nghiệp dịch vụ kế toán",
    ]

    for query in test_queries:
        try:
            response = requests.post(
                f"{mcp_endpoint}/mcp/tools/mcp_tools-mcp_chromadb_chromadb_query",
                json={
                    "collectionName": "luat_ke_toan_vietnam_2015",
                    "queryTexts": [query],
                    "nResults": 3,
                    "includeMetadata": True,
                },
            )

            if response.status_code == 200:
                results = response.json()
                print(f"\n📋 Query: '{query}'")
                if results.get("documents") and results["documents"][0]:
                    for j, doc in enumerate(
                        results["documents"][0][:2]
                    ):  # Show top 2 results
                        metadata = (
                            results["metadatas"][0][j]
                            if results.get("metadatas")
                            else {}
                        )
                        distance = (
                            results["distances"][0][j]
                            if results.get("distances")
                            else "N/A"
                        )
                        print(
                            f"  {j+1}. {metadata.get('title', 'Unknown')} (Distance: {distance:.3f})"
                        )
                        print(
                            f"     Type: {metadata.get('type')}, Chapter: {metadata.get('chapter')}"
                        )
                else:
                    print("     No results found")
            else:
                print(f"❌ Query failed: {response.text}")

        except Exception as e:
            print(f"❌ Error testing query '{query}': {e}")


def main():
    """Main function"""
    try:
        print("🚀 Starting ChromaDB ingestion process...")

        # Load law data
        law_data = load_law_chunks()
        print(f"📖 Loaded {len(law_data['chunks'])} chunks from law file")

        # Add to ChromaDB
        success = add_chunks_to_chromadb(law_data)

        if success:
            # Test semantic search
            test_semantic_search()

            print("\n✅ ChromaDB ingestion completed successfully!")
            print("🔍 You can now perform semantic search on Vietnamese Accounting Law")
            print("📊 Collection: luat_ke_toan_vietnam_2015")
            print(f"📄 Total documents: {len(law_data['chunks'])}")

        else:
            print("❌ ChromaDB ingestion failed")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
