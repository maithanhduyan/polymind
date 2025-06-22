Để lập "Bảng cân đối kế toán" theo chuẩn VAS, bạn cần:

1. Xác định các yếu tố tài sản, nợ phải trả, vốn chủ sở hữu từ dữ liệu thực tế trong PostgreSQL (Odoo).
2. Tổng hợp số dư cuối kỳ của từng tài khoản kế toán theo nhóm (tài sản, nợ, vốn).
3. Trình bày theo mẫu quy định của VAS.

### Các bước thực hiện:

#### 1. Lấy danh mục tài khoản và phân loại nhóm
- Truy vấn bảng `account_account` để lấy danh sách tài khoản và trường `user_type_id` (hoặc liên kết với bảng loại tài khoản để biết nhóm: tài sản, nợ, vốn).

#### 2. Tổng hợp số dư cuối kỳ từng tài khoản
- Truy vấn bảng `account_move_line` để lấy số dư cuối kỳ của từng tài khoản (thường là tổng phát sinh Nợ - Có đến ngày báo cáo).
- Ví dụ SQL:
```sql
SELECT aa.code, aa.name, aut.name AS account_type, 
       SUM(aml.debit - aml.credit) AS balance
FROM account_move_line aml
JOIN account_account aa ON aml.account_id = aa.id
JOIN account_account_type aut ON aa.user_type_id = aut.id
WHERE aml.date <= '2025-06-22'
GROUP BY aa.code, aa.name, aut.name
ORDER BY aa.code;
```
- Lưu ý: Có thể cần lọc thêm theo trạng thái chứng từ (`account_move.state = 'posted'`).

#### 3. Tổng hợp theo nhóm tài khoản
- Nhóm các tài khoản theo loại: Tài sản (Asset), Nợ phải trả (Liability), Vốn chủ sở hữu (Equity).

#### 4. Trình bày theo mẫu VAS
- Sắp xếp các khoản mục theo đúng thứ tự quy định trong mẫu bảng cân đối kế toán VAS.

---

Bạn muốn tôi thực hiện truy vấn thực tế trên database để lấy số dư tài khoản theo nhóm (tài sản, nợ, vốn) không? Nếu có, vui lòng xác nhận hoặc cung cấp ngày chốt số liệu (mặc định là ngày hiện tại).