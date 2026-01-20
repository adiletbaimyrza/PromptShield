// Store the mapping globally
let currentMapping = {};

document.getElementById('anonymize').addEventListener('click', async () => {
  const input = document.getElementById('input').value;
  const output = document.getElementById('output');
  const copyBtn = document.getElementById('copy');
  const anonymizeBtn = document.getElementById('anonymize');
  
  if (!input.trim()) {
    output.innerHTML = '<span class="error">Please enter some text</span>';
    output.classList.remove('hidden');
    copyBtn.classList.add('hidden');
    return;
  }
  
  // Disable button during request
  anonymizeBtn.disabled = true;
  anonymizeBtn.textContent = 'Processing...';
  
  try {
    const response = await fetch('http://localhost:5000/anonymize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: input })
    });
    
    const data = await response.json();
    currentMapping = data.mapping || {};
    
    // Make placeholders clickable
    makeClickable(data.result);
    
    output.classList.remove('hidden');
    copyBtn.classList.remove('hidden');
  } catch (error) {
    output.innerHTML = '<span class="error">Error: Make sure the server is running on localhost:5000</span>';
    output.classList.remove('hidden');
    copyBtn.classList.add('hidden');
  } finally {
    anonymizeBtn.disabled = false;
    anonymizeBtn.textContent = 'Anonymize';
  }
});

// Make placeholders clickable
function makeClickable(text) {
  const output = document.getElementById('output');
  
  // Replace all placeholders with clickable spans
  const placeholderPattern = /\[([A-Z_\-À-ÿ\s]+)_(\d+)\]/g;
  let html = text.replace(placeholderPattern, function(match) {
    return `<span class="placeholder" data-placeholder="${match}" data-state="placeholder">${match}</span>`;
  });
  
  output.innerHTML = html;
  
  // Add click listeners to all placeholders
  const placeholders = output.querySelectorAll('.placeholder');
  placeholders.forEach(placeholder => {
    placeholder.addEventListener('click', function() {
      togglePlaceholder(this);
    });
  });
}

// Toggle between placeholder and original value
function togglePlaceholder(element) {
  const placeholder = element.dataset.placeholder;
  const currentState = element.dataset.state;
  
  if (currentState === 'placeholder') {
    // Restore to original value
    if (!currentMapping[placeholder]) return;
    
    const originalValue = currentMapping[placeholder];
    element.textContent = originalValue;
    element.classList.add('restored');
    element.dataset.state = 'restored';
    element.title = `Click to show ${placeholder}`;
  } else {
    // Restore to placeholder
    element.textContent = placeholder;
    element.classList.remove('restored');
    element.dataset.state = 'placeholder';
    element.title = 'Click to restore original value';
  }
}

// Copy to clipboard
document.getElementById('copy').addEventListener('click', () => {
  const output = document.getElementById('output');
  const text = output.textContent;
  const copyBtn = document.getElementById('copy');
  
  navigator.clipboard.writeText(text).then(() => {
    const originalText = copyBtn.textContent;
    copyBtn.textContent = 'Copied!';
    copyBtn.classList.add('copied');
    
    setTimeout(() => {
      copyBtn.textContent = originalText;
      copyBtn.classList.remove('copied');
    }, 2000);
  });
});
