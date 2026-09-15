# V1 Ollama: tích hợp pipeline sandbox

`run_eval.py --provider ollama` mặc định dùng pipeline `planned`.
Không còn phải chạy sandbox riêng để dùng router/planner.
Model do `--model` chọn, không có model mặc định hoặc fallback 7B trong pipeline này.

```powershell
python run_eval.py --provider ollama --model qwen2.5:3b --version v1 --suite base --eval-cases data/eval_base.json
```

Có thể ghi rõ `--pipeline planned`. Để chạy lại cách chọn tool native cũ:

```powershell
python run_eval.py --provider ollama --model qwen2.5:3b --pipeline native --version v1 --suite base --eval-cases data/eval_base.json
```

## Luồng Thực Thi

1. Gửi hội thoại gốc cho Qwen để phân loại các trường in_scope, stop, device_diagnostic, employee_lookup, needs_ticket_confirmation và environment.
2. Kiểm tra thông tin phân loại có căn cứ trong lời người dùng: ID theo mẫu lab, tên môi trường nguyên văn, yêu cầu ticket.
3. Chọn nhánh không tool hoặc thu hẹp schema cho hỏi lại/xác nhận. Nhánh đủ thông tin dùng các tool đã khai báo.
4. Cùng model Qwen xuất kế hoạch JSON gồm name/args. Expected của eval không được gửi vào bước này.
5. HelpdeskAgent thực thi các tool qua TOOL_FUNCTIONS, giữ kết quả như luồng native trước đây.
6. Evaluator hiện tại so sánh kế hoạch thực tế với expected; không đổi đáp án hoặc công thức chấm.

Pipeline planned không dùng expect.no_tool để ép tool_choice. Dữ liệu nhiều
lượt là các message gốc, thay vì đoạn lịch sử ghép vào một user message.
Đây là thay đổi pipeline; điểm không phải kết quả của một lượt native đơn thuần.

## File Và Trace

- `providers/ollama_plan_provider.py`: router, grounding và planner.
- `artifacts/ollama_router_prompt.md`: chỉ dẫn phân loại.
- `artifacts/ollama_planner_prompt.md`: chỉ dẫn lập kế hoạch, mặc định system prompt cho planned.
- `run_eval.py`: chọn pipeline/prompt, dùng lịch sử gốc, lưu metadata.
- `agent.py`: thực thi tool, trả thêm raw trace.
- `tests/test_ollama_plan_provider.py`: kiểm tra nhánh hủy, thiếu ID, môi trường được paraphrase, phân loại nhầm ticket và không dùng forced choice.

Controller còn giữ title/template nguyên văn và phạm vi/category theo chủ đề
trong schema; lọc các nguồn không còn hiệu lực ở lượt cuối; giới hạn tối thiểu
số lời gọi khi so sánh hoặc yêu cầu nhiều nguồn. Đây là quy tắc nghiệp vụ
chung từ input, không dùng case IDs hay expected để sửa kế hoạch model.

Log mới có `pipeline`, đường dẫn/hash router prompt và `results[].pipeline_trace`
(route, grounding_issues, router_raw, planner_raw), kèm tool_results. Các lần
chạy từ mã hiện tại còn lưu artifact_snapshot của prompt/router/tools.
Artifact version cũ chỉ hash system prompt và tools; đối chiếu thêm pipeline
và router_prompt_sha256 khi so sánh cấu hình planned.

## Giới Hạn

Không giới hạn requests/minute mặc định khi local. Router/planner thường cần
hai lượt model thay vì một. Điểm 9/9 trong sandbox không chứng minh cả bộ
30 câu, phải dùng log chạy cả bộ đã tích hợp.
Grounding theo mẫu lab chưa giải quyết mọi chủ thể mới, ID cũ hết hiệu lực,
tên môi trường nhiều từ hoặc các cách diễn đạt không có nhãn rõ ràng.
Evaluator chấm tool calls/args được chỉ định, chưa chấm toàn bộ chất lượng reply.
Provider `ollama_router` chuyển 3B sang 7B có sẵn trong repo vẫn giữ riêng,
không được dùng bởi pipeline planned này.

## Kết Quả Đã Kiểm Chứng

`runs/v1_B_base_ollama_20260915T201500811475.json`: 30/30, measured=30,
provider errors=0, case/routing/argument/multiturn accuracy đều 1.0.
Model `qwen2.5:3b`, pipeline planned, cùng bộ base gốc.
9 unittest trong `tests/test_ollama_plan_provider.py` đã qua.

Lần tích hợp đầu `runs/v1_B_base_ollama_20260915T201016170088.json` chỉ đạt
20/30. Sau đó bổ sung các kiểm tra nguồn còn hiệu lực, title/scope/category,
phân biệt so sánh với môi trường mơ hồ và phạm vi IT để đạt kết quả trên.
Giữ cả log fail và pass để kiểm tra diễn biến; 30/30 không có nghĩa model tự
chọn đúng nếu bỏ controller, hay bộ test độc lập cũng chắc chắn đạt 100%.
