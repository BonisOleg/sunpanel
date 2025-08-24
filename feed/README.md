# 📦 GreenSolarTech JSON Feeds

Ця папка містить JSON фіди з усіма товарами каталогу GreenSolarTech.

## 📁 Структура файлів

### Основні файли:
- **`full_catalog.json`** - Повний каталог з усіма даними (152KB)
- **`products.json`** - Тільки товари (148KB)
- **`categories.json`** - Категорії товарів (1.4KB)
- **`brands.json`** - Бренди (2.5KB)

### Файли по категоріях:
- **`category_-1.json`** - Інвертори (59KB)
- **`category_-3.json`** - Акумуляторні батареї (52KB)
- **`category_-5.json`** - Сонячні панелі (20KB)
- **`category_.json`** - Комплекти резервного живлення (16KB)
- **`category_-2.json`** - Додаткові послуги (2.5KB)

### Файли по брендах:
- **`brand_deye.json`** - Deye (71KB)
- **`brand_must.json`** - Must (33KB)
- **`brand_lvtopsun.json`** - Lvtopsun (20KB)
- **`brand_longi-solar.json`** - LONGi Solar (17KB)
- **`brand_risen-energy.json`** - Risen Energy (3.7KB)
- **`brand_topsun.json`** - TopSun (3.7KB)

## 📊 Статистика

- **Товарів**: 42
- **Категорій**: 5
- **Брендів**: 10
- **Файлів**: 19
- **Загальний розмір**: ~500KB

## 🔧 Структура JSON

### Метадані (meta):
```json
{
  "export_date": "2025-08-01T12:51:37.764292+00:00",
  "total_products": 42,
  "total_categories": 5,
  "total_brands": 10,
  "version": "1.0",
  "source": "GreenSolarTech Catalog"
}
```

### Товар (product):
```json
{
  "id": 854,
  "name": "Гібридний інвертор Deye 80 кВт",
  "description": "Опис товару...",
  "price": 274000.0,
  "model": "Deye Model",
  "power": "80 кВт",
  "efficiency": "98%",
  "warranty": "5 років",
  "country": "Китай",
  "in_stock": true,
  "featured": false,
  "created_at": "2025-07-27T09:42:22.543501+00:00",
  "updated_at": "2025-07-27T09:45:31.436679+00:00",
  "category": {
    "id": 47,
    "name": "Інвертори",
    "slug": "-1"
  },
  "brand": {
    "id": 6,
    "name": "Deye",
    "slug": "deye"
  },
  "images": [
    {
      "type": "main",
      "url": "https://greensolartech.com.ua/media/products/...",
      "alt": "Назва товару"
    },
    {
      "type": "gallery",
      "url": "https://greensolartech.com.ua/media/products/gallery/...",
      "alt": "Опис зображення",
      "is_main": false,
      "order": 1
    }
  ]
}
```

## 🚀 Використання

### Отримання всіх товарів:
```javascript
fetch('/feed/products.json')
  .then(response => response.json())
  .then(data => {
    console.log('Товари:', data.products);
  });
```

### Отримання товарів категорії:
```javascript
fetch('/feed/category_-1.json') // Інвертори
  .then(response => response.json())
  .then(data => {
    console.log('Інвертори:', data.products);
  });
```

### Отримання товарів бренду:
```javascript
fetch('/feed/brand_deye.json')
  .then(response => response.json())
  .then(data => {
    console.log('Товари Deye:', data.products);
  });
```

## 🔄 Оновлення фідів

Для оновлення фідів запустіть команду:

```bash
python manage.py export_products_json --include-images
```

## 📈 API Endpoints

- **Всі товари**: `/feed/products.json`
- **Повний каталог**: `/feed/full_catalog.json`
- **Категорії**: `/feed/categories.json`
- **Бренди**: `/feed/brands.json`
- **Товари категорії**: `/feed/category_{slug}.json`
- **Товари бренду**: `/feed/brand_{slug}.json`

## 🎯 Призначення

Ці JSON фіди можна використовувати для:
- Інтеграції з зовнішніми системами
- Створення мобільних додатків
- Партнерських програм
- Аналітики та звітності
- SEO оптимізації
- Розробки API

## 📝 Примітки

- Всі ціни в гривнях (UAH)
- Дати в форматі ISO 8601
- Зображення доступні через HTTPS
- Кодування UTF-8
- Формат JSON з відступами для читабельності 