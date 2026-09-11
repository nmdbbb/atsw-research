# ATSW — biểu diễn tái sử dụng cho adapted OT

Nghiên cứu biểu diễn cấu trúc thông tin của quá trình ngẫu nhiên để chứng nhận
quan hệ gần–xa theo adapted OT với chi phí thấp. Đích là kết quả về kích thước
biểu diễn, độ sắc bảo đảm và chi phí quyết định.

- [Tài liệu thống nhất](docs/README.md): mục tiêu, kiến thức, phương pháp, bằng chứng và thí nghiệm.
- [Bắt đầu phiên](START_HERE.md): entrypoint cho PO và agent.
- [Quy trình](WORKFLOW.md): lựa chọn đầu tư, kiểm claim, điều phối và phục hồi.
- [Checkpoint](status.orchestrator.json): task và kế hoạch hiện hành.

Code candidate ở adapters/; oracle/checkers ở tools/, certify/ và tests/.
objective.json cùng ledger/contract.json giữ hợp đồng mục tiêu. Hồ sơ proof,
review và run là evidence được dẫn từ tài liệu, có phạm vi hiệu lực riêng.
