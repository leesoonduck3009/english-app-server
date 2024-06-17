require('dotenv').config();
const express = require('express');
const multer = require('multer');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const app = express();
const port = 8080;
const upload = multer({ dest: 'uploads/' });
const OpenAI = require('openai');
const apiOpenAI = process.env.API_OPENAI
app.use(express.json());
const removeFirstThreeLines = (inputString) => {
    const lines = inputString.split('\n'); // Tách chuỗi thành các dòng
    const remainingLines = lines.slice(3); // Loại bỏ ba dòng đầu tiên
    const outputString = remainingLines.join('\n'); // Kết hợp các dòng còn lại thành chuỗi mới
    return outputString;
};
app.post('/detect', upload.single('image'), (req, res) => {
    const imagePath = req.file.path;
    console.log("Hello");
    // Gọi Python script để xử lý ảnh
    const pythonProcess = spawn('python', ['detect.py', imagePath, apiOpenAI]);

    let dataChunks = [];
    
    pythonProcess.stdout.on('data', (data) => {
        dataChunks.push(data);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
        res.status(500).json({data: data});
    });

    pythonProcess.on('close', (code) => {
        const output = Buffer.concat(dataChunks).toString();

        if (output) {
            try {
                console.log(output)
                //
                const cleanedString = removeFirstThreeLines(output);
                // Chuyển đổi chuỗi JSON thành đối tượng JavaScript
                const jsonData = JSON.parse(cleanedString);
                return res.status(200).json({data: jsonData});
            } catch (error) {
                console.error('Error parsing JSON:', error);
                res.status(500).send('Error parsing JSON output from Python script.');
            }
        } else {
            res.status(500).send('No output from Python script.');
        }

        fs.unlinkSync(imagePath); // Xóa file tạm sau khi xử lý xong
        console.log(`child process exited with code ${code}`);
    });
});
// app.post('/upload', upload.single('image'), (req, res) => {
//     const imagePath = req.file.path;
//     console.log(imagePath);
//     // Gọi Python script để xử lý ảnh
//     res.json({data: imagePath});
// });
app.get('/test', (req, res) => {
    //const imagePath = req.file.path;

    // Gọi Python script để xử lý ảnh
    res.json({data: apiOpenAI});
});
app.listen(port, () => {
    console.log(`Example app listening on port ${port}`);
  });