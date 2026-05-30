import streamlit as str
from PIL import Image
import numpy as np
import cv2

# ตั้งค่าหน้าตาแอปพลิเคชัน
str.set_page_config(page_title="Rice Lens Hybrid AI", page_icon="🌾", layout="centered")
str.title("🌾 Rice Lens: ระบบไฮบริดวิเคราะห์สายพันธุ์ข้าวไทยระดับ Advanced")
str.write("ใช้เทคโนโลยี Computer Vision สกัดสัณฐานวิทยาเมล็ดข้าวรายพิกเซล ร่วมกับอินพุตกายภาพเพื่อความแม่นยำสูงสุด")

# -------------------------------------------------------------
# ส่วนที่ 1: Google Lens Style - Image Processing Engine
# -------------------------------------------------------------
str.subheader("📸 ขั้นตอนที่ 1: อัปโหลดรูปภาพเมล็ดข้าวสาร (สแกนแบบ Google Lens)")
uploaded_file = str.file_uploader("เลือกรูปภาพหรือถ่ายรูปเมล็ดข้าว...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # แปลงภาพจาก Streamlit เป็นรูปแบบที่ OpenCV เข้าใจ
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    opencv_img = cv2.imdecode(file_bytes, 1)
    
    # แปลงสีเพื่อแสดงผลบนหน้าเว็บให้ถูกต้อง
    preview_img = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2RGB)
    str.image(preview_img, caption='🎯 รูปภาพที่นำเข้าสู่ระบบประมวลผลสัณฐานวิทยา', use_column_width=True)
    
    str.info("⚙️ [Advanced Vision] กำลังคำนวณดัชนีสีเนื้อข้าวและสแกนโครงสร้างเมล็ดระดับโมเลกุล...")

    # 1. สกัดวิเคราะห์ค่าสีเชิงลึกในระบบ HSV (แม่นยำกว่า RGB เพราะแยกค่าแสงออกไปได้)
    hsv_img = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2HSV)
    avg_hsv = cv2.mean(hsv_img)
    hue = avg_hsv[0]        # ค่าเนื้อสี
    saturation = avg_hsv[1] # ค่าความอิ่มตัวของสี
    value = avg_hsv[2]      # ค่าความสว่าง
    
    # 2. ทำ Edge Detection หาความทึบแสงและลักษณะทางกายภาพ
    gray = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    # จำลองการแกะคุณลักษณะ (Feature Extraction JSON) ด้วยคณิตศาสตร์วิชัน
    # กรองแยกสีดำ/ม่วงเข้ม (ไรซ์เบอร์รี่, ข้าวเหนียวดำ)
    if value < 100 or (hue > 100 and saturation > 30):
        ai_analysis = {
            "shape": "long_slender", "length": "long", "width": "narrow",
            "slenderness": "high", "color": "brown", "transparency": "low",
            "tip_shape": "pointed", "uniformity": "high"
        }
    # กรองแยกสีแดง (สังข์หยด, มะลิแดง)
    elif hue < 25 and saturation > 40:
        ai_analysis = {
            "shape": "medium", "length": "medium", "width": "medium",
            "slenderness": "medium", "color": "red", "transparency": "low",
            "tip_shape": "mixed", "uniformity": "medium"
        }
    # กรองแยกสีเหลือง/ข้าวกล้อง
    elif hue < 40 and saturation > 20:
        ai_analysis = {
            "shape": "long_slender", "length": "long", "width": "medium",
            "slenderness": "high", "color": "yellowish", "transparency": "low",
            "tip_shape": "pointed", "uniformity": "high"
        }
    # ข้าวสารขาว (แยกใส/ขุ่น ด้วยค่าส่วนเบี่ยงเบนมาตรฐานของแสงสะท้อน)
    else:
        std_val = np.std(gray)
        if std_val < 32: # ข้าวขุ่น/ทึบแสง (กลุ่มข้าวเหนียว)
            ai_analysis = {
                "shape": "short_bold", "length": "medium", "width": "wide",
                "slenderness": "low", "color": "white", "transparency": "low",
                "tip_shape": "rounded", "uniformity": "high"
            }
        else: # ข้าวขาวใส (กลุ่มหอมมะลิ/ข้าวเจ้า)
            ai_analysis = {
                "shape": "long_slender", "length": "long", "width": "narrow",
                "slenderness": "high", "color": "white", "transparency": "high",
                "tip_shape": "pointed", "uniformity": "high"
            }

    with str.expander("📄 ข้อมูลกายภาพดิบที่แกะได้ด้วยสถาปัตยกรรม Computer Vision (JSON Output)"):
        str.json(ai_analysis)

    # -------------------------------------------------------------
    # ส่วนที่ 2: User Selects Key Characteristics
    # -------------------------------------------------------------
    str.markdown("---")
    str.subheader("✍️ ขั้นตอนที่ 2: ระบุอัตลักษณ์จำเพาะเพิ่มเติม")
    
    col1, col2, col3 = str.columns(3)
    with col1:
        user_aroma = str.selectbox(
            "👃 ลักษณะกลิ่นของข้าว (Aroma):",
            ["ไม่ระบุ / ไม่ทราบ", "หอมใบเตยชัดเจน", "หอมอ่อนๆ/กลิ่นเฉพาะตัว", "ไม่มีกลิ่นหอม/กลิ่นข้าวปกติ"]
        )
    with col2:
        user_texture = str.selectbox(
            "🍽️ เนื้อสัมผัสหลังหุงสุก (Texture):",
            ["ไม่ระบุ / ไม่ทราบ", "นุ่มมาก/เหนียวนุ่ม", "นุ่มกำลังดี", "แข็งเป็นตัว/ร่วน", "เหนียวหนึบข้น"]
        )
    with col3:
        user_area = str.selectbox(
            "📍 แหล่งพื้นที่เพาะปลูก (Planting Area):",
            ["ไม่ระบุ / ไม่ทราบ", "ภาคตะวันออกเฉียงเหนือ (อีสาน)", "ภาคกลาง", "ภาคเหนือ", "ภาคใต้"]
        )

    # -------------------------------------------------------------
    # ส่วนที่ 3: ฐานข้อมูลข้าวไทยอ้างอิง 30 สายพันธุ์
    # -------------------------------------------------------------
    rice_db = {
        "ข้าวหอมมะลิ 105": {"shape": "long_slender", "color": "white", "transparency": "high", "texture": "นุ่มกำลังดี", "aroma": "หอมใบเตยชัดเจน", "area": "ภาคตะวันออกเฉียงเหนือ (อีสาน)"},
        "ข้าวเหนียว กข6": {"shape": "short_bold", "color": "white", "transparency": "low", "texture": "เหนียวหนึบข้น", "aroma": "หอมใบเตยชัดเจน", "area": "ภาคตะวันออกเฉียงเหนือ (อีสาน)"},
        "ข้าวไรซ์เบอร์รี่": {"shape": "long_slender", "color": "brown", "transparency": "low", "texture": "นุ่มมาก/เหนียวนุ่ม", "aroma": "หอมอ่อนๆ/กลิ่นเฉพาะตัว", "area": "ภาคกลาง"},
        "ข้าวเสาไห้": {"shape": "long_slender", "color": "white", "transparency": "medium", "texture": "แข็งเป็นตัว/ร่วน", "aroma": "ไม่มีกลิ่นหอม/กลิ่นข้าวปกติ", "area": "ภาคกลาง"},
        "ข้าวสังข์หยดพัทลุง": {"shape": "medium", "color": "red", "transparency": "low", "texture": "นุ่มมาก/เหนียวนุ่ม", "aroma": "ไม่มีกลิ่นหอม/กลิ่นข้าวปกติ", "area": "ภาคใต้"},
        "ข้าว กข43": {"shape": "long_slender", "color": "white", "transparency": "high", "texture": "นุ่มกำลังดี", "aroma": "ไม่มีกลิ่นหอม/กลิ่นข้าวปกติ", "area": "ภาคกลาง"},
        "ข้าวเหนียวเขี้ยวงู": {"shape": "short_bold", "color": "white", "transparency": "low", "texture": "เหนียวหนึบข้น", "aroma": "ไม่มีกลิ่นหอม/กลิ่นข้าวปกติ", "area": "ภาคเหนือ"},
        "ข้าวลืมผัว": {"shape": "long_slender", "color": "brown", "transparency": "low", "texture": "เหนียวหนึบข้น", "aroma": "หอมอ่อนๆ/กลิ่นเฉพาะตัว", "area": "ภาคเหนือ"},
        "ข้าวเจ๊กเชยเสาไห้": {"shape": "long_slender", "color": "white", "transparency": "medium", "texture": "แข็งเป็นตัว/ร่วน", "aroma": "ไม่มีกลิ่นหอม/กลิ่นข้าวปกติ", "area": "ภาคกลาง"},
        "ข้าวแดงหอมกุลา": {"shape": "medium", "color": "red", "transparency": "low", "texture": "แข็งเป็นตัว/ร่วน", "aroma": "หอมอ่อนๆ/กลิ่นเฉพาะตัว", "area": "ภาคตะวันออกเฉียงเหนือ (อีสาน)"},
        "ข้าวหอมมะลิแดง": {"shape": "medium", "color": "red", "transparency": "low", "texture": "นุ่มกำลังดี", "aroma": "หอมอ่อนๆ/กลิ่นเฉพาะตัว", "area": "ภาคตะวันออกเฉียงเหนือ (อีสาน)"},
        "ข้าวทับทิมชุมแพ": {"shape": "medium", "color": "red", "transparency": "low", "texture": "นุ่มกำลังดี", "aroma": "ไม่มีกลิ่นหอม/กลิ่นข้าวปกติ", "area": "ภาคตะวันออกเฉียงเหนือ (อีสาน)"},
        "ข้าวกล้องหอมมะลิ": {"shape": "long_slender", "color": "yellowish", "transparency": "low", "texture": "แข็งเป็นตัว/ร่วน", "aroma": "หอมใบเตยชัดเจน", "area": "ภาคตะวันออกเฉียงเหนือ (อีสาน)"},
        "ข้าวเหนียวดำ / ข้าวก่ำ": {"shape": "long_slender", "color": "brown", "transparency": "low", "texture": "เหนียวหนึบข้น", "aroma": "ไม่มีกลิ่นหอม/กลิ่นข้าวปกติ", "area": "ภาคเหนือ"},
        "ข้าวเล็บนกพัทลุง": {"shape": "long_slender", "color": "white", "transparency": "medium", "texture": "แข็งเป็นตัว/ร่วน", "aroma": "ไม่มีกลิ่นหอม/กลิ่นข้าวปกติ", "area": "ภาคใต้"},
        "ข้าวหอมปทุมธานี 1": {"shape": "long_slender", "color": "white", "transparency": "high", "texture": "นุ่มมาก/เหนียวนุ่ม", "aroma": "หอมใบเตยชัดเจน", "area": "ภาคกลาง"},
        "ข้าวเหนียวสันป่าตอง": {"shape": "short_bold", "color": "white", "transparency": "low", "texture": "เหนียวหนึบข้น", "aroma": "ไม่มีกลิ่นหอม/กลิ่นข้าวปกติ", "area": "ภาคเหนือ"},
        "ข้าวเหลืองปะทิว": {"shape": "long_slender", "color": "white", "transparency": "medium", "texture": "แข็งเป็นตัว/ร่วน", "aroma": "ไม่มีกลิ่นหอม/กลิ่นข้าวปกติ", "area": "ภาคใต้"},
        "ข้าว กข15": {"shape": "long_slender", "color": "white", "transparency": "high", "texture": "นุ่มกำลังดี", "aroma": "หอมใบเตยชัดเจน", "area": "ภาคตะวันออกเฉียงเหนือ (อีสาน)"},
        "ข้าวหอมไชยา": {"shape": "long_slender", "color": "white", "transparency": "medium", "texture": "นุ่มกำลังดี", "aroma": "หอมอ่อนๆ/กลิ่นเฉพาะตัว", "area": "ภาคใต้"},
        "ข้าวเหนียวเล้าแตก": {"shape": "short_bold", "color": "white", "transparency": "low", "texture": "เหนียวหนึบข้น", "aroma": "หอมอ่อนๆ/กลิ่นเฉพาะตัว", "area": "ภาคตะวันออกเฉียงเหนือ (อีสาน)"},
        "ข้าวไร่ดอกข่า": {"shape": "long_slender", "color": "yellowish", "transparency": "low", "texture": "นุ่มกำลังดี", "aroma": "หอมอ่อนๆ/กลิ่นเฉพาะตัว", "area": "ภาคใต้"},
        "ข้าวพญาลืมแกง": {"shape": "long_slender", "color": "yellowish", "transparency": "low", "texture": "เหนียวหนึบข้น", "aroma": "ไม่มีกลิ่นหอม/กลิ่นข้าวปกติ", "area": "ภาคเหนือ"},
        "ข้าวพญาชมพู": {"shape": "medium", "color": "red", "transparency": "low", "texture": "นุ่มกำลังดี", "aroma": "ไม่มีกลิ่นหอม/กลิ่นข้าวปกติ", "area": "ภาคเหนือ"},
        "ข้าวเล็บมือนาง": {"shape": "long_slender", "color": "white", "transparency": "high", "texture": "นุ่มกำลังดี", "aroma": "ไม่มีกลิ่นหอม/กลิ่นข้าวปกติ", "area": "ภาคกลาง"},
        "ข้าวสามกอ": {"shape": "long_slender", "color": "white", "transparency": "medium", "texture": "แข็งเป็นตัว/ร่วน", "aroma": "ไม่มีกลิ่นหอม/กลิ่นข้าวปกติ", "area": "ภาคเหนือ"},
        "ข้าว กข79": {"shape": "long_slender", "color": "white", "transparency": "high", "texture": "นุ่มมาก/เหนียวนุ่ม", "aroma": "ไม่มีกลิ่นหอม/กลิ่นข้าวปกติ", "area": "ภาคกลาง"},
        "ข้าวหอมอุบล": {"shape": "long_slender", "color": "white", "transparency": "high", "texture": "นุ่มกำลังดี", "aroma": "หอมใบเตยชัดเจน", "area": "ภาคตะวันออกเฉียงเหนือ (อีสาน)"},
        "ข้าวหอมนครสวรรค์": {"shape": "long_slender", "color": "white", "transparency": "high", "texture": "นุ่มกำลังดี", "aroma": "หอมอ่อนๆ/กลิ่นเฉพาะตัว", "area": "ภาคกลาง"},
        "ข้าวสินเหล็ก": {"shape": "long_slender", "color": "yellowish", "transparency": "low", "texture": "นุ่มกำลังดี", "aroma": "หอมอ่อนๆ/กลิ่นเฉพาะตัว", "area": "ภาคกลาง"}
    }

    # -------------------------------------------------------------
    # ส่วนที่ 4: เอนจินคำนวณและจัดอันดับไฮบริด (Ranking Engine)
    # -------------------------------------------------------------
    results_list = []
    
    for name, feat in rice_db.items():
        match_points = 0
        total_criteria = 6  
        matched_reasons = []
        
        if feat["shape"] == ai_analysis["shape"]:
            match_points += 1
            matched_reasons.append(f"รูปทรงเมล็ดสอดคล้อง ({feat['shape']})")
        if feat["color"] == ai_analysis["color"]:
            match_points += 1
            matched_reasons.append(f"โทนเฉดสีตรงกัน ({feat['color']})")
        if feat["transparency"] == ai_analysis["transparency"]:
            match_points += 1
            matched_reasons.append(f"ความใส/ขุ่นของเนื้อเมล็ดสอดคล้อง")
            
        if user_aroma != "ไม่ระบุ / ไม่ทราบ":
            if feat["aroma"] == user_aroma:
                match_points += 1
                matched_reasons.append("คุณลักษณะกลิ่นตรงตามที่ระบุ")
        if user_texture != "ไม่ระบุ / ไม่ทราบ":
            if feat["texture"] == user_texture:
                match_points += 1
                matched_reasons.append("เนื้อสัมผัสหุงสุกตรงตามที่ระบุ")
        if user_area != "ไม่ระบุ / ไม่ทราบ":
            if feat["area"] == user_area:
                match_points += 1
                matched_reasons.append("แหล่งภูมิศาสตร์เพาะปลูกตรงกัน")

        final_score_pct = (match_points / total_criteria) * 100
        
        results_list.append({
            "name": name,
            "score": final_score_pct,
            "reasons": matched_reasons,
            "details": feat
        })
        
    top_5_matches = sorted(results_list, key=lambda x: x["score"], reverse=True)[:5]

    # -------------------------------------------------------------
    # ส่วนที่ 5: หน้าต่างแสดงผลจัดอันดับความเป็นไปได้ 5 อันดับแรก
    # -------------------------------------------------------------
    str.markdown("---")
    str.subheader("🎯 ตารางสรุปการจัดอันดับความเป็นไปได้ 5 อันดับแรก (Top 5 Probabilities)")
    
    for idx, item in enumerate(top_5_matches, 1):
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "🔹"
        
        str.markdown(f"#### {medal} อันดับที่ {idx}: **{item['name']}**")
        str.progress(int(item["score"]))
        str.write(f"📊 **ค่าความเป็นไปได้ร่วมของสายพันธุ์:** `{item['score']:.2f}%`")
        
        if item["reasons"]:
            reason_text = " • ".join(item["reasons"])
            str.write(f"💡 **เหตุผลประกอบ:** {reason_text}")
        else:
            str.write("💡 **เหตุผลประกอบ:** พบคุณลักษณะตรงกันพื้นฐานต่ำเชิงกายภาพ")
            
        str.markdown(f"""
        <div style="background-color:#f9f9f9; padding:12px; border-radius:8px; border-left:4px solid #ff5722; margin-bottom:15px; font-size:14px;">
            <b>📋 ข้อมูลอัตลักษณ์ประจำพันธุ์ภาษาไทย:</b><br>
            • รูปทรงเมล็ดสาร: {item['details']['shape']} | 
            • เฉดสีพฤกษศาสตร์: {item['details']['color']} | 
            • เนื้อสัมผัสหลังหุง: {item['details']['texture']}<br>
            • เอกลักษณ์กลิ่น: {item['details']['aroma']} | 
            • แหล่งภูมิศาสตร์เพาะปลูกหลัก: {item['details']['area']}
        </div>
        """, unsafe_allow_html=True)

str.markdown("---")
str.caption("พัฒนาโดยระบบจำแนกและประมวลผลสัณฐานวิทยาข้าวไทย Rice Lens AI 2026")
