# Sửa tiếp v1 cho Ollama Qwen 3B

Trace đầu vào: `runs/v1_B_base_ollama_20260915T193404346317.json`.
Artifact đầu vào: `v1+pad857e8bfd66+t511e2bf34ed4`; kết quả 22/30.

| Case | Lỗi quan sát từ actual_tool_calls | Hướng sửa đã thử |
| --- | --- | --- |
| H08 | search_kb cho công thức, category=recipe ngoài enum | Quyết định ngoài IT phải trả lời không tool; description search_kb chỉ cho IT, cấm enum mới |
| H10 | Bịa asset_id=LT-1234 | Thiếu ID phải clarify text, không lấy ID ví dụ và không đổi sang shared status |
| H11 | Bịa employee_id=EMP-1003 | Thiếu mã nhân viên phải clarify text; schema description không cho dùng phòng ban hoặc mã ví dụ |
| H13 | Đủ hai tool nhưng check=all thay vì vpn | Scope VPN vẫn là vpn khi yêu cầu thêm status; bỏ default all khỏi schema check |
| H19 | environment=demo ngoài enum | Môi trường được nêu nhưng không hỗ trợ phải clarify choice, không tự đoán staging |
| H20 | Chỉ gọi report nhưng tự đổi incident_title | Sao chép nguyên văn tiêu đề; bổ sung description incident_title |
| M07 | clarify yes_no để xác nhận việc hủy | Hủy có hiệu lực ngay; lượt yêu cầu acknowledgment sau hủy không dùng tool |
| M08 | Chỉ gọi status, thiếu inspect_device | Dùng mã máy đã sửa mới nhất cho “máy đó”; yêu cầu hai nguồn cần hai tool trong cùng phản hồi |

H13 có nhãn wrong_tool nhưng thực tế wrong_arg_value. H20 có nhãn
unnecessary_tool nhưng không gọi thừa. M08 có nhãn wrong_arg_value nhưng
thực tế thiếu tool. Nhãn định sẵn của case không thay thế phân tích trace.

## File thay đổi

- `artifacts/system_prompt.md`: giữ cấu trúc rules của bản đầu, chỉ bổ sung tiêu đề nguyên văn và scope VPN không chuyển thành all khi yêu cầu thêm status.
- `artifacts/tools.yaml`: description check và incident_title cụ thể hơn. Giữ các default/required và description còn lại của bản đầu.
- Không sửa expected answers, cách chấm điểm, provider hay thực thi tool trong lượt này.

## Giới hạn

Đây là sửa prompt/schema, không phải bộ luật tự ghi đè tool calls của model.
Schema không được Ollama tự thực thi nghiêm ngặt trong mọi trường hợp: trace
đầu vào đã chứa recipe/demo ngoài enum. Không được khẳng định required hoặc
enum tự bảo đảm correctness. Nếu model còn sai, cần báo accuracy thực tế;
không sửa expected để đạt điểm. Chỉ so sánh các lần chạy cùng model/dataset.

Lệnh chạy lại từ `starter_v0`:

```powershell
python run_eval.py --provider ollama --model qwen2.5:3b --version v1 --suite base --eval-cases data/eval_base.json
```

Ollama không có giới hạn requests/minute mặc định trong repo hiện tại.

## Thử nghiệm không được giữ lại

Viết lại toàn bộ prompt theo thứ tự quyết định và dùng phần quyết định tiếng
Việt đã đạt 18/30 trong log `runs/v1_B_base_ollama_20260915T194106592538.json`.
H08/H13/H20 pass nhưng nhiều case cũ hồi quy. Cách viết lại này đã được bỏ,
quay về cấu trúc rules trước với bổ sung hẹp. Không dùng 18/30 để báo kết quả
của cấu hình cuối.

Bản quay về rules nhưng giữ nhiều bổ sung đạt 22/30 trong
`runs/v1_B_base_ollama_20260915T194316674536.json`, song M03/H18 hồi quy.
Các bổ sung rộng đó cũng đã được bỏ. Bản cuối chỉ giữ hai sửa hẹp nêu trên.
Những hướng sửa khác trong bảng là thí nghiệm, không phải toàn bộ thay đổi
được giữ lại. Không được nói đã sửa thành công cả 8 lỗi.

## Kết quả bản cuối

Log: `runs/v1_B_base_ollama_20260915T194530565065.json`.
Artifact: `v1+p73ca1c1809e4+t24609aa5261c`.
Model: `qwen2.5:3b`, Ollama local, cùng bộ base, không giới hạn tốc độ.
24/30 (80%), không provider errors; routing 80%, argument 80%, multiturn 80%.
H13 và H20 chuyển từ fail sang pass; tất cả 22 case pass ban đầu vẫn pass.
Còn fail H08, H10, H11, H19, M07, M08. Chưa đạt mục tiêu 100%.
Các thử nghiệm prompt rộng không giải quyết ổn định nhóm lỗi còn lại.
Hướng tiếp theo cần kiểm chứng là bộ lập kế hoạch/kiểm tra tool calls riêng
hoặc thay cách biểu diễn lịch sử hội thoại; chưa triển khai trong lượt này.
