import streamlit as st
import torch
import torch.nn.functional as F
from torchvision import transforms as T
from PIL import Image
import streamlit.components.v1 as components
import time
import os
import timm

UNSPLASH_ACCESS_KEY = "rMGFr2HLP5oI5DH4q1MdG0Gh9uZkY4EcgDoqmge8Eu0"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "leaf_best.pth")

CLASS_NAMES = {
    0: "Green Anthracnose (Hijau Antraknos)",
    1: "Green Rust (Hijau Karat)",
    2: "Green Healthy (Hijau Sehat)",
    3: "Red Healthy (Merah Sehat)"
}

RECOMMENDATIONS = {
    0: {
        "status": "Diseased",
        "description": "Anthracnose is a fungal disease causing dark, sunken lesions on leaves.",
        "recommended_pesticides": "Copper-based fungicides (e.g., Copper Oxychloride), Mancozeb.",
        "usage_instructions": "Mix 2-3g per liter of water. Spray thoroughly on affected plants every 7-10 days.",
        "prevention_tips": "Ensure good air circulation, avoid overhead watering, and remove infected leaves promptly."
    },
    1: {
        "status": "Diseased",
        "description": "Rust is a fungal issue characterized by rust-colored spots on the leaf surface.",
        "recommended_pesticides": "Propiconazole, Hexaconazole, or Wettable Sulfur.",
        "usage_instructions": "Apply 1-2ml per liter of water at the first sign of disease. Repeat after 14 days if needed.",
        "prevention_tips": "Maintain proper spacing between plants and avoid wetting the foliage during irrigation."
    },
    2: {
        "status": "Healthy",
        "description": "The green betel leaf is perfectly healthy.",
        "tips": "Continue regular watering and ensure balanced sunlight exposure."
    },
    3: {
        "status": "Healthy",
        "description": "The red betel leaf is perfectly healthy.",
        "tips": "Maintain optimal soil moisture and provide organic compost monthly."
    }
}

st.set_page_config(page_title="Betel Leaf Disease Intelligence System", page_icon="🌿", layout="centered")

@st.cache_resource
def load_model():
    try:
        model = timm.create_model('rexnet_150', pretrained=False, num_classes=4)
        state_dict = torch.load(MODEL_PATH, map_location=torch.device('cpu'), weights_only=False)
        model.load_state_dict(state_dict)
        model.eval()
        return model
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None

def preprocess_image(image: Image.Image):
    mean, std, im_size = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225], 224
    transformations = T.Compose([
        T.Resize((im_size, im_size)),
        T.ToTensor(),
        T.Normalize(mean=mean, std=std)
    ])
    return transformations(image).unsqueeze(0)

def predict_image(model, image_tensor):
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = F.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)
        return predicted.item(), confidence.item() * 100

def get_recommendation(class_idx):
    result = RECOMMENDATIONS.get(class_idx, {})
    class_name = CLASS_NAMES.get(class_idx, "Unknown")
    return class_name, result

def fetch_unsplash_images():
    js_code = f"""
    <script>
    const accessKey = "{UNSPLASH_ACCESS_KEY}";
    let currentImageIndex = 0;
    let imageUrls = [];

    async function fetchImages() {{
        try {{
            const response = await fetch(`https://api.unsplash.com/photos/random?query=agriculture,green,leaf&count=10&client_id=${{accessKey}}`);
            const data = await response.json();
            imageUrls = data.map(img => img.urls.regular);
            changeBackground();
        }} catch(e) {{
            console.log("Error fetching from Unsplash:", e);
            imageUrls = [
                "https://images.unsplash.com/photo-1542838132-92c53300491e?w=1600",
                "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=1600"
            ];
            changeBackground();
        }}
    }}

    function changeBackground() {{
        if (imageUrls.length === 0) return;
        const doc = window.parent.document;
        const appNode = doc.querySelector('.stApp');
        if (appNode) {{
            appNode.style.backgroundImage = `linear-gradient(rgba(0,0,0,0.65), rgba(0,0,0,0.75)), url('${{imageUrls[currentImageIndex]}}')`;
            appNode.style.backgroundSize = "cover";
            appNode.style.backgroundPosition = "center";
            appNode.style.backgroundAttachment = "fixed";
            appNode.style.transition = "background-image 1s ease-in-out";
            
            currentImageIndex = (currentImageIndex + 1) % imageUrls.length;
        }}
    }}

    fetchImages();
    setInterval(changeBackground, 5000);
    setInterval(fetchImages, 60000); 
    </script>
    """
    return js_code

def set_background():
    components.html(fetch_unsplash_images(), height=0, width=0)

def inject_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }

        .glass-card {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 35px;
            color: white;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.35);
            margin-bottom: 25px;
        }

        h1, h2, h3, h4, p, span, div {
            color: #ffffff !important;
        }

        .healthy {
            border-left: 6px solid #2ecc71;
            background: rgba(46, 204, 113, 0.15);
        }

        .diseased {
            border-left: 6px solid #e74c3c;
            background: rgba(231, 76, 60, 0.15);
        }

        .stButton>button {
            background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%) !important;
            color: white !important;
            border-radius: 10px !important;
            border: none !important;
            padding: 12px 24px !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease;
            width: 100%;
            box-shadow: 0 4px 15px rgba(46, 204, 113, 0.4);
        }

        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(46, 204, 113, 0.6);
        }

        [data-testid="stFileUploadDropzone"] {
            background: rgba(255, 255, 255, 0.05);
            border: 2px dashed rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            transition: all 0.3s;
        }

        [data-testid="stFileUploadDropzone"]:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.6);
        }
        
        .progress-bar-bg {
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            height: 12px;
            width: 100%;
            margin-top: 10px;
            margin-bottom: 20px;
            overflow: hidden;
        }
        
        .progress-bar-fill {
            height: 100%;
            border-radius: 8px;
            transition: width 1s ease-in-out;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

def main():
    set_background()
    inject_styles()

    st.markdown(
        """
        <div class="glass-card" style="text-align: center;">
            <h1 style="font-size: 2.8em; font-weight: 700; margin-bottom: 5px;">🌿 Betel Leaf Disease Detection</h1>
            <p style="font-size: 1.2em; opacity: 0.85; font-weight: 300;">Upload an image to identify diseases and receive smart pesticide recommendations.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    model = load_model()

    if "show_results" not in st.session_state:
        st.session_state.show_results = False
    
    uploaded_file = st.file_uploader("Drag & Drop or Click to Upload Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="Uploaded Image Preview", use_container_width=True)

            if st.button("Analyze Leaf"):
                if model is None:
                    st.error("Model could not be loaded. Please ensure 'leaf_best.pth' is in the current directory.")
                    return

                with st.spinner("Analyzing image..."):
                    time.sleep(1.5)
                    tensor = preprocess_image(image)
                    class_idx, confidence = predict_image(model, tensor)
                    st.session_state.result_idx = class_idx
                    st.session_state.confidence = confidence
                    st.session_state.show_results = True

        except Exception as e:
            st.error(f"Error processing image. Make sure it is a valid image file. Details: {e}")

    if uploaded_file is None:
        st.session_state.show_results = False

    if st.session_state.show_results:
        class_name, result = get_recommendation(st.session_state.result_idx)
        status = result.get("status", "")
        conf = st.session_state.confidence
        
        progress_color = "#2ecc71" if status == "Healthy" else "#e74c3c"
        
        if status == "Healthy":
            theme = "healthy"
            content = f"""
<h2 style='color: #2ecc71 !important; margin-bottom: 0px;'>✅ Status: {status}</h2>
<h3 style='margin-top: 5px; opacity: 0.9;'>{class_name}</h3>

<p style='margin-bottom: 5px; opacity: 0.8;'>Confidence Score: <b>{conf:.1f}%</b></p>
<div class='progress-bar-bg'>
    <div class='progress-bar-fill' style='width: {conf}%; background-color: {progress_color};'></div>
</div>

<hr style='border-color: rgba(255,255,255,0.1);'/>
<p style='font-size: 1.1em;'>{result.get('description', '')}</p>
<br/>
<h4 style='color: #2ecc71 !important;'>🌿 Maintenance Tips:</h4>
<p>{result.get('tips', '')}</p>
"""
        else:
            theme = "diseased"
            content = f"""
<h2 style='color: #e74c3c !important; margin-bottom: 0px;'>⚠️ Status: {status}</h2>
<h3 style='margin-top: 5px; opacity: 0.9;'>{class_name}</h3>

<p style='margin-bottom: 5px; opacity: 0.8;'>Confidence Score: <b>{conf:.1f}%</b></p>
<div class='progress-bar-bg'>
    <div class='progress-bar-fill' style='width: {conf}%; background-color: {progress_color};'></div>
</div>

<hr style='border-color: rgba(255,255,255,0.1);'/>
<p style='font-size: 1.1em;'>{result.get('description', '')}</p>
<br/>
<h4 style='color: #f1c40f !important;'>💊 Recommended Pesticides:</h4>
<p>{result.get('recommended_pesticides', '')}</p>
<br/>
<h4 style='color: #f1c40f !important;'>📝 Usage Instructions:</h4>
<p>{result.get('usage_instructions', '')}</p>
<br/>
<h4 style='color: #f1c40f !important;'>🛡️ Prevention Tips:</h4>
<p>{result.get('prevention_tips', '')}</p>
"""
        
        st.markdown(f'<div class="glass-card {theme}">{content}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
