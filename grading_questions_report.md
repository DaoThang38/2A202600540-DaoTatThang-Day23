# KẾT QUẢ CHẠY GRADING QUESTIONS QUA LANGGRAPH AGENT

*Lưu ý: Agent Day 08 chưa được tích hợp RAG thực tế, nên các câu trả lời sẽ phụ thuộc vào kiến thức nền của LLM.*

| ID | Phân Loại (Route) | Trạng thái (Pass/Fail) | Trích xuất câu trả lời |
|---|---|---|---|
| gq_d10_01 | `tool` | ❌ Fail | Theo chính sách hoàn tiền hiện hành, khách hàng có tối đa 30 ngày làm việc để gửi yêu cầu hoàn tiền sau khi đơn được xác... |
| gq_d10_02 | `simple` | ❌ Fail | Các loại sản phẩm thường bị loại khỏi điều kiện hoàn tiền bao gồm: sản phẩm đã qua sử dụng, sản phẩm bị hư hỏng, sản phẩ... |
| gq_d10_03 | `tool` | ❌ Fail | Thời gian xử lý yêu cầu hoàn tiền của đội ngũ tài chính thường phụ thuộc vào quy trình nội bộ của công ty. Thông thường,... |
| gq_d10_04 | `simple` | ❌ Fail | SLA phản hồi ban đầu cho ticket P1 thường là 1 giờ. Tuy nhiên, thời gian cụ thể có thể thay đổi tùy thuộc vào chính sách... |
| gq_d10_05 | `simple` | ✅ Pass | SLA resolution cho ticket P1 thường là 1 giờ hoặc 4 giờ, tùy thuộc vào chính sách của từng tổ chức. Bạn nên kiểm tra quy... |
| gq_d10_06 | `missing_info` | ❌ Fail | Bạn có thể cho biết hệ thống mà bạn đang đề cập đến là gì không?... |
| gq_d10_07 | `simple` | ✅ Pass | Tài khoản thường bị khóa sau 3 đến 5 lần đăng nhập sai liên tiếp, tùy thuộc vào chính sách bảo mật của từng dịch vụ. Bạn... |
| gq_d10_08 | `simple` | ❌ Fail | Số lượng thiết bị mà một VPN cho phép kết nối cùng lúc phụ thuộc vào nhà cung cấp dịch vụ VPN cụ thể. Một số VPN cho phé... |
| gq_d10_09 | `simple` | ✅ Pass | Theo chính sách HR 2026, nhân viên có dưới 3 năm kinh nghiệm sẽ được hưởng 12 ngày phép năm.... |
| gq_d10_10 | `missing_info` | ❌ Fail | Bạn có thể cho biết rõ hơn về hệ thống hoặc tổ chức mà bạn đang đề cập đến không?... |

**Tỷ lệ pass tiêu chí answer:** 3/10
