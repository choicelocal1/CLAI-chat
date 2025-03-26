import { createDOM } from '../utils/dom';

export class LeadForm {
  constructor(options) {
    this.onSubmit = options.onSubmit;
    this.fields = options.fields || ['name', 'email', 'phone'];
    
    this.element = this.render();
  }
  
  render() {
    const formContainer = createDOM('div', { 
      className: 'clai-chat-form',
      id: 'clai-lead-form'
    });
    
    // Create form fields
    this.fields.forEach(field => {
      const fieldContainer = createDOM('div', { className: 'clai-chat-form-field' });
      
      const label = createDOM('label', {
        for: `clai-form-${field}`,
        innerText: this.getFieldLabel(field)
      });
      
      const input = createDOM('input', {
        type: this.getInputType(field),
        id: `clai-form-${field}`,
        name: field,
        placeholder: this.getPlaceholder(field),
        required: this.isRequired(field)
      });
      
      fieldContainer.appendChild(label);
      fieldContainer.appendChild(input);
      formContainer.appendChild(fieldContainer);
    });
    
    // Create submit button
    const submitButton = createDOM('button', {
      className: 'clai-chat-form-submit',
      type: 'button',
      innerText: 'Submit',
      onClick: () => this.handleSubmit()
    });
    
    formContainer.appendChild(submitButton);
    
    return formContainer;
  }
  
  handleSubmit() {
    const formData = {};
    
    // Collect form data
    this.fields.forEach(field => {
      const input = document.getElementById(`clai-form-${field}`);
      formData[field] = input.value;
      
      // Basic validation
      if (this.isRequired(field) && !input.value) {
        input.classList.add('error');
        return;
      }
    });
    
    // Check if required fields are filled
    const allFilled = this.fields
      .filter(field => this.isRequired(field))
      .every(field => document.getElementById(`clai-form-${field}`).value);
    
    if (allFilled) {
      this.onSubmit(formData);
      
      // Remove form
      this.element.remove();
    }
  }
  
  getFieldLabel(field) {
    const labels = {
      name: 'Name',
      email: 'Email',
      phone: 'Phone',
      company: 'Company',
      message: 'Message'
    };
    
    return labels[field] || field.charAt(0).toUpperCase() + field.slice(1);
  }
  
  getInputType(field) {
    if (field === 'email') return 'email';
    if (field === 'phone') return 'tel';
    if (field === 'message') return 'textarea';
    return 'text';
  }
  
  getPlaceholder(field) {
    const placeholders = {
      name: 'Your name',
      email: 'your.email@example.com',
      phone: '(123) 456-7890',
      company: 'Your company name',
      message: 'Your message'
    };
    
    return placeholders[field] || '';
  }
  
  isRequired(field) {
    // Make email and name required by default
    return field === 'email' || field === 'name';
  }
}
