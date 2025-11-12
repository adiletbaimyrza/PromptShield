document.getElementById('anonymizeForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const userText = document.getElementById('userText').value;
  const loading = document.getElementById('loadingSection');
  const result = document.getElementById('resultSection');
  const error = document.getElementById('errorSection');
  
  loading.style.display = 'block';
  result.style.display = 'none';
  error.style.display = 'none';
  
  try {
    const response = await fetch('/anonymize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: userText })
    });
    
    const data = await response.json();
    
    document.getElementById('originalText').textContent = userText;
    document.getElementById('anonymizedText').textContent = data.anonymized;
    document.getElementById('entityCount').textContent = `${data.entities} found`;
    
    loading.style.display = 'none';
    result.style.display = 'block';
  } catch (err) {
    document.getElementById('errorMessage').textContent = 'Error processing prompt. Please try again.';
    loading.style.display = 'none';
    error.style.display = 'block';
  }
});

function copyToClipboard() {
  const text = document.getElementById('anonymizedText').textContent;
  navigator.clipboard.writeText(text).then(() => {
    alert('Copied to clipboard!');
  });
}
