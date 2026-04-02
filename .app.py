import streamlit as st
import google.generativeai as genai
import base64
import random

# --- ١. ڕێکخستنی سەرەکی ---
st.set_page_config(page_title="وەرگێڕی شێوەزارە کوردییەکان", page_icon="☀️", layout="centered")

def get_base_64(file):
    try:
        with open(file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except: return ""

logo = get_base_64("logo.gif")
search_icon = get_base_64("search.gif")

# --- ٢. داتای وشەکان و ڕێنمایی وەرگێڕان ---
K_BASE = """
تۆ پسپۆڕی زمانی کوردیت، شارەزایی تەواوت هەیە لە هەموو شێوەزارەکان، وشە ئەکادیمی و فۆلکلۆریەکان دەزانیت
زۆر وردی لە وەرگێڕان، بێ ئەوەی هیچی زیاد بنوسیت ڕستەکە وەک کەسێکی شارەزا له (لوڕی و هەورامی و kurmancî و
zazakî و سۆرانی) وەردەگێڕیت
١. لە وەرگێڕاندا: تەنها وەڵامە وەرگێڕدراوەکە بنووسە.
٢. لە ڕێنووسدا: دەقەکە لە پیتی ئارامییەوە بگۆڕە بۆ لاتینی، یان بەپێچەوانەوە (بەپێی دەقەکە) تەنها لەڕووی ڕێنوسەوە بیگۆڕە نەوەک شێوەزار، بۆ نمونە 
(سڵاو چۆنیت من ناوم ئەحمەدە ←slaw chonit mn nawm ahmede) کاری تۆ تەنها گۆڕینی ڕێنوسە لێرەدا نەوەک وەرگێڕان.
.٣. لە گۆڕینی ژمارە بۆ شێوەزارەکان ورد بە، شێوەزارەکان تێکەڵ مەکە.
.٤. سۆرانی و هەورامی و لوڕی پیتی ئارامین، kurmancî و zazakî لاتینی.
وشەکان:
- خەو: (H:وەرەم, Z:Hewn). پێڵاو: (H:کڵاش/کاڵە, L:کەوش). 
    - زۆر: (K:Gelek, L:فرە, Z:Zof/Zaf). کەم: (H:کەمێ, Z:Şenik).
    - منداڵ: (H:زارۆڵە, L:بچەک, K:Zarok). کچ: (H:کناچە, L:دۆێت, K:Keç).
    - باش: (H:خاس, L:خاس, K:Rind/Baş). جوان: (H:ڕەنگین, L:قەشەنگ, K:Bedew).
    - بەیانی (Tomorrow): (K:Sibê, Z:Meşte). ئێستا: (H:ئیسە, L:ئیسە, K:Niha).
    - بۆچی: (H:پەی چێشی, L:ئەڕا چە, K:Çima). چۆن: (H:چەنی, L:چۊن, K:Çawa).
    - سپاس: (K:Spas, Z:Berxudar be). بەڵێ: (Z:Eya, K:Erê). نەخێر: (Z:Nê, K:Na).
    - نان: (H:نان, L:نۊن, Z:Sifre). ئاو: (H:ئاو, L:ئاو, Z:Awe)..
    - وەرە: (H:بەو, L:بیا). بڕۆ: (H:لوە, L:بچوو).
    - گەورە: (H:گۆرە, L:گەپ, K:Mezin). بچووک: (H:ورتە, L:قیتە, K:Biçûk).
    - تەڕ: (H:خیوس). ئاوێنە: (H:وینەنمای). دۆست: (Z:Olbaz/Embaz).
    - مریشک: (H:کەرگە, L:کەرک). منداڵ: (H:زارۆڵە, L:چەکەڵ, K:Zarok). نان: (H:نان, L:نۊن, Z:Sifre).
    - کچ: (H:کناچە, L:دۆێت, K:Keç). کوڕ: (H:کوڕە, L:کۆڕ). باوک: (H:بابە, L:بووە). دایک: (H:ئەدە, L:داڵک).
    - برا: (H:تاتا, L:برار). خوشک: (H:واڵە, L:خوەشک). خواردن: (H:واردەی, L:هۆردەن). ڕۆیشتن: (H:لوای, L:ڕەدە).
    - هێلکە: (H:هێڵە, L:خا). لووت: (H:لووتە, L:پۆز). چاو: (H:چەم, L:تیە). قاچ: (H:پا, L:قۆڵ).
    - ئێستا: (H:ئیسە, L:ئیسە). بەیانی: (H:سەحەر, L:سوو). گەورە: (H:گۆرە, L:گەپ). جوان: (H:ڕەنگین, L:قەشەنگ).
    - بۆچی: (H:پەی چێشی, L:ئەڕا چە). چۆن: (H:چەنی, L:چۊن). بەیانی (سبەی): (K:Sibê, Z:Meşte).
    - تەواو: (Z:Qediya). کەم: (K:Hindik, Z:Şenik). زۆر: (K:Gelek, Z:Zof). پێکەنین: (K:Kenîn, Z:Huyayene).
    - گریان: (H:بەرمە, K:Girîn, Z:Bermayiş). پێکەنین: (K:Kenîn, Z:Huyayiş, H:خەنە).
- سوێر: (H:سۆر, L:شۊر, K:Şor, Z:Solin). خۆشەویستی: (K:Evîn, Z:Heskerdene, H:وەشەویسی).
- هاوڕێ: (L:دۆس, K:Heval, Z:Embaz, H:ڕەفێق). مێرد: (H:شوی, K:Mêr, Z:Mêrdek).
- خەزوور: (H:وەسیە, K:Xezûr, Z:Vesur). بووک: (H:وەیوە, L:بۊگ, K:Bûk, Z:Veyve).
- زاوا: (K:Zava, Z:Zama). پرسیار: (H:پەرسار, K:Pirs, Z:Pers). وەڵام: (K:Bersiv).
- ڕاست: (Z:Raşt). درۆ: (L:درۊ, K:Derew, Z:Zûr). ڕۆیشتن: (H:لوای, L:ڕۊین, K:Çûn, Z:Şiyayiş).
- دانیشتن: (K:Rûniştin, Z:Roniştiş, H:نیشتەی). هەستان: (H:هۆرزای, L:هەسان, K:Rabin, Z:Werziştiş).
- نووستن: (H:وەتەی, L:خەفتن, K:Razan, Z:Rakewtiş). کراس: (H:کەوا).
- شەرواڵ: (H:پانتۆڵ). سمێڵ: (H:سێپاڵە, K:Simêl, Z:Simbêl). مل: (K:Stû).
- سک: (H:زگ, K:Zik). سنگ: (K:Sîng, Z:Sêne). قۆڵ: (K:Mil, Z:Bask).
- گەدە: (K:Aşîk, Z:Mide). جگەر: (K:Keze). پەنجە: (K:Tilî, Z:Bişte).
- نینۆک: (H:ناخوون, K:Neynok, Z:Ningi). قورس: (K:Giran). سووک: (L:سۊک, K:Sivik).
- درێژ: (L:دریژ, Z:Derx). کورت: (H:کوڵ, Z:Kilim). تەنک: (K:Zirav).
- ئەستوور: (L:ئەستۊر, K:Stûr, Z:Oç). تفت: (K:Tif). زوو: (L:زۊ, Z:Rew).
- درەنگ: (H:دێر, K:Dereng, Z:Ere). تاریک: (K:Tarî). ڕووناک: (H:ڕۆشن, K:Ronî, Z:Aşti).
- بەرز: (K:Bilind). قوڵ: (L:قۊڵ, K:Kûr, Z:Xorî). تەنیا: (K:Bi tenê, Z:Teyna).
- پێکەوە: (H:پێوە, L:وەگەردیەک, K:Bi hev re, Z:Pêra). نزیک: (Z:Nezdî). دوور: (L:دۊر, Z:Dûrî).
- لێرە: (H:چێگە, K:Li vir, Z:Tiya). لەوێ: (H:چەولای, K:Li wir, Z:Uca). ژیان: (H:ژیای, Z:Ciwîyayiş).
- شەڕ: (H:جەنگ, Z:Ceng). برسی: (H:وێسی, K:Birçî, Z:Veyşan). تینوو: (H:تەژنە, L:تێنی, K:Tî, Z:Têşan).
- تێر: (Z:Mird). ترس: (H:تەرسێ, K:Tirs, Z:Ters). هێز: (H:تاقەت, K:Hêz, Z:Qewet).
- پەلە: (H:شتاو, K:Lez). چاوەڕێ: (H:چەمەڕا, K:Li bendê, Z:Pepa). جێگا: (H:یاگە, K:Cih, Z:Caa).
- ڕەگ: (K:Reh, Z:Rîşe). لق: (H:چڵ, K:Şax). گۆزە: (H:کەنوو, K:Kûz, Z:Dîze).
- کلیل: (K:Mifte, Z:Kilît). دیوار: (Z:Dês). سەقف: (H:بان, L:بان, K:Bani, Z:Bane).
- حەوشە: (H:حەوشێ, K:Hewş). دراوسێ: (H:هەمسایە, L:هاوسا, K:Cîran). میوان: (H:مێمان, L:میەمان, K:Mêvan, Z:Meyman).
- گۆڕانکاری: (H:فاڕیای, L:ئاڵشتکاری, K:Guhertin, Z:Vuriyayiş). نەخۆش: (H:وەشەو, K:Nexweş, Z:Nêweş).
- دەرمان: (H:دەوا). پزیشک: (H:حەکیم, K:Nijdar). خوێندن: (H:وەنەی, L:خوەنین, Z:Wendene).
- یاری: (K:Lîstik, Z:Kay). گۆرانی: (K:Stran, Z:Klam). هەڵپەڕکێ: (L:چووپی, K:Govend, Z:Govende).
- شمشێر: (K:Şûr). ئەڵقە: (K:Gusti). گوارە: (K:Guhar, Z:Goşare). ملوانکە: (H:گەردەنە, K:Gerdenî, Z:Gerdeniye).
​گریان: (H: بەرمە، K: Girîn، Z: Bermayiş)
​پێکەنین: (H: خەنە، L: خەنە، K: Kenîn، Z: Huyayiş)
​سوێر: (H: سۆر، L: شۊر، K: Şor، Z: Solin)
​زەوی: (H: زەمین، L: زەمین، K: Zevî، Z: Zemîn)
​خۆشەویستی: (H: وەشەویسی، L: خوەشەویسی، K: Evîn، Z: Heskerdene)
​هاوڕێ: (H: ڕەفێق، L: دۆس، K: Heval، Z: Embaz)
​مێرد: (H: شوی، K: Mêr، Z: Mêrdek)
​خەزوور: (H: وەسیە، L: خەسۊر، K: Xezûr، Z: Vesur)
​بووک: (H: وەیوە، L: بۊگ، K: Bûk، Z: Veyve)
​زاوا: (K: Zava، Z: Zama)
​پرسیار: (H: پەرسار، K: Pirs، Z: Pers)
​وەڵام: (H: جەواب، L: جەواو، K: Bersiv، Z: Cewab)
​ڕاست: (H: ڕاس، L: ڕاس، K: Rast، Z: Raşt)
​درۆ: (L: درۊ، K: Derew، Z: Zûr)
​ڕۆیشتن: (H: لوای، L: ڕۊین، K: Çûn، Z: Şiyayiş)
​دانیشتن: (H: نیشتەی، L: نیشتن، K: Rûniştin، Z: Roniştiş)
​هەستان: (H: هۆرزای، L: هەسان، K: Rabin، Z: Werziştiş)
​نووستن: (H: وەتەی، L: خەفتن، K: Razan، Z: Rakewtiş)
​کراس: (H: کەوا، K: Kiras، Z: Kiras)
​شەرواڵ: (H: پانتۆڵ، K: Şelwal، Z: Şelwal)
​مل: (K: Stû، Z: Mil)
​سک: (H: زگ، L: زگ، K: Zik، Z: Zik)
​سنگ: (H: سینە، K: Sîng، Z: Sêne)
​قۆڵ: (K: Mil، Z: Bask)
​گەدە: (H: مەعیدە، K: Aşîk، Z: Mide)
​جگەر: (H: جەرگ، L: جەرگ، K: Keze، Z: Ceger)
​پەنجە: (H: پنچە، K: Tilî، Z: Bişte)
​نینۆک: (H: ناخوون، L: نینۆگ، K: Neynok، Z: Ningi)
​قورس: (K: Giran، Z: Giran)
​سووک: (H: سوک، L: سۊک، K: Sivik، Z: Sivik)
​درێژ: (L: دریژ، K: Dirêj، Z: Derx)
​کورت: (H: کوڵ، L: کوڵ، K: Kurd، Z: Kilim)
​تەنک: (K: Zirav، Z: Tenik)
​ئەستوور: (L: ئەستۊر، K: Stûr، Z: Oç)
​زوو: (L: زۊ، K: Zû، Z: Rew)
​درەنگ: (H: دێر، L: دێر، K: Dereng، Z: Ere)
​قوڵ: (H: قووڵ، L: قۊڵ، K: Kûr، Z: Xorî)
​تەنیا: (K: Bi tenê، Z: Teyna)
​پێکەوە: (H: پێوە، L: وەگەردیەک، K: Bi hev re، Z: Pêra)
​نزیک: (H: نێزیک، L: نێزیک، K: Nêzîk، Z: Nezdî)
​دوور: (L: دۊر، K: Dûr، Z: Dûrî)
​لێرە: (H: چێگە، L: ئێرە، K: Li vir، Z: Tiya)
​لەوێ: (H: چەولای، L: ئەوێ، K: Li wir، Z: Uca)
​ژیان: (H: ژیای، K: Jiyan، Z: Ciwîyayiş)
​شەڕ: (H: جەنگ، K: Şer، Z: Ceng)
​برسی: (H: وێسی، K: Birçî، Z: Veyşan)
​تینوو: (H: تەژنە، L: تێنی، K: Tî، Z: Têşan)
​تێر: (K: Têr، Z: Mird)
​ترس: (H: تەرسێ، K: Tirs، Z: Ters)
​هێز: (H: تاقەت، K: Hêz، Z: Qewet)
​پەلە: (H: شتاو، K: Lez، Z: Lez)
​چاوەڕێ: (H: چەمەڕا، L: چەوەڕێ، K: Li bendê، Z: Pepa)
​جێگا: (H: یاگە، L: جێ، K: Cih، Z: Caa)
​ڕەگ: (H: ڕیشە، K: Reh، Z: Rîşe)
​لق: (H: چڵ، K: Şax، Z: Liq)
​گۆزە: (H: کەنوو، K: Kûz، Z: Dîze)
​کلیل: (K: Mifte، Z: Kilît)
​دیوار: (K: Dîwar، Z: Dês)
​سەقف: (H: بان، L: بان، K: Bani، Z: Bane)
​دراوسێ: (H: هەمسایە، L: هاوسا، K: Cîran، Z: Cîran)
​میوان: (H: مێمان، L: میەمان، K: Mêvan، Z: Meyman)
​گۆڕانکاری: (H: فاڕیای، L: ئاڵشتکاری، K: Guhertin، Z: Vuriyayiş)
​نەخۆش: (H: وەشەو، L: نەخوەش، K: Nexweş، Z: Nêweş)
​دەرمان: (H: دەوا، K: Derman، Z: Derman)
​پزیشک: (H: حەکیم، L: دکتۆر، K: Nijdar، Z: Doktor)
​خوێندن: (H: وەنەی، L: خوەنین، K: Xwendin، Z: Wendene)
​یاری: (H: بازی، L: بازی، K: Lîstik، Z: Kay)
​گۆرانی: (K: Stran، Z: Klam)
​هەڵپەڕکێ: (L: چووپی، K: Govend، Z: Govende)
​قەڵغان: (K: Mertal، Z: Qelxan)
​گوارە: (H: گۆشەوارە، K: Guhar، Z: Goşare)
​ملوانکە: (H: گەردەنە، K: Gerdenî، Z: Gerdeniye)
​ڕاکردن: (H: تەردەی، L: تەقانن، K: Bezîn، Z: Remayiş)
​فڕین: (H: فڕیەی، K: Firîn، Z: Perayiş)
​سووتان: (H: سۆچیای، L: سزیان، K: Şewitîn، Z: Vêşayiş)
​کڕین: (H: ئەسیەی، L: سەنن، K: Kirîn، Z: Eritiş)
​فرۆشتن: (H: وەردەی، L: فرۊتن، K: Firotin، Z: Rotiş)
​دۆزینەوە: (H: ئێستەی، L: پەیاکردن، K: Dîtin، Z: Diyayiş)
​شکان: (H: مڕیای، K: Şikestin، Z: Şikiyayiş)
​بەستن: (H: بەستەی، L: بەسن، K: Girêdan، Z: Girediş)
​بیستن: (H: ئەژنەویەی، L: ژنەفتن، K: Bîhîstin، Z: Eşnawitiş)
​بۆنکردن: (H: بۆکەردەی، L: بۊکردن، K: Bêhnkirin، Z: Bokerdene)
​قەڵەو: (K: Qelew، Z: Xişn)
​لاواز: (H: زەعیف، L: لاغەر، K: Zeyîf، Z: Zeîf)
​شێت: (K: Dîn، Z: Xêc)
​ژیر: (H: عاقڵ، L: عاقڵ، K: Jîr، Z: Aqilmend)
​پیس: (L: چەپەڵ، K: Gemar، Z: Leymin)
​هەژار: (H: فەقیر، L: دەسکوتا، K: Hejar، Z: Feqîr)
​دەوڵەمەند: (H: دەوڵەمەن، L: پۊلدار، K: Dewlemend، Z: Zengîn)
​توند: (H: قایم، L: تۊن، K: Tund، Z: Pêt)
​شل: (K: Sist، Z: Şil)
​وشک: (L: هوشک، K: Hişk، Z: Huşk)
​تەڕ: (K: Ter، Z: Hêdî)
​بەتاڵ: (H: واڵی، L: خاڵی، K: Vala، Z: Veng)
​کراوە: (H: کەردەوا، L: واکریاگ، K: Vekirî، Z: Akerde)
​داخراو: (H: بەسیە، L: بەسیەی، K: Girtî، Z: Girewte)
​قوڕ: (K: Herî، Z: Lêr)
​تۆز: (L: تەپوز، K: Toz، Z: Toz)
​دووکەڵ: (L: دۊکەڵ، K: Dû، Z: Duman)
​شوشە: (H: شیشە، L: شیشە، K: Şûşe، Z: Şuşe)
​ئاسن: (K: Hesin، Z: Asin)
​زێڕ: (H: زەڕ، L: تەڵا، K: Zêr، Z: Zêr)
​زیو: (L: نوقرە، K: Zîv، Z: Zêm)
​مێش: (H: مەشێ، L: مەگس، K: Mêş، Z: Mêşe)
​مێشوولە: (H: پەشە، L: پەشە، K: Pêşû، Z: Viza)
​پەپوولە: (L: پەپۊلە، K: Piling، Z: Perperik)
​دووپشک: (H: کۆڵدم، K: Dûpişk، Z: Dumare)
​مێشک: (H: مەزگ، L: مەزگ، K: Mêjî، Z: Mezg)
​ڕیخۆڵە: (H: ڕۆیەڵە، L: ڕۊەڵە، K: Rovî، Z: Rovî)
​گورچیلە: (H: وەڵک، L: گورچگ، K: Gurçik، Z: Gurçike)
​سێبەر: (H: سایە، L: سایە، K: Sî، Z: Sersî)
​چیا: (H: کۆ، L: کۊە، K: Çiya، Z: Ko)
​کێڵگە: (H: مەزرەعە، K: Zevî، Z: Zewî)
​گەنم: (L: گەنن، K: Genim، Z: Genim)
​جۆ: (H: جەو، L: جۊ، K: Ceh، Z: Cew)
​ڕۆن: (H: ڕۆەن، L: ڕۊن، K: Rûn، Z: Rûn)
​ماست: (H: ماس، L: ماس، K: Mast، Z: Mast)
​دۆ: (L: دۊ، K: Dew، Z: Dew)
​ئارەقە: (H: ئارەق، L: ئارەق، K: Xwêdan، Z: Areq)
​فرمێسک: (H: ئەسرین، L: ئەسر، K: Hêsir، Z: Hesir)
​تف: (H: تیک، K: Tif، Z: Tuf)
​کۆکە: (L: کۆخە، K: Kuxik، Z: Kuxik)
​پژمە: (K: Bêhn، Z: Pişme)
​هەناسە: (K: Bêhn، Z: Henase)
​ڕۆح: (H: گیان، L: گیان، K: Rih، Z: Giyan)
​مردوو: (H: مەردە، L: مردگ، K: Mirî، Z: Merde)
​زیندوو: (H: زینە، L: زنە، K: Zindî، Z: Gane)
​کوێر: (H: کۆر، L: کۊر، K: Kor، Z: Kor)
​تاوان: (K: Sûc، Z: Sûc)
​سزا: (K: Ceza، Z: Ceza)
​خەڵات: (K: Xelat، Z: Xelat)
​جەژن: (H: جەژنە، K: Cejn، Z: Roşan)
​پرسە: (K: Şîn، Z: Şîn)
​بوومەلەرزە: (L: زەمین‌لەرزە، K: Erdhej، Z: Bumelerze)
​لافاو: (K: Lehî، Z: Lafaw)
​گوڵزار: (H: وڵزار، K: Gulistan، Z: Gulistan)
​ئامێر: (K: Amûr، Z: Hacet)
​وێنە: (K: Wêne، Z: Resim)
​دەنگ: (K: Deng، Z: Veng)
​نامە: (K: Name، Z: Mektube)
​چیرۆک: (H: حیکایەت، K: Çîrok، Z: Estanike)
​کتێب: (L: کتێو، K: Pirtûk، Z: Kıtab)
​قەڵەم: (K: Pênûs، Z: Qeleme)
​مێز: (K: Mase، Z: Mase)
​نوێن: (L: نۊن، K: Nivîn، Z: Nivîn)
​خەنجەر: (K: Xencer، Z: Xencer)
​کەشتی: (H: گەمیە، K: Keştî، Z: Gemi)
​فڕۆکە: (H: تەیارە، L: تەیارە، K: Bafir، Z: Teyare)
​شەمەندەفەر: (H: قەتار، L: قەتار، K: Tirên، Z: Tirên)
​پرد: (K: Pir، Z: Pird)
​جادە: (K: Cadde، Z: Cade)
​کۆڵان: (L: کۊچە، K: Kolan، Z: Kolan)
​بازاڕ: (K: Bazar، Z: Çarşî)
​دوکان: (H: دۆکان، L: دۊکان، K: Dikan، Z: Dikan)
​مزگەوت: (H: مزگی، L: مزگەفت، K: Mizgeft، Z: Mizgeft)
​گۆڕستان: (H: قەورسان، L: قەورسان، K: Goristan، Z: Mezel)
​جوتیار: (H: وەرزێر، K: Cotkar، Z: Cotkar)
​سەرباز: (K: Leşker، Z: Esker)
"""

# --- ٣. دیزاینی CSS (چاککردنی بۆکسە ڕەشەکە و لادانی هێڵەکان) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{ 
        background-color: #0E0A1A !important; 
        background-image: radial-gradient(circle at 50% 0%, #2A1B54 0%, transparent 50%);
        overflow: hidden !important;
    }}
    
    #MainMenu, header, footer, .stDeployButton {{visibility: hidden; display: none;}}
    .block-container {{ padding-top: 1rem !important; max-width: 450px !important; }}
    
    * {{ font-family: 'Vazirmatn', sans-serif !important; direction: rtl; text-align: right; color: #F8FDFE !important; }}

    /* چاککردنی بۆکسە ڕەشەکەی ناو وێنەکە (Dropdown Menu) */
    div[data-baseweb="popover"], div[data-baseweb="menu"] {{
        background-color: #1A1230 !important;
        border: 1px solid rgba(107, 91, 226, 0.4) !important;
        border-radius: 12px !important;
    }}
    li[data-baseweb="option"] {{
        background-color: transparent !important;
        color: white !important;
    }}
    li[data-baseweb="option"]:hover {{
        background-color: #5A49D9 !important;
    }}

    /* لادانی هێڵی تەنیشت زاراوە و هێڵە سوورەکان */
    div[data-baseweb="select"] > div {{
        background: rgba(42, 27, 84, 0.4) !important;
        border: 1px solid rgba(107, 91, 226, 0.2) !important;
        border-radius: 15px !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] div {{ border: none !important; }}
    
    *:focus, *:active, div[data-baseweb="base-input"]:focus-within {{
        outline: none !important; border-color: rgba(107, 91, 226, 0.5) !important; box-shadow: none !important;
    }}

    /* تابەکان */
    .stTabs [data-baseweb="tab-list"] {{ 
        display: grid !important; grid-template-columns: 1fr 1fr 1fr !important;
        background: rgba(255, 255, 255, 0.03); padding: 5px; border-radius: 15px; border-bottom: none !important;
    }}
    .stTabs [data-baseweb="tab"] {{ width: 100% !important; border: none !important; }}
    button[data-baseweb="tab"][aria-selected="true"] {{ background: #5A49D9 !important; border-radius: 10px !important; }}
    .stTabs [data-baseweb="tab-highlight"] {{ display: none !important; }}

    /* بۆکسی ئەنجام و نوسین */
    textarea {{ background: rgba(30, 20, 60, 0.7) !important; border-radius: 20px !important; border: 1px solid rgba(107, 91, 226, 0.3) !important; }}
    .result-area {{ background: rgba(90, 73, 217, 0.1) !important; padding: 20px; border-radius: 20px; border: 1px solid rgba(107, 91, 226, 0.3) !important; text-align: center; font-size: 1.2rem; }}

    .stButton>button {{ background: linear-gradient(135deg, #6B5BE2 0%, #5A49D9 100%) !important; border-radius: 15px !important; border: none !important; height: 50px; }}
    
    .daily-banner {{ background: rgba(90, 73, 217, 0.15); padding: 8px; border-radius: 12px; text-align: center; margin-bottom: 15px; color: #B5AAFF !important; font-size: 0.8rem; }}
    </style>
    """, unsafe_allow_html=True)

# --- ٤. لۆژیکی AI ---
def stream_ai(text, src, trg, ttype):
    keys = [st.secrets.get(f"GEMINI_KEY_{i}") for i in range(1, 21) if st.secrets.get(f"GEMINI_KEY_{i}")]
    if not keys: return None
    genai.configure(api_key=random.choice(keys))
    try:
        model = genai.GenerativeModel('gemini-3.1-flash-lite-preview', system_instruction=K_BASE)
        if ttype == "translate": p = f"وەرگێڕە بۆ {trg}: {text}"
        elif ttype == "abc": p = f"ئەم دەقە بگۆڕە (ئارامی بۆ لاتینی یان بەپێچەوانە): {text}"
        else: p = f"ئەم ژمارەیە بکە بە پیت بە {trg}: {text}"
        return model.generate_content(p)
    except: return None

# --- ٥. UI ---
st.markdown('<div class="daily-banner">✨ بەخێربێن بۆ یەکەمین وەرگێڕی شێوەزارە کوردییەکان</div>', unsafe_allow_html=True)
if logo: st.markdown(f'<div style="text-align:center; margin-bottom: 10px;"><img src="data:image/gif;base64,{logo}" width="65"></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["وەرگێڕان", "ژمارە", "ڕێنووس"])
dlcts = ["سۆرانی", "Kurmancî", "هەورامی", "Zazakî", "لوڕی"]

with tab1:
    c1, c2 = st.columns(2)
    s_v, t_v = c1.selectbox("لە:", dlcts, key="s1"), c2.selectbox("بۆ:", dlcts, index=2, key="t1")
    u_in = st.text_area("", key="i1", placeholder="دەق لێرە بنووسە...", height=110)
    if st.button("وەرگێڕان ⚡", key="b1"):
        if u_in:
            res_box = st.empty()
            if search_icon: res_box.markdown(f'<div style="text-align:center; margin-top:20px;"><img src="data:image/gif;base64,{search_icon}" width="80"></div>', unsafe_allow_html=True)
            resp = stream_ai(u_in, s_v, t_v, "translate")
            if resp: res_box.markdown(f'<div class="result-area">{resp.text}</div>', unsafe_allow_html=True)

with tab2:
    n_v = st.selectbox("شێوەزار:", dlcts, key="s2")
    n_in = st.text_input("ژمارە:", key="i2")
    if st.button("گۆڕین 🔢"):
        if n_in:
            res_box = st.empty()
            if search_icon: res_box.markdown(f'<div style="text-align:center;"><img src="data:image/gif;base64,{search_icon}" width="80"></div>', unsafe_allow_html=True)
            resp = stream_ai(n_in, "", n_v, "num")
            if resp: res_box.markdown(f'<div class="result-area">{resp.text}</div>', unsafe_allow_html=True)

with tab3:
    a_in = st.text_area("", key="i3", placeholder="دەقی ئارامی یان لاتینی لێرە دابنێ...", height=110)
    if st.button("گۆڕینی ڕێنووس ✨"):
        if a_in:
            res_box = st.empty()
            if search_icon: res_box.markdown(f'<div style="text-align:center;"><img src="data:image/gif;base64,{search_icon}" width="80"></div>', unsafe_allow_html=True)
            resp = stream_ai(a_in, "", "", "abc")
            if resp: res_box.markdown(f'<div class="result-area">{resp.text}</div>', unsafe_allow_html=True)

st.markdown("<p style='text-align:center; opacity:0.3; font-size:0.7rem; margin-top:25px;'>I_KURD|v1.3beta</p>", unsafe_allow_html=True)
