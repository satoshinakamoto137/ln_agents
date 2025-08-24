import button_searcher as but
import cv2
import time
import os
import ocr_functs as ocr

def search_4_current_element(view):
    results = []

    for idx, (name, asset) in enumerate([
        ("key_fill", "./assets/key_fill.png"),
        ("multi_select", "./assets/multi-select.png"),
        ("select_circle", "./assets/circle-select.png")
    ], start=1):
        found, t_f, b_r, score = detect_element_and_highlight(
            screenshot_path=view,
            element_path=asset,
            output_path=f'./assets/debug_{name}.png',
            threshold=0.8,
            debug=True
        )
        results.append((name, idx, score, found, t_f, b_r))

    # Keep only detected elements
    results = [r for r in results if r[3]]
    if not results:
        print("No element detected")
        return 0, None, None

    # Pick the highest score
    best = max(results, key=lambda x: x[2])
    print(f"Best match: {best[0]} with score {best[2]:.4f}")

    # Crop the question text above the detected element
    '''
    crop_question_text_square(
        screenshot_path=view,
        t_f=best[4],
        b_r=best[5],
        square_height=60,
        square_length=400,
        output_name=f"q_text_{best[0]}.png"
    )
    '''
    return best[0], best[1], best[4], best[5]  # type index, top_left, bottom_right


def search_4_key_fill(view):
    found, t_f, b_r, score = detect_element_and_highlight(
        screenshot_path=view,
        element_path='./assets/key_fill.png',
        output_path='./assets/formulary_state.png',
        threshold=0.8
    )
    return found,t_f, b_r

def search_4_multi_select(view):
    found, t_f, b_r, score = detect_element_and_highlight(
        screenshot_path=view,
        element_path='./assets/multi-select.png',
        output_path='./assets/formulary_state.png',
        threshold=0.8
    )
    return found, t_f, b_r

def search_4_select_circle(view):
    found, t_f, b_r, score = detect_element_and_highlight(
        screenshot_path=view,
        element_path='./assets/circle-select.png',
        output_path='./assets/formulary_state.png',
        threshold=0.8
    )
    return found, t_f, b_r

def search_4_selected_next(view):
    found, t_f, b_r, score = detect_element_and_highlight(
        screenshot_path=view,
        element_path='./assets/selected_next.png',
        output_path='./assets/formulary_state.png',
        threshold=0.8,
        debug=True
    )
    return found, t_f, b_r

def search_4_ssubmit_app(view):
    found, t_f, b_r, score = detect_element_and_highlight(
        screenshot_path=view,
        element_path='./assets/ssub.png',
        output_path='./assets/formulary_state.png',
        threshold=0.8,
        debug=True
    )
    return found, t_f, b_r

def search_4_sreview(view):
    found, t_f, b_r, score = detect_element_and_highlight(
        screenshot_path=view,
        element_path='./assets/srev.png',
        output_path='./assets/formulary_state.png',
        threshold=0.8,
        debug=True
    )
    return found, t_f, b_r

def detect_element_and_highlight(screenshot_path, element_path, output_path, threshold=0.8, debug=True):
    screenshot = cv2.imread(screenshot_path)
    element = cv2.imread(element_path)

    if screenshot is None or element is None:
        raise FileNotFoundError(f"No se pudo cargar {screenshot_path} o {element_path}")

    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    element_gray = cv2.cvtColor(element, cv2.COLOR_BGR2GRAY)

    # Template matching
    result = cv2.matchTemplate(screenshot_gray, element_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    h, w = element_gray.shape
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    # Extraer región encontrada
    matched_region = screenshot_gray[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

    # Calcular diferencia exacta
    if matched_region.shape == element_gray.shape:
        diff = cv2.absdiff(matched_region, element_gray)
        non_zero_count = cv2.countNonZero(diff)
        match_ratio = 1 - (non_zero_count / (w * h))
    else:
        match_ratio = 0

    # Debug info
    if debug:
        print(f"[DEBUG] Element: {os.path.basename(element_path)}")
        print(f"        Max Val (template match): {max_val:.4f}")
        print(f"        Match Ratio (pixel diff): {match_ratio:.4f}")
        debug_path = f"./debug_{os.path.basename(element_path)}"
        cv2.imwrite(debug_path, matched_region)
        print(f"        Saved matched region to: {debug_path}")

    # Decisión final
    if max_val >= threshold and match_ratio >= 0.98:
        cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 255), 3)
        cv2.imwrite(output_path, screenshot)
        return True, top_left, bottom_right, max_val
    else:
        return False, None, None, max_val
    
def search_4_any(view, elements):
    """
    Tries to detect any matching UI element in a screenshot from a list of target elements.

    Parameters:
    - view (str): Path to the screenshot image where elements will be searched.
    - elements (List[Tuple[str, str]]): A list of tuples in the format (label, element_path),
      where `label` is a name/identifier for the element, and `element_path` is the path
      to the PNG file that represents the UI element to detect.

    Returns:
    - found (bool): True if any element is found, False otherwise.
    - label (str or None): The label of the detected element. None if no match found.
    - top_left (Tuple[int, int] or None): Top-left corner of the matched region. None if not found.
    - bottom_right (Tuple[int, int] or None): Bottom-right corner of the matched region. None if not found.
    - score (float or None): Template matching score of the best match. None if no match found.
    """
    for label, element_path in elements:
        found, t_f, b_r, score = detect_element_and_highlight(
            screenshot_path=view,
            element_path=element_path,
            output_path='./assets/formulary_state.png',
            threshold=0.8,
            debug=True
        )
        if found:
            print(f"[INFO] Match found: {label} (score: {score:.4f})")
            return True, label, t_f, b_r, score

    print("[INFO] No match found for any element.")
    return False, None, None, None, None

def run_ending_element_detection(screenshot_path):
    """
    Runs multi-element detection on the provided screenshot.
    
    Parameters:
    - screenshot_path (str): Path to the screenshot to analyze.

    Returns:
    - Tuple: (found, label, top_left, bottom_right, score)
    """
    elements_to_check = [
        ("selected_next", "./assets/selected_next.png"),
        ("s_submit_app", "./assets/ssub.png"),
        ("s_review", "./assets/srev.png")
    ]

    found, label, top_left, bottom_right, score = search_4_any(screenshot_path, elements_to_check)

    if found:
        print(f"Element '{label}' found at {top_left} with score {score:.4f}")
    else:
        print("No element matched.")

    return found, label, top_left, bottom_right, score

    

def crop_text_square_simple(screenshot_path, t_f, b_r, square_height, square_length, output_name="question_crop.png"):
    """
    Crops the question text area above a detected form element and saves the image.
    
    Args:
        screenshot_path (str): Path to the screenshot file.
        t_f (tuple): (x, y) top-left coordinates of the detected element.
        b_r (tuple): (x, y) bottom-right coordinates of the detected element.
        square_height (int): Height of the crop area.
        square_length (int): Width of the crop area.
        output_name (str): File name to save in ./assets/.
    """
    img = cv2.imread(screenshot_path)
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar {screenshot_path}")

    x1, y1 = t_f
    # For question text above the element, shift upward by square_height
    y1_crop = max(0, y1 - square_height)
    x1_crop = x1
    x2_crop = min(img.shape[1], x1_crop + square_length)
    y2_crop = y1

    # Crop the area
    cropped = img[y1_crop:y2_crop, x1_crop:x2_crop]

    # Draw rectangle on a copy for debug
    debug_img = img.copy()
    cv2.rectangle(debug_img, (x1_crop, y1_crop), (x2_crop, y2_crop), (0, 255, 255), 2)

    # Save both the cropped and debug images
    cropped_path = os.path.join("./assets", output_name)
    debug_path = os.path.join("./assets", f"debug_{output_name}")
    cv2.imwrite(cropped_path, cropped)
    cv2.imwrite(debug_path, debug_img)

    print(f"[INFO] Question text cropped and saved to: {cropped_path}")
    print(f"[DEBUG] Highlighted image saved to: {debug_path}")

    return cropped_path

def crop_text_square_with_direction(screenshot_path, t_f, b_r, square_height, square_length, output_name="question_crop.png"):
    img = cv2.imread(screenshot_path)
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar {screenshot_path}")

    x1, y1 = t_f

    # Upward crop for question text
    y1_crop = max(0, y1 - square_height)
    y2_crop = y1

    # Handle direction for square_length
    if square_length > 0:
        x1_crop = x1
        x2_crop = min(img.shape[1], x1 + square_length)
    else:
        x1_crop = max(0, x1 + square_length)  # going left
        x2_crop = x1

    # Prevent invalid crop
    if x2_crop <= x1_crop or y2_crop <= y1_crop:
        print(f"[ERROR] Invalid crop coordinates: ({x1_crop},{y1_crop}) to ({x2_crop},{y2_crop})")
        return None

    cropped = img[y1_crop:y2_crop, x1_crop:x2_crop]

    # Draw debug rectangle
    debug_img = img.copy()
    cv2.rectangle(debug_img, (x1_crop, y1_crop), (x2_crop, y2_crop), (0, 255, 255), 2)

    cropped_path = os.path.join("./assets", output_name)
    debug_path = os.path.join("./assets", f"debug_{output_name}")
    cv2.imwrite(cropped_path, cropped)
    cv2.imwrite(debug_path, debug_img)

    print(f"[INFO] Question text cropped and saved to: {cropped_path}")
    print(f"[DEBUG] Highlighted image saved to: {debug_path}")

    return cropped_path

def crop_by_element(view, element_name, element_type, t_f, b_r):
    if element_type == 1: # fill
        cropped_path = crop_text_square_with_direction(view, t_f, b_r, 35, -666, f"q_text_{element_name}.png")
    elif element_type == 2: # multi
        cropped_path = crop_text_square_with_direction(view, t_f, b_r, 35, -666, f"q_text_{element_name}.png")
    elif element_type == 3: # circle
        cropped_path = crop_text_square_with_direction(view, t_f, b_r, 35, 650, f"q_text_{element_name}.png")

    return cropped_path

def get_element_n_text(view):
    """
    Detecta el elemento actual, recorta el área de la pregunta y extrae su texto por OCR.
    
    Args:
        view (str): Ruta de la captura de pantalla.
    
    Returns:
        tuple: (element_type (int), question_text (str))
    """
    print("[INFO] Searching for current element...")
    element_name, element_type, t_f, b_r = search_4_current_element(view)
    
    print(f"[INFO] Detected type: {element_type}, Coordinates: {t_f} to {b_r}")

    cropped_path = crop_by_element(
        view,
        element_name,
        element_type,
        t_f=t_f,
        b_r=b_r,
    )
    
    question_text = ocr.get_text(cropped_path, lang="eng+spa")
    print(f"[INFO] Extracted question text: {question_text}")

    return element_type, question_text

#testing
'''
if __name__ == "__main__":
    #test_fill = './assets/test/test_fill.png'
    #test_circle = './assets/test/test_circle.png'
    #test_multi = './assets/test/test_multi.png'

    #current_test = test_multi
    
    #current_test = './assets/test/test_snext.png'

    #print("Searching for current element...")
    #elemt_type, question_text = get_element_n_text(current_test)
    #print(f"Element type: {elemt_type}, Question text: {question_text}")

    found, t_f, b_r = search_4_selected_next(current_test)
    if found:
        print(f"Element found at: {t_f} to {b_r}")
        crop_text_square_simple(current_test, t_f, b_r, 60, 400, "q_text_selected_next.png")
    else:
        print("Element not found.")
'''
if __name__ == "__main__":
    print("testing ending element detection...XD")
    #found = search_4_sreview('./assets/test/test_srev.png')
    #found = search_4_ssubmit_app('./assets/test/test_ssub.png')
    #print(found)

    run_ending_element_detection('./assets/test/test_next.png')