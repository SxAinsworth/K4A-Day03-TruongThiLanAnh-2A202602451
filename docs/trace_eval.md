# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** [Trương Thị Lan Anh]  
> **Mã Sinh Viên / Mã Học viên:** [2A202602451]  
> **Chủ đề Lựa chọn:** [Trợ lý Tư vấn Sức khỏe Vinmec]  

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | **4 / 5** | Bài toán yêu cầu nhiều bước xử lý nối tiếp: xác định chuyên khoa → tìm bác sĩ → kiểm tra lịch còn trống → lựa chọn khung giờ phù hợp → đặt lịch. Tuy nhiên, chuỗi xử lý tương đối ngắn và các bước nghiệp vụ chưa có quá nhiều nhánh suy luận phức tạp. |
| **2. Tool Interaction** | **5 / 5** | Đây là thành phần cốt lõi của bài toán. Agent cần sử dụng các Tool thông qua MCP Server để tìm bác sĩ (`search_doctors`), kiểm tra lịch (`get_doctor_schedule`) và đặt lịch (`book_appointment`). Các thông tin về bác sĩ và lịch khám không nên được LLM tự sinh mà phải lấy từ Tool. |
| **3. Dynamic Decision** | **4 / 5** | Hành động tiếp theo phụ thuộc vào Observation của Tool trước đó. Ví dụ, sau khi tìm được bác sĩ, Agent mới có thể kiểm tra lịch; nếu khung giờ yêu cầu còn trống thì mới đặt lịch, còn nếu không có bác sĩ hoặc không có lịch thì Agent phải dừng hoặc đưa ra phương án khác. Tuy nhiên, số lượng nhánh quyết định hiện tại vẫn còn tương đối giới hạn. |
| **4. Long Horizon Goal** | **3 / 5** | Agent cần giữ mục tiêu cuối cùng là hoàn thành việc đặt lịch và duy trì một số thông tin như chuyên khoa, bác sĩ, ngày khám, giờ khám và tên bệnh nhân qua nhiều bước ReAct. Tuy nhiên, một phiên đặt lịch thường chỉ diễn ra trong vài bước và chưa phải bài toán dài hạn gồm nhiều tác vụ kéo dài hoặc nhiều mục tiêu phụ. |
| **TỔNG ĐIỂM AGENTIC FIT** | **16 / 20** | **Bài toán phù hợp để triển khai Agentic System vì yêu cầu phối hợp nhiều Tool, xử lý theo chuỗi nhiều bước và lựa chọn hành động dựa trên Observation. Tuy nhiên, workflow hiện tại tương đối ngắn và mức độ suy luận/ra quyết định chưa quá phức tạp.** |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

```json
[
  {
    "step": 1,
    "action_type": "TOOL_EXECUTION",
    "tool_name": "academic_query",
    "arguments": {
      "student_id": "SV2026001"
    },
    "observation": {
      "status": "SUCCESS",
      "student_id": "SV2026001",
      "data": {
        "full_name": "Nguyễn Văn An",
        "gpa": 3.85
      }
    },
    "latency_ms": 120.5
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [ ] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini/OpenAI).
- **Tổng số Test Cases đã chạy thành công:** ___ / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** ___ lượt.
- **Kết quả đẩy Repo nộp bài:** [ ] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
