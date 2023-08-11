//此测试文件为废弃方案
fetch('http://127.0.0.1:8000/ask', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ question: '宿舍是上床下桌吗' })
})
  .then(response => {
    const reader = response.body.getReader();
    return new ReadableStream({
      start(controller) {
        function read() {
          reader.read().then(({ done, value }) => {
            if (done) {
              controller.close();
              return;
            }
            const decodedString = new TextDecoder().decode(value);
            console.log(decodedString);
            read();
          });
        }
        read();
      }
    });
  })
  .catch(error => console.error(error));