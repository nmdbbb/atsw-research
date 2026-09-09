from pathlib import Path
import json

root = Path(__file__).resolve().parent
css = (root / 'style.css').read_text(encoding='utf-8')
content = (root / 'content.js').read_text(encoding='utf-8')
ui = (root / 'ui.js').read_text(encoding='utf-8')
html = '''<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Đọc sâu paper ATSW: bản chất, toán từng bước, ví dụ tương tác và toàn bộ kết quả của bản thảo.">
<title>ATSW — Hiểu từ bên trong</title><style>''' + css + '''</style></head>
<body><header><a class="brand" href="#1" aria-label="Về trang đầu">A<span>↗</span> <b>ATSW</b><small>ĐỌC TỪ BẢN CHẤT</small></a>
<div class="header-actions"><button id="toc-toggle" aria-expanded="false" aria-controls="toc">☰ <span>Mục lục</span></button><button id="reading-toggle" aria-pressed="false">Đọc liền</button><button id="print">In / PDF</button></div></header>
<aside id="toc" hidden><div class="toc-head"><h2>Lộ trình đọc</h2><button id="toc-close" aria-label="Đóng mục lục">×</button></div><input id="search" type="search" placeholder="Tìm khái niệm, ví dụ, kết quả…" aria-label="Tìm slide"><nav id="toc-list" aria-label="Mục lục slide"></nav></aside>
<main id="deck"></main><footer><div class="foot-left"><span id="chapter-name"></span><span class="keyboard">← → chuyển slide · M mục lục</span></div><div class="navigation"><button id="prev" aria-label="Slide trước">←</button><label class="page-label"><input id="page-number" type="number" min="1" aria-label="Đến slide"> <span id="page-total"></span></label><button id="next" aria-label="Slide sau">→</button></div></footer><div id="progress"></div>
<noscript>Deck cần JavaScript để hiển thị các slide và ví dụ tương tác.</noscript><script>''' + content + '\n' + ui + '</script></body></html>'
(root.parent / 'atsw-deck-de-hieu.html').write_text(html, encoding='utf-8')
print('Built atsw-deck-de-hieu.html:', len(html), 'characters')
