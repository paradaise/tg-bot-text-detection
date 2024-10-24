from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np
from ultralytics import YOLO  # Assuming YOLOv8 is used
import easyocr
import io


def preprocess_image(image):
    # Изменение размера изображения
    image = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)

    # Усиление контраста изображения
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.5)

    # Преобразование в оттенки серого и применение адаптивной бинаризации
    image = image.convert('L')
    image = ImageOps.invert(image)  # Инвертируем цвета для лучшего распознавания
    image = image.filter(ImageFilter.MedianFilter(size=1))  # Применяем медианный фильтр для удаления шума

    return image

def perform_ocr(image):
    # Инициализация OCR
    reader = easyocr.Reader(['ru', 'en'],gpu= True)

    # Выполнение OCR
    result = reader.readtext(np.array(image))

    # Сбор данных из результатов OCR
    boxes = []
    txts = []
    scores = []

    for line in result:
        boxes.append(line[0])
        txts.append(line[1])
        scores.append(line[2])

    return boxes, txts, scores

def perform_ocr(image):
    # Инициализация OCR
    reader = easyocr.Reader(['ru', 'en'],gpu= True)

    # Выполнение OCR
    result = reader.readtext(np.array(image))

    # Сбор данных из результатов OCR
    boxes = []
    txts = []
    scores = []

    for line in result:
        boxes.append(line[0])
        txts.append(line[1])
        scores.append(line[2])

    return boxes, txts, scores

def crop_and_ocr(img_path):
    results = yolo(img_path)
    regions = [box.xyxy[0].cpu().numpy().tolist() for reg in results for box in reg.boxes] if results[0].boxes is not None else []

    image = Image.open(img_path).convert('RGB')

    if regions:
        result_msg = '<i>Вот что мне удалось увидеть:</i>\n'
        result_imgs = []

        for i, region in enumerate(regions):
            cropped_image = image.crop(region)
            cropped_image = preprocess_image(cropped_image)
            boxes, txts, scores = perform_ocr(cropped_image)

            result_img = io.BytesIO()
            cropped_image.save(result_img, format='PNG')
            result_img = result_img.getvalue()
            result_imgs.append(result_img)

            for txt, score in zip(txts, scores):
                if (score > 0.4 and regions):
                    result_msg += f"{txt}: {score:.2f}%\n"

        return result_msg, result_imgs
    else:
        result_msg = 'Мне ничего не удалось найти🥺. Попробуйте другое фото'
        return result_msg, None

yolo = YOLO('best.pt')
