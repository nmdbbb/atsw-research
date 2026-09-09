# Nguồn deck ATSW

Mở `../atsw-deck-de-hieu.html` trực tiếp bằng trình duyệt. Deck tự chứa HTML, CSS, JavaScript và các hình SVG; không cần mạng để đọc hoặc dùng tương tác. Đặt `paper.pdf` cùng thư mục để mở liên kết về trang nguồn.

- `content.js`: nội dung 55 slide và 8 bảng tra cứu từ PDF.
- `style.css`: bố cục phần bản chất ở trên, đặc điểm ở dưới; màn hình nhỏ và bản in.
- `ui.js`: điều hướng, tìm kiếm, chế độ đọc, biểu đồ và ví dụ tương tác.
- `build.py`: ghép nguồn thành một HTML độc lập; chạy `python deck-source/build.py` từ thư mục build.
- `verify.py`: kiểm tra bằng Chrome headless qua Playwright; chạy `python deck-source/verify.py`.
- `verification/`: báo cáo kiểm tra, ảnh màn hình và PDF kiểm tra phân trang.

Các ví dụ số bổ sung và biểu đồ mô phỏng được ghi rõ trong slide, tách khỏi số liệu paper. Kết quả Lean và thực nghiệm của paper chưa được chạy lại vì workspace không có source hoặc result files.

Bản cũ được giữ ở `../atsw-deck-de-hieu.backup.html`.
