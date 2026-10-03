# iGOLab
interactive Geometrical Optics Laboratory

افتح index.html لتشغيل المحاكي. الإصدار igolab-name-rc1 مبني على aperture-fix-rc2.
تغير عنوان الصفحة والعنوان الظاهر وبيانات تعريف التطبيق فقط؛ JavaScript وCSS مطابقان تماماً لنسخة RC2.

## نتائج التحقق الجديدة
- المقارنات العددية 164/164؛ فحوص البؤرة 232/232؛ فحوص حالة الفتحة 12/12.
- فحص صياغة 31 نص JavaScript.
- Chromium 134.0.6998.35، Linux، Playwright 1.51.0، تشغيل headless: الأساسي 13/13، البؤرة 21/21، الفتحة 5/5، وخمسة أحجام شاشة محاكاة.
- النتائج الجديدة في corrected_browser_results وaperture_results_*؛ النتائج الأصلية في المجلدات المجاورة محفوظة كما وردت.

## إعادة التشغيل
نفذ node run_numeric.cjs ثم node test_focal_numeric.cjs ثم node test_aperture.cjs.
على Windows مع Edge استخدم RUN_FINAL_BROWSER_CHECKS.cmd بعد تثبيت playwright.
لفحوص البؤرة والفتحة في بيئة أخرى يمكن تحديد IGOLAB_BROWSER لمسار المتصفح وIGOLAB_HEADLESS=1 للتشغيل دون نافذة. المشغل الأساسي يقبل --executable.

صيغة المشاريع GeometricalOpticsInteractiveLabProject وامتداد .opticslab ومعرّفات الواجهة القديمة محفوظة للتوافق مع المشاريع والاختبارات السابقة؛ ليست الاسم المعروض للبرنامج.
