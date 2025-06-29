# Generated by Copilot

"""
AI Chunk Service Demo
Demonstrates how to use AI chunking service with Vietnamese legal documents
"""

import asyncio
import json
import requests
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

MCP_SERVER_URL = "http://localhost:3001"


def load_sample_law_text():
    """Load a sample from the Vietnamese Accounting Law"""

    # Sample from Điều 13 - Prohibited acts in accounting
    sample_text = """
    Điều 13. Những hành vi bị nghiêm cấm trong kế toán
    
    1. Làm giả chứng từ kế toán, sổ kế toán, báo cáo tài chính và các tài liệu kế toán khác.
    
    2. Cố ý làm sai lệch số liệu kế toán, báo cáo tài chính.
    
    3. Che giấu, tiêu hủy bất hợp pháp chứng từ kế toán, sổ kế toán và các tài liệu kế toán khác.
    
    4. Cung cấp, công bố thông tin kế toán, báo cáo tài chính sai sự thật.
    
    5. Lợi dụng chức vụ, quyền hạn can thiệp trái phép vào công việc kế toán của đơn vị kế toán.
    
    6. Các hành vi khác vi phạm pháp luật về kế toán.
    """

    return sample_text.strip()


def test_server_connection():
    """Test if MCP server is running"""
    try:
        response = requests.get(f"{MCP_SERVER_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def demo_keyword_extraction(text):
    """Demo keyword extraction from Vietnamese legal text"""
    print("🏷️  Keyword Extraction Demo")
    print("-" * 40)

    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/call-tool",
            json={
                "name": "ai_chunk.ai_chunk_extract_keywords",
                "arguments": {"text": text, "maxKeywords": 8, "language": "vi"},
            },
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Keywords extracted successfully:")

            keywords = result.get("keywords", [])
            for i, kw in enumerate(keywords, 1):
                keyword = kw.get("keyword", "unknown")
                relevance = kw.get("relevance", 0)
                frequency = kw.get("frequency", 0)
                print(
                    f"   {i}. {keyword} (relevance: {relevance:.2f}, frequency: {frequency})"
                )

            print(f"\n📊 Total keywords: {result.get('totalKeywords', 0)}")
            print(f"🌐 Language: {result.get('language', 'unknown')}")

        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")


def demo_document_analysis(text):
    """Demo document structure analysis"""
    print("\n📊 Document Analysis Demo")
    print("-" * 40)

    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/call-tool",
            json={
                "name": "ai_chunk.ai_chunk_analyze_structure",
                "arguments": {"text": text, "language": "vi"},
            },
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Document analysis completed:")

            print(f"   Language: {result.get('language', 'unknown')}")
            print(f"   Document Type: {result.get('documentType', 'unknown')}")

            sections = result.get("sections", [])
            print(f"   Sections found: {len(sections)}")

            for i, section in enumerate(sections[:3], 1):  # Show first 3 sections
                section_type = section.get("type", "unknown")
                content_preview = section.get("content", "")[:50] + "..."
                print(f"     {i}. {section_type}: {content_preview}")

            metadata = result.get("metadata", {})
            print(f"\n📈 Metadata:")
            print(f"   Total sections: {metadata.get('totalSections', 0)}")
            print(f"   Reading time: {metadata.get('estimatedReadingTime', 0)} minutes")
            print(f"   Complexity: {metadata.get('complexity', 'unknown')}")

        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")


def demo_smart_chunking(text):
    """Demo AI-powered smart chunking"""
    print("\n🧠 Smart Chunking Demo")
    print("-" * 40)

    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/call-tool",
            json={
                "name": "ai_chunk.ai_chunk_smart_chunk",
                "arguments": {
                    "text": text,
                    "chunkSize": 400,
                    "overlap": 50,
                    "language": "vi",
                    "preserveStructure": True,
                    "documentType": "legal",
                },
            },
            timeout=60,
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Smart chunking completed:")

            total_chunks = result.get("totalChunks", 0)
            avg_size = result.get("averageChunkSize", 0)

            print(f"   Total chunks: {total_chunks}")
            print(f"   Average chunk size: {avg_size} characters")

            metadata = result.get("metadata", {})
            print(f"   Original length: {metadata.get('originalLength', 0)} characters")
            print(f"   Processing time: {metadata.get('processingTime', 0)}ms")
            print(f"   Detected language: {metadata.get('language', 'unknown')}")

            # Show details of first chunk
            chunks = result.get("chunks", [])
            if chunks:
                first_chunk = chunks[0]
                print(f"\n📄 First chunk details:")
                print(f"   ID: {first_chunk.get('id', 'unknown')}")
                print(f"   Size: {len(first_chunk.get('content', ''))} characters")
                print(f"   Content preview: {first_chunk.get('content', '')[:100]}...")

                chunk_metadata = first_chunk.get("metadata", {})
                if chunk_metadata.get("keywords"):
                    print(
                        f"   Keywords: {', '.join(chunk_metadata['keywords'][:3])}..."
                    )
                if chunk_metadata.get("summary"):
                    print(f"   Summary: {chunk_metadata['summary'][:80]}...")
                print(f"   Importance: {chunk_metadata.get('importance', 'unknown')}")

        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")


def demo_summary_generation(text):
    """Demo text summarization"""
    print("\n📝 Summary Generation Demo")
    print("-" * 40)

    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/call-tool",
            json={
                "name": "ai_chunk.ai_chunk_generate_summary",
                "arguments": {"text": text, "maxLength": 200, "language": "vi"},
            },
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Summary generated successfully:")

            summary = result.get("summary", "")
            print(f"   Summary: {summary}")

            print(f"\n📊 Statistics:")
            print(f"   Original length: {result.get('originalLength', 0)} characters")
            print(f"   Summary length: {result.get('summaryLength', 0)} characters")
            print(f"   Compression ratio: {result.get('compressionRatio', 0)}%")
            print(f"   Language: {result.get('language', 'unknown')}")

        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main demo function"""
    print("🚀 AI Chunk Service Demo")
    print("Demonstrating Vietnamese legal document processing")
    print("=" * 60)

    # Check server connection
    if not test_server_connection():
        print("❌ Cannot connect to MCP server at http://localhost:3001")
        print("Please ensure the server is running with:")
        print("   cd mcp-server && node dist/server.js --http --port 3001")
        return

    print("✅ Connected to MCP server")

    # Load sample text
    sample_text = load_sample_law_text()
    print(f"\n📖 Sample text loaded ({len(sample_text)} characters)")
    print("Content preview:")
    print(f"   {sample_text[:150]}...")

    # Run demos
    try:
        demo_keyword_extraction(sample_text)
        demo_document_analysis(sample_text)
        demo_summary_generation(sample_text)
        demo_smart_chunking(sample_text)

        print("\n" + "=" * 60)
        print("🎉 Demo completed successfully!")
        print("\n💡 Use cases for AI Chunk Service:")
        print("   • Legal document processing and analysis")
        print("   • Intelligent text chunking for vector databases")
        print("   • Vietnamese content summarization")
        print("   • Keyword extraction for search optimization")
        print("   • Document structure analysis for automation")

    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
