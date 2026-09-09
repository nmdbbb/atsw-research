from pathlib import Path
from playwright.sync_api import sync_playwright
import json

root = Path(__file__).resolve().parent.parent
out = root / 'deck-source' / 'verification'
out.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe', headless=True)
    page = browser.new_page(viewport={'width':1440,'height':900}, device_scale_factor=1, reduced_motion='reduce')
    errors=[]
    page.on('pageerror',lambda error: errors.append(str(error)))
    page.goto((root/'atsw-deck-de-hieu.html').as_uri())
    page.wait_for_selector('.slide.active')
    count = page.locator('.slide').count()
    assert count > 40
    assert page.locator('.slide .essence').count() == count
    assert page.locator('.slide .traits').count() == count
    dimensions=[]
    for i in range(count):
        page.evaluate('(i)=>go(i)',i)
        dimensions.append(page.evaluate('''()=>({slide:current+1,title:slides[current].title,height:document.querySelector('.slide.active').getBoundingClientRect().height,
        overlap:document.querySelector('.slide.active .essence').getBoundingClientRect().bottom>document.querySelector('.slide.active .traits').getBoundingClientRect().top+1,
        horizontal:document.documentElement.scrollWidth>innerWidth+1})'''))
    assert not any(x['overlap'] or x['horizontal'] for x in dimensions),dimensions
    page.evaluate('go(0)')
    page.keyboard.press('ArrowRight')
    assert page.locator('#page-number').input_value()=='2'
    page.locator('#toc-toggle').click()
    page.locator('#search').fill('min/max')
    assert page.locator('.toc-link').count()>0
    page.locator('#toc-close').click()
    page.evaluate("go(slides.findIndex(s=>s.title.startsWith('Coupling là')))")
    page.locator('#coupling-a').evaluate("e=>{e.value='0.25';e.dispatchEvent(new Event('input'))}")
    assert '1,00' in page.locator('#coupling-result').inner_text()
    page.evaluate("go(slides.findIndex(s=>s.title.startsWith('Tự tính adapted')))")
    page.locator('#epsilon').evaluate("e=>{e.value='0.01';e.dispatchEvent(new Event('input'))}")
    assert '1,01' in page.locator('#epsilon-viz').inner_text()
    page.evaluate("go(slides.findIndex(s=>s.title.startsWith('Cùng một U')))")
    page.locator('#quantile-u').evaluate("e=>{e.value='0.75';e.dispatchEvent(new Event('input'))}")
    assert 'X = 2, Y = 1' in page.locator('#quantile-u-result').inner_text()
    page.evaluate("go(slides.findIndex(s=>s.title.startsWith('Cửa sổ k:')))")
    page.locator('[data-window="3"]').click()
    assert 'khác cửa sổ' in page.locator('#window-result').inner_text()
    page.evaluate("go(slides.findIndex(s=>s.title.startsWith('Lượng tử hóa:')))")
    page.locator('#grid-x').evaluate("e=>{e.value='-0.1';e.dispatchEvent(new Event('input'))}")
    assert '= -1;' in page.locator('#grid-result').inner_text()
    page.evaluate("go(slides.findIndex(s=>s.title.startsWith('Thực nghiệm chỉ')))")
    page.locator('.slide.active .open-tables').click()
    for i,n in enumerate([9,8,13,6,8,4,5,16]):
        page.locator('#table-select').select_option(str(i))
        assert page.locator('#paper-table-body tbody tr').count()==n
    page.locator('#tables-close').click()
    page.evaluate("go(slides.findIndex(s=>s.title.startsWith('Bạn đã hiểu bicausality')))")
    page.locator('.slide.active [data-choice="1"]').click()
    assert page.locator('.slide.active .quiz-feedback').inner_text().startswith('Đúng')
    sim = page.evaluate('window.limitSimulation')
    assert abs(sim['mean']-.4514)<.012,sim
    for keyword,name in [('So sánh hai','01-opening'),('Cùng một U','02-quantile'),('Viết lại thuật toán','03-recursion'),('Bước 4:','04-proof'),('Hình dạng giới hạn','05-limit')]:
        page.evaluate('(k)=>go(slides.findIndex(s=>s.title.startsWith(k)))',keyword)
        page.screenshot(path=str(out/(name+'.png')),full_page=True)
    page.locator('#reading-toggle').click()
    assert page.locator('body.reading').count()==1
    assert page.locator('.slide:visible').count()==count
    page.locator('#reading-toggle').click()
    page.set_viewport_size({'width':390,'height':844})
    mobile=[]
    for i in range(count):
        page.evaluate('(i)=>go(i)',i)
        if page.evaluate('document.documentElement.scrollWidth>innerWidth+1'):mobile.append(i+1)
    assert not mobile,mobile
    page.evaluate("go(slides.findIndex(s=>s.title.startsWith('Cùng một U')))")
    page.screenshot(path=str(out/'06-mobile.png'),full_page=True)
    page.set_viewport_size({'width':1440,'height':900})
    page.emulate_media(media='print')
    page.pdf(path=str(out/'print-check.pdf'),prefer_css_page_size=True,print_background=True)
    assert not errors,errors
    result={'slides':count,'desktop_slides_requiring_vertical_scroll':[x for x in dimensions if x['height']>770], 'mobile_horizontal_overflow':mobile,'javascript_errors':errors,'limit_simulation':sim,'checks':'navigation, search, probability coupling, epsilon, quantile, window, negative floor, 8 tables, quiz, reading mode, mobile and print'}
    (out/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True,indent=2))
    browser.close()
