import streamlit as str
from PIL import Image, ImageOps
import numpy as np

# ตั้งค่าหน้าตาแอปพลิเคชัน
str.set_page_config(page_title="Rice Hybrid Matcher 30", page_icon="🌾", layout="centered")
str.title("🌾 ระบบไฮบริดวิเคราะห์กายภาพและจัดอันดับสายพันธุ์ข้าวไทย")
str.write("วิเคราะห์สัณฐานวิทยาของเมล็ดข้าวสารร่วมกับอินพุตจำเพาะ เพื่อคำนวณและจัดอันดับความน่าจะเป็น 5 อันดับแรก จากฐานข้อมูลข้าวไทย 30 สายพันธุ์")

# -------------------------------------------------------------
# ส่วนที่ 1: ขั้นตอนผู้ใช้อัปโหลดรูปภาพ (Upload Rice Image)
# -------------------------------------------------------------
str.subheader("📸 ขั้นตอนที่ 1: อัปโหลดรูปภาพเมล็ดข้าวสารเพื่อวิเคราะห์กายภาพ")
uploaded_file = str.file_uploader("เลือกรูปภาพหรือถ่ายรูปเมล็ดข้าวของคุณ...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    user_img = Image.open(uploaded_file).convert('RGB')
    str.image(user_img, caption='🎯 รูปภาพเมล็ดข้าวที่นำเข้าสู่กระบวนการสแกน', use_column_width=True)
    
    str.info("⚙️ [ระบบวิเคราะห์วิสัยทัศน์คอมพิวเตอร์] กำลังสแกนลักษณะพิกเซลพื้นผิวเพื่อจำแนกกายภาพดิบ...")
    
    # ดึงค่าเฉลี่ยสเปกตรัมเม็ดสีและความสว่าง (Image Processing - No CV2)
    gray_img = ImageOps.grayscale(user_img)
    img_array = np.array(user_img)
    gray_array = np.array(gray_img)
    
    # กรองแยกสีพื้นหลังสีขาว/จานสะท้อนออก คัดเฉพาะเมล็ดข้าวสาร
    rice_pixels = img_array[(gray_array > 35) & (gray_array < 235)] 
    if len(rice_pixels) == 0:
        rice_pixels = img_array.reshape(-1, 3)
        
    mean_r = np.mean(rice_pixels[:, 0])
    mean_g = np.mean(rice_pixels[:, 1])
    mean_b = np.mean(rice_pixels[:, 2])
    
    # ดัชนีคำนวณความสว่างสัมพัทธ์ (Luminance)
    luminance = 0.299 * mean_r + 0.587 * mean_g + 0.114 * mean_b
    brightness_std = np.std(gray_array)
    
    # 🧠 สมองกลแปลงค่าภาพถ่ายเป็นกลุ่มกายภาพ (ดักจับกลุ่มข้าวสีเข้ม/ข้าวสาร/ข้าวกล้อง)
    if luminance < 120 or (mean_b > mean_g and mean_r < 135):
        # กลุ่มข้าวไรซ์เบอร์รี่ ข้าวเหนียวดำ ข้าวก่ำ ข้าวลืมผัว (สีดำ/น้ำตาลเข้ม)
        ai_analysis = {
            "shape": "long_slender", "length": "long", "width": "narrow",
            "slenderness": "high", "color": "brown", "transparency": "low",
            "tip_shape": "pointed", "uniformity": "high"
        }
    elif mean_r > 130 and mean_g < 120 and mean_b < 115:
        # กลุ่มข้าวเฉดสีแดง/ชมพู (สังข์หยด, มะลิแดง)
        ai_analysis = {
            "shape": "medium", "length": "medium", "width": "medium",
            "slenderness": "medium", "color": "red", "transparency": "low",
            "tip_shape": "mixed", "uniformity": "medium"
        }
    elif mean_r > 140 and mean_r < 195 and mean_g > 120 and mean_g < 170 and mean_b < 140:
        # กลุ่มข้าวกล้อง/เหลืองนวล
        ai_analysis = {
            "shape": "long_slender", "length": "long", "width": "medium",
            "slenderness": "high", "color": "yellowish", "transparency": "low",
            "tip_shape": "pointed", "uniformity": "high"
        }
    else:
        # กลุ่มข้าวสารขาวปกติ
        if brightness_std < 36: # ข้าวเหนียวขุ่น
            ai_analysis = {
                "shape": "short_bold", "length": "medium", "width": "wide",
                "slenderness": "low", "color": "white", "transparency": "low",
                "tip_shape": "rounded", "uniformity": "high"
            }
        else: # ข้าวขาวใส (หอมมะลิ)
            ai_analysis = {
                "shape": "long_slender", "length": "long", "width": "narrow",
                "slenderness": "high", "color": "white", "transparency": "high",
                "tip_shape": "pointed", "uniformity": "high"
            }

    # แสดงผลลัพธ์ข้อมูลกายภาพในรูปแบบ JSON
    with str.expander("📄 ผลลัพธ์ข้อมูลสัณฐานวิทยาที่สกัดได้จากรูปภาพ (Physical Analysis JSON)"):
        str.json(ai_analysis)

    # -------------------------------------------------------------
    # ส่วนที่ 2: ผู้ใช้เลือกคุณลักษณะสำคัญ (User Selects Key Characteristics)
    # -------------------------------------------------------------
    str.markdown("---")
    str.subheader("✍️ ขั้นตอนที่ 2: ระบุอัตลักษณ์เพิ่มเติมประจำสายพันธุ์")
    
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
                matched_reasons.append("เนื้อสัมผัสหลังหุงตรงตามที่ระบุ")
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
        <div style="background-color:#f9f9f9; padding:12px; border-radius:8px; border-left:4px solid #4CAF50; margin-bottom:15px; font-size:14px;">
            <b>📋 ข้อมูลอัตลักษณ์ประจำพันธุ์ภาษาไทย:</b><br>
            • รูปทรงเมล็ดสาร: {item['details']['shape']} | 
            • เฉดสีพฤกษศาสตร์: {item['details']['color']} | 
            • เนื้อสัมผัสหลังหุง: {item['details']['texture']}<br>
            • เอกลักษณ์กลิ่น: {item['details']['aroma']} | 
            • แหล่งภูมิศาสตร์เพาะปลูกหลัก: {item['details']['area']}
        </div>
        """, unsafe_allow_html=True)

str.markdown("---")
str.caption("พัฒนาโดยระบบจำแนกและประมวลผลสัณฐานวิทยาข้าวไทยระดับมหาชน 2026")
