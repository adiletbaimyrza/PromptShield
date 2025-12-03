document.getElementById('anonymize').addEventListener('click', async () => {
  const input = document.getElementById('input').value;
  const output = document.getElementById('output');
  
  if (!input.trim()) {
    output.textContent = 'Please enter some text';
    output.classList.remove('hidden');
    return;
  }
  
  try {
    const response = await fetch('http://localhost:5000/anonymize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: input })
    });
    
    const data = await response.json();
    output.textContent = data.result;
    output.classList.remove('hidden');
  } catch (error) {
    output.textContent = 'Error: Make sure the server is running on localhost:5000';
    output.classList.remove('hidden');
  }
});
