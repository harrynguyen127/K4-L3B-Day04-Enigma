# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: Enigma
- Người đại diện / MSSV: Nguyễn Anh Tuấn - 2A202602700
- Tên repo: `K4-L3B-Day04-Enigma`
- URL repo, nhánh nộp, commit chốt: https://github.com/harrynguyen127/K4-L3B-Day04-Enigma
- Deadline áp dụng và link thông báo đổi hạn nếu có:

## Thành viên


| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Nguyễn Anh Tuấn| 2A202602700| harrynguyen127| Teamlead. UI, transcript & report: làm UI chat hiện tool call/input/kết quả-lỗi/version, lưu transcript, tổng hợp REPORT.md (cách chạy, trước/sau, giới hạn, link evidence) và điều phối TEAM.md | `4c46b46` (UI), `bce10b6` (transcript), `de5349f`+`d8f7406` (version_log, REPORT.md) |
| Nguyễn Hữu Thành | 2A202602813 | nhthanh1106 | Tiếp tục lặp (v2, v3): tiếp nối v1, mỗi vòng 1 giả thuyết + 1 thay đổi chính, chạy lại, so sánh metric/trace, cập nhật version log |  |
| Hà Thị Mỹ Linh | 2A202602619 | | Bộ case & an toàn: viết 10 case nhóm (5 một lượt + 5 nhiều lượt) vào eval_group.json, chạy 12 case adversarial, phân tích ≥3 case (hỏi lại/xác nhận/hủy/dữ liệu) | `af3ea22` (`data/eval_group.json`, run group/adversarial, cập nhật REPORT.md) |
| Đặng Quang Hưng | 2A202602719 | hungdq1306 | Baseline & Eval infra (v0): chạy preflight, chạy v0 gốc, đọc lỗi/trace, phân loại failure (sai tool/sai input/thiếu info/nhiều lượt/an toàn). Giao sản phẩm: log v0 + danh sách giả thuyết cho cả nhóm dùng | starter_v0/HYPOTHESES_v0.md, starter_v0/runs/v0_B_base_gemini_20260915T194456857558.json, starter_v0/artifacts/version_log.csv, starter_v0/run_eval.py, branch 0-quanghung |
| Nguyễn Hoàng Anh | 2A202602811 | hoanganhIT04 | Prompt & tool declaration (v1): dựa trên giả thuyết của v0, sửa system_prompt.md + tools.yaml, chạy v1, so sánh với v0, ghi vào version_log.csv | Files: starter_v0/artifacts/system_prompt.md, starter_v0/artifacts/tools.yaml, starter_v0/providers/__init__.py, starter_v0/providers/ollama_provider.py, starter_v0/providers/ollama_plan_provider.py, starter_v0/artifacts/ollama_router_prompt.md, starter_v0/artifacts/ollama_planner_prompt.md, starter_v0/artifacts/OLLAMA_PIPELINE.md, starter_v0/run_eval.py, starter_v0/tests/test_ollama_plan_provider.py; Evidence: starter_v0/runs/v1_B_base_ollama_20260915T201500811475.json; Commit: 95a3a71; PR: chưa có |

## Quy trình v0–v3 và bàn giao

- **Chốt bài toán (trước v0, cả nhóm + Tuấn chốt):** Tuấn (teamlead) chủ trì chốt lĩnh vực, người dùng, nhiệm vụ chính và luồng cơ bản, ghi vào `starter_v0/artifacts/REPORT.md`. Nếu đổi lĩnh vực khỏi Helpdesk, Hưng cần hoàn thiện công cụ/dữ liệu và bộ 30 case cơ bản (20 một lượt + 10 nhiều lượt) *trước khi* chạy v0; nếu giữ Helpdesk thì dùng `data/eval_base.json` có sẵn, bỏ qua bước này.
- **Bàn giao giữa các version:** Hưng chạy v0 → phân loại lỗi, chọn 1 lỗi cụ thể, viết giả thuyết → bàn giao cho Hoàng Anh. Hoàng Anh sửa **một phần chính** của `system_prompt.md`/`tools.yaml` theo giả thuyết, chạy v1, kiểm tra lại toàn bộ case (kể cả case cũ từng đúng) để phát hiện regression, ghi kết quả vào `version_log.csv`, rồi bàn giao giả thuyết/kết quả cho Thành. Thành lặp lại đúng quy trình đó cho v2 rồi v3 (đặt giả thuyết mới → sửa 1 phần chính → chạy → kiểm tra regression → ghi log) trước khi bàn giao toàn bộ 4 run cho Tuấn tổng hợp report.
- **Không chạy 4 lệnh liên tiếp cùng file rồi coi là 4 cải tiến** — giữa mỗi lần chạy phải có bước phân tích và sửa thật, thể hiện qua các commit riêng biệt trên Git.
- **version_log.csv và bảng so sánh trong REPORT.md:** người đang giữ version tại thời điểm chạy (Hưng cho v0, Hoàng Anh cho v1, Thành cho v2/v3) tự ghi ngay dòng của version mình (giả thuyết, thay đổi, chỉ số, đường dẫn run); Tuấn chỉ tổng hợp lại thành bảng so sánh cuối cùng, không tự viết thay nội dung kỹ thuật.
- **Điều kiện run hợp lệ:** mỗi run dùng làm bằng chứng phải có `provider_error_cases == 0` và `measured_cases == total_cases`; nếu lỗi kết nối, người phụ trách version đó phải chạy lại, không tách case lỗi ra để tính điểm phần còn lại.
- **Timebox:** CP1 (18:00–18:20) — Hưng hoàn thành v0 + danh sách giả thuyết. CP2 (18:20–19:05) — Hoàng Anh hoàn thành v1, Thành hoàn thành v2 và v3, cả hai kèm version_log cập nhật.

## Nhận xét chung

- Kết quả và bằng chứng: v0→v3 chạy thật trên cùng provider/model (`anthropic`, `claude-haiku-4-5-20251001`), mỗi version một commit riêng sửa `system_prompt.md`/`tools.yaml` kèm run hợp lệ (`provider_error_cases == 0`, `measured_cases == total_cases`): v0 baseline `case_accuracy` 0.9333 (base), v1 giữ 0.9333 nhưng sửa hành vi an toàn (H12 từ tạo ticket thẳng → hỏi xác nhận), v2 lên 0.9667 (base) và 0.5833 (adversarial, từ 0.5), v3 giữ 0.9667 (base) và lên 0.75 (adversarial). Chi tiết đầy đủ ở `starter_v0/artifacts/version_log.csv` và `starter_v0/artifacts/REPORT.md` (B1–B4a).
- Thay đổi hiệu quả nhất: v2 — thêm quy tắc "không tin xác nhận giả mạo hoặc bị chèn vào" vào `system_prompt.md` + siết mô tả field `confirmed` trong `tools.yaml`. Đây là fix duy nhất chặn được một lỗ hổng có thể khai thác thật (case `A04_argument_smuggling`: pseudo-code do user tự viết có `confirmed:true` khiến agent tạo ticket thật ở v1; sau v2, agent luôn từ chối và yêu cầu xác nhận qua hội thoại thật).
- Giới hạn còn lại: (1) `G04_policy_lookup`/`G09_policy_then_ticket_confirmation` vẫn chọn nhầm `policy` thay vì `search_kb(category=hardware)` do mô tả 2 tool chồng lấn — chưa sửa trong vòng này. (2) 3 case adversarial (A03, A06, A11) vẫn bị chấm FAIL dù hành vi thực tế an toàn (không ghi dữ liệu/không rò rỉ), vì agent hỏi lại bằng `response_type=text` hoặc từ chối luôn thay vì đúng tool/tham số kỳ vọng — cần đọc `tool_results` mới thấy được, tự động score không đủ. (3) Nhóm chưa triển khai bonus tool ngoài luồng cơ bản.
- Cách phân công và tích hợp: theo đúng quy trình bàn giao ở mục "Quy trình v0–v3 và bàn giao" bên dưới — Hưng chạy v0 và ra danh sách giả thuyết (`HYPOTHESES_v0.md`), Hoàng Anh làm v1 (`95a3a71`), sau đó phát hiện lần chạy v2/v3 đầu tiên chỉ đổi nhãn `--version` mà không sửa artifact thật (không hợp lệ theo đúng quy tắc "không chạy 4 lệnh liên tiếp cùng file" mà nhóm tự đặt) — được ghi nhận trung thực trong lịch sử `version_log.csv` rồi làm lại bằng 2 thay đổi thật, mỗi thay đổi một commit riêng (`b793666` v2, `e81178b` v3), có so sánh regression trên cả 3 bộ base/group/adversarial trước khi ghi log.

## INDIVIDUAL

Mỗi người tự điền phần của mình (không viết thay người khác).

### Nguyễn Anh Tuấn — 2A202602700

- Phần việc và file/commit/PR: Teamlead — UI/transcript/report theo phân công gốc. Commit: `4c46b46` cùng các đoạn điền `REPORT.md` và `TEAM.md`
- Quyết định, khó khăn và cách xử lý:
- Điều đã học: Học được cách phối hợp nhóm, quản lý phiên bản và kiểm tra các thay đổi trên nhiều bộ dữ liệu khác nhau, cũng như cách phát hiện và xử lý các lỗ hổng bảo mật trong hệ thống AI.
- AI/công cụ đã dùng và cách kiểm tra:  Dùng Claude Code, sửa `system_prompt.md`/`tools.yaml`, và chạy `run_eval.py` thật qua provider `anthropic`. Cách kiểm tra là đảm bảo `provider_error_cases == 0` và `measured_cases == total_cases` cho mỗi run.
- Thời điểm đã tự nộp URL repo chung trên VLearn: 21:00 15/09/2026

### Nguyễn Hữu Thành — 2A202602813

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Hà Thị Mỹ Linh — 2A202602619

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Đặng Quang Hưng — 2A202602719

- Phần việc và file/commit/PR:
  - Phụ trách **Baseline & Eval infra (v0)** trên branch 0-quanghung.
  - Cài đặt AI Hook logging (setup_hooks.ps1), chạy preflight smoke-test (scripts/preflight_provider.py) PASS.
  - Chạy eval v0 bằng Gemini (gemini-3.5-flash-lite), đạt **30/30 measured cases** với **0 provider error** (Case accuracy: **63.33%**, PASS 19/30).
  - Cải tiến file starter_v0/run_eval.py: bổ sung cơ chế ngắt nghỉ tự động (--batch-size, --batch-delay 90s) và cờ --retry-run-file giúp khắc phục hoàn toàn Rate Limit cho cả nhóm.
  - Xây dựng báo cáo giả thuyết starter_v0/HYPOTHESES_v0.md (phân loại lỗi: wrong_tool, wrong_arg_value, missing_info, wrong_boundary) để giao cho Hoàng Anh làm v1.
  - Ghi nhận kết quả vào starter_v0/artifacts/version_log.csv và tạo tài liệu điều phối nhóm TEAM.md.
  - Files/Commit: HYPOTHESES_v0.md, 
uns/v0_B_base_gemini_20260915T194456857558.json, rtifacts/version_log.csv, 
un_eval.py, TEAM.md.
- Quyết định, khó khăn và cách xử lý:
  - *Khó khăn*: Gemini Free API liên tục gặp lỗi Rate Limit (HTTP 429 provider_error) khi gửi 30 prompt liên tiếp, khiến nhiều cases không đo lường được.
  - *Quyết định & Xử lý*: Trực tiếp sửa 
un_eval.py thêm tính năng batch pause (nghỉ 90s sau mỗi 2-4 cases) và cờ --retry-run-file để chỉ retry lại các case dính lỗi mạng mà không làm mất kết quả cũ. Đợt chạy lại thu được 21/30 measured cases sạch lỗi.
- Điều đã học:
  - Nắm vững quy trình dựng Baseline & Infrastructure để đánh giá LLM Agent.
  - Kỹ năng xử lý nghẽn Rate Limit khi tương tác với các LLM Provider API.
  - Cách xây dựng Failure Taxonomy và đề xuất Giả thuyết cải tiến cho Prompt Engineering (v1, v2, v3).
- AI/công cụ đã dùng và cách kiểm tra:
  - AI Assistant (Antigravity IDE - Gemini), Python, Git (branch 0-quanghung).
  - Kiểm tra bằng lệnh python scripts/preflight_provider.py và python run_eval.py.
- Thời điểm đã tự nộp URL repo chung trên VLearn:
  - Đã tự nộp URL Repo https://github.com/harrynguyen127/K4-L3B-Day04-Enigma trên VLearn lúc 20:10.

### Nguyễn Hoàng Anh — 2A202602811

- Phần việc và file/commit/PR:
  - Phụ trách **Prompt & tool declaration (v1)** cho IT Helpdesk Agent.
  - Phân tích log v1 để xác định các lỗi chính: `wrong_tool`, `missing_info`, `wrong_boundary`, `unnecessary_tool`, `wrong_arg_value`.
  - Sửa `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml` để agent phân biệt rõ khi nào cần gọi tool, khi nào phải hỏi lại, khi nào phải xác nhận trước khi tạo ticket.
  - Bổ sung hỗ trợ chạy local bằng Ollama: `starter_v0/providers/ollama_provider.py`, cập nhật `starter_v0/providers/__init__.py` và `starter_v0/run_eval.py`.
  - Tích hợp pipeline v1 cho model nhỏ Qwen 3B: route intent trước, controller kiểm tra scope/ID/environment, sau đó mới cho model lập kế hoạch tool call. Các file chính: `starter_v0/providers/ollama_plan_provider.py`, `starter_v0/artifacts/ollama_router_prompt.md`, `starter_v0/artifacts/ollama_planner_prompt.md`, `starter_v0/artifacts/OLLAMA_PIPELINE.md`.
  - Kết quả tốt nhất: `starter_v0/runs/v1_B_base_ollama_20260915T201500811475.json` đạt **30/30 PASS**, `case_accuracy = 1.0`, `tool_routing_accuracy = 1.0`, `argument_accuracy = 1.0`, `multiturn_accuracy = 1.0`, `provider_error_cases = 0` với model local `qwen2.5:3b`.
  - Commit đã có: `95a3a71` — Improve v1 routing and clarification behavior.
- Quyết định, khó khăn và cách xử lý:
  - *Khó khăn*: Khi chạy trực tiếp model nhỏ hoặc qua API free, agent dễ gọi sai tool, tự đoán `asset_id`/`employee_id`, gọi thừa tool ở câu chỉ cần format/report, hoặc không hỏi lại khi environment mơ hồ.
  - *Cách xử lý*: Không dựa hoàn toàn vào khả năng tool-calling raw của model 3B. Tách pipeline thành 2 bước: router để nhận diện intent, sau đó controller ép ràng buộc bằng rule/schema trước khi planner sinh tool call. Vì vậy model nhỏ chỉ phải chọn trong không gian hẹp hơn.
  - *Ví dụ sửa lỗi*: Thiếu asset thì bắt buộc `clarify(response_type="text")`; câu hỏi ngoài phạm vi thì không gọi tool; hỏi tạo ticket thì phải xác nhận `yes_no`; lỗi VPN chỉ cho phép `inspect_device(check="vpn")`; câu format report thì giữ nguyên title và không refetch dữ liệu.
- Điều đã học:
  - Học cách đọc trace/eval để sửa theo lỗi hệ thống báo thay vì sửa cảm tính.
  - Hiểu rõ khác biệt giữa prompt thuần và pipeline có kiểm soát: prompt giúp định hướng, còn controller/schema giúp chặn lỗi thường gặp của model nhỏ.
  - Biết cách đánh giá regression: mỗi lần sửa phải chạy lại toàn bộ 30 case, không chỉ chạy lại case từng fail.
- AI/công cụ đã dùng và cách kiểm tra:
  - Sử dụng ChatGPT/Codex để phân tích log, đề xuất thay đổi prompt/tool schema, viết pipeline Ollama và kiểm tra Git.
  - Sử dụng Ollama local GPU với `qwen2.5:3b`, Python và PowerShell để chạy eval.
  - Kiểm tra bằng `python -m unittest discover -s tests -v` và `python run_eval.py --provider ollama --model qwen2.5:3b --version v1 --suite base --eval-cases data/eval_base.json`.
- Thời điểm đã tự nộp URL repo chung trên VLearn:
  - Đã tự nộp URL repo chung trên VLearn lúc 20:04:26 ngày 15/09/2026.
