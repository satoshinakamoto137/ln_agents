import pytesseract
import cv2

def get_text(cropped_image_path, lang="eng"):
    img = cv2.imread(cropped_image_path)
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar {cropped_image_path}")

    # 1. Escalar la imagen para que Tesseract vea mejor
    scale_factor = 2.0
    img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)

    # 2. Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Mejorar contraste y binarizar
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                 cv2.THRESH_BINARY, 15, 10)

    # 4. Configuración de Tesseract
    config = "--psm 7 -c tessedit_char_whitelist='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ?!*:;.,()'"

    # 5. OCR
    text = pytesseract.image_to_string(gray, lang=lang, config=config)

    # 6. Limpieza
    text = text.strip().replace("\n", " ")
    print(f"[OCR] Extracted text: {text}")

    return text
