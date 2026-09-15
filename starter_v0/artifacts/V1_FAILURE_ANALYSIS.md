# Phân tích v1 và sửa cho v2

## Bằng chứng

Trace gốc: `runs/v1_B_base_openrouter_20260915T183909014234.json`.
Model: `openai/gpt-4o-mini`. Artifact: `v1+p1fa40bb76f7e+td4848549884e`.
Kết quả: 21/30, không có provider error.

`failure_type` khi fail lấy từ nhãn định sẵn của case. Vì thế nhãn
`wrong_tool` không nhất thiết nghĩa là model chọn sai tool. Đọc thêm
`routing_correct`, `observed_mismatch`, `failures` và `actual_tool_calls`.
Lỗi thực tế: 5 case sai/thiếu tham số, 1 case gọi thừa, 3 case thiếu clarify.

## Từng lỗi và thay đổi cụ thể

| Case | Trace thực tế | Hành vi cần có | Sửa và vị trí trong file hiện tại |
| --- | --- | --- | --- |
| H03 | Gọi đúng search_kb nhưng thiếu category | category=email vì yêu cầu Outlook | system_prompt.md:23 ánh xạ chủ đề; tools.yaml:21,26 mô tả; tools.yaml:28 bắt buộc category |
| H04 | lookup_user đúng, nhưng gọi thêm inspect_device(asset_id=EMP-1003) | Chỉ lookup_user; assigned_assets đã có trong kết quả | system_prompt.md:19,24 phân biệt ID và phạm vi lookup; tools.yaml:40,44,49 mô tả ID/phạm vi |
| H10 | inspect_device(asset_id=laptop) | clarify(response_type=text) để xin asset ID | system_prompt.md:19,20 cấm dùng tên loại thiết bị làm ID; tools.yaml:11,40,44 mô tả điều kiện gọi |
| H11 | lookup_user(employee_id=Sales) | clarify(response_type=text) để xin employee ID | system_prompt.md:19,20 cấm dùng phòng ban làm ID; tools.yaml:49 mô tả điều kiện lookup |
| H12 | clarify(response_type=text), xin thêm summary | Tự tóm tắt lỗi VPN trên LT-204, priority high; hỏi xác nhận yes_no | system_prompt.md:14 phân biệt xin thông tin và xác nhận payload; tools.yaml:16,18 định nghĩa/bắt buộc response_type; tools.yaml:99 mô tả write action |
| H13 | Có đủ hai tool nhưng inspect_device thiếu check | inspect_device(check=vpn), giữ status VPN production | system_prompt.md:22 ánh xạ phạm vi; tools.yaml:40 mô tả; tools.yaml:46 bắt buộc check |
| M06 | Đã chuyển sang search_kb nhưng category=all; query chỉ Wi-Fi | category=wifi; query giữ chủ đề Wi-Fi và nền tảng Windows | system_prompt.md:15,16 giữ ngữ cảnh còn hiệu lực; system_prompt.md:23 ánh xạ category; tools.yaml:25,28 mô tả query/bắt buộc category |
| H17 | Đủ ba tool, nhưng check=all và search_kb thiếu category | check=vpn và category=vpn; giữ status VPN production | system_prompt.md:22,23 chọn phạm vi hẹp; tools.yaml:28,46 bắt buộc hai tham số |
| H19 | Tự suy diễn demo của QA thành staging | clarify(response_type=choice, options=[production, staging]) | system_prompt.md:21 phân biệt bỏ trống với mơ hồ; tools.yaml:11,31 mô tả điều kiện clarify |

Các số dòng tính trên file sau sửa. Chỉ dẫn là quy tắc chung theo chủ đề,
loại ID và trạng thái hội thoại; không gắn case ID vào prompt hay mã chạy.

## Vì sao sửa ở prompt và schema

Trace quan sát được cho thấy model bỏ tham số optional, chọn all khi chủ đề
đã rõ, và tự dùng từ mô tả làm ID. Prompt bổ sung quyết định nghiệp vụ;
description giải thích ý nghĩa tool; required yêu cầu model phát tham số rõ ràng.
Đây là giải thích phù hợp với trace, không phải bằng chứng về suy nghĩ bên trong model.

Các thay đổi required so với bản đầu:

```yaml
clarify: [question] -> [question, response_type]
search_kb: [query] -> [query, category]
check_service_status: [service] -> [service, environment]
inspect_device: [asset_id] -> [asset_id, check]
```

Default trong hàm tool có thể được áp dụng khi chạy, nhưng evaluator so sánh
tham số model phát ra trước khi default đó được bổ sung. H03 vẫn tìm thấy
bài Outlook, nhưng không đáp ứng hợp đồng category=email; H13 trả diagnostics
all, nhưng không phát check=vpn. Required không tự bảo đảm giá trị đúng hoặc
mọi provider đều thực thi schema nghiêm ngặt; cần quy tắc ngữ nghĩa và eval.

Trong lượt này bổ sung system_prompt.md:16 (giữ chủ đề khi chỉ đổi nền tảng),
system_prompt.md:25 (kiểm tra tham số trước khi gọi) và tools.yaml:25 (query
gồm chủ đề/nền tảng). Đồng thời thu hẹp ánh xạ certificate thành VPN certificate
ở system_prompt.md:22 để tránh coi mọi certificate là VPN.
Các sửa chính cho 9 lỗi đã được áp dụng ở những lượt trước và được giữ lại.

## Giới hạn để trả lời phản biện

- 30/30 chỉ chứng minh kết quả trên bộ base trong lần chạy được báo cáo; không chứng minh đúng mọi câu hỏi hoặc mọi model.
- Bộ base đã được dùng để chỉnh prompt, nên cần adversarial/group độc lập để đánh giá khả năng khái quát.
- Eval đo tool calls và một phần args, không đánh giá toàn bộ chất lượng câu trả lời hoặc nội dung câu hỏi xác nhận.
- Với no_tool, evaluator chỉ kiểm tra không gọi tool; câu trả lời vẫn cần kiểm tra riêng.
- run_eval.py:302 chọn tool_choice=required dựa vào expect.no_tool. Vì vậy bài đo đã cung cấp tín hiệu bắt buộc dùng tool ở các case có tool; chưa đo hoàn toàn khả năng tự quyết định có gọi tool trong thực tế.
- Multi-turn hiện ghép lịch sử vào một user message và chỉ gọi model cho lượt cuối; chưa phải chạy hội thoại tương tác từng lượt.
- H12 không thực sự tạo ticket trái phép: model đã hỏi lại, nhưng hỏi sai kiểu. Quy tắc xác nhận ticket là yêu cầu nghiệp vụ của lab.
- Trong lượt sửa này không đổi dataset hay logic chấm điểm. Lần kiểm chứng dùng nhãn v2 để phân biệt với trace v1 cũ.
- Log cũ có hash/path artifact, không chứa toàn bộ nội dung prompt/tools; không thể khôi phục chính xác v1 chỉ từ log đó.

## Kết quả kiểm chứng trong lượt này

Lệnh: `python run_eval.py --provider openrouter --version v2 --suite base --eval-cases data/eval_base.json`.
Tốc độ mặc định: 5 câu/phút. Artifact: `v2+pad857e8bfd66+t511e2bf34ed4`.
Log: `runs/v2_B_base_openrouter_20260915T192147360082.json`.
30 provider errors, measured_cases=0; tất cả báo
`RuntimeError: Missing API key env var: OPENROUTER_API_KEY`.
Không có đủ dữ liệu kết luận accuracy của bản bổ sung trong lượt này.
Chạy lại trong terminal đã cấu hình key, giữ cùng model để so sánh.
`git diff --check` đã qua; kiểm tra này chỉ xác nhận định dạng diff.
