/**
 * Create a DOM element with attributes and event handlers
 * @param {string} tag - HTML tag name
 * @param {Object} options - Element options
 * @returns {HTMLElement} - The created element
 */
export function createDOM(tag, options = {}) {
  const element = document.createElement(tag);
  
  // Set attributes and properties
  for (const [key, value] of Object.entries(options)) {
    // Handle event handlers
    if (key.startsWith('on') && typeof value === 'function') {
      const eventName = key.substring(2).toLowerCase();
      element.addEventListener(eventName, value);
    }
    // Handle innerHTML
    else if (key === 'innerHTML') {
      element.innerHTML = value;
    }
    // Handle innerText
    else if (key === 'innerText' || key === 'textContent') {
      element.textContent = value;
    }
    // Handle regular attributes
    else {
      element.setAttribute(key, value);
    }
  }
  
  return element;
}
