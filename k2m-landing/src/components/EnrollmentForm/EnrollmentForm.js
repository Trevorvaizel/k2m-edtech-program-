/**
 * Enrollment Form Modal Controller - Task 7.1
 * Integrates with /api/interest endpoint from cis-discord-bot
 * Handles form submission, validation, success/error states
 */

const INTEREST_API_URL = import.meta.env.VITE_INTEREST_API_URL || 'http://localhost:8081/api/interest';

export function initEnrollmentForm() {
  const modal = document.getElementById('enrollmentModal');
  const form = document.getElementById('enrollmentForm');
  const backdrop = document.getElementById('modalBackdrop');
  const closeBtn = document.getElementById('modalClose');
  const successMsg = document.getElementById('formSuccess');
  const errorMsg = document.getElementById('formError');
  const submitBtn = document.getElementById('formSubmit');
  const errorRetry = document.getElementById('errorRetry');

  if (!modal || !form) {
    console.warn('Enrollment form modal not found - skipping initialization');
    return;
  }

  // Open modal function (exported for use by other components)
  window.openEnrollmentForm = function() {
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    console.log('✅ Enrollment form opened');
  };

  // Close modal function
  const closeModal = () => {
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    // Reset form state after close animation
    setTimeout(() => {
      form.reset();
      form.classList.remove('hidden');
      successMsg.hidden = true;
      errorMsg.hidden = true;
      submitBtn.disabled = false;
    }, 300);
  };

  // Close on backdrop click
  if (backdrop) {
    backdrop.addEventListener('click', closeModal);
  }

  // Close on X button
  if (closeBtn) {
    closeBtn.addEventListener('click', closeModal);
  }

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.getAttribute('aria-hidden') === 'false') {
      closeModal();
    }
  });

  // Form submission
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const data = {
      name: formData.get('name')?.trim() || '',
      email: formData.get('email')?.trim() || '',
      phone: formData.get('phone')?.trim() || '',
      profession: formData.get('profession') || 'Other'
    };

    // Client-side validation
    if (!data.name || !data.email || !data.phone) {
      showError('Please fill in all required fields.');
      return;
    }

    if (!isValidEmail(data.email)) {
      showError('Please enter a valid email address.');
      return;
    }

    // Show loading state
    submitBtn.disabled = true;
    submitBtn.querySelector('.submit-text').textContent = 'Submitting...';
    submitBtn.querySelector('.submit-loader').hidden = false;

    try {
      const response = await fetch(INTEREST_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });

      const result = await response.json();

      if (response.ok && result.success) {
        // Success
        form.classList.add('hidden');
        successMsg.hidden = false;
        console.log('✅ Enrollment successful:', result);

        // Track conversion (optional)
        if (window.gtag) {
          window.gtag('event', 'generate_lead', {
            'event_category': 'enrollment',
            'event_label': result.waitlisted ? 'waitlist' : 'enrolled'
          });
        }
      } else {
        // API returned error
        showError(result.error || 'Something went wrong. Please try again.');
      }
    } catch (error) {
      console.error('❌ Enrollment submission error:', error);
      showError('Network error. Please check your connection and try again.');
    } finally {
      submitBtn.disabled = false;
      submitBtn.querySelector('.submit-text').textContent = 'Enroll Now';
      submitBtn.querySelector('.submit-loader').hidden = true;
    }
  });

  // Error display function
  function showError(message) {
    form.classList.add('hidden');
    errorMsg.hidden = false;
    document.getElementById('errorText').textContent = message;
  }

  // Retry button (resets form)
  if (errorRetry) {
    errorRetry.addEventListener('click', () => {
      errorMsg.hidden = true;
      form.classList.remove('hidden');
    });
  }

  console.log('✅ Enrollment form initialized');
}

/**
 * Email validation helper
 */
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Export for use in ProgramMatcher
 */
export function openEnrollmentFormForSegment(segment) {
  if (window.openEnrollmentForm) {
    window.openEnrollmentForm();

    // Pre-select profession if segment maps to one
    const professionSelect = document.getElementById('enrollmentProfession');
    if (professionSelect) {
      const professionMap = {
        'gap-year': 'Gap Year Student',
        'teacher': 'Teacher / Educator',
        'professional': 'Working Professional'
      };

      const mappedProfession = professionMap[segment];
      if (mappedProfession) {
        professionSelect.value = mappedProfession;
      }
    }
  }
}
