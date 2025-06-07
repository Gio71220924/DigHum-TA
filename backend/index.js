const express = require('express');
const multer = require('multer');
const Tesseract = require('tesseract.js');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
app.use(cors());
app.use(express.json());

const upload = multer({ dest: 'uploads/' });

// Tambahkan route ini:
app.get('/', (req, res) => {
  res.send('✅ OCR backend is running!');
});

app.post('/ocr', upload.single('image'), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No image uploaded' });

  const imagePath = path.resolve(req.file.path);

  try {
    const { data: { text } } = await Tesseract.recognize(imagePath, 'ind+eng', {
    logger: m => console.log(m),
    tessedit_pageseg_mode: 6
    });

    fs.unlinkSync(imagePath);
    res.json({ text });
  } catch (err) {
    res.status(500).json({ error: 'OCR failed', detail: err.message });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`✅ OCR backend running at http://localhost:${PORT}`));