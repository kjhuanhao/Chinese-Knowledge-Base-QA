fetch('http://127.0.0.1:8000/ask', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ question: 'how about the dormitory' })
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