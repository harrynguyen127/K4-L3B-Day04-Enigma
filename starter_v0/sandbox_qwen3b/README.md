# Qwen 2.5 3B: sandbox chỉ chạy câu lỗi

Đây là thư mục thí nghiệm tách khỏi agent/provider/prompt v1 chính.
Không phải máy ảo hoặc sandbox bảo mật: model vẫn chạy qua Ollama local/GPU.
Thí nghiệm chỉ lập kế hoạch và chấm tool calls, KHÔNG thực thi các tool đã chọn.
Không gọi cloud API, không giới hạn tốc độ, không đặt model mặc định.

## Pipeline thử nghiệm

1. Đọc các log được chỉ định và lấy hợp ID của các case fail.
2. Lấy nguyên câu hỏi và expected từ eval_base.json. Expected chỉ dùng để chấm, không gửi vào model.
3. Qwen 2.5 3B phân loại các trường in_scope, stop, device_diagnostic, employee_lookup, needs_ticket_confirmation, environment.
4. Kiểm tra dữ liệu từ lời người dùng: mã asset/employee, chuỗi môi trường và việc nhắc tới ticket. Không dùng ID trong tool description làm dữ liệu người dùng.
5. Ngoài phạm vi/hủy -> không tool. Thiếu ID -> chỉ clarify text. Môi trường không hỗ trợ -> chỉ clarify choice với production/staging. Xác nhận ticket -> chỉ clarify yes_no.
6. Qwen xuất kế hoạch JSON với schema tương ứng; chấm bằng evaluate_phase_b và summarize của repo.

Khác biệt có chủ đích: lịch sử nhiều lượt được gửi dưới dạng các message gốc,
thay vì ghép vào một user message. Bộ tool phù hợp được lọc bởi bước phân loại;
schema response_type/options được thu hẹp cho clarify. Đây là sửa pipeline,
không phải chỉ sửa prompt và không phải accuracy native v1 cũ.

Các kiểm tra grounding chỉ là quy tắc chung, không chứa case IDs hay expected calls.
Chúng còn giới hạn: nhận diện ID theo mẫu lab; chưa giải quyết mọi trường hợp
đổi chủ thể hoặc ID cũ không còn liên quan. Bộ lập kế hoạch vẫn có thể hiểu sai.

## Chạy từ starter_v0

```powershell
python sandbox_qwen3b/run_failed.py --model qwen2.5:3b --failed-run runs/v1_B_base_ollama_20260915T194530565065.json --failed-run runs/v1-local-qwen25-3b_B_base_ollama_20260915T194933074788.json
```

Hai log trên tạo hợp 9 câu lỗi: H04, H08, H10, H11, M05, H18, H19, M07, M08.
Muốn chỉ chạy lỗi còn lại của một lần sandbox, dùng file focused đó:

```powershell
python sandbox_qwen3b/run_failed.py --model qwen2.5:3b --failed-run sandbox_qwen3b/focused_20260915T195446573880.json
```

Mỗi lần chạy lưu focused_<timestamp>.json trong thư mục này, gồm input,
expected, tool plan, phân loại gốc, grounding_issues, response Ollama và summary.
Model/prompt/tools được lưu trong report để đối chiếu.

## Phạm Vi Kết Luận

Điểm trên các câu lỗi chỉ là targeted regression, chưa phải accuracy 30 câu.
Chưa kiểm chứng 21 câu còn lại, chưa tích hợp vào run_eval.py, chưa đánh giá
toàn bộ nội dung reply/question, và không chứng minh model đúng mọi tình huống.
Giữ riêng cấu hình v1 hiện tại để so sánh trước khi tích hợp pipeline mới.

Pipeline đã được tích hợp vào `run_eval.py --provider ollama` qua provider
planned. Xem `artifacts/OLLAMA_PIPELINE.md` để chạy cả bộ; các giới hạn/chưa
tích hợp ở phần trên mô tả trạng thái thí nghiệm ban đầu. Luồng đã tích hợp
có thêm controller cho nguồn còn hiệu lực, title, phạm vi và category.

## Kết Quả Cuối

`focused_20260915T195818326616.json`: 9/9 pass, provider errors=0;
case/routing/argument/multiturn accuracy đều 1.0 trên đúng nhóm 9 câu lỗi.
Model `qwen2.5:3b`, Ollama local, không chạy cả bộ 30 câu.

Thay đổi giúp giải quyết H18/M08: chỉ cho xác nhận ticket nếu lời người dùng
có nhắc ticket; bỏ môi trường do router bịa không có trong lời người dùng;
đưa các ID được cung cấp theo thứ tự vào kế hoạch để xử lý mã đã sửa.
H19 dùng tên môi trường nguyên văn sau nhãn “môi trường/environment” thay
vì bản dịch/paraphrase của router. Quy tắc này có giới hạn với các tên môi
trường nhiều từ và cách diễn đạt không có nhãn; chưa kiểm chứng ngoài bộ lỗi.

H08/M07 dùng nhánh không tool; H10/H11 chỉ clarify text; M05 chỉ clarify
yes_no; H19 chỉ clarify choice với đúng hai options; H04 chỉ lookup_user;
H18/M08 lập đủ hai lời gọi. Các expected answers và evaluator được giữ nguyên.
