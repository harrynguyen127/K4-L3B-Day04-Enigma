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
| Đặng Quang Hưng | 2A202602719 | hungdq1306 | Baseline & Eval infra (v0): chạy preflight, chạy v0 gốc, đọc lỗi/trace, phân loại failure (sai tool/sai input/thiếu info/nhiều lượt/an toàn). Giao sản phẩm: log v0 + danh sách giả thuyết cho cả nhóm dùng | `48c2f3e` (`HYPOTHESES_v0.md`), `e626aca` (`version_log.csv` dòng v0) |
| Nguyễn Hoàng Anh | 2A202602811 | hoanganhIT04 | Prompt & tool declaration (v1): dựa trên giả thuyết của v0, sửa system_prompt.md + tools.yaml, chạy v1, so sánh với v0, ghi vào version_log.csv | `95a3a71` (`system_prompt.md`, `tools.yaml`) |

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

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

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
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Nguyễn Hoàng Anh — 2A202602811

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:
