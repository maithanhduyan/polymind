Dưới đây là một quy trình (workflow) ví dụ vận hành từ lúc tiếp nhận một tệp văn bản đầu vào đến khi lưu trữ dữ liệu đã xử lý vào cơ sở dữ liệu vector (ví dụ: ChromaDB). Quy trình được triển khai theo thứ tự tuần tự, cùng với phần mô tả về các siêu dữ liệu (metadata) cần thiết ở mỗi bước.

────────────────────────────────────────────────────────────────────────────
1. TIẾP NHẬN VĂN BẢN ĐẦU VÀO
────────────────────────────────────────────────────────────────────────────
• Bước 1.1 – Thu thập tệp:
  – Đầu vào: Tệp .md (Markdown) hoặc văn bản khác (PDF, DOCX, TXT, …).  
  – Ví dụ ở đây: “truyen_xuyen_khong_chapter_01.md”.
  – Mục đích: Chuẩn bị dữ liệu thô trước khi xử lý.

• Bước 1.2 – Đọc nội dung & siêu dữ liệu cơ bản:
  – Phân tích (parse) để lấy:
    1) Nội dung chính (text).  
    2) Đường dẫn (filepath) hoặc ID tệp.  
    3) Thông tin về định dạng (loại file: md/pdf/docx).  
    4) Tiêu đề/tiêu đề chương (nếu có).  
  – Tạo cấu trúc lưu ban đầu (metadata sơ bộ).  

Ví dụ (metadata ban đầu) – dạng JSON/từ điển Python minh họa:
{
  "filepath": "c:\\Users\\tiach\\Downloads\\polymind\\mcp-server\\docs\\novels\\truyen_xuyen_khong\\truyen_xuyen_khong_chapter_01.md",
  "document_title": "ĐẶC CÔNG XUYÊN KHÔNG THÀNH CẬU BÉ THỜI NGUYÊN THỦY",
  "chapter_title": "Phần 1",
  "file_format": "markdown",
  "raw_text_length": 12000  // ví dụ
}

────────────────────────────────────────────────────────────────────────────
2. TIỀN XỬ LÝ DỮ LIỆU (DATA PREPROCESSING)
────────────────────────────────────────────────────────────────────────────
• Bước 2.1 – Làm sạch (cleaning):
  – Loại bỏ các ký tự thừa, các dấu markdown nếu không cần thiết (ví dụ: “#”, “##”, “```markdown” v.v.).
  – Xử lý xuống dòng, nối lại thành đoạn văn hoàn chỉnh (nếu thích hợp).
  – Chuẩn hóa dấu câu, xóa khoảng trắng dư thừa.

• Bước 2.2 – Chuẩn bị siêu dữ liệu (metadata) nâng cao:
  – Xác định (hoặc phát sinh) các trường bổ sung, ví dụ:
    • “author_name”: Tác giả (nếu biết).  
    • “chapter_index”: Số thứ tự chương (nếu văn bản có tính chương hồi).  
    • “source”: Nguồn gốc (nếu văn bản sưu tầm từ tài liệu có sẵn).  
    • “language”: “vi” (tiếng Việt).  
    • “category”: “Tiểu thuyết / Xuyên không / Thời nguyên thủy” (nếu cần).  
  – Nâng cấp metadata sơ bộ thành cấu trúc phong phú hơn, kèm giá trị cụ thể.

Ví dụ (metadata nâng cao) – dạng JSON minh họa:
{
  "title": "ĐẶC CÔNG XUYÊN KHÔNG THÀNH CẬU BÉ THỜI NGUYÊN THỦY",
  "chapter": "Phần 1",
  "filepath": "...",
  "author": null,
  "chapter_index": 1,
  "language": "vi",
  "category": ["Xuyên không", "nguyên thủy", "tiểu thuyết"],
  "text_cleaned_length": 11582
}

────────────────────────────────────────────────────────────────────────────
3. CHUNKING (CẮT CHIA VĂN BẢN)
────────────────────────────────────────────────────────────────────────────
• Bước 3.1 – Tạo các đoạn (chunk) phù hợp:
  – Mục đích: Những mô hình embedding thường có giới hạn về độ dài văn bản cho mỗi lần mã hóa (embedding). Ta cần chia nội dung thành từng đoạn ngắn (ví dụ: 500-1000 tokens).
  – Có thể cắt theo từng đoạn văn, hoặc theo quy tắc cắt fix-size (mỗi đoạn ~500-800 từ/token).

• Bước 3.2 – Tạo metadata cho từng đoạn:
  – Mỗi đoạn (chunk) sẽ kèm theo các trường:
    1) “chunk_index” (thứ tự đoạn trong chương).  
    2) “text_chunk” (nội dung của đoạn).  
    3) “original_source” (đường dẫn về tệp gốc).  
    4) “chapter” hoặc “chapter_index”, v.v.  
  – Hai trường quan trọng:
    – “chunk_id”: ID duy nhất của đoạn.  
    – “text_chunk”: nội dung chính của đoạn.  

Ví dụ (metadata cho đoạn) – dạng JSON:
{
  "chunk_id": "truyen_xuyen_khong_chapter_01_chunk_01",
  "text_chunk": "Vốn là một đặc công, Hàn Phong...",
  "chapter": "Phần 1",
  "filepath": "...",
  "chunk_index": 1,
  "language": "vi"
}

────────────────────────────────────────────────────────────────────────────
4. TẠO EMBEDDING (VECTOR HÓA)
────────────────────────────────────────────────────────────────────────────
• Bước 4.1 – Chọn mô hình embedding:
  – Dùng một mô hình ngôn ngữ (LLM) hoặc mô hình embedding phù hợp tiếng Việt (ví dụ: “sentence-transformers/....”).

• Bước 4.2 – Sinh embeddings:
  – Với mỗi “text_chunk”, gửi nội dung sang mô hình embedding để nhận về vector (numpy array hoặc list float).
  – Mỗi chunk sẽ có vector riêng.

• Bước 4.3 – Gắn embeddings vào metadata:
  – Mỗi chunk sau bước 4.2 sẽ có thêm trường “embedding_vector”.

Ví dụ (metadata + embedding):
{
  "chunk_id": "truyen_xuyen_khong_chapter_01_chunk_01",
  "text_chunk": "Vốn là một đặc công...",
  "embedding_vector": [0.023, 0.517, 0.001, ...],
  "chapter": "Phần 1"
}

────────────────────────────────────────────────────────────────────────────
5. LƯU KẾT QUẢ VÀO CHROMADB
────────────────────────────────────────────────────────────────────────────
• Bước 5.1 – Khởi tạo kết nối đến ChromaDB:
  – Sử dụng client ChromaDB (hoặc library tương tự).
  – Tạo (hoặc lấy) collection tương ứng, ví dụ: “novels_vi” (nếu đã có sẵn).

• Bước 5.2 – Thêm (upsert) các bản ghi (documents) gồm:
  – “ids”: Mảng/Key cho chunk_id.  
  – “embeddings”: Mảng vectors (float).  
  – “metadatas”: Mảng metadata dictionary.  
  – “documents” (nếu ChromaDB cho phép): Nội dung gốc hoặc text_chunk.  

Ví dụ (pseudo-code Python):
collection.upsert(
  ids=[chunk["chunk_id"] for chunk in chunks],
  embeddings=[chunk["embedding_vector"] for chunk in chunks],
  metadatas=[{
    "chapter": chunk["chapter"],
    "filepath": chunk["filepath"],
    "chunk_index": chunk["chunk_index"],
    ...
  } for chunk in chunks],
  documents=[chunk["text_chunk"] for chunk in chunks]
)

• Bước 5.3 – Kiểm tra log lưu trữ:
  – Đảm bảo tất cả các đoạn (chunk) được indexing xong.  
  – Xác minh số lượng bản ghi đã được upsert trùng khớp với số chunk.

────────────────────────────────────────────────────────────────────────────
6. THEO DÕI, QUẢN LÝ PHIÊN BẢN (VERSIONING) & BẢO TRÌ
────────────────────────────────────────────────────────────────────────────
• Bước 6.1 – Theo dõi phiên bản:
  – Nếu văn bản thay đổi, nâng phiên bản (“version 2”, …), lặp lại quy trình.  
  – Thêm trường “version” vào metadata, ví dụ: "version": "v1.0".

• Bước 6.2 – Bảo trì database:
  – Có thể thiết lập thời gian chạy batch định kỳ (cron job) để nén/chỉ mục lại (reindex), xóa dữ liệu cũ.
  – Giữ lịch sử embeddings để so sánh khi cần.

────────────────────────────────────────────────────────────────────────────
TỔNG KẾT QUY TRÌNH
────────────────────────────────────────────────────────────────────────────
1. Input & tách metadata sơ bộ → 2. Tiền xử lý & chuẩn hóa → 3. Chunking văn bản → 4. Sinh embeddings (vector) → 5. Upsert vào ChromaDB kèm metadata đầy đủ → 6. Kiểm tra & bảo trì, quản lý phiên bản.

Quy trình trên cho phép ta liên kết chặt chẽ giữa nội dung gốc, các đoạn đã xử lý, cũng như đảm bảo khả năng tìm kiếm (semantic search) và truy vấn context chuẩn xác nhờ việc lưu embeddings kèm theo siêu dữ liệu rõ ràng.